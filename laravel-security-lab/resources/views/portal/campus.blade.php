@extends('layouts.portal')

@section('title', 'Mur du Campus — Portail Académique UT LOKO')

@section('content')
  <div class="page-head">
    <div class="page-kicker">Vie Universitaire • Licence 3</div>
    <h1 class="page-title">Mur du Campus &amp; Avis Étudiants</h1>
    <p class="page-sub">Partagez les annonces de promotion, comptes rendus de projets et informations du département.</p>
  </div>

  <div class="grid-2" style="grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr); align-items: start;">
    <div style="display: flex; flex-direction: column; gap: 14px;">
      @foreach ($posts as $post)
        <div class="card">
          <div style="display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 8px;">
            <strong style="font-size: 16px; color: #0F172A;">{{ $post->title }}</strong>
            <span style="font-size: 11.5px; font-weight: 700; color: #8B1518; background: #FEF2F2; padding: 3px 10px; border-radius: 999px;">
              {{ $post->category }}
            </span>
          </div>

          <div style="font-size: 14px; color: #334155; margin-bottom: 10px; word-break: break-word;">
            @if ($hardened)
              {{ $post->content }}
            @else
              {!! $post->content !!}
            @endif
          </div>

          <div style="font-size: 12px; color: #64748B;">
            Publié par <strong>{{ $post->author_name }}</strong>
          </div>
        </div>
      @endforeach
    </div>

    <div class="card">
      <h2 style="font-size: 17px; font-weight: 700; margin-bottom: 14px;">Publier une annonce</h2>

      @auth
        <form method="POST" action="{{ route('portal.campus.store') }}">
          @csrf

          <div class="form-group">
            <label for="title">Titre du message</label>
            <input type="text" id="title" name="title" class="form-control" placeholder="Ex. Support de révision disponible" required>
          </div>

          <div class="form-group">
            <label for="category">Catégorie</label>
            <select id="category" name="category" class="form-control">
              <option value="Projet L3">Projet L3</option>
              <option value="Annonce L3">Annonce L3</option>
              <option value="Entraide">Entraide</option>
            </select>
          </div>

          <div class="form-group">
            <label for="content">Contenu du message</label>
            <textarea id="content" name="content" rows="4" class="form-control" placeholder="Rédigez votre publication..." required></textarea>
          </div>

          <button type="submit" class="btn btn-primary" style="width: 100%;">Publier sur le mur</button>
        </form>
      @else
        <p style="font-size: 14px; color: #475569; margin-bottom: 14px;">
          Vous devez être connecté avec votre compte UT LOKO pour publier un message sur le mur.
        </p>
        <a href="{{ route('login') }}" class="btn btn-primary" style="width: 100%;">Se connecter</a>
      @endauth
    </div>
  </div>
@endsection
