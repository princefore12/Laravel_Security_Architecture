@extends('layouts.lab')

@section('title', 'Pilier 4 — Faille CSRF & Jeton CSRF')

@section('content')
<div class="mode-switcher">
    <div>
        <div style="font-size:11.5px; color:#8B1518; font-weight:800;">PILIER 4 (12:00 – 16:00) • INTERVENANTE : TRAORÉ CHARIFAT LEYLA</div>
        <h2 style="font-size:22px; font-weight:900; color:#0F172A;">Atelier 4 : Cross-Site Request Forgery (CSRF) &amp; Jeton <code>@@csrf</code></h2>
    </div>
    <div style="display:flex; gap:10px; align-items:center;">
        <span class="mode-badge {{ $mode === 'vulnerable' ? 'vuln' : 'sec' }}">
            {{ $mode === 'vulnerable' ? '🔴 ROUTE EXEMPTE DE CSRF' : '🟢 VALIDATECSRFTOKEN ACTIF' }}
        </span>
        <a href="{{ route('lab.csrf', ['mode' => 'vulnerable']) }}" class="btn {{ $mode === 'vulnerable' ? 'btn-vuln' : 'btn-ghost' }}">🔴 Vulnérable</a>
        <a href="{{ route('lab.csrf', ['mode' => 'secure']) }}" class="btn {{ $mode === 'secure' ? 'btn-sec' : 'btn-ghost' }}">🟢 Sécurisé</a>
    </div>
</div>

@if($csrfNotice)
    <div class="alert {{ $csrfType === 'exploited' ? 'alert-exploited' : 'alert-blocked' }}">
        {{ $csrfNotice }}
    </div>
@endif

<div class="grid-2">
    <div class="card">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <h3 style="font-size:16px; color:#0F172A;">🎓 Portail Officiel LOKO-Vault (Note en Base MariaDB)</h3>
            <form method="POST" action="{{ route('lab.csrf.reset-grade') }}">
                @csrf
                <input type="hidden" name="mode" value="{{ $mode }}">
                <button type="submit" class="btn btn-ghost" style="padding:5px 10px; font-size:12px;">↺ Restaurer 15.75</button>
            </form>
        </div>

        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:12px; padding:16px; margin-bottom:16px;">
            <div style="font-size:12px; color:#475569; font-weight:700;">ÉTUDIANT : {{ $grade->student->full_name }} ({{ $grade->course_code }})</div>
            <div style="font-size:28px; font-weight:900; color:{{ $grade->score >= 19.5 ? '#DC2626' : '#059669' }}; margin:6px 0;">
                {{ number_format((float)$grade->score, 2) }} / 20
            </div>
            <div style="font-size:13px; color:#334155;">Observation jury : <em>{{ $grade->jury_remark }}</em></div>
        </div>

        <form method="POST" action="{{ route('lab.csrf.secure-update') }}">
            @csrf
            <label for="legit_score">Modification légitime par le professeur (formulaire avec <code>@@csrf</code>)</label>
            <div style="display:flex; gap:10px;">
                <input type="number" step="0.25" min="0" max="20" id="legit_score" name="score" value="{{ $grade->score }}">
                <button type="submit" class="btn btn-sec">✅ Valider avec @@csrf</button>
            </div>
        </form>
    </div>

    <div class="card {{ $mode === 'vulnerable' ? 'card-vuln' : 'card-sec' }}">
        <h3 style="font-size:16px; color:#0F172A; margin-bottom:10px;">🏴‍☠️ Simulateur de Site Piège Externe (Sans Jeton <code>_token</code>)</h3>
        <p style="font-size:13px; color:#475569; margin-bottom:12px;">
            L'enseignant connecté ouvre cette page piège externe. Le bouton envoie une requête <code>POST</code> cachée (<code>score=20</code>) vers
            <code>{{ $mode === 'vulnerable' ? '/lab/csrf/vulnerable-update' : '/lab/csrf/secure-update' }}</code> sans jeton CSRF :
        </p>

        <iframe src="{{ route('lab.csrf.evil', ['mode' => $mode]) }}" style="width:100%; height:245px; border:2px dashed #D97706; border-radius:10px; background:#FFFFFF;"></iframe>
    </div>
</div>

@include('lab.partials.sql-inspector', ['queries' => $queries])
@endsection
