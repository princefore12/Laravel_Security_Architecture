@extends('layouts.portal')

@section('title', 'Relevé de Notes — Portail Académique UT LOKO')

@section('content')
  <div class="page-head">
    <div class="page-kicker">Scolarité • Relevé Individuel N° {{ $grade->id }}</div>
    <h1 class="page-title">Relevé de Notes Officiel</h1>
    <p class="page-sub">Document académique personnel de l'Université Tertiaire &amp; Technologique LOKO.</p>
  </div>

  <div class="card" style="max-width: 740px;">
    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 16px; border-bottom: 1px solid #E2E8F0; padding-bottom: 16px; margin-bottom: 18px; flex-wrap: wrap;">
      <div>
        <div style="font-size: 12px; color: #64748B; text-transform: uppercase; font-weight: 700;">Étudiant titulaire</div>
        <div style="font-size: 20px; font-weight: 800; color: #0F172A; margin-top: 2px;">{{ $grade->student?->full_name }}</div>
        <div style="font-size: 13px; color: #475569; margin-top: 2px;">
          Matricule : <span style="font-family: Consolas, monospace;">{{ $grade->student?->matricule }}</span> • {{ $grade->student?->filiere }}
        </div>
      </div>

      <div style="text-align: right;">
        <div style="font-size: 12px; color: #64748B; text-transform: uppercase; font-weight: 700;">Note obtenue</div>
        <div style="font-size: 28px; font-weight: 800; color: #8B1518;">{{ $grade->score }} / 20</div>
      </div>
    </div>

    <table class="data-table">
      <tbody>
        <tr>
          <td style="color: #64748B; font-weight: 600; width: 210px;">Code Unité d'Enseignement</td>
          <td style="font-family: Consolas, monospace; font-weight: 700;">{{ $grade->course_code }}</td>
        </tr>
        <tr>
          <td style="color: #64748B; font-weight: 600;">Intitulé du module</td>
          <td><strong>{{ $grade->course_name }}</strong></td>
        </tr>
        <tr>
          <td style="color: #64748B; font-weight: 600;">Appréciation confidentielle du jury</td>
          <td>{{ $grade->jury_remark }}</td>
        </tr>
      </tbody>
    </table>

    <div style="margin-top: 20px; display: flex; gap: 10px;">
      <a href="{{ route('portal.home') }}" class="btn btn-outline btn-sm">← Retour à l'accueil</a>
    </div>
  </div>
@endsection
