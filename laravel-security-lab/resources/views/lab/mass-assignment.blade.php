@extends('layouts.lab')

@section('title', 'Pilier 2 — Mass Assignment')

@section('content')
<div class="mode-switcher">
    <div>
        <div style="font-size:11.5px; color:#8B1518; font-weight:800;">PILIER 2 (04:00 – 08:00) • INTERVENANT : SIBY MODY</div>
        <h2 style="font-size:22px; font-weight:900; color:#0F172A;">Atelier 2 : Mass Assignment &amp; Validation <code>FormRequest</code></h2>
    </div>
    <div style="display:flex; gap:10px; align-items:center;">
        <span class="mode-badge {{ $mode === 'vulnerable' ? 'vuln' : 'sec' }}">
            {{ $mode === 'vulnerable' ? '🔴 MODE VULNÉRABLE ACTIF' : '🟢 MODE SÉCURISÉ ACTIF' }}
        </span>
        <a href="{{ route('lab.mass-assignment', ['mode' => 'vulnerable']) }}" class="btn {{ $mode === 'vulnerable' ? 'btn-vuln' : 'btn-ghost' }}">🔴 Vulnérable</a>
        <a href="{{ route('lab.mass-assignment', ['mode' => 'secure']) }}" class="btn {{ $mode === 'secure' ? 'btn-sec' : 'btn-ghost' }}">🟢 Sécurisé</a>
    </div>
</div>

@if($outcomeMessage)
    <div class="alert {{ $outcomeType === 'exploited' ? 'alert-exploited' : ($outcomeType === 'blocked' ? 'alert-blocked' : 'alert-info') }}">
        {{ $outcomeMessage }}
    </div>
@endif

@if($errors->any())
    <div class="alert alert-blocked">
        ✅ Validation <code>UpdateProfileRequest</code> : {{ $errors->first() }}
    </div>
@endif

<div class="grid-2">
    <div class="card {{ $mode === 'vulnerable' ? 'card-vuln' : 'card-sec' }}">
        <h3 style="font-size:16px; color:#0F172A; margin-bottom:12px;">📝 Formulaire de Mise à Jour du Profil Étudiant</h3>

        <form method="POST" action="{{ $mode === 'vulnerable' ? route('lab.mass-assignment.vulnerable') : route('lab.mass-assignment.secure') }}">
            @csrf
            <div style="margin-bottom:12px;">
                <label for="ma_name">Nom complet</label>
                <input type="text" id="ma_name" name="name" value="{{ old('name', $targetUser->name) }}" required>
            </div>
            <div style="margin-bottom:12px;">
                <label for="ma_email">Adresse e-mail</label>
                <input type="email" id="ma_email" name="email" value="{{ old('email', $targetUser->email) }}" required>
            </div>

            <div style="background:#FFFBEB; border:1px dashed #D97706; border-radius:10px; padding:12px; margin-bottom:14px;">
                <label for="ma_role" style="color:#92400E;">🕵️ Champ caché injecté par l'attaquant (via DevTools F12)</label>
                <select id="ma_role" name="role">
                    <option value="student">role = "student" (Légitime)</option>
                    <option value="admin" selected>role = "admin" (Tentative d'escalade !)</option>
                </select>
            </div>

            <button type="submit" class="btn {{ $mode === 'vulnerable' ? 'btn-vuln' : 'btn-sec' }}" style="width:100%; justify-content:center;">
                {{ $mode === 'vulnerable' ? '💀 Soumettre via forceFill($request->all())' : '🛡️ Soumettre via UpdateProfileRequest + #[Fillable]' }}
            </button>
        </form>
    </div>

    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
            <h3 style="font-size:16px; color:#0F172A;">🗄️ État Actuel en Base MariaDB (<code>users</code>)</h3>
            <form method="POST" action="{{ route('lab.mass-assignment.reset-role') }}">
                @csrf
                <input type="hidden" name="mode" value="{{ $mode }}">
                <button type="submit" class="btn btn-ghost" style="padding:5px 10px; font-size:12px;">↺ Remettre en student</button>
            </form>
        </div>

        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:12px; padding:16px; margin-bottom:16px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; flex-wrap:wrap; gap:8px;">
                <strong style="font-size:17px; color:#0F172A;">{{ $targetUser->name }}</strong>
                @if($targetUser->role === 'admin')
                    <span class="mode-badge vuln">⚠️ RÔLE BDD : ADMIN (COMPROMIS !)</span>
                @else
                    <span class="mode-badge sec">✅ RÔLE BDD : STUDENT (INTÈGRE)</span>
                @endif
            </div>
            <p style="font-size:13px; color:#475569;">E-mail : <code>{{ $targetUser->email }}</code> • ID : {{ $targetUser->id }}</p>
        </div>

        <h4 style="font-size:13.5px; color:#8B1518; margin-bottom:6px;">Code exécuté dans le modèle &amp; le contrôleur :</h4>
        @if($mode === 'vulnerable')
<pre>// ❌ VULNÉRABLE : contourne #[Fillable] et écrit 'role'
$user->forceFill($request->only(['name', 'email', 'role']))->save();</pre>
        @else
<pre>// ✅ SÉCURISÉ : app/Models/User.php
#[Fillable(['name', 'email', 'password'])] // 'role' absent !

// ✅ Contrôleur avec FormRequest :
$user->update($request->validated());</pre>
        @endif
    </div>
</div>

@include('lab.partials.sql-inspector', ['queries' => $queries])
@endsection
