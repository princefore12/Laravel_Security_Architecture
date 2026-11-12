@extends('layouts.portal')

@section('title', 'Administration Notes — Portail Académique UT LOKO')

@section('content')
  <div class="page-head">
    <div class="page-kicker">Espace Administrateur • Département ITER</div>
    <h1 class="page-title">Gestion Officielle des Notes L3</h1>
    <p class="page-sub">Modifiez et validez les notes enregistrées dans MariaDB (<code>loko_security_lab</code>).</p>
  </div>

  <div class="card" style="padding: 0; overflow: hidden;">
    <div style="overflow-x: auto;">
      <table class="data-table">
        <thead>
          <tr>
            <th>Bulletin</th>
            <th>Étudiant</th>
            <th>Matricule</th>
            <th>Matière</th>
            <th>Note actuelle</th>
            <th>Modifier la note</th>
          </tr>
        </thead>
        <tbody>
          @foreach ($grades as $grade)
            <tr>
              <td><a href="{{ route('portal.grades.show', $grade) }}" style="color: #8B1518; font-weight: 700; text-decoration: none;">#{{ $grade->id }}</a></td>
              <td><strong>{{ $grade->student?->full_name }}</strong></td>
              <td style="font-family: Consolas, monospace; font-size: 13px;">{{ $grade->student?->matricule }}</td>
              <td>{{ $grade->course_code }} — {{ $grade->course_name }}</td>
              <td><strong style="font-size: 15px; color: #0F172A;">{{ $grade->score }} / 20</strong></td>
              <td>
                <form method="POST" action="{{ route('portal.grades.update', $grade) }}" style="display: flex; gap: 8px; align-items: center;">
                  @csrf
                  <input type="number" step="0.25" min="0" max="20" name="score" value="{{ $grade->score }}" class="form-control" style="width: 90px; padding: 6px 8px;">
                  <button type="submit" class="btn btn-primary btn-sm">Enregistrer</button>
                </form>
              </td>
            </tr>
          @endforeach
        </tbody>
      </table>
    </div>
  </div>
@endsection
