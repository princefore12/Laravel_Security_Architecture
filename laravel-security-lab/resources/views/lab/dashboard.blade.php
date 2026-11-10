@extends('layouts.lab')

@section('title', 'Tableau de Bord CyberLab')

@section('content')
<div class="card" style="background: linear-gradient(135deg, #FFFFFF 0%, #FEF2F2 100%); border: 1px solid #FECACA; border-left: 6px solid #8B1518; margin-bottom:22px;">
    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:16px;">
        <div>
            <div style="font-size:12px; color:#8B1518; font-weight:800; text-transform:uppercase; letter-spacing:1px;">
                UT LOKO • Licence 3 Informatique • Professeur : M. CAMARA
            </div>
            <h2 style="font-size:26px; font-weight:900; color:#0F172A; margin:6px 0;">
                Thème n° 12 : La Sécurité dans une Application Laravel
            </h2>
            <p style="color:#334155; font-size:14px; max-width:820px;">
                Laboratoire interactif du <strong>Groupe 5</strong> connecté en temps réel à <strong>{{ strtoupper($dbDriver) }} ({{ $dbName }})</strong> sous XAMPP.
                Chaque atelier permet de basculer en 1 clic entre le <strong>Mode Vulnérable</strong> et le <strong>Mode Sécurisé</strong>.
            </p>
        </div>
        <div style="display:flex; gap:12px; flex-wrap:wrap;">
            <div style="background:#EFF6FF; border:1px solid #93C5FD; border-radius:10px; padding:10px 16px; text-align:center;">
                <div style="font-size:22px; font-weight:900; color:#1D4ED8;">{{ $stats['students'] }}</div>
                <div style="font-size:11px; color:#1E40AF; font-weight:700;">Étudiants BDD</div>
            </div>
            <div style="background:#FEF2F2; border:1px solid #FCA5A5; border-radius:10px; padding:10px 16px; text-align:center;">
                <div style="font-size:22px; font-weight:900; color:#DC2626;">{{ $stats['exploited'] }}</div>
                <div style="font-size:11px; color:#991B1B; font-weight:700;">Failles exploitées</div>
            </div>
            <div style="background:#ECFDF5; border:1px solid #6EE7B7; border-radius:10px; padding:10px 16px; text-align:center;">
                <div style="font-size:22px; font-weight:900; color:#059669;">{{ $stats['blocked'] }}</div>
                <div style="font-size:11px; color:#065F46; font-weight:700;">Attaques bloquées</div>
            </div>
        </div>
    </div>
</div>

<div class="grid-5" style="margin-bottom:24px;">
    <a href="{{ route('lab.sqli') }}" class="card card-vuln" style="display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div style="font-size:11px; color:#DC2626; font-weight:800;">00:00 – 04:00 • PILIER 1</div>
            <h3 style="font-size:16px; color:#0F172A; margin:6px 0;">Injection SQL (SQLi)</h3>
            <p style="font-size:12.5px; color:#475569;">Concaténation brute vs PDO &amp; Eloquent ORM (<code>' OR '1'='1</code>, <code>UNION SELECT</code>).</p>
        </div>
        <div style="margin-top:14px; font-size:12.5px; font-weight:800; color:#8B1518;">🎤 Sore Ramatou →</div>
    </a>

    <a href="{{ route('lab.mass-assignment') }}" class="card" style="border:2px solid #FCD34D; background:linear-gradient(180deg,#FFFBEB 0%,#FFFFFF 35%); display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div style="font-size:11px; color:#D97706; font-weight:800;">04:00 – 08:00 • PILIER 2</div>
            <h3 style="font-size:16px; color:#0F172A; margin:6px 0;">Mass Assignment</h3>
            <p style="font-size:12.5px; color:#475569;">Escalade de rôle <code>role=admin</code> vs <code>#[Fillable]</code> &amp; <code>FormRequest</code>.</p>
        </div>
        <div style="margin-top:14px; font-size:12.5px; font-weight:800; color:#8B1518;">🎤 Siby Mody →</div>
    </a>

    <a href="{{ route('lab.xss.vulnerable') }}" class="card" style="border:2px solid #7DD3FC; background:linear-gradient(180deg,#F0F9FF 0%,#FFFFFF 35%); display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div style="font-size:11px; color:#0284C7; font-weight:800;">08:00 – 12:00 • PILIER 3</div>
            <h3 style="font-size:16px; color:#0F172A; margin:6px 0;">XSS Stockée &amp; Blade</h3>
            <p style="font-size:12.5px; color:#475569;">Rendu brut <code>@verbatim{!! !!}@endverbatim</code> vs échappé <code>@verbatim{{ }}@endverbatim</code> et en-têtes <code>CSP</code>.</p>
        </div>
        <div style="margin-top:14px; font-size:12.5px; font-weight:800; color:#8B1518;">🎤 Boin Naomi →</div>
    </a>

    <a href="{{ route('lab.csrf') }}" class="card" style="border:2px solid #D8B4FE; background:linear-gradient(180deg,#FAF5FF 0%,#FFFFFF 35%); display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div style="font-size:11px; color:#7C3AED; font-weight:800;">12:00 – 16:00 • PILIER 4</div>
            <h3 style="font-size:16px; color:#0F172A; margin:6px 0;">Faille CSRF</h3>
            <p style="font-size:12.5px; color:#475569;">Site piège externe sans jeton vs <code>@@csrf</code> &amp; erreur <strong>HTTP 419</strong>.</p>
        </div>
        <div style="margin-top:14px; font-size:12.5px; font-weight:800; color:#8B1518;">🎤 Traoré Charifat Leyla →</div>
    </a>

    <a href="{{ route('lab.access') }}" class="card card-sec" style="display:flex; flex-direction:column; justify-content:space-between;">
        <div>
            <div style="font-size:11px; color:#059669; font-weight:800;">16:00 – 20:00 • PILIER 5</div>
            <h3 style="font-size:16px; color:#0F172A; margin:6px 0;">Bcrypt, IDOR &amp; RateLimit</h3>
            <p style="font-size:12.5px; color:#475569;"><code>GradePolicy</code> (403), <code>Hash::make</code> vs MD5 et <code>RateLimiter</code> (429).</p>
        </div>
        <div style="margin-top:14px; font-size:12.5px; font-weight:800; color:#8B1518;">🎤 Djan Kouassi Noël →</div>
    </a>
</div>

<div class="card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <h3 style="font-size:16px; color:#0F172A;">📜 Journal d'Audit en Temps Réel (Table <code>security_logs</code> dans MariaDB)</h3>
        <span style="font-size:12px; color:#475569; font-weight:600;">Derniers {{ count($logs) }} événements enregistrés</span>
    </div>
    <table>
        <thead>
            <tr>
                <th>Date</th>
                <th>Pilier</th>
                <th>Mode</th>
                <th>Intervenant / Acteur</th>
                <th>Payload testé</th>
                <th>Résultat</th>
            </tr>
        </thead>
        <tbody>
            @foreach($logs as $log)
                <tr>
                    <td style="color:#64748B;">{{ $log->created_at?->format('H:i:s') }}</td>
                    <td><strong>{{ $log->pillar }}</strong></td>
                    <td>
                        @if($log->mode === 'vulnerable')
                            <span style="color:#DC2626; font-weight:800;">🔴 VULNÉRABLE</span>
                        @else
                            <span style="color:#059669; font-weight:800;">🟢 SÉCURISÉ</span>
                        @endif
                    </td>
                    <td>{{ $log->actor }}</td>
                    <td><code>{{ \Illuminate\Support\Str::limit($log->payload ?? '-', 52) }}</code></td>
                    <td>
                        @if($log->outcome === 'exploited')
                            <span style="background:#FEE2E2; color:#991B1B; padding:2px 8px; border-radius:6px; font-weight:800;">EXPLOITÉE</span>
                        @elseif($log->outcome === 'blocked')
                            <span style="background:#D1FAE5; color:#065F46; padding:2px 8px; border-radius:6px; font-weight:800;">BLOQUÉE</span>
                        @else
                            <span style="background:#DBEAFE; color:#1E40AF; padding:2px 8px; border-radius:6px; font-weight:700;">INFO</span>
                        @endif
                    </td>
                </tr>
            @endforeach
        </tbody>
    </table>
</div>
@endsection
