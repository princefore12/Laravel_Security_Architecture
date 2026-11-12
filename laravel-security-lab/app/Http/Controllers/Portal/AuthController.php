<?php

namespace App\Http\Controllers\Portal;

use App\Http\Controllers\Controller;
use App\Models\SecurityLog;
use App\Models\User;
use App\Support\SecurityConfig;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\View\View;

class AuthController extends Controller
{
    public function showLogin(Request $request): View
    {
        $rateKey = 'portal-login:' . $request->ip();

        return view('portal.login', [
            'remainingAttempts' => SecurityConfig::isHardened()
                ? RateLimiter::remaining($rateKey, 5)
                : null,
        ]);
    }

    public function login(Request $request): RedirectResponse|Response|View
    {
        $email = (string) $request->input('email', '');
        $password = (string) $request->input('password', '');
        $hardened = SecurityConfig::isHardened();

        if (! $hardened) {
            return $this->attemptVulnerableLogin($request, $email, $password);
        }

        $rateKey = 'portal-login:' . $request->ip();
        if (RateLimiter::tooManyAttempts($rateKey, 5)) {
            $seconds = RateLimiter::availableIn($rateKey);
            SecurityLog::create([
                'pillar' => 'Authentification',
                'mode' => 'secure',
                'actor' => $email !== '' ? $email : 'Anonyme',
                'payload' => 'HTTP 429 Too Many Requests',
                'executed_sql' => 'RateLimiter lock (max 5 essais/min)',
                'outcome' => 'blocked',
                'ip_address' => $request->ip(),
            ]);

            return response()->view('portal.login', [
                'authError' => "Trop de tentatives de connexion. Compte temporairement verrouillé pendant {$seconds} secondes (HTTP 429).",
                'remainingAttempts' => 0,
                'oldEmail' => $email,
            ], 429);
        }

        RateLimiter::hit($rateKey, 60);

        $validated = $request->validate([
            'email' => ['required', 'string', 'max:150'],
            'password' => ['required', 'string'],
        ]);

        $user = User::query()->where('email', $validated['email'])->first();

        if (! $user || ! Hash::check($validated['password'], $user->password)) {
            SecurityLog::create([
                'pillar' => 'Authentification',
                'mode' => 'secure',
                'actor' => $validated['email'],
                'payload' => 'Identifiants rejetés (bcrypt + requête préparée)',
                'executed_sql' => 'SELECT * FROM users WHERE email = ? LIMIT 1',
                'outcome' => 'blocked',
                'ip_address' => $request->ip(),
            ]);

            return response()->view('portal.login', [
                'authError' => 'Adresse e-mail ou mot de passe incorrect.',
                'remainingAttempts' => RateLimiter::remaining($rateKey, 5),
                'oldEmail' => $validated['email'],
            ], 401);
        }

        RateLimiter::clear($rateKey);
        Auth::login($user);
        $request->session()->regenerate();

        return redirect()->route('portal.home')->with('status', "Bienvenue, {$user->name}.");
    }

    public function logout(Request $request): RedirectResponse
    {
        Auth::logout();
        $request->session()->invalidate();
        $request->session()->regenerateToken();

        return redirect()->route('portal.home');
    }

    private function attemptVulnerableLogin(Request $request, string $email, string $password): RedirectResponse|Response|View
    {
        $md5 = md5($password);
        // VOLONTAIREMENT VULNÉRABLE : concaténation directe dans SQL + MD5 sans sel
        $sql = "SELECT id, name, email, role FROM users WHERE email = '{$email}' AND legacy_md5 = '{$md5}' LIMIT 1";
        $rows = DB::select($sql);

        if (count($rows) > 0) {
            $row = $rows[0];
            $user = User::query()->find($row->id);
            if ($user) {
                Auth::login($user);
                $isBypass = $user->email !== $email;
                SecurityLog::create([
                    'pillar' => 'Injection SQL (Auth)',
                    'mode' => 'vulnerable',
                    'actor' => $user->name,
                    'payload' => $email,
                    'executed_sql' => $sql,
                    'outcome' => $isBypass ? 'exploited' : 'info',
                    'ip_address' => $request->ip(),
                ]);

                return redirect()->route('portal.home');
            }
        }

        return response()->view('portal.login', [
            'authError' => 'Identifiants invalides sur le portail.',
            'remainingAttempts' => null,
            'oldEmail' => $email,
        ], 401);
    }
}
