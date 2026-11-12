@extends('layouts.portal')

@section('title', 'Mon Profil — Portail Académique UT LOKO')

@section('content')
  <div class="page-head">
    <div class="page-kicker">Compte Personnel</div>
    <h1 class="page-title">Mon Profil</h1>
    <p class="page-sub">Mettez à jour vos coordonnées enregistrées auprès de la scolarité UT LOKO.</p>
  </div>

  <div class="grid-2">
    <div class="card">
      <h2 style="font-size: 17px; font-weight: 700; margin-bottom: 16px;">Informations du compte</h2>

      <form method="POST" action="{{ route('portal.profile.update') }}">
        @csrf
        <!-- Table users : champs formulaire (name, email) | colonne privilege interne : role -->

        <div class="form-group">
          <label for="name">Nom complet</label>
          <input type="text" id="name" name="name" class="form-control" value="{{ old('name', $user->name) }}" required>
        </div>

        <div class="form-group">
          <label for="email">Adresse e-mail institutionnelle</label>
          <input type="email" id="email" name="email" class="form-control" value="{{ old('email', $user->email) }}" required>
        </div>

        <button type="submit" class="btn btn-primary">Enregistrer mes informations</button>
      </form>
    </div>

    <div class="card">
      <h2 style="font-size: 17px; font-weight: 700; margin-bottom: 16px;">Statut &amp; Rattachement Académique</h2>

      <table class="data-table">
        <tbody>
          <tr>
            <td style="color: #64748B; font-weight: 600;">Identifiant interne</td>
            <td><strong>#{{ $user->id }}</strong></td>
          </tr>
          <tr>
            <td style="color: #64748B; font-weight: 600;">Rôle actif</td>
            <td>
              <span class="role-badge {{ $user->isAdmin() ? 'admin' : 'student' }}">
                {{ $user->isAdmin() ? 'Administrateur (admin)' : 'Étudiant (student)' }}
              </span>
            </td>
          </tr>
          @if ($user->student)
            <tr>
              <td style="color: #64748B; font-weight: 600;">Matricule</td>
              <td style="font-family: Consolas, monospace;">{{ $user->student->matricule }}</td>
            </tr>
            <tr>
              <td style="color: #64748B; font-weight: 600;">Filière</td>
              <td>{{ $user->student->filiere }}</td>
            </tr>
          @endif
        </tbody>
      </table>
    </div>
  </div>
@endsection
