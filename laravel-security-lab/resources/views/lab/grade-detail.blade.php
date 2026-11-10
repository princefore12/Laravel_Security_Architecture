@extends('layouts.lab')

@section('title', 'Détail Bulletin — Test IDOR')

@section('content')
<div class="card {{ $mode === 'vulnerable' ? 'card-vuln' : 'card-sec' }}">
    <h2 style="font-size:20px; color:#0F172A; margin-bottom:10px;">
        Bulletin #{{ $grade->id }} — {{ $grade->student->full_name }}
    </h2>
    @if($isForeign)
        <div class="alert alert-exploited">
            🚨 FUITE DE DONNÉES (IDOR) : Vous êtes connecté en tant que <strong>{{ $actingUser->name }}</strong> mais consultez le dossier confidentiel de <strong>{{ $grade->student->full_name }}</strong> !
        </div>
    @else
        <div class="alert alert-blocked">
            ✅ Accès légitime autorisé par <code>GradePolicy</code> pour <strong>{{ $actingUser->name }}</strong>.
        </div>
    @endif
    <p style="margin-bottom:6px;"><strong>Matière :</strong> {{ $grade->course_code }} — {{ $grade->course_name }}</p>
    <p style="margin-bottom:6px;"><strong>Note :</strong> {{ $grade->score }} / 20</p>
    <p style="margin-bottom:6px;"><strong>Appréciation confidentielle :</strong> {{ $grade->jury_remark }}</p>
    <a href="{{ route('lab.access', ['mode' => $mode]) }}" class="btn btn-ghost" style="margin-top:14px;">← Retour à l'Atelier 5</a>
</div>
@endsection
