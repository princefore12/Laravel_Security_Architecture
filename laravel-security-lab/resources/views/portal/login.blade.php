@extends('layouts.portal')

@section('title', 'Connexion — Portail Académique UT LOKO')

@section('content')
  <div style="max-width: 440px; margin: 28px auto;">
    <div class="card">
      <div class="page-head" style="margin-bottom: 18px;">
        <div class="page-kicker">Accès Espace Étudiant &amp; Enseignant</div>
        <h1 class="page-title" style="font-size: 22px;">Connexion au Portail</h1>
        <p class="page-sub">Identifiez-vous avec votre adresse institutionnelle <code>@loko.ci</code>.</p>
      </div>

      @if (!empty($authError))
        <div class="alert alert-error">{{ $authError }}</div>
      @endif

      <form method="POST" action="{{ route('portal.login.submit') }}">
        @csrf

        <div class="form-group">
          <label for="email">Adresse e-mail universitaire</label>
          <input
            type="text"
            id="email"
            name="email"
            class="form-control"
            value="{{ old('email', $oldEmail ?? '') }}"
            placeholder="prenom.nom@loko.ci"
            autocomplete="username"
            required
          >
        </div>

        <div class="form-group">
          <label for="password">Mot de passe</label>
          <input
            type="password"
            id="password"
            name="password"
            class="form-control"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          >
        </div>

        @if ($remainingAttempts !== null && $remainingAttempts < 5)
          <div style="font-size: 12.5px; color: #B45309; margin-bottom: 12px; font-weight: 600;">
            Tentatives restantes avant blocage temporaire : {{ $remainingAttempts }} / 5
          </div>
        @endif

        <button type="submit" class="btn btn-primary" style="width: 100%; padding: 11px;">Se connecter</button>
      </form>
    </div>
  </div>
@endsection
