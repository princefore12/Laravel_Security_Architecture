<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>@yield('title', 'Portail Académique — UT LOKO')</title>
  <style>
    :root {
      --loko-red: #8B1518;
      --loko-red-dark: #680E10;
      --loko-gold: #B45309;
      --bg-page: #F8FAFC;
      --bg-card: #FFFFFF;
      --text-main: #0F172A;
      --text-muted: #475569;
      --border: #E2E8F0;
      --border-strong: #CBD5E1;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
      background: var(--bg-page);
      color: var(--text-main);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      line-height: 1.5;
    }

    .top-stripe {
      height: 4px;
      background: linear-gradient(90deg, var(--loko-red), #D97706);
    }

    .site-header {
      background: #FFFFFF;
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      z-index: 40;
    }

    .header-inner {
      max-width: 1260px;
      margin: 0 auto;
      padding: 12px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 14px;
      flex-wrap: wrap;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      text-decoration: none;
      color: var(--text-main);
    }

    .brand img {
      height: 42px;
      width: auto;
      object-fit: contain;
    }

    .brand-text strong {
      display: block;
      font-size: 16px;
      font-weight: 800;
      color: var(--loko-red);
      letter-spacing: -0.2px;
    }

    .brand-text span {
      display: block;
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 500;
    }

    .main-nav {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }

    .nav-link {
      text-decoration: none;
      color: #334155;
      font-size: 13.5px;
      font-weight: 600;
      padding: 7px 11px;
      border-radius: 8px;
      transition: background 0.15s, color 0.15s;
      white-space: nowrap;
    }

    .nav-link:hover {
      background: #F1F5F9;
      color: var(--loko-red);
    }

    .nav-link.active {
      background: #FEF2F2;
      color: var(--loko-red);
    }

    .nav-link.admin-link {
      background: #FFFBEB;
      color: #92400E;
      border: 1px solid #FDE68A;
    }

    .user-actions {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .user-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      text-decoration: none;
      background: #F8FAFC;
      border: 1px solid var(--border-strong);
      border-radius: 999px;
      padding: 5px 12px;
      font-size: 13px;
      color: var(--text-main);
      font-weight: 600;
    }

    .role-badge {
      font-size: 11px;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 999px;
      text-transform: uppercase;
      letter-spacing: 0.4px;
    }

    .role-badge.student {
      background: #E0F2FE;
      color: #0369A1;
    }

    .role-badge.admin {
      background: #DCFCE7;
      color: #166534;
    }

    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 9px 16px;
      border-radius: 8px;
      font-size: 13.5px;
      font-weight: 600;
      cursor: pointer;
      border: 1px solid transparent;
      text-decoration: none;
      font-family: inherit;
    }

    .btn-primary {
      background: var(--loko-red);
      color: #FFFFFF;
    }

    .btn-primary:hover {
      background: var(--loko-red-dark);
    }

    .btn-outline {
      background: #FFFFFF;
      color: #334155;
      border-color: var(--border-strong);
    }

    .btn-outline:hover {
      background: #F8FAFC;
    }

    .btn-sm {
      padding: 6px 12px;
      font-size: 12.5px;
    }

    .container {
      width: 100%;
      max-width: 1180px;
      margin: 28px auto;
      padding: 0 24px;
      flex: 1;
    }

    .card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 24px;
      box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
    }

    .page-head {
      margin-bottom: 22px;
    }

    .page-kicker {
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.7px;
      color: var(--loko-red);
      margin-bottom: 4px;
    }

    .page-title {
      font-size: 26px;
      font-weight: 800;
      color: var(--text-main);
    }

    .page-sub {
      color: var(--text-muted);
      font-size: 14.5px;
      margin-top: 4px;
    }

    .grid-2 {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 20px;
    }

    .grid-3 {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 18px;
    }

    @media (max-width: 840px) {
      .grid-2, .grid-3 { grid-template-columns: 1fr; }
    }

    .alert {
      padding: 12px 16px;
      border-radius: 9px;
      font-size: 14px;
      font-weight: 500;
      margin-bottom: 18px;
      border: 1px solid transparent;
    }

    .alert-success {
      background: #ECFDF5;
      border-color: #A7F3D0;
      color: #065F46;
    }

    .alert-error {
      background: #FEF2F2;
      border-color: #FECACA;
      color: #991B1B;
    }

    .form-group {
      margin-bottom: 16px;
    }

    .form-group label {
      display: block;
      font-size: 13.5px;
      font-weight: 600;
      color: #1E293B;
      margin-bottom: 6px;
    }

    .form-control {
      width: 100%;
      padding: 10px 13px;
      border: 1px solid var(--border-strong);
      border-radius: 8px;
      font-size: 14px;
      font-family: inherit;
      color: var(--text-main);
      background: #FFFFFF;
    }

    .form-control:focus {
      outline: none;
      border-color: var(--loko-red);
      box-shadow: 0 0 0 3px rgba(139, 21, 24, 0.1);
    }

    table.data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }

    table.data-table th {
      text-align: left;
      padding: 11px 14px;
      background: #F8FAFC;
      border-bottom: 2px solid var(--border);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--text-muted);
      font-weight: 700;
    }

    table.data-table td {
      padding: 12px 14px;
      border-bottom: 1px solid var(--border);
      color: var(--text-main);
      vertical-align: middle;
    }

    table.data-table tr:hover td {
      background: #F8FAFC;
    }

    .site-footer {
      background: #FFFFFF;
      border-top: 1px solid var(--border);
      padding: 18px 24px;
      margin-top: 40px;
      text-align: center;
      font-size: 13px;
      color: var(--text-muted);
    }
  </style>
</head>
<body>
  <div class="top-stripe"></div>

  <header class="site-header">
    <div class="header-inner">
      <a href="{{ route('portal.home') }}" class="brand">
        <img src="/images/logo_ut_loko.png" alt="Logo UT LOKO">
        <div class="brand-text">
          <strong>Portail Académique UT LOKO</strong>
          <span>Département ITER • Licence 3 Informatique</span>
        </div>
      </a>

      <nav class="main-nav">
        <a href="{{ route('portal.home') }}" class="nav-link {{ request()->routeIs('portal.home') ? 'active' : '' }}">Accueil</a>
        <a href="{{ route('portal.directory') }}" class="nav-link {{ request()->routeIs('portal.directory') ? 'active' : '' }}">Annuaire</a>
        <a href="{{ route('portal.campus') }}" class="nav-link {{ request()->routeIs('portal.campus') ? 'active' : '' }}">Mur du Campus</a>
        @auth
          <a href="{{ route('portal.my-grades') }}" class="nav-link {{ request()->routeIs('portal.grades.*') ? 'active' : '' }}">Mes Notes</a>
          @if (auth()->user()->isAdmin())
            <a href="{{ route('portal.admin.grades') }}" class="nav-link admin-link {{ request()->routeIs('portal.admin.*') ? 'active' : '' }}">Administration</a>
          @endif
        @endauth
      </nav>

      <div class="user-actions">
        @auth
          <a href="{{ route('portal.profile') }}" class="user-pill">
            <span>{{ auth()->user()->name }}</span>
            <span class="role-badge {{ auth()->user()->isAdmin() ? 'admin' : 'student' }}">
              {{ auth()->user()->isAdmin() ? 'Administrateur' : 'Étudiant' }}
            </span>
          </a>
          <form method="POST" action="{{ route('portal.logout') }}">
            @csrf
            <button type="submit" class="btn btn-outline btn-sm">Déconnexion</button>
          </form>
        @else
          <a href="{{ route('login') }}" class="btn btn-primary btn-sm">Se connecter</a>
        @endauth
      </div>
    </div>
  </header>

  <main class="container">
    @if (session('status'))
      <div class="alert alert-success">{{ session('status') }}</div>
    @endif

    @if ($errors->any())
      <div class="alert alert-error">
        @foreach ($errors->all() as $error)
          <div>{{ $error }}</div>
        @endforeach
      </div>
    @endif

    @yield('content')
  </main>

  <footer class="site-footer">
    Université Tertiaire &amp; Technologique LOKO — Département ITER • Licence 3 Informatique &amp; Télécommunication • Année académique 2025 – 2026
  </footer>
</body>
</html>
