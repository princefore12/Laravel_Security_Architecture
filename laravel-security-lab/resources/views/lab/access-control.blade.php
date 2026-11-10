@extends('layouts.lab')

@section('title', 'Pilier 5 — Bcrypt, IDOR & RateLimiter')

@section('content')
<div class="mode-switcher">
    <div>
        <div style="font-size:11.5px; color:#8B1518; font-weight:800;">PILIER 5 (16:00 – 20:00) • INTERVENANT : DJAN KOUASSI NOËL</div>
        <h2 style="font-size:22px; font-weight:900; color:#0F172A;">Atelier 5 : Authentification, Hachage Bcrypt, IDOR (Policies) &amp; RateLimiter</h2>
    </div>
    <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
        <form method="POST" action="{{ route('lab.access.actor') }}" style="display:flex; gap:8px; align-items:center;">
            @csrf
            <input type="hidden" name="mode" value="{{ $mode }}">
            <span style="font-size:12.5px; color:#475569; font-weight:700;">Session active :</span>
            <select name="email" onchange="this.form.submit()" style="width:auto; padding:6px 10px; font-size:12.5px;">
                <option value="ramatou.sore@loko.ci" {{ $actingUser->email === 'ramatou.sore@loko.ci' ? 'selected' : '' }}>👤 Sore Ramatou (Étudiante #1)</option>
                <option value="mody.siby@loko.ci" {{ $actingUser->email === 'mody.siby@loko.ci' ? 'selected' : '' }}>👤 Siby Mody (Étudiant #2)</option>
                <option value="admin@loko.ci" {{ $actingUser->email === 'admin@loko.ci' ? 'selected' : '' }}>👑 Prof. M. Camara (Admin)</option>
            </select>
        </form>
        <a href="{{ route('lab.access', ['mode' => 'vulnerable']) }}" class="btn {{ $mode === 'vulnerable' ? 'btn-vuln' : 'btn-ghost' }}">🔴 Vulnérable</a>
        <a href="{{ route('lab.access', ['mode' => 'secure']) }}" class="btn {{ $mode === 'secure' ? 'btn-sec' : 'btn-ghost' }}">🟢 Sécurisé</a>
    </div>
</div>

@if($idorOutcome === 'exploited')
    <div class="alert alert-exploited">
        🚨 FAILLE IDOR EXPLOITÉE : {{ $actingUser->name }} a consulté le relevé privé de {{ $inspectedGrade['student_name'] ?? 'un autre étudiant' }} ({{ $inspectedGrade['score'] ?? '' }}/20) sans contrôle d'accès !
    </div>
@elseif($idorOutcome === 'blocked')
    <div class="alert alert-blocked">
        🛡️ BLOQUÉ PAR <code>GradePolicy</code> (HTTP 403 Forbidden) : {{ $actingUser->name }} n'a pas le droit de consulter le dossier d'un autre étudiant !
    </div>
@elseif($idorOutcome === 'own' && $inspectedGrade)
    <div class="alert alert-info">
        ✅ Consultation légitime autorisée : {{ $inspectedGrade['student_name'] }} — {{ $inspectedGrade['course_name'] }} ({{ $inspectedGrade['score'] }}/20).
    </div>
@endif

<div class="grid-2" style="margin-bottom:20px;">
    <div class="card {{ $mode === 'vulnerable' ? 'card-vuln' : 'card-sec' }}">
        <h3 style="font-size:16px; color:#0F172A; margin-bottom:10px;">🔐 A. Contrôle d'Accès : Faille IDOR vs <code>GradePolicy</code></h3>
        <p style="font-size:13px; color:#475569; margin-bottom:12px;">
            Connecté en tant que <strong>{{ $actingUser->name }} ({{ strtoupper($actingUser->role) }})</strong>. Cliquez sur un bulletin pour tester l'accès :
        </p>

        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Propriétaire</th>
                    <th>Matière</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                @foreach($grades->take(3) as $g)
                    <tr>
                        <td>#{{ $g->id }}</td>
                        <td>{{ $g->student->full_name }}</td>
                        <td>{{ $g->course_code }}</td>
                        <td style="display:flex; gap:6px;">
                            @if($mode === 'vulnerable')
                                <a href="{{ route('lab.access.grade.vulnerable', ['grade' => $g->id]) }}" class="btn btn-vuln" style="padding:4px 9px; font-size:11.5px;">Ouvrir (Vulnérable)</a>
                            @else
                                <a href="{{ route('lab.access.grade.secure', ['grade' => $g->id, 'inline' => 1]) }}" class="btn btn-sec" style="padding:4px 9px; font-size:11.5px;">Vérifier Policy</a>
                                <a href="{{ route('lab.access.grade.secure', ['grade' => $g->id]) }}" target="_blank" class="btn btn-ghost" style="padding:4px 8px; font-size:11.5px;" title="Tester la vraie page HTTP 403">403 Réel ↗</a>
                            @endif
                        </td>
                    </tr>
                @endforeach
            </tbody>
        </table>
    </div>

    <div class="card">
        <h3 style="font-size:16px; color:#0F172A; margin-bottom:10px;">🔑 B. Comparateur Cryptographique : MD5 vs <code>bcrypt</code></h3>
        <form method="POST" action="{{ route('lab.access.hash') }}" style="margin-bottom:12px;">
            @csrf
            <input type="hidden" name="mode" value="{{ $mode }}">
            <label for="plain_pw">Mot de passe à hacher dans MariaDB</label>
            <div style="display:flex; gap:10px;">
                <input type="text" id="plain_pw" name="plain_password" value="{{ $hashComparison['plain'] ?? 'Loko@2026!' }}">
                <button type="submit" class="btn btn-gold">⚡ Comparer 2x</button>
            </div>
        </form>

        @if($hashComparison)
            <pre><strong style="color:#DC2626;">❌ MD5 (Sans sel, identique et cassable) :</strong>
Essai 1 : {{ $hashComparison['md5_a'] }}
Essai 2 : {{ $hashComparison['md5_b'] }}

<strong style="color:#059669;">✅ Laravel Hash::make() (bcrypt + sel aléatoire 128 bits) :</strong>
Essai 1 : {{ $hashComparison['bcrypt_a'] }}
Essai 2 : {{ $hashComparison['bcrypt_b'] }}
Hash::check() valide : {{ $hashComparison['verified'] ? 'OUI (true)' : 'NON' }}</pre>
        @else
            <p style="font-size:13px; color:#475569;">Cliquez sur <strong>Comparer 2x</strong> pour démontrer que <code>bcrypt</code> génère deux empreintes uniques grâce à son sel aléatoire.</p>
        @endif
    </div>
</div>

<div class="card" style="border-color:#F59E0B; background:#FFFDF7;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:12px;">
        <div>
            <h3 style="font-size:16px; color:#0F172A;">🚦 C. Protection Anti-Brute-Force (<code>RateLimiter</code> : Max 5 essais / minute)</h3>
            <p style="font-size:13px; color:#475569;">Essais restants pour votre IP locale : <strong id="remainingBadge" style="color:#059669;">{{ $remainingAttempts }} / 5</strong></p>
        </div>
        <div style="display:flex; gap:10px;">
            <button type="button" class="btn btn-vuln" onclick="runBruteForce()">🚀 Simuler Attaque Brute-Force (6 essais)</button>
            <button type="button" class="btn btn-ghost" onclick="resetRateLimit()">↺ Débloquer IP</button>
        </div>
    </div>
    <div id="bruteLog" style="display:grid; grid-template-columns:repeat(6, 1fr); gap:8px;"></div>
</div>

@include('lab.partials.sql-inspector', ['queries' => $idorQueries])

<script>
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

async function runBruteForce() {
    const log = document.getElementById('bruteLog');
    log.innerHTML = '';
    for (let i = 1; i <= 6; i++) {
        const res = await fetch('{{ route("lab.access.rate-limit") }}', {
            method: 'POST',
            headers: { 'X-CSRF-TOKEN': csrfToken, 'Accept': 'application/json' }
        });
        const data = await res.json();
        document.getElementById('remainingBadge').textContent = data.remaining + ' / 5';
        const is429 = res.status === 429;
        const card = document.createElement('div');
        card.style.padding = '10px';
        card.style.borderRadius = '8px';
        card.style.fontSize = '12px';
        card.style.fontWeight = '800';
        card.style.textAlign = 'center';
        card.style.background = is429 ? '#ECFDF5' : '#FEF2F2';
        card.style.border = is429 ? '1px solid #059669' : '1px solid #DC2626';
        card.style.color = is429 ? '#065F46' : '#991B1B';
        card.innerHTML = `Essai #${i}<br>HTTP ${res.status}<br>${is429 ? '🛡️ BLOQUÉ !' : 'Échec login'}`;
        log.appendChild(card);
    }
}

async function resetRateLimit() {
    await fetch('{{ route("lab.access.rate-limit.clear") }}', {
        method: 'POST',
        headers: { 'X-CSRF-TOKEN': csrfToken, 'Accept': 'application/json' }
    });
    document.getElementById('remainingBadge').textContent = '5 / 5';
    document.getElementById('bruteLog').innerHTML = '';
}
</script>
@endsection
