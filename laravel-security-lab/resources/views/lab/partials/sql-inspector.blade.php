<div class="card" style="margin-top:20px; border-color: #93C5FD; background:#F8FAFC;">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px; gap:10px; flex-wrap:wrap;">
        <h3 style="font-size:15.5px; color:#1D4ED8;">🔬 Inspecteur SQL en Direct (DB::listen → MariaDB / SQLite)</h3>
        <span style="font-size:12px; color:#475569; font-weight:700;">{{ count($queries) }} requête(s) capturée(s)</span>
    </div>

    @if(empty($queries))
        <p style="font-size:13px; color:#475569;">Exécutez une action ci-dessus pour observer la requête SQL réelle et ses bindings transmis par PDO.</p>
    @else
        @foreach($queries as $idx => $q)
            <div style="margin-bottom:10px;">
                <div style="font-size:11.5px; color:#8B1518; font-weight:700; margin-bottom:4px;">
                    Requête #{{ $idx + 1 }} • Durée : {{ $q['time_ms'] }} ms
                </div>
                <pre style="background:#FFFFFF;"><strong style="color:#1D4ED8;">SQL préparé / brut :</strong> {{ $q['sql'] }}
<strong style="color:#047857;">Bindings PDO       :</strong> {{ json_encode($q['bindings'], JSON_UNESCAPED_UNICODE) }}
<strong style="color:#9A3412;">Rendu exécuté      :</strong> {{ $q['rendered'] }}</pre>
            </div>
        @endforeach
    @endif
</div>
