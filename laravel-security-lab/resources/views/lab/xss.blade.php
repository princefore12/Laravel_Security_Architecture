@extends('layouts.lab')

@section('title', 'Pilier 3 — Faille XSS & Blade')

@section('content')
<div class="mode-switcher">
    <div>
        <div style="font-size:11.5px; color:#8B1518; font-weight:800;">PILIER 3 (08:00 – 12:00) • INTERVENANTE : BOIN NAOMI</div>
        <h2 style="font-size:22px; font-weight:900; color:#0F172A;">Atelier 3 : Cross-Site Scripting (XSS Stocké), Blade &amp; CSP</h2>
    </div>
    <div style="display:flex; gap:10px; align-items:center;">
        <span class="mode-badge {{ $mode === 'vulnerable' ? 'vuln' : 'sec' }}">
            @if($mode === 'vulnerable')
                🔴 BLADE BRUT : @verbatim{!! $bio !!}@endverbatim
            @else
                🟢 BLADE ÉCHAPPÉ : @verbatim{{ $bio }}@endverbatim + CSP
            @endif
        </span>
        <a href="{{ route('lab.xss.vulnerable') }}" class="btn {{ $mode === 'vulnerable' ? 'btn-vuln' : 'btn-ghost' }}">🔴 Vulnérable</a>
        <a href="{{ route('lab.xss.secure') }}" class="btn {{ $mode === 'secure' ? 'btn-sec' : 'btn-ghost' }}">🟢 Sécurisé</a>
    </div>
</div>

<div class="grid-2">
    <div class="card {{ $mode === 'vulnerable' ? 'card-vuln' : 'card-sec' }}">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <h3 style="font-size:16px; color:#0F172A;">✍️ Enregistrer la Biographie de {{ $student->full_name }}</h3>
            <form method="POST" action="{{ route('lab.xss.reset-bio') }}">
                @csrf
                <input type="hidden" name="mode" value="{{ $mode }}">
                <button type="submit" class="btn btn-ghost" style="padding:5px 10px; font-size:12px;">↺ Bio saine</button>
            </form>
        </div>

        <form method="POST" action="{{ route('lab.xss.store') }}">
            @csrf
            <input type="hidden" name="mode" value="{{ $mode }}">
            <label for="xss_bio">Biographie stockée dans la table <code>students</code> (MariaDB)</label>
            <textarea id="xss_bio" name="bio" rows="4">{{ $student->bio }}</textarea>

            <div class="payload-row" style="margin-bottom:14px;">
                <button type="button" class="btn-payload" onclick="setXssPayload('normal')">✅ Texte normal</button>
                <button type="button" class="btn-payload" onclick="setXssPayload('banner')">⚡ Payload XSS : Injection DOM &amp; Capture Cookie</button>
            </div>

            <button type="submit" class="btn {{ $mode === 'vulnerable' ? 'btn-vuln' : 'btn-sec' }}" style="width:100%; justify-content:center;">
                💾 Enregistrer en Base MariaDB &amp; Afficher la Fiche
            </button>
        </form>

        <div style="margin-top:16px;">
            <h4 style="font-size:13.5px; color:#8B1518; margin-bottom:6px;">Code dans la vue <code>xss.blade.php</code> :</h4>
            @if($mode === 'vulnerable')
<pre>&lt;!-- ❌ VULNÉRABLE : Désactive l'échappement Blade --&gt;
&lt;div class="bio-preview"&gt;@verbatim{!! $student->bio !!}@endverbatim&lt;/div&gt;</pre>
            @else
<pre>&lt;!-- ✅ SÉCURISÉ : Appelle htmlspecialchars() + SecurityHeadersMiddleware --&gt;
&lt;div class="bio-preview"&gt;@verbatim{{ $student->bio }}@endverbatim&lt;/div&gt;</pre>
            @endif
        </div>
    </div>

    <div class="card">
        <h3 style="font-size:16px; color:#0F172A; margin-bottom:12px;">🖥️ Rendu Navigateur de la Fiche Étudiant</h3>

        <div style="background:#F8FAFC; border:1px solid #CBD5E1; border-radius:12px; padding:16px; margin-bottom:14px;">
            <div style="font-size:12px; color:#64748B; font-weight:700;">FICHE PUBLIQUE CONSULTÉE PAR L'ADMINISTRATEUR :</div>
            <div style="font-size:18px; font-weight:900; color:#0F172A; margin:4px 0 10px;">{{ $student->full_name }} ({{ $student->matricule }})</div>
            <div style="padding:12px; border-radius:8px; background:#FFFFFF; border:1px solid #E2E8F0; color:#1E293B;">
                @if($mode === 'vulnerable')
                    {!! $student->bio !!}
                @else
                    {{ $student->bio }}
                @endif
            </div>
            <div id="xss-demo-result" style="display:none;"></div>
        </div>

        @if($mode === 'secure')
            <div class="alert alert-blocked" style="margin-bottom:0;">
                🛡️ En-têtes HTTP injectés par <code>SecurityHeadersMiddleware</code> :<br>
                <code>Content-Security-Policy: default-src 'self'; object-src 'none'; frame-ancestors 'none'</code><br>
                <code>X-Content-Type-Options: nosniff</code> • <code>X-Frame-Options: DENY</code> • Session Cookie <code>HttpOnly</code>
            </div>
        @elseif($hasDangerousTag)
            <div class="alert alert-exploited" style="margin-bottom:0;">
                🚨 Payload HTML/JS actif stocké en base MariaDB et interprété par le navigateur !
            </div>
        @endif
    </div>
</div>

@include('lab.partials.sql-inspector', ['queries' => $queries])

<script>
function setXssPayload(type) {
    const el = document.getElementById('xss_bio');
    if (type === 'normal') {
        el.value = 'Étudiante en L3 Informatique à UT LOKO, passionnée par la sécurité Blade.';
    } else {
        el.value = 'Étudiante L3 UT LOKO <img src="x" onerror="var b=document.getElementById(\'xss-demo-result\');b.style.display=\'block\';b.style.marginTop=\'12px\';b.style.padding=\'12px\';b.style.borderRadius=\'8px\';b.style.background=\'#FEE2E2\';b.style.border=\'2px solid #DC2626\';b.style.color=\'#991B1B\';b.style.fontWeight=\'800\';b.innerHTML=\'🚨 EXÉCUTION JAVASCRIPT RÉUSSIE ! DOM piraté par XSS stockée en base MariaDB (le cookie HttpOnly protège heureusement laravel_session).\';">';
    }
}
</script>
@endsection
