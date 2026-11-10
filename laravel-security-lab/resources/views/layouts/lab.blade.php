<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'LOKO-Vault CyberLab') — Sécurité Laravel &amp; XAMPP</title>
    <style>
        :root {
            --loko-red: #8B1518;
            --loko-red-dark: #6D1012;
            --loko-gold: #D97706;
            --bg-page: #F8FAFC;
            --bg-card: #FFFFFF;
            --bg-soft: #F1F5F9;
            --border: #E2E8F0;
            --text: #0F172A;
            --muted: #475569;
            --vuln: #DC2626;
            --sec: #059669;
            --blue: #0284C7;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: var(--bg-page);
            color: var(--text);
            min-height: 100vh;
            line-height: 1.55;
        }
        a { color: inherit; text-decoration: none; }
        .warning-strip {
            background: #FEF2F2;
            border-bottom: 2px solid #FECACA;
            color: #991B1B;
            font-size: 12.5px;
            font-weight: 700;
            text-align: center;
            padding: 7px 16px;
        }
        .navbar {
            background: #FFFFFF;
            border-bottom: 3px solid var(--loko-red);
            padding: 12px 26px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            flex-wrap: wrap;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.05);
        }
        .brand-wrap {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .brand-logo {
            background: #FFFFFF;
            border: 1px solid var(--border);
            padding: 4px 8px;
            border-radius: 8px;
            height: 46px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .brand-logo img { height: 36px; object-fit: contain; }
        .brand-text h1 { font-size: 19px; font-weight: 900; color: var(--text); letter-spacing: 0.2px; }
        .brand-text h1 span { color: var(--loko-red); }
        .brand-text p { font-size: 12px; color: var(--muted); font-weight: 600; }
        .nav-actions { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
        .pill-db {
            background: #EFF6FF;
            border: 1px solid #BFDBFE;
            color: #1D4ED8;
            padding: 6px 13px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
        }
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 7px;
            padding: 8px 15px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 700;
            border: 1px solid transparent;
            cursor: pointer;
            transition: transform 0.12s, box-shadow 0.15s;
        }
        .btn:hover { transform: translateY(-1px); box-shadow: 0 3px 10px rgba(15,23,42,0.1); }
        .btn-red { background: var(--loko-red); color: #FFF; }
        .btn-vuln { background: #DC2626; color: #FFF; }
        .btn-sec { background: #059669; color: #FFF; }
        .btn-gold { background: #FEF3C7; color: #92400E; border-color: #F59E0B; }
        .btn-ghost { background: #FFFFFF; color: #334155; border-color: #CBD5E1; }

        .pillar-tabs {
            background: #FFFFFF;
            border-bottom: 1px solid var(--border);
            padding: 10px 26px;
            display: flex;
            gap: 8px;
            overflow-x: auto;
        }
        .tab-link {
            padding: 8px 14px;
            border-radius: 9px;
            background: #F8FAFC;
            border: 1px solid #E2E8F0;
            font-size: 12.5px;
            font-weight: 700;
            color: #1E293B;
            white-space: nowrap;
            display: flex;
            flex-direction: column;
        }
        .tab-link small { font-size: 10.5px; color: var(--muted); font-weight: 600; }
        .tab-link:hover { background: #F1F5F9; border-color: #CBD5E1; }
        .tab-link.active {
            background: var(--loko-red);
            border-color: var(--loko-red-dark);
            color: #FFFFFF;
        }
        .tab-link.active small { color: #FDE68A; }

        .container { max-width: 1320px; margin: 24px auto; padding: 0 24px 48px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
        .grid-5 { display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }
        @media (max-width: 980px) {
            .grid-2, .grid-3, .grid-5 { grid-template-columns: 1fr; }
        }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 20px;
            box-shadow: 0 4px 16px rgba(15, 23, 42, 0.05);
        }
        .card-vuln { border: 2px solid #FCA5A5; background: linear-gradient(180deg, #FEF2F2 0%, #FFFFFF 35%); }
        .card-sec { border: 2px solid #6EE7B7; background: linear-gradient(180deg, #ECFDF5 0%, #FFFFFF 35%); }

        .mode-switcher {
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 14px;
            background: #FFFFFF;
            border: 1px solid var(--border);
            border-left: 5px solid var(--loko-red);
            border-radius: 14px;
            padding: 16px 22px;
            margin-bottom: 20px;
            box-shadow: 0 3px 12px rgba(15, 23, 42, 0.04);
        }
        .mode-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 6px 14px;
            border-radius: 999px;
            font-size: 12.5px;
            font-weight: 800;
        }
        .mode-badge.vuln { background: #FEE2E2; color: #991B1B; border: 1px solid #EF4444; }
        .mode-badge.sec { background: #D1FAE5; color: #065F46; border: 1px solid #10B981; }

        .alert {
            padding: 13px 18px;
            border-radius: 10px;
            margin-bottom: 18px;
            font-weight: 700;
            font-size: 13.5px;
            border: 1px solid transparent;
        }
        .alert-exploited { background: #FEF2F2; border-color: #EF4444; color: #991B1B; }
        .alert-blocked { background: #ECFDF5; border-color: #10B981; color: #065F46; }
        .alert-info { background: #EFF6FF; border-color: #3B82F6; color: #1E40AF; }

        label { display: block; font-size: 12.5px; font-weight: 700; color: #334155; margin-bottom: 5px; }
        input[type="text"], input[type="email"], input[type="number"], input[type="password"], textarea, select {
            width: 100%;
            background: #FFFFFF;
            border: 1px solid #CBD5E1;
            color: #0F172A;
            padding: 10px 13px;
            border-radius: 8px;
            font-size: 13.5px;
            font-family: inherit;
        }
        input:focus, textarea:focus, select:focus {
            outline: 2px solid rgba(139, 21, 24, 0.25);
            border-color: var(--loko-red);
        }
        pre {
            background: #F8FAFC;
            border: 1px solid #CBD5E1;
            border-radius: 10px;
            padding: 13px 15px;
            font-family: 'Cascadia Code', 'Consolas', monospace;
            font-size: 12.5px;
            color: #0F172A;
            overflow-x: auto;
            white-space: pre-wrap;
        }
        code {
            font-family: 'Cascadia Code', 'Consolas', monospace;
            background: #F1F5F9;
            color: #991B1B;
            padding: 1px 5px;
            border-radius: 4px;
            font-size: 12.5px;
        }
        pre code { background: transparent; color: inherit; padding: 0; }
        table { width: 100%; border-collapse: collapse; font-size: 13px; }
        th { background: #F1F5F9; color: #0F172A; text-align: left; padding: 10px 12px; font-weight: 800; border-bottom: 2px solid #CBD5E1; }
        td { padding: 9px 12px; border-bottom: 1px solid #E2E8F0; color: #1E293B; }
        .payload-row { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }
        .btn-payload {
            background: #FFFBEB;
            border: 1px dashed #D97706;
            color: #92400E;
            padding: 6px 11px;
            border-radius: 7px;
            font-size: 12px;
            font-weight: 700;
            cursor: pointer;
        }
        .btn-payload:hover { background: #FEF3C7; }
    </style>
</head>
<body>

<div class="warning-strip">
    ⚠️ LABORATOIRE PÉDAGOGIQUE LOCAL UNIQUEMENT (UT LOKO • Groupe 5 • Prof. M. CAMARA) — Les routes vulnérables ne doivent jamais être déployées en production.
</div>

<nav class="navbar">
    <a href="{{ route('lab.dashboard') }}" class="brand-wrap">
        <div class="brand-logo">
            <img src="{{ asset('images/logo_ut_loko.png') }}" alt="UT LOKO">
            <img src="{{ asset('images/logo_groupe_loko.png') }}" alt="Groupe LOKO">
        </div>
        <div class="brand-text">
            <h1>LOKO-<span>Vault</span> CyberLab</h1>
            <p>Sécurité Laravel 13 &amp; Base de Données MariaDB (XAMPP)</p>
        </div>
    </a>

    <div class="nav-actions">
        <span class="pill-db">🗄️ XAMPP DB : loko_security_lab</span>
        <a href="http://localhost/phpmyadmin" target="_blank" class="btn btn-ghost">🔍 phpMyAdmin</a>
        <form method="POST" action="{{ route('lab.reset') }}" style="display:inline;">
            @csrf
            <button type="submit" class="btn btn-gold">🔄 Réinitialiser la BDD</button>
        </form>
    </div>
</nav>

<div class="pillar-tabs">
    <a href="{{ route('lab.dashboard') }}" class="tab-link {{ request()->routeIs('lab.dashboard') ? 'active' : '' }}">
        <span>🏠 Tableau de Bord</span>
        <small>Vue d'ensemble &amp; Logs</small>
    </a>
    <a href="{{ route('lab.sqli') }}" class="tab-link {{ request()->routeIs('lab.sqli*') ? 'active' : '' }}">
        <span>1. Injection SQL (SQLi)</span>
        <small>Sore Ramatou • 00:00–04:00</small>
    </a>
    <a href="{{ route('lab.mass-assignment') }}" class="tab-link {{ request()->routeIs('lab.mass-assignment*') ? 'active' : '' }}">
        <span>2. Mass Assignment</span>
        <small>Siby Mody • 04:00–08:00</small>
    </a>
    <a href="{{ route('lab.xss.vulnerable') }}" class="tab-link {{ request()->routeIs('lab.xss*') ? 'active' : '' }}">
        <span>3. Faille XSS &amp; Blade</span>
        <small>Boin Naomi • 08:00–12:00</small>
    </a>
    <a href="{{ route('lab.csrf') }}" class="tab-link {{ request()->routeIs('lab.csrf*') ? 'active' : '' }}">
        <span>4. Faille CSRF &amp; @@csrf</span>
        <small>Traoré C. Leyla • 12:00–16:00</small>
    </a>
    <a href="{{ route('lab.access') }}" class="tab-link {{ request()->routeIs('lab.access*') ? 'active' : '' }}">
        <span>5. Bcrypt, IDOR &amp; RateLimit</span>
        <small>Djan K. Noël • 16:00–20:00</small>
    </a>
</div>

<main class="container">
    @if(session('status'))
        <div class="alert alert-blocked">✅ {{ session('status') }}</div>
    @endif

    @yield('content')
</main>

</body>
</html>
