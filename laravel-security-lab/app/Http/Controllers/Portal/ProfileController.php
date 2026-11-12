<?php

namespace App\Http\Controllers\Portal;

use App\Http\Controllers\Controller;
use App\Http\Requests\UpdateProfileRequest;
use App\Models\SecurityLog;
use App\Support\SecurityConfig;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class ProfileController extends Controller
{
    public function edit(Request $request): View
    {
        return view('portal.profile', [
            'user' => $request->user(),
        ]);
    }

    public function update(Request $request): RedirectResponse
    {
        $user = $request->user();
        $hardened = SecurityConfig::isHardened();

        if (! $hardened) {
            $payload = $request->only(['name', 'email', 'role']);
            // VOLONTAIREMENT VULNÉRABLE : forceFill contourne #[Fillable] et accepte un <input name="role"> injecté via F12
            $user->forceFill($payload)->save();
            $user->refresh();

            SecurityLog::create([
                'pillar' => '2. Mass Assignment',
                'mode' => 'vulnerable',
                'actor' => $user->name,
                'payload' => json_encode($payload, JSON_UNESCAPED_UNICODE),
                'executed_sql' => "UPDATE users SET role='{$user->role}' WHERE id = {$user->id}",
                'outcome' => $user->isAdmin() ? 'exploited' : 'info',
                'ip_address' => $request->ip(),
            ]);

            return redirect()->route('portal.profile')->with('status', 'Vos informations personnelles ont été enregistrées.');
        }

        $formRequest = UpdateProfileRequest::createFrom($request);
        $formRequest->setContainer(app())->setRedirector(app('redirect'));
        $formRequest->validateResolved();
        $validated = $formRequest->validated();

        // SÉCURISÉ : validated() ne retient que name & email, et #[Fillable] verrouille role
        $user->update($validated);

        return redirect()->route('portal.profile')->with('status', 'Votre profil a été mis à jour avec succès.');
    }
}
