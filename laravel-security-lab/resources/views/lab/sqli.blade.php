@extends('layouts.lab')

@section('title', 'Pilier 1 — Injection SQL (SQLi)')

@section('content')
<div class="mode-switcher">
    <div>
        <div style="font-size:11.5px; color:#8B1518; font-weight:800;">PILIER 1 (00:00 – 04:00) • INTERVENANTE : SORE RAMATOU</div>
        <h2 style="font-size:22px; font-weight:900; color:#0F172A;">Atelier 1 : Injection SQL (SQLi) vs PDO &amp; Eloquent ORM</h2>
    </div>
    <div style="display:flex; gap:10px; align-items:center;">
        <span class="mode-badge {{ $mode === 'vulnerable' ? 'vuln' : 'sec' }}">
            {{ $mode === 'vulnerable' ? '🔴 MODE VULNÉRABLE ACTIF' : '🟢 MODE SÉCURISÉ ACTIF' }}
        </span>
        <a href="{{ route('lab.sqli', ['mode' => 'vulnerable', 'q' => $query]) }}" class="btn {{ $mode === 'vulnerable' ? 'btn-vuln' : 'btn-ghost' }}">🔴 Vulnérable</a>
        <a href="{{ route('lab.sqli', ['mode' => 'secure', 'q' => $query]) }}" class="btn {{ $mode === 'secure' ? 'btn-sec' : 'btn-ghost' }}">🟢 Sécurisé</a>
    </div>
</div>

@if($statusBadge)
    <div class="alert {{ str_contains($statusBadge, 'EXPLOITÉE') ? 'alert-exploited' : (str_contains($statusBadge, 'NEUTRALISÉE') ? 'alert-blocked' : 'alert-info') }}">
        {{ $statusBadge }}
    </div>
@endif

@if($sqlError)
    <div class="alert alert-exploited">❌ Erreur SQL MariaDB/PDO exposée : <code>{{ $sqlError }}</code></div>
@endif

<div class="grid-2">
    <div class="card {{ $mode === 'vulnerable' ? 'card-vuln' : 'card-sec' }}">
        <h3 style="font-size:16px; color:#0F172A; margin-bottom:12px;">🔍 Rechercher un Dossier Étudiant par Matricule</h3>
        <form method="GET" action="{{ route('lab.sqli') }}">
            <input type="hidden" name="mode" value="{{ $mode }}">
            <label for="sqli_q">Matricule étudiant (ou payload d'injection SQL)</label>
            <div style="display:flex; gap:10px;">
                <input type="text" id="sqli_q" name="q" value="{{ $query }}" placeholder="Ex: LOKO-2026-001">
                <button type="submit" class="btn {{ $mode === 'vulnerable' ? 'btn-vuln' : 'btn-sec' }}">Exécuter</button>
            </div>
        </form>

        <div style="margin-top:14px;">
            <span style="font-size:12px; color:#475569; font-weight:700;">Payloads de démonstration en 1 clic :</span>
            <div class="payload-row">
                <button type="button" class="btn-payload" onclick="setPayload('LOKO-2026-001')">✅ Normal : LOKO-2026-001</button>
                <button type="button" class="btn-payload" onclick="setPayload(&quot;' OR '1'='1&quot;)">⚡ Bypass : ' OR '1'='1</button>
                <button type="button" class="btn-payload" onclick="setPayload(&quot;' UNION SELECT id, email, password, role, 0 FROM users -- &quot;)">💀 Exfiltration UNION (table users)</button>
            </div>
        </div>

        <div style="margin-top:16px;">
            <h4 style="font-size:13.5px; color:#8B1518; margin-bottom:6px;">Code PHP exécuté dans <code>SqlInjectionController</code> :</h4>
            @if($mode === 'vulnerable')
<pre>// ❌ DANGER : Concaténation directe dans DB::select()
$students = DB::select(
  "SELECT id, matricule, full_name, filiere, moyenne
   FROM students WHERE matricule = '{$query}'"
);</pre>
            @else
<pre>// ✅ SÉCURISÉ : Eloquent ORM (Requête préparée PDO ?)
$students = Student::query()
  ->where('matricule', $query)
  ->get(['id', 'matricule', 'full_name', 'filiere', 'moyenne']);</pre>
            @endif
        </div>
    </div>

    <div class="card">
        <h3 style="font-size:16px; color:#0F172A; margin-bottom:12px;">📋 Résultats retournés par la Base de Données ({{ count($rows) }})</h3>
        @if(empty($rows))
            <p style="font-size:13.5px; color:#475569;">
                Aucune ligne retournée.
                @if($mode === 'secure' && $query !== '')
                    <br><strong style="color:#059669;">PDO a traité l'attaque comme une valeur littérale inexistante !</strong>
                @endif
            </p>
        @else
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Matricule / Email</th>
                        <th>Nom / Hash</th>
                        <th>Filière / Rôle</th>
                        <th>Moyenne</th>
                    </tr>
                </thead>
                <tbody>
                    @foreach($rows as $r)
                        <tr>
                            <td>{{ $r->id }}</td>
                            <td><code>{{ $r->matricule }}</code></td>
                            <td style="max-width:210px; overflow:hidden; text-overflow:ellipsis;">{{ $r->full_name }}</td>
                            <td>{{ $r->filiere }}</td>
                            <td><strong>{{ $r->moyenne }}</strong></td>
                        </tr>
                    @endforeach
                </tbody>
            </table>
        @endif
    </div>
</div>

@include('lab.partials.sql-inspector', ['queries' => $queries])

<script>
function setPayload(val) {
    document.getElementById('sqli_q').value = val;
}
</script>
@endsection
