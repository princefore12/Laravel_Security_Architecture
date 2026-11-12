@extends('layouts.portal')

@section('title', 'Annuaire Étudiants — Portail Académique UT LOKO')

@section('content')
  <div class="page-head">
    <div class="page-kicker">Département ITER • Promotion 2025 – 2026</div>
    <h1 class="page-title">Annuaire des Étudiants L3</h1>
    <p class="page-sub">Recherchez un étudiant par numéro de matricule ou par nom complet.</p>
  </div>

  <div class="card" style="margin-bottom: 20px;">
    <form method="GET" action="{{ route('portal.directory') }}" style="display: flex; gap: 12px; flex-wrap: wrap; align-items: flex-end;">
      <div style="flex: 1; min-width: 240px;">
        <label for="q" style="display:block; font-size:13px; font-weight:600; margin-bottom:5px;">Matricule ou nom</label>
        <input type="text" id="q" name="q" class="form-control" value="{{ $search }}" placeholder="Ex. LOKO-2026-001 ou Sore">
      </div>

      <div style="width: 190px;">
        <label for="sort" style="display:block; font-size:13px; font-weight:600; margin-bottom:5px;">Trier par</label>
        <select id="sort" name="sort" class="form-control">
          <option value="matricule" {{ $sort === 'matricule' ? 'selected' : '' }}>Matricule</option>
          <option value="full_name" {{ $sort === 'full_name' ? 'selected' : '' }}>Nom complet</option>
          <option value="moyenne" {{ $sort === 'moyenne' ? 'selected' : '' }}>Moyenne</option>
        </select>
      </div>

      <div>
        <button type="submit" class="btn btn-primary">Rechercher</button>
      </div>
    </form>
  </div>

  <div class="card" style="padding: 0; overflow: hidden;">
    <div style="overflow-x: auto;">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Matricule / Identifiant</th>
            <th>Nom complet / Information</th>
            <th>Filière / Trace</th>
            <th>Moyenne / Rôle</th>
          </tr>
        </thead>
        <tbody>
          @forelse ($students as $row)
            <tr>
              <td><strong>#{{ $row->id }}</strong></td>
              <td style="font-family: Consolas, monospace; font-size: 13px;">{{ $row->matricule }}</td>
              <td style="word-break: break-all;"><strong>{{ $row->full_name }}</strong></td>
              <td style="font-family: Consolas, monospace; font-size: 12.5px; word-break: break-all;">{{ $row->filiere }}</td>
              <td>{{ $row->moyenne }}</td>
            </tr>
          @empty
            <tr>
              <td colspan="5" style="text-align: center; padding: 28px; color: #64748B;">
                Aucun étudiant ne correspond à votre recherche.
              </td>
            </tr>
          @endforelse
        </tbody>
      </table>
    </div>
  </div>
@endsection
