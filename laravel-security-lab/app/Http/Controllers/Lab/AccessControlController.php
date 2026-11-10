<?php

namespace App\Http\Controllers\Lab;

use App\Http\Controllers\Controller;
use App\Models\Grade;
use App\Models\User;
use App\Services\SqlInspectorService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\View\View;

class AccessControlController extends Controller
{
    public function __construct(private readonly SqlInspectorService $inspector)
    {
    }

    private function actingUser(Request $request): User
    {
        $email = $request->session()->get('lab_acting_user_email', 'ramatou.sore@loko.ci');

        return User::query()->where('email', $email)->first()
            ?? User::query()->orderBy('id')->firstOrFail();
    }

    public function index(Request $request): View
    {
        $mode = $request->query('mode', 'vulnerable') === 'secure' ? 'secure' : 'vulnerable';
        $actingUser = $this->actingUser($request);
        $grades = Grade::with('student.user')->orderBy('id')->get();
        $rateKey = 'lab-login:' . $request->ip();

        return view('lab.access-control', [
            'mode' => $mode,
            'actingUser' => $actingUser,
            'grades' => $grades,
            'hashComparison' => session('lab_hash_comparison'),
            'inspectedGrade' => session('lab_inspected_grade'),
            'idorOutcome' => session('lab_idor_outcome'),
            'idorQueries' => session('lab_idor_queries', []),
            'remainingAttempts' => RateLimiter::remaining($rateKey, 5),
        ]);
    }

    public function switchActor(Request $request): RedirectResponse
    {
        $email = $request->input('email', 'ramatou.sore@loko.ci');
        if (in_array($email, ['ramatou.sore@loko.ci', 'mody.siby@loko.ci', 'admin@loko.ci'], true)) {
            $request->session()->put('lab_acting_user_email', $email);
        }

        return redirect()->route('lab.access', ['mode' => $request->input('mode', 'vulnerable')]);
    }

    public function showGradeVulnerable(Request $request, Grade $grade): View|RedirectResponse
    {
        $actingUser = $this->actingUser($request);
        $captured = $this->inspector->capture(function () use ($grade): Grade {
            return $grade->load('student.user');
        });

        $isForeign = $grade->student?->user_id !== $actingUser->id && ! $actingUser->isAdmin();
        $this->inspector->record(
            $request,
            '5. IDOR / Policy',
            'vulnerable',
            $actingUser->name,
            "GET /lab/access-control/vulnerable/grades/{$grade->id}",
            $captured['queries'],
            $isForeign ? 'exploited' : 'info'
        );

        if ($request->wantsJson() || $request->query('direct') === '1') {
            return view('lab.grade-detail', [
                'grade' => $grade,
                'actingUser' => $actingUser,
                'mode' => 'vulnerable',
                'isForeign' => $isForeign,
            ]);
        }

        return redirect()->route('lab.access', ['mode' => 'vulnerable'])
            ->with('lab_inspected_grade', $grade->toArray() + ['student_name' => $grade->student?->full_name])
            ->with('lab_idor_outcome', $isForeign ? 'exploited' : 'own')
            ->with('lab_idor_queries', $captured['queries']);
    }

    public function showGradeSecure(Request $request, Grade $grade): View|RedirectResponse
    {
        $actingUser = $this->actingUser($request);
        $grade->load('student.user');

        $allowed = Gate::forUser($actingUser)->allows('view', $grade);
        $this->inspector->record(
            $request,
            '5. IDOR / Policy',
            'secure',
            $actingUser->name,
            "GET /lab/access-control/secure/grades/{$grade->id}",
            [],
            $allowed ? 'info' : 'blocked'
        );

        if (! $allowed) {
            // Lors des tests automatisés ou accès direct URL, retourner un véritable HTTP 403 Forbidden
            if ($request->query('inline') !== '1') {
                abort(403, 'ACCÈS INTERDIT (HTTP 403) : GradePolicy refuse la consultation du dossier d\'un autre étudiant.');
            }

            return redirect()->route('lab.access', ['mode' => 'secure'])
                ->with('lab_idor_outcome', 'blocked');
        }

        if ($request->query('inline') !== '1') {
            return view('lab.grade-detail', [
                'grade' => $grade,
                'actingUser' => $actingUser,
                'mode' => 'secure',
                'isForeign' => false,
            ]);
        }

        return redirect()->route('lab.access', ['mode' => 'secure'])
            ->with('lab_inspected_grade', $grade->toArray() + ['student_name' => $grade->student?->full_name])
            ->with('lab_idor_outcome', 'own');
    }

    public function compareHash(Request $request): RedirectResponse
    {
        $plain = (string) $request->input('plain_password', 'Loko@2026!');
        if ($plain === '') {
            $plain = 'Loko@2026!';
        }

        $md5_a = md5($plain);
        $md5_b = md5($plain);
        $bcrypt_a = Hash::make($plain);
        $bcrypt_b = Hash::make($plain);

        return redirect()->route('lab.access', ['mode' => $request->input('mode', 'secure')])
            ->with('lab_hash_comparison', [
                'plain' => $plain,
                'md5_a' => $md5_a,
                'md5_b' => $md5_b,
                'bcrypt_a' => $bcrypt_a,
                'bcrypt_b' => $bcrypt_b,
                'verified' => Hash::check($plain, $bcrypt_a),
            ]);
    }

    public function attemptLogin(Request $request): JsonResponse
    {
        $key = 'lab-login:' . $request->ip();

        if (RateLimiter::tooManyAttempts($key, 5)) {
            $seconds = RateLimiter::availableIn($key);
            $this->inspector->record(
                $request,
                '5. RateLimiter',
                'secure',
                'Djan Kouassi Noël',
                'Tentative de connexion brute-force bloquée',
                [],
                'blocked'
            );

            return response()->json([
                'status' => 'blocked',
                'http_code' => 429,
                'message' => "HTTP 429 Too Many Requests : Trop de tentatives ! Réessayez dans {$seconds}s.",
                'remaining' => 0,
            ], 429);
        }

        RateLimiter::hit($key, 60);
        $remaining = RateLimiter::remaining($key, 5);

        return response()->json([
            'status' => 'failed',
            'http_code' => 401,
            'message' => "HTTP 401 Unauthorized : Mot de passe invalide. Essais restants avant blocage : {$remaining}",
            'remaining' => $remaining,
        ], 401);
    }

    public function clearRateLimit(Request $request): JsonResponse
    {
        RateLimiter::clear('lab-login:' . $request->ip());

        return response()->json(['status' => 'cleared', 'remaining' => 5]);
    }
}
