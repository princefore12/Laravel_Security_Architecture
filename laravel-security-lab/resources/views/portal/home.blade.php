@extends('layouts.portal')

@section('title', 'Accueil — Portail Académique UT LOKO')

@section('content')
  <div class="card" style="background: linear-gradient(135deg, #8B1518 0%, #680E10 100%); color: #FFFFFF; border: none; margin-bottom: 24px; padding: 32px;">
    <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #FDE68A; margin-bottom: 8px;">
      Année Académique 2025 – 2026 • Groupe 5
    </div>
    <h1 style="font-size: 28px; font-weight: 800; margin-bottom: 10px;">
      Espace Numérique de Travail — Licence 3 Informatique
    </h1>
    <p style="font-size: 15px; color: #F1F5F9; max-width: 720px; margin-bottom: 22px;">
      Consultez l'annuaire de la promotion, suivez les publications du département ITER et accédez à vos relevés de notes semestriels sous l'encadrement académique du département.
    </p>
    <div style="display: flex; gap: 12px; flex-wrap: wrap;">
      <a href="{{ route('portal.directory') }}" class="btn" style="background: #FFFFFF; color: #8B1518;">Consulter l'annuaire</a>
      <a href="{{ route('portal.campus') }}" class="btn" style="background: rgba(255,255,255,0.16); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.35);">Actualités du campus</a>
      @guest
        <a href="{{ route('login') }}" class="btn" style="background: rgba(255,255,255,0.16); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.35);">Connexion étudiant</a>
      @endguest
    </div>
  </div>

  <div class="grid-3" style="margin-bottom: 24px;">
    <div class="card">
      <div style="font-size: 12.5px; color: #64748B; font-weight: 700; text-transform: uppercase;">Promotion L3 ITER</div>
      <div style="font-size: 32px; font-weight: 800; color: #0F172A; margin: 6px 0;">{{ $studentCount }}</div>
      <div style="font-size: 13.5px; color: #475569;">Étudiants actifs enregistrés dans le système universitaire.</div>
    </div>

    <div class="card">
      <div style="font-size: 12.5px; color: #64748B; font-weight: 700; text-transform: uppercase;">Module Principal</div>
      <div style="font-size: 20px; font-weight: 800; color: #8B1518; margin: 10px 0 6px;">Bases de Données &amp; Laravel</div>
      <div style="font-size: 13.5px; color: #475569;">Infrastructure locale MariaDB / XAMPP — Université UT LOKO.</div>
    </div>

    <div class="card">
      <div style="font-size: 12.5px; color: #64748B; font-weight: 700; text-transform: uppercase;">Services en ligne</div>
      <div style="font-size: 20px; font-weight: 800; color: #047857; margin: 10px 0 6px;">Opérationnels</div>
      <div style="font-size: 13.5px; color: #475569;">Annuaire, gestion de profil, bulletins et mur collaboratif.</div>
    </div>
  </div>

  <div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
      <h2 style="font-size: 18px; font-weight: 700;">Dernières annonces du campus</h2>
      <a href="{{ route('portal.campus') }}" style="font-size: 13.5px; font-weight: 600; color: #8B1518; text-decoration: none;">Voir tout →</a>
    </div>

    <div style="display: flex; flex-direction: column; gap: 12px;">
      @foreach ($recentPosts as $post)
        <div style="border: 1px solid #E2E8F0; border-radius: 10px; padding: 14px 16px; background: #F8FAFC;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; gap: 10px;">
            <strong style="font-size: 15px; color: #0F172A;">{{ $post->title }}</strong>
            <span style="font-size: 11.5px; font-weight: 700; color: #8B1518; background: #FEF2F2; padding: 2px 9px; border-radius: 999px;">{{ $post->category }}</span>
          </div>
          <div style="font-size: 13.5px; color: #475569;">{{ \Illuminate\Support\Str::limit(strip_tags($post->content), 160) }}</div>
          <div style="font-size: 12px; color: #64748B; margin-top: 6px;">Publié par {{ $post->author_name }}</div>
        </div>
      @endforeach
    </div>
  </div>
@endsection
