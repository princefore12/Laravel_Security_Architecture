<?php

namespace App\Http\Controllers\Lab;

use App\Http\Controllers\Controller;
use App\Http\Requests\UpdateProfileRequest;
use App\Models\User;
use App\Services\SqlInspectorService;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class MassAssignmentController extends Controller
{
    public function __construct(private readonly SqlInspectorService $inspector)
    {
    }

    public function index(Request $request): View
    {
        $mode = $request->query('mode', 'vulnerable') === 'secure' ? 'secure' : 'vulnerable';
        $targetUser = User::query()->where('email', 'mody.siby@loko.ci')->firstOrFail();

        return view('lab.mass-assignment', [
            'mode' => $mode,
            'targetUser' => $targetUser,
            'queries' => session('lab_ma_queries', []),
            'outcomeMessage' => session('lab_ma_message'),
            'outcomeType' => session('lab_ma_type'),
        ]);
    }

    public function updateVulnerable(Request $request): RedirectResponse
    {
        $user = User::query()->where('email', 'mody.siby@loko.ci')->firstOrFail();
        $attemptedRole = $request->input('role', 'student');

        $captured = $this->inspector->capture(function () use ($user, $request): void {
            // VOLONTAIREMENT VULNÉRABLE : forceFill() contourne #[Fillable] et écrit 'role'
            $user->forceFill($request->only(['name', 'email', 'role']))->save();
        });

        $user->refresh();
        $exploited = $user->role === 'admin';
        $this->inspector->record(
            $request,
            '2. Mass Assignment',
            'vulnerable',
            'Siby Mody',
            json_encode($request->only(['name', 'email', 'role']), JSON_UNESCAPED_UNICODE),
            $captured['queries'],
            $exploited ? 'exploited' : 'info'
        );

        return redirect()->route('lab.mass-assignment', ['mode' => 'vulnerable'])
            ->with('lab_ma_queries', $captured['queries'])
            ->with('lab_ma_type', $exploited ? 'exploited' : 'info')
            ->with('lab_ma_message', $exploited
                ? "ESCALADE DE PRIVILÈGES RÉUSSIE : le champ caché role={$attemptedRole} a modifié la base MariaDB ! Siby Mody est maintenant ADMIN."
                : 'Profil mis à jour en mode vulnérable (rôle inchangé).');
    }

    public function updateSecure(UpdateProfileRequest $request): RedirectResponse
    {
        $user = User::query()->where('email', 'mody.siby@loko.ci')->firstOrFail();
        $attemptedRole = $request->input('role');

        $captured = $this->inspector->capture(function () use ($user, $request): void {
            // SÉCURISÉ : Double barrière UpdateProfileRequest::validated() + User #[Fillable]
            $user->update($request->validated());
        });

        $user->refresh();
        $blockedAttempt = $attemptedRole !== null && $attemptedRole !== $user->role;

        $this->inspector->record(
            $request,
            '2. Mass Assignment',
            'secure',
            'Siby Mody',
            json_encode($request->only(['name', 'email', 'role']), JSON_UNESCAPED_UNICODE),
            $captured['queries'],
            $blockedAttempt ? 'blocked' : 'info'
        );

        return redirect()->route('lab.mass-assignment', ['mode' => 'secure'])
            ->with('lab_ma_queries', $captured['queries'])
            ->with('lab_ma_type', $blockedAttempt ? 'blocked' : 'info')
            ->with('lab_ma_message', $blockedAttempt
                ? "ATTAQUE BLOQUÉE : le paramètre injecté role={$attemptedRole} a été rejeté par FormRequest + #[Fillable]. Rôle en BDD : {$user->role}."
                : 'Profil mis à jour de manière sécurisée (rôle protégé).');
    }

    public function resetRole(Request $request): RedirectResponse
    {
        $user = User::query()->where('email', 'mody.siby@loko.ci')->firstOrFail();
        $user->forceFill(['role' => 'student', 'name' => 'Siby Mody'])->save();

        return redirect()->route('lab.mass-assignment', ['mode' => $request->input('mode', 'vulnerable')])
            ->with('lab_ma_type', 'info')
            ->with('lab_ma_message', 'Compte Siby Mody réinitialisé au rôle légitime STUDENT.');
    }
}
