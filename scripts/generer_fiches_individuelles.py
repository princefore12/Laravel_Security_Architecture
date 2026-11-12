#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Générateur des 5 Fiches Individuelles de Soutenance & Démonstration via ReportLab
Groupe 5 — Thème n° 12 : La sécurité dans une application Laravel (XAMPP / MariaDB)
Université Tertiaire & Technologique LOKO (UT LOKO) — Licence 3 Informatique
"""

import os
import html
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, PageBreak, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "livrables" / "fiches-individuelles"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Couleurs officielles
C_BORDEAUX = HexColor("#8B1518")
C_GOLD = HexColor("#D97706")
C_NAVY = HexColor("#0F172A")
C_SLATE = HexColor("#1E293B")
C_MUTED = HexColor("#64748B")
C_LIGHT_BG = HexColor("#F8FAFC")
C_BORDER = HexColor("#CBD5E1")
C_CODE_BG = HexColor("#0F172A")
C_CODE_TXT = HexColor("#38BDF8")
C_ALERT_BG = HexColor("#FEF3C7")
C_ALERT_BORDER = HexColor("#F59E0B")
C_SUCCESS_BG = HexColor("#ECFDF5")
C_SUCCESS_BORDER = HexColor("#10B981")
C_TECH_BG = HexColor("#EFF6FF")
C_TECH_BORDER = HexColor("#3B82F6")

FICHES = [
    {
        "id": "sore_ramatou",
        "filename": "Fiche_Oral_Demo_Sore_Ramatou",
        "nom_complet": "SORE RAMATOU",
        "role_titre": "Coordinatrice — Accueil Général & Pilier 1 : Injection SQL (SQLi)",
        "timing": "00:00 – 04:00 (4 minutes chrono)",
        "slides": "Diapositives 1 à 7 (Accueil, Problématique, Architecture 7 couches, Pilier 1 SQLi)",
        "theme_color": HexColor("#8B1518"),
        "url_cible": "http://127.0.0.1:8000/annuaire et http://127.0.0.1:8000/connexion",
        "identifiants": "admin@loko.ci'# (ou admin@loko.ci' -- ') avec mot de passe quelconque",
        "discours": [
            (
                "1. Accueil & Lancement officiel (00:00 – 01:15)",
                "« Bonjour Monsieur CAMARA, bonjour chers camarades. Nous sommes le <b>Groupe 5</b>, composé de "
                "<b>Sore Ramatou, Siby Mody, Boin Naomi, Traoré Charifat Leyla et Djan Kouassi Noël</b>. Aujourd'hui, nous "
                "avons l'honneur de vous présenter le <b>Thème n° 12 : La sécurité dans une application Laravel</b>, "
                "reliée à une base de données <b>MySQL / MariaDB sous XAMPP</b>.<br/><br/>"
                "Dans les exposés précédents, notre promotion a exploré l'architecture MVC, le routage, les contrôleurs, Blade "
                "et les migrations. Mais <b>une application fonctionnelle qui n'est pas sécurisée est une porte grande ouverte sur son serveur</b>. "
                "Selon le référentiel mondial <b>OWASP Top 10</b>, plus de 70 % des compromissions ciblent directement la couche applicative web.<br/><br/>"
                "La philosophie de Laravel est <i>\"Secure by Default\"</i> (sécurisé par défaut). Mais dès qu'un développeur commet l'erreur "
                "de contourner ses conventions natives, il réintroduit des failles critiques. »"
            ),
            (
                "2. Annonce du dispositif en direct (01:15 – 02:15)",
                "« Pour vous le prouver sans artifice, nous avons conçu le <b>Portail Académique UT LOKO</b> (<code>127.0.0.1:8000</code>). "
                "Aucun bouton de triche à l'écran : nous allons l'attaquer <b>exactement comme de vrais pirates</b> avec les outils "
                "standards du navigateur (barre d'adresse, <code>F12</code>, payloads SQL et site leurre sur le port <code>8001</code>).<br/><br/>"
                "Puis en fin de parcours, <b>Djan Kouassi Noël</b> activera en un clic les défenses globales dans le fichier <code>.env</code>. "
                "J'ouvre immédiatement les hostilités avec le <b>Pilier n° 1 : l'Injection SQL</b>. »"
            ),
            (
                "3. Transition vers Siby Mody (03:50 – 04:00)",
                "« Protéger la lecture des données est primordial, mais que se passe-t-il lorsqu'un étudiant manipule directement "
                "le formulaire HTML dans son navigateur avec <code>F12</code> pour s'octroyer les droits administrateur ? "
                "Je cède la parole à <b>Siby Mody</b> pour le <b>Mass Assignment</b>. »"
            )
        ],
        "demo": [
            {
                "etape": "Étape 1 : Provocation d'une erreur SQL brute (02:15)",
                "action": "Ouvrir l'onglet <b>Annuaire</b> (<code>http://127.0.0.1:8000/annuaire</code>). Dans le champ de recherche, saisir une simple apostrophe : <code>'</code> puis valider.",
                "effet": "<b>Effet WAHOU :</b> Avec <code>APP_DEBUG=true</code>, Laravel affiche l'erreur Ignition et la requête SQL brute brisée dans MariaDB !",
                "payload": "'"
            },
            {
                "etape": "Étape 2 : Exfiltration de la table 'users' via UNION SELECT (02:50)",
                "action": "Revenir sur <code>/annuaire</code> et coller le payload UNION dans le champ de recherche :",
                "effet": "<b>Effet WAHOU :</b> La table de l'annuaire affiche les e-mails, les hash <b>Bcrypt</b>, les anciens hash <b>MD5</b> identiques (<code>9c9b18b4...</code>) et les rôles !",
                "payload": "' AND 1=0 UNION SELECT id, email, password, legacy_md5, role FROM users -- '"
            },
            {
                "etape": "Étape 3 : Contournement d'authentification (Auth Bypass) (03:25)",
                "action": "Cliquer sur <b>Se connecter</b> (<code>/connexion</code>). Saisir l'injection ci-dessous avec n'importe quel mot de passe :",
                "effet": "<b>Effet WAHOU :</b> Vous entrez instantanément sous l'identité <b>Prof. M. Camara • Administrateur</b> et le menu <b>Administration</b> apparaît ! Cliquez sur <b>Déconnexion</b>.",
                "payload": "admin@loko.ci'#"
            }
        ],
        "qr": [
            (
                "Q1 : Si j'utilise Eloquent ORM dans Laravel, suis-je protégé à 100 % contre les injections SQL ?",
                "<b>Non, pas à 100 %</b> si le développeur utilise mal les méthodes brutes comme <code>whereRaw()</code>, "
                "<code>selectRaw()</code>, <code>orderByRaw()</code> ou <code>DB::raw()</code> en y concaténant directement une variable "
                "(ex. <code>whereRaw(\"matricule = '$q'\")</code>). Pour rester protégé même en SQL brut, il faut <b>toujours passer un tableau "
                "de paramètres préparés PDO en second argument</b> : <code>whereRaw('matricule = ?', [$q])</code>."
            ),
            (
                "Q2 : Comment fonctionne concrètement une requête préparée (Prepared Statement) entre Laravel (PDO) et MariaDB sous XAMPP ?",
                "Elle s'exécute en <b>deux étapes distinctes</b> :<br/>"
                "1. Laravel envoie d'abord le squelette SQL avec des marqueurs <code>?</code> à MariaDB (<code>SELECT * FROM students WHERE matricule = ?</code>). MariaDB compile l'arbre syntaxique.<br/>"
                "2. Laravel envoie ensuite la valeur du paramètre séparément. Même si le paramètre contient <code>' OR '1'='1</code>, MariaDB ne recompile plus le SQL : il compare simplement la colonne comme une chaîne littérale inoffensive."
            ),
            (
                "Q3 : Pourquoi est-il dangereux de laisser l'utilisateur 'root' sans mot de passe de XAMPP dans le fichier .env en production ?",
                "L'utilisateur <code>root</code> de MariaDB possède les pleins privilèges (<code>DROP DATABASE</code>, création d'utilisateurs, "
                "lecture de toutes les bases du serveur XAMPP, et écriture de fichiers via <code>INTO OUTFILE</code>). "
                "En cas de faille, l'attaquant contrôle l'intégralité du serveur. En production, on applique le <b>principe du moindre privilège</b> "
                "avec un utilisateur SQL dédié limité aux seules commandes <code>SELECT, INSERT, UPDATE, DELETE</code> sur la base de l'application."
            )
        ],
        "memo": [
            "Si l'erreur SQL ne s'affiche pas à l'étape 1, vérifiez que <code>APP_DEBUG=true</code> dans <code>laravel-security-lab/.env</code>.",
            "Pour le payload UNION, attention à l'espace après les deux tirets : <code>-- '</code>. L'apostrophe finale évite que Laravel ne tronque l'espace.",
            "N'oubliez pas de vous <b>déconnecter</b> avant de laisser la place à Siby Mody !"
        ]
    },
    {
        "id": "siby_mody",
        "filename": "Fiche_Oral_Demo_Siby_Mody",
        "nom_complet": "SIBY MODY",
        "role_titre": "Présentateur — Pilier 2 : Mass Assignment & Validation FormRequest",
        "timing": "04:00 – 08:00 (4 minutes chrono)",
        "slides": "Diapositives 8 et 9 (Mass Assignment, Attribut $fillable, FormRequest & Escalade BDD)",
        "theme_color": HexColor("#1E3A8A"),
        "url_cible": "http://127.0.0.1:8000/connexion puis http://127.0.0.1:8000/profil",
        "identifiants": "mody.siby@loko.ci / Loko@2026!",
        "discours": [
            (
                "1. Introduction du concept (04:00 – 04:50)",
                "« Merci Ramatou. Bonjour Monsieur le Professeur, bonjour à tous. Je suis <b>Siby Mody</b>, et je vais vous "
                "présenter une vulnérabilité redoutable propre aux frameworks ORM modernes comme Eloquent : le <b>Mass Assignment</b> "
                "(ou assignation de masse) et son impact direct sur l'intégrité de notre base de données MariaDB.<br/><br/>"
                "Pour accélérer le développement, Laravel permet d'insérer ou de mettre à jour un modèle en une seule ligne grâce à "
                "<code>$request->all()</code> ou <code>update()</code>. C'est extrêmement rapide… mais particulièrement dangereux si le modèle "
                "n'est pas strictement verrouillé ! »"
            ),
            (
                "2. Explication de la faille en BDD (04:50 – 05:45)",
                "« Pourquoi ? Dans notre table <code>users</code> sous XAMPP, nous stockons le nom, l'email, le mot de passe, mais aussi "
                "une colonne critique : <b><code>role</code></b>, qui vaut <code>student</code> pour les étudiants et <code>admin</code> "
                "pour les professeurs.<br/><br/>"
                "Sur l'interface de profil, seuls le nom et l'email sont modifiables. Mais je vais ouvrir les <b>outils de développement "
                "du navigateur (<code>F12</code>)</b> comme un pirate, <b>injecter un champ HTML caché <code>role=admin</code></b>, et "
                "soumettre le formulaire. Regardez bien l'escalade de privilèges en direct. »"
            ),
            (
                "3. Transition vers Boin Naomi (07:45 – 08:00)",
                "« Nous venons de voir comment une requête HTTP falsifiée peut corrompre un rôle dans MariaDB. Mais que se passe-t-il "
                "si un étudiant injecte du code JavaScript malveillant sur le mur d'actualités de l'université ? "
                "<b>Boin Naomi</b> vous présente le <b>Pilier n° 3 : la faille XSS</b>. »"
            )
        ],
        "demo": [
            {
                "etape": "Étape 1 : Connexion étudiante & Constat initial (05:45)",
                "action": "Se connecter sur <code>/connexion</code> avec <code>mody.siby@loko.ci</code> / <code>Loko@2026!</code>. Cliquer sur son nom en haut à droite → <b>Mon Profil</b> (<code>/profil</code>).",
                "effet": "<b>Constat :</b> Seuls <i>Nom</i> et <i>Email</i> sont éditables. Le badge affiche <b>Étudiant (student)</b> et le menu d'administration n'existe pas.",
                "payload": "mody.siby@loko.ci"
            },
            {
                "etape": "Étape 2 : Injection du champ caché dans DevTools (F12) (06:30)",
                "action": "Appuyer sur <b>F12</b> (Onglet Éléments). Repérer la balise <code>&lt;form method=\"POST\" action=\".../profil\"&gt;</code>. Faire <b>Clic droit → Edit as HTML</b>, et coller avant le bouton :",
                "effet": "Le champ caché est maintenant injecté directement dans le DOM en mémoire du navigateur.",
                "payload": '<input type="hidden" name="role" value="admin">'
            },
            {
                "etape": "Étape 3 : Validation & Escalade de privilèges (07:15)",
                "action": "Fermer <code>F12</code> et cliquer sur le bouton bleu <b>« Enregistrer mes informations »</b>.",
                "effet": "<b>Effet WAHOU :</b> La page se recharge : le badge passe à <b>Administrateur (admin)</b>, le menu <b>Administration</b> apparaît, et la table <code>users</code> confirme <code>role = 'admin'</code> ! Cliquez sur <b>Déconnexion</b>.",
                "payload": "Validation du formulaire"
            }
        ],
        "qr": [
            (
                "Q4 : Quelle est la différence exacte entre $fillable et $guarded dans un modèle Eloquent ? Et lequel recommandez-vous ?",
                "<b>$fillable</b> est une <b>liste blanche (whitelist)</b> : seuls les attributs explicitement mentionnés peuvent être assignés en masse (<code>create()</code>, <code>update()</code>).<br/>"
                "<b>$guarded</b> est une <b>liste noire (blacklist)</b> : les attributs listés sont protégés, tous les autres sont autorisés.<br/>"
                "<b>Recommandation formelle :</b> Toujours utiliser <b><code>$fillable</code></b>. Si un développeur ajoute plus tard une colonne sensible en base (ex. <code>solde</code> ou <code>is_admin</code>) et oublie de l'inscrire dans <code>$guarded</code>, elle devient automatiquement piratable. De plus, écrire <code>$guarded = []</code> supprime toute sécurité."
            ),
            (
                "Q5 : Si j'utilise déjà $fillable sur mon modèle User, pourquoi utiliser en plus une classe FormRequest (UpdateProfileRequest) ?",
                "C'est le principe fondamental de <b>défense en profondeur (Defense in Depth)</b> :<br/>"
                "- La <code>FormRequest</code> filtre et valide la requête dès la <b>couche HTTP d'entrée</b> : elle vérifie les types de données, les formats e-mail, les contraintes métier et renvoie des erreurs claires à l'utilisateur. Sa méthode <code>$request->validated()</code> n'extrait que les champs déclarés.<br/>"
                "- <code>$fillable</code> agit en <b>dernier rempart</b> au niveau du modèle ORM juste avant l'écriture en base de données MariaDB."
            ),
            (
                "Q6 : Comment un administrateur légitime fait-il pour modifier le champ 'role' d'un utilisateur si 'role' n'est pas dans $fillable ?",
                "Dans un contrôleur d'administration sécurisé par une Policy ou un middleware d'autorisation, l'administrateur assigne l'attribut de manière explicite : "
                "<code>$user->role = 'admin'; $user->save();</code>.<br/>"
                "L'assignation manuelle propriété par propriété contourne volontairement <code>$fillable</code> car le développeur a explicitement et consciemment nommé la colonne dans son code source."
            )
        ],
        "memo": [
            "Pour modifier le HTML dans F12 : repérez bien la balise <code>&lt;form&gt;</code>, faites Clic droit → <i>Edit as HTML</i>, collez la ligne et cliquez en dehors du bloc pour valider.",
            "Si le badge ne change pas, vérifiez que le nom du champ est bien <code>name=\"role\"</code> et sa valeur <code>value=\"admin\"</code>.",
            "N'oubliez pas de cliquer sur <b>Déconnexion</b> après avoir montré le menu Administration débloqué."
        ]
    },
    {
        "id": "boin_naomi",
        "filename": "Fiche_Oral_Demo_Boin_Naomi",
        "nom_complet": "BOIN NAOMI",
        "role_titre": "Présentatrice — Pilier 3 : Cross-Site Scripting (XSS Stocké) & Moteur Blade",
        "timing": "08:00 – 12:00 (4 minutes chrono)",
        "slides": "Diapositives 10 et 11 (XSS Stocké, Blade {{ }} vs {!! !!}, Cookies HttpOnly & En-tête CSP)",
        "theme_color": HexColor("#047857"),
        "url_cible": "http://127.0.0.1:8000/campus",
        "identifiants": "naomi.boin@loko.ci / Loko@2026!",
        "discours": [
            (
                "1. Définition et mécanisme du XSS Stocké (08:00 – 08:50)",
                "« Merci Mody. Bonjour à tous. Je suis <b>Boin Naomi</b> et j'aborde le <b>Pilier n° 3 : le Cross-Site Scripting (XSS)</b> "
                "et la protection assurée par le moteur de templates <b>Blade</b>.<br/><br/>"
                "Contrairement à l'injection SQL qui attaque directement le serveur MariaDB, la faille <b>XSS Stockée (Stored XSS)</b> "
                "utilise la base de données (notre table <code>campus_posts</code>) comme <b>vecteur de stockage et de propagation</b>. "
                "L'attaquant publie un message d'apparence anodine, mais qui contient une charge utile JavaScript malveillante.<br/><br/>"
                "Dès qu'un autre utilisateur — qu'il soit étudiant, enseignant ou recteur — consulte le <b>Mur du Campus</b>, son propre navigateur "
                "interprète et exécute ce script à son insu. Si le cookie de session n'est pas protégé, le pirate peut voler son compte ! »"
            ),
            (
                "2. La syntaxe Blade au cœur de la vulnérabilité (08:50 – 09:45)",
                "« Dans Laravel, la frontière entre vulnérabilité et sécurité tient en deux syntaxes dans les vues <code>.blade.php</code> :<br/>"
                "- La syntaxe <code>{!! $post->content !!}</code> (point d'exclamation) affiche le contenu brut sans aucun filtrage : c'est la porte ouverte au XSS.<br/>"
                "- La syntaxe sécurisée <code>{{ $post->content }}</code> (doubles accolades) appelle automatiquement la fonction d'échappement <code>e()</code>.<br/><br/>"
                "Regardons ce qui se passe actuellement sur notre Portail lorsque nous publions un payload XSS. »"
            ),
            (
                "3. Transition vers Traoré Charifat Leyla (11:45 – 12:00)",
                "« Même si aucun script malveillant ne s'exécute sur notre propre site, un attaquant peut piéger un utilisateur connecté "
                "depuis un site tiers complètement distinct pour effectuer des opérations à son insu. "
                "<b>Traoré Charifat Leyla</b> vous présente le <b>Pilier n° 4 : la faille CSRF</b>. »"
            )
        ],
        "demo": [
            {
                "etape": "Étape 1 : Connexion étudiante & Inspection des cookies (09:45)",
                "action": "Se connecter avec <code>naomi.boin@loko.ci</code> / <code>Loko@2026!</code>, puis aller sur <b>Mur du Campus</b> (<code>/campus</code>). Ouvrir <b>F12 → Application → Cookies → http://127.0.0.1:8000</b>.",
                "effet": "<b>Preuve technique :</b> La case <b>HttpOnly</b> du cookie <code>laravel_session</code> est décochée, et dans l'onglet <b>Network</b>, l'en-tête <code>Content-Security-Policy</code> est totalement absent.",
                "payload": "F12 > Application > Cookies"
            },
            {
                "etape": "Étape 2 : Publication de la charge utile XSS (10:30)",
                "action": "Dans le formulaire de publication sur <code>/campus</code>, saisir l'annonce suivante :",
                "effet": "Le message est persisté dans la table <code>campus_posts</code> de MariaDB sans aucun nettoyage côté serveur.",
                "payload": "<img src=\"x\" onerror=\"alert('XSS UT LOKO ! Cookie volé : ' + document.cookie)\">"
            },
            {
                "etape": "Étape 3 : Exécution du script & Pop-up de vol de session (11:15)",
                "action": "Cliquer sur le bouton vert <b>« Publier sur le mur »</b>.",
                "effet": "<b>Effet WAHOU :</b> La page se recharge et une vraie alerte JavaScript surgit à l'écran : <code>XSS UT LOKO ! Cookie volé : laravel_session=...</code> ! Cliquez sur OK. N'importe quel visiteur du mur voit cette alerte.",
                "payload": "Clic sur Publier"
            }
        ],
        "qr": [
            (
                "Q7 : Que fait exactement Laravel derrière les doubles accolades {{ $variable }} dans une vue Blade ?",
                "Le compilateur Blade traduit <code>{{ $variable }}</code> en code PHP natif : <code>&lt;?php echo e($variable); ?&gt;</code>.<br/>"
                "Le helper interne <code>e()</code> exécute la fonction PHP <code>htmlspecialchars($variable, ENT_QUOTES, 'UTF-8', true)</code>. "
                "Cela convertit systématiquement les 5 caractères spéciaux HTML sensibles (<code>&amp;</code>, <code>\"</code>, <code>'</code>, <code>&lt;</code>, <code>&gt;</code>) "
                "en leurs entités HTML inoffensives correspondantes (ex. <code>&amp;lt;script&amp;gt;</code>), neutralisant toute tentative d'injection dans le navigateur."
            ),
            (
                "Q8 : Dans quel cas légitime a-t-on quand même besoin d'utiliser {!! $variable !!} et comment le sécuriser ?",
                "On utilise <code>{!! !!}</code> lorsqu'on doit afficher du HTML enrichi rédigé via un éditeur WYSIWYG (comme TinyMCE ou CKEditor pour des cours en ligne).<br/>"
                "<b>Pour le sécuriser :</b> Il ne faut <b>jamais</b> afficher directement la saisie brute ! Il est obligatoire de la nettoyer côté serveur avant l'affichage avec un purificateur HTML basé sur une liste blanche stricte, comme le package <b>HTMLPurifier</b> (<code>mews/purifier</code> dans Laravel), qui élimine impitoyablement les balises <code>&lt;script&gt;</code> et les événements <code>onerror</code>."
            ),
            (
                "Q9 : Si un pirate réussit malgré tout une faille XSS, comment Laravel empêche-t-il le vol du cookie de session en JavaScript ?",
                "Grâce au drapeau de sécurité <b><code>HttpOnly</code></b> ! Dans <code>config/session.php</code>, Laravel configure par défaut la directive <code>'http_only' =&gt; true</code>.<br/>"
                "Lorsque le serveur envoie le cookie au navigateur via l'en-tête HTTP <code>Set-Cookie: laravel_session=...; HttpOnly</code>, le moteur du navigateur interdit formellement à tout script JavaScript (y compris <code>document.cookie</code>) d'accéder au contenu du cookie. Même si le code pirate s'exécute, il ne peut ni lire ni exfiltrer la session."
            )
        ],
        "memo": [
            "Le payload utilise une balise <code>&lt;img&gt;</code> avec une source invalide (<code>src=\"x\"</code>) pour déclencher immédiatement l'événement <code>onerror</code>.",
            "Après avoir cliqué sur OK dans la boîte de dialogue alert(), laissez le mur affiché pour que le jury constate la présence du message.",
            "Rappelez que lors du durcissement final de Noël, ce message sera automatiquement échappé et n'exécutera plus rien."
        ]
    },
    {
        "id": "traore_charifat_leyla",
        "filename": "Fiche_Oral_Demo_Traore_Charifat_Leyla",
        "nom_complet": "TRAORÉ CHARIFAT LEYLA",
        "role_titre": "Présentatrice — Pilier 4 : Cross-Site Request Forgery (CSRF) & Sessions",
        "timing": "12:00 – 16:00 (4 minutes chrono)",
        "slides": "Diapositives 12 et 13 (CSRF, Jeton secret @_csrf, Falsification inter-sites & Cookie SameSite)",
        "theme_color": HexColor("#B45309"),
        "url_cible": "http://127.0.0.1:8000/admin/notes et http://127.0.0.1:8001",
        "identifiants": "admin@loko.ci / Camara@Loko2026",
        "discours": [
            (
                "1. Le piège du Cross-Site Request Forgery (12:00 – 12:50)",
                "« Merci Naomi. Bonjour Monsieur CAMARA, bonjour à tous. Je suis <b>Traoré Charifat Leyla</b>, et je vais vous "
                "présenter le <b>Pilier n° 4 : le Cross-Site Request Forgery (CSRF)</b>, ou falsification de requête inter-sites.<br/><br/>"
                "Le scénario d'attaque est redoutablement classique : un enseignant ou un administrateur est connecté sur le "
                "<b>Portail UT LOKO (<code>http://127.0.0.1:8000</code>)</b>. Son navigateur conserve un cookie de session valide. "
                "Pendant qu'il travaille, il clique sur un lien externe envoyé par email ou hébergé sur un autre domaine — ici, notre "
                "second serveur indépendant <b><code>http://127.0.0.1:8001</code></b> déguisé en <i>Programme National Bourses d'Excellence</i>.<br/><br/>"
                "Ce site externe contient un formulaire caché qui cible directement notre portail académique. Puisque le navigateur "
                "transmet automatiquement les cookies lors des requêtes HTTP, l'attaque réussit si aucune vérification n'est effectuée ! »"
            ),
            (
                "2. Le bouclier @csrf de Laravel (12:50 – 13:45)",
                "« Pour bloquer ce piratage, Laravel intègre nativement la directive Blade <b><code>@csrf</code></b>. Elle génère un jeton "
                "cryptographique aléatoire secret (<code>_token</code>) stocké dans la session de l'utilisateur.<br/><br/>"
                "À chaque requête <code>POST</code>, <code>PUT</code> ou <code>DELETE</code>, le middleware <code>ValidateCsrfToken</code> "
                "vérifie la correspondance exacte entre le jeton soumis et celui de la session. Un site tiers ne pouvant pas lire ce jeton "
                "secret, la requête est impitoyablement rejetée avec l'erreur <b>HTTP 419 Page Expired</b>.<br/><br/>"
                "Faisons l'expérience en direct entre nos deux serveurs ! »"
            ),
            (
                "3. Transition vers Djan Kouassi Noël (15:45 – 16:00)",
                "« Nous avons piraté la base de données via SQLi, usurpé les droits administrateur via Mass Assignment, volé des sessions via XSS "
                "et falsifié des notes via CSRF. Il nous reste à sécuriser les accès individuels, le hachage des mots de passe, et surtout à activer "
                "en direct le bouclier global de Laravel. Je cède la parole à <b>Djan Kouassi Noël pour le bouquet final</b>. »"
            )
        ],
        "demo": [
            {
                "etape": "Étape 1 : Connexion Administrateur & Constat de la note initiale (13:45)",
                "action": "Sur <code>http://127.0.0.1:8000/connexion</code>, se connecter avec le compte officiel <code>admin@loko.ci</code> / <code>Camara@Loko2026</code>. Ouvrir le menu <b>Administration</b> (<code>/admin/notes</code>).",
                "effet": "<b>Constat initial :</b> Dans la table des notes, le Bulletin n° 4 de <b>Traoré Charifat Leyla</b> affiche la note légitime de <b>16.00 / 20</b>.",
                "payload": "admin@loko.ci"
            },
            {
                "etape": "Étape 2 : Bascule sur le site leurre externe (Port 8001) (14:30)",
                "action": "Ouvrir l'onglet du site tiers externe : <b><code>http://127.0.0.1:8001</code></b> (Programme Bourses d'Excellence CI). Appuyer sur <b>Ctrl + U</b> pour montrer le code source.",
                "effet": "<b>Preuve du piège :</b> Le formulaire HTML pointe vers <code>http://127.0.0.1:8000/notes/4/modifier</code> avec <code>score=20.00</code> et <b>aucun champ _token</b> !",
                "payload": "Ctrl + U sur :8001"
            },
            {
                "etape": "Étape 3 : Déclenchement de l'attaque CSRF (15:15)",
                "action": "Sur la page <code>:8001</code>, cliquer sur le gros bouton jaune <b>« Vérifier mon éligibilité à la Bourse »</b>.",
                "effet": "<b>Effet WAHOU :</b> La requête est transmise avec la session admin active. La page se redirige et le Bulletin n° 4 affiche désormais <b>20.00 / 20</b> dans MariaDB ! La falsification inter-sites a réussi !",
                "payload": "Clic sur le bouton piège"
            }
        ],
        "qr": [
            (
                "Q10 : Pourquoi les requêtes GET ne sont-elles pas soumises à la vérification du jeton CSRF dans Laravel ?",
                "Conformément à la spécification officielle du protocole HTTP (norme <b>RFC 9110</b>), les requêtes <code>GET</code> et <code>HEAD</code> "
                "sont définies comme des <b>méthodes sûres (safe) et idempotentes</b> : elles sont strictement réservées à la lecture et à la consultation "
                "d'informations, sans jamais altérer l'état de la base de données.<br/>"
                "C'est pourquoi une opération métier sensible (modification de note, virement, suppression de compte) ne doit <b>jamais</b> être "
                "associée à une route <code>Route::get(...)</code>, mais obligatoirement à <code>POST</code>, <code>PUT</code>, <code>PATCH</code> ou <code>DELETE</code>, "
                "toutes protégées par le middleware CSRF."
            ),
            (
                "Q11 : Que signifie exactement le code d'erreur HTTP 419 Page Expired de Laravel ? Est-ce un code HTTP officiel ?",
                "Le code <b>HTTP 419</b> n'est pas un code officiel du standard IANA (les standards recommandent plutôt 403 Forbidden ou 400 Bad Request).<br/>"
                "Il a été spécialement inventé par Laravel pour signaler une exception interne <b><code>TokenMismatchException</code></b> levée par le middleware "
                "<code>ValidateCsrfToken</code>. Cela signifie que le jeton <code>_token</code> soumis par le formulaire ne correspond pas à celui enregistré "
                "dans la session de l'utilisateur (soit parce qu'il s'agit d'une attaque CSRF externe sans jeton, soit parce que la session a expiré)."
            ),
            (
                "Q12 : Quel est le rôle de l'attribut de cookie 'same_site' configuré sur 'lax' dans config/session.php ?",
                "L'attribut <b><code>SameSite</code></b> est un mécanisme de sécurité moderne géré directement par le navigateur.<br/>"
                "Réglé sur <code>'lax'</code> par défaut dans Laravel, il ordonne au navigateur de <b>ne jamais envoyer le cookie de session lors d'une requête inter-sites "
                "provenant d'un domaine tiers initiée par un formulaire <code>POST</code></b>.<br/>"
                "Il constitue ainsi une seconde ligne de défense en profondeur, parfaitement complémentaire au jeton secret <code>@csrf</code>."
            )
        ],
        "memo": [
            "Assurez-vous que l'onglet <code>http://127.0.0.1:8001</code> est bien ouvert avant de commencer votre intervention.",
            "Avant de cliquer sur le bouton du site leurre, montrez bien au professeur que la note de Leyla est à 16/20 sur le portail :8000.",
            "Après le clic sur le bouton leurre, basculez sur l'onglet :8000 pour montrer la note qui s'est transformée en 20/20 sous ses yeux."
        ]
    },
    {
        "id": "djan_kouassi_noel",
        "filename": "Fiche_Oral_Demo_Djan_Kouassi_Noel",
        "nom_complet": "DJAN KOUASSI NOËL",
        "role_titre": "Présentateur & Clôture — Pilier 5 : IDOR, Bcrypt, Durcissement .env & Bilan",
        "timing": "16:00 – 20:00 (4 minutes chrono)",
        "slides": "Diapositives 14 à 19 (IDOR/Policies, Bcrypt, RateLimiter, Basculement .env & Bonnes pratiques)",
        "theme_color": HexColor("#7C2D12"),
        "url_cible": "http://127.0.0.1:8000/bulletins/1 -> /bulletins/2 et fichier .env",
        "identifiants": "ramatou.sore@loko.ci / Loko@2026! puis modification de laravel-security-lab/.env",
        "discours": [
            (
                "1. Le Pilier n° 5 et l'exploitation IDOR en direct (16:00 – 17:15)",
                "« Merci Leyla. Bonjour Monsieur le Professeur, bonjour chers camarades. Je suis <b>Djan Kouassi Noël</b>, et j'ai "
                "le privilège de clôturer notre présentation avec le <b>Pilier n° 5 : Cryptographie en base, Contrôle d'accès "
                "(<code>IDOR</code> / <code>Policies</code>), Anti-Brute-Force et Durcissement global <code>.env</code></b>.<br/><br/>"
                "Commençons par la faille <b>IDOR (Insecure Direct Object Reference)</b> : un utilisateur légitimement connecté peut-il "
                "accéder aux données privées d'un autre utilisateur en modifiant simplement un chiffre dans la barre d'adresse ?<br/><br/>"
                "Connectons-nous en tant qu'étudiante simple avec le compte de <b>Sore Ramatou</b> (<code>ramatou.sore@loko.ci</code>). "
                "Elle clique sur <i>Mes Notes</i> : l'URL est <code>/bulletins/1</code>. Je remplace simplement <code>/1</code> par <code>/2</code> "
                "dans le navigateur… et sans aucune autorisation, j'accède instantanément au relevé confidentiel de <b>Siby Mody (16.25/20)</b> ! »"
            ),
            (
                "2. Le Climax : Le Basculement à chaud .env (17:15 – 18:45)",
                "« Regardez maintenant la puissance architecturale de Laravel. Nous n'allons même pas redémarrer le serveur PHP ! "
                "J'ouvre le fichier <code>.env</code> dans VS Code et je bascule la variable <code>SECURITY_HARDENED=false</code> vers <b><code>true</code></b>.<br/><br/>"
                "Dès cet instant, l'armure native de Laravel s'active : requêtes préparées PDO, validation <code>FormRequest</code>, "
                "protection Blade <code>{{ }}</code>, cookie <code>HttpOnly</code>, CSP, contrôle d'accès <code>GradePolicy</code> et jeton <code>@csrf</code>.<br/><br/>"
                "Reprenons immédiatement nos 5 attaques avec un simple rafraîchissement <b><code>F5</code></b> pour constater le blocage intégral ! »"
            ),
            (
                "3. Bonnes pratiques de production & Conclusion (18:45 – 20:00)",
                "« Enfin, sur les diapositives 17 à 19, nous synthétisons les <b>3 règles d'or entre Laravel et XAMPP/MariaDB</b> en environnement réel :<br/>"
                "1. Impérativement <code>APP_DEBUG=false</code> et <code>APP_ENV=production</code> pour ne jamais exposer nos requêtes SQL.<br/>"
                "2. Un utilisateur MariaDB dédié avec les seuls droits <code>SELECT, INSERT, UPDATE, DELETE</code>, jamais le compte <code>root</code>.<br/>"
                "3. La racine Apache pointée exclusivement sur le dossier <code>/public</code> pour protéger le fichier <code>.env</code> et le code source.<br/><br/>"
                "<b>En conclusion</b>, notre suite automatisée <b>PHPUnit (8 tests, 65 assertions)</b> valide en continu ces 5 piliers de sécurité. "
                "Laravel offre une armure exceptionnelle contre l'OWASP Top 10 dès lors que l'on applique ses conventions. "
                "Nous vous remercions pour votre attention et sommes à votre entière disposition pour répondre à vos questions ! »"
            )
        ],
        "demo": [
            {
                "etape": "Étape 1 : Exploitation IDOR par manipulation d'URL (16:15)",
                "action": "Se connecter avec <code>ramatou.sore@loko.ci</code> / <code>Loko@2026!</code>. Cliquer sur <b>Mes Notes</b> (<code>/bulletins/1</code>). Dans la barre d'adresse du navigateur, remplacer <code>/1</code> par <b><code>/2</code></b> puis appuyer sur Entrée.",
                "effet": "<b>Effet WAHOU :</b> Le relevé de notes confidentiel de <b>Siby Mody (16.25 / 20)</b> s'affiche à l'écran sans aucun contrôle d'accès !",
                "payload": "http://127.0.0.1:8000/bulletins/2"
            },
            {
                "etape": "Étape 2 : LE CLIMAX DU PASSAGE — Basculement .env en direct (17:15)",
                "action": "Basculer sur VS Code (fichier <code>laravel-security-lab/.env</code> ligne 5). Remplacer <code>SECURITY_HARDENED=false</code> par <b><code>SECURITY_HARDENED=true</code></b> et enregistrer avec <b>Ctrl + S</b>.",
                "effet": "Hot-reload instantané de l'architecture de sécurité sans redémarrage de serveur.",
                "payload": "SECURITY_HARDENED=true"
            },
            {
                "etape": "Étape 3 : La preuve des 5 blocages avec un simple F5 (17:45)",
                "action": "Revenir sur le navigateur et faire <b>F5</b> sur les différentes pages devant le professeur :",
                "effet": (
                    "• <b>Sur /bulletins/2 :</b> 403 | THIS ACTION IS UNAUTHORIZED (GradePolicy)<br/>"
                    "• <b>Sur /campus :</b> Balise inerte &lt;img...&gt;, HttpOnly coché, CSP actif<br/>"
                    "• <b>Sur :8001 :</b> Clic sur le bouton de bourse renvoie 419 | PAGE EXPIRED (CSRF)<br/>"
                    "• <b>Sur /annuaire :</b> 0 résultat grâce aux requêtes préparées PDO<br/>"
                    "• <b>Sur /connexion :</b> 5 erreurs bloquent avec 429 | TOO MANY REQUESTS"
                ),
                "payload": "Touche F5 sur chaque onglet"
            }
        ],
        "qr": [
            (
                "Q13 : Quelle est la différence fondamentale entre le Hachage (Hash::make) et le Chiffrement (Crypt::encryptString) dans Laravel ?",
                "La différence réside dans la <b>réversibilité</b> de l'opération :<br/>"
                "- Le <b>Hachage (<code>Hash::make</code> avec l'algorithme <code>bcrypt</code> ou <code>argon2id</code>)</b> est <b>strictement irréversible (à sens unique)</b>. Il est mathématiquement impossible de retrouver le mot de passe initial à partir de son condensat. On vérifie une saisie uniquement par comparaison avec <code>Hash::check($saisie, $hash)</code>. C'est obligatoire pour tous les mots de passe.<br/>"
                "- Le <b>Chiffrement (<code>Crypt::encryptString</code> avec AES-256-CBC et la clé secrète <code>APP_KEY</code>)</b> est <b>réversible</b> grâce à <code>Crypt::decryptString()</code>. On l'utilise exclusivement pour des données métier sensibles que l'application a impérativement besoin de relire en clair (ex. un numéro de pièce ou une clé d'API tierce stockée en base)."
            ),
            (
                "Q14 : Quelle est la distinction exacte entre l'Authentification (Authentication) et l'Autorisation (Authorization / Policies) ?",
                "- <b>L'Authentification (Middleware <code>auth</code>)</b> répond à la question : <i>« Qui êtes-vous ? »</i>. Elle vérifie l'identité de l'utilisateur par ses identifiants (login/mot de passe). En cas d'échec, elle renvoie le code <code>401 Unauthorized</code> ou redirige vers le formulaire de connexion.<br/>"
                "- <b>L'Autorisation (Classes <code>Policies</code> et <code>Gates</code>)</b> répond à la question : <i>« Cet utilisateur a-t-il le droit d'effectuer cette action précise sur cette ressource précise ? »</i>.<br/>"
                "Dans notre démonstration, Sore Ramatou est parfaitement <b>authentifiée</b>, mais la classe <code>GradePolicy</code> vérifie que <code>$user->id === $grade->student->user_id</code>. Si ce n'est pas son bulletin, elle lui refuse l'accès avec le code <b><code>403 Forbidden</code></b>, neutralisant ainsi la faille IDOR."
            ),
            (
                "Q15 : Quelles sont les conséquences critiques de laisser APP_DEBUG=true dans le fichier .env sur un serveur en production ?",
                "Laisser <code>APP_DEBUG=true</code> en production est une faute grave de sécurité. À la moindre exception PHP ou erreur SQL, "
                "le gestionnaire d'erreurs Ignition affiche publiquement :<br/>"
                "1. Les chemins physiques complets des dossiers sur le disque dur du serveur.<br/>"
                "2. Les fragments de code source PHP entourant l'erreur.<br/>"
                "3. Les requêtes SQL brutes avec la structure exacte des tables de la base MariaDB.<br/>"
                "4. Et dans certains cas, la liste complète des variables d'environnement, incluant <code>DB_PASSWORD</code> et <code>APP_KEY</code> !<br/>"
                "En production, il faut impérativement configurer <b><code>APP_DEBUG=false</code></b> et <b><code>APP_ENV=production</code></b>, "
                "ce qui redirige les erreurs détaillées dans les fichiers de log internes (<code>storage/logs/laravel.log</code>) et affiche une page 500 générique aux utilisateurs."
            )
        ],
        "memo": [
            "Gardez le fichier <code>laravel-security-lab/.env</code> ouvert en arrière-plan dans VS Code sur la ligne 5 (<code>SECURITY_HARDENED=false</code>).",
            "Au moment du basculement, annoncez bien à la classe que vous n'avez pas besoin de redémarrer le serveur web.",
            "Après avoir sauvegardé le fichier .env (Ctrl + S), un simple F5 sur le navigateur suffit à prouver l'activation de tous les boucliers !"
        ]
    }
]

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(HexColor("#64748B"))
        
        # En-tête discret (pages 2+)
        if self._pageNumber > 1:
            self.setStrokeColor(HexColor("#E2E8F0"))
            self.setLineWidth(0.5)
            self.line(14 * mm, 287 * mm, 196 * mm, 287 * mm)
            self.drawString(14 * mm, 289 * mm, "Groupe 5 • Thème n° 12 : Sécurité Laravel — Fiche Individuelle")
            self.drawRightString(196 * mm, 289 * mm, "UT LOKO • Licence 3 Informatique")

        # Pied de page
        self.setStrokeColor(HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(14 * mm, 12 * mm, 196 * mm, 12 * mm)
        self.drawString(14 * mm, 8.5 * mm, "Université LOKO • Département ITER • Année 2025–2026 • Prof. M. CAMARA")
        page_str = f"Page {self._pageNumber} sur {total_pages}"
        self.drawRightString(196 * mm, 8.5 * mm, page_str)
        self.restoreState()

def build_pdf_fiche(fiche):
    pdf_filename = OUTPUT_DIR / f"{fiche['filename']}.pdf"
    doc = SimpleDocTemplate(
        str(pdf_filename),
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=14 * mm,
        bottomMargin=16 * mm
    )

    styles = getSampleStyleSheet()

    # Styles personnalisés
    style_normal = ParagraphStyle(
        'FicheNormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=C_SLATE
    )

    style_header_title = ParagraphStyle(
        'HeaderTitle',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=fiche['theme_color']
    )

    style_header_sub = ParagraphStyle(
        'HeaderSub',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=C_MUTED
    )

    style_header_right = ParagraphStyle(
        'HeaderRight',
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        alignment=2,
        textColor=C_NAVY
    )

    style_name = ParagraphStyle(
        'SpeakerName',
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=15,
        textColor=C_NAVY
    )

    style_role = ParagraphStyle(
        'SpeakerRole',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=fiche['theme_color']
    )

    style_detail = ParagraphStyle(
        'SpeakerDetail',
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=C_SLATE
    )

    style_badge_time = ParagraphStyle(
        'BadgeTime',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=10.5,
        alignment=2,
        textColor=fiche['theme_color']
    )

    style_sec_title = ParagraphStyle(
        'SecTitle',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12,
        textColor=C_NAVY,
        spaceBefore=8,
        spaceAfter=4
    )

    style_speech_title = ParagraphStyle(
        'SpeechTitle',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=C_NAVY
    )

    style_speech_body = ParagraphStyle(
        'SpeechBody',
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=C_SLATE
    )

    style_demo_title = ParagraphStyle(
        'DemoTitle',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=fiche['theme_color']
    )

    style_demo_action = ParagraphStyle(
        'DemoAction',
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=C_NAVY
    )

    style_demo_payload = ParagraphStyle(
        'DemoPayload',
        fontName='Courier-Bold',
        fontSize=8,
        leading=10,
        textColor=C_CODE_TXT
    )

    style_demo_effect = ParagraphStyle(
        'DemoEffect',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=HexColor("#065F46")
    )

    style_qr_q = ParagraphStyle(
        'QRQuestion',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=HexColor("#92400E")
    )

    style_qr_a = ParagraphStyle(
        'QRAnswer',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=HexColor("#451A03")
    )

    style_memo = ParagraphStyle(
        'MemoText',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10.5,
        textColor=C_SLATE
    )

    story = []

    # 1. En-tête officiel
    header_data = [
        [
            Paragraph("<b>FICHE DE SOUTENANCE ORALE & DÉMONSTRATION</b>", style_header_title),
            Paragraph("<b>Groupe 5 • Licence 3 Informatique</b><br/>Année 2025–2026 • Prof. M. CAMARA", style_header_right)
        ],
        [
            Paragraph("Université LOKO • Thème n° 12 : Sécurité dans une application Laravel (XAMPP / MariaDB)", style_header_sub),
            Paragraph("", style_header_right)
        ]
    ]
    t_header = Table(header_data, colWidths=[120 * mm, 62 * mm])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('LINEBELOW', (0,1), (-1,1), 1.5, fiche['theme_color']),
    ]))
    story.append(t_header)
    story.append(Spacer(1, 4 * mm))

    # 2. Carte d'identité de l'intervenant
    id_data = [
        [
            Paragraph(f"<b>{fiche['nom_complet']}</b>", style_name),
            Paragraph(f"⏱️ <b>{fiche['timing']}</b>", style_badge_time)
        ],
        [
            Paragraph(f"{fiche['role_titre']}", style_role),
            Paragraph(f"<b>Portail :</b> <code>127.0.0.1:8000</code>", style_badge_time)
        ],
        [
            Paragraph(f"<b>Diapositives :</b> {fiche['slides']}", style_detail),
            Paragraph("", style_detail)
        ]
    ]
    t_id = Table(id_data, colWidths=[125 * mm, 57 * mm])
    t_id.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('LINEBEFORE', (0,0), (0,-1), 3.5, fiche['theme_color']),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_id)
    story.append(Spacer(1, 3 * mm))

    # 3. Accès & Identifiants
    tech_data = [
        [
            Paragraph(f"<b>🎯 Cible navigateur :</b> <code>{fiche['url_cible']}</code><br/>"
                      f"<b>🔑 Identifiants / Accès :</b> <code>{fiche['identifiants']}</code>", style_detail)
        ]
    ]
    t_tech = Table(tech_data, colWidths=[182 * mm])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), C_TECH_BG),
        ('BOX', (0,0), (-1,-1), 1, C_TECH_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 3 * mm))

    # 4. SECTION 1 : DISCOURS ORAL MOT-À-MOT
    story.append(Paragraph("🗣️ <b>1. Discours Oral Mot-à-Mot (À déclamer au jury)</b>", style_sec_title))
    for titre, texte in fiche['discours']:
        speech_box = [
            [Paragraph(f"<b>{titre}</b>", style_speech_title)],
            [Paragraph(texte, style_speech_body)]
        ]
        t_sp = Table(speech_box, colWidths=[182 * mm])
        t_sp.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), HexColor("#FFFFFF")),
            ('BOX', (0,0), (-1,-1), 0.75, HexColor("#E2E8F0")),
            ('LINEBEFORE', (0,0), (0,-1), 2.5, HexColor("#64748B")),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(t_sp)
        story.append(Spacer(1, 2 * mm))

    story.append(Spacer(1, 2 * mm))

    # 5. SECTION 2 : DÉMONSTRATION EN DIRECT
    story.append(Paragraph("💻 <b>2. Chorégraphie de Démonstration en Direct (Pas-à-Pas)</b>", style_sec_title))
    for dem in fiche['demo']:
        demo_box = [
            [Paragraph(f"<b>{dem['etape']}</b>", style_demo_title)],
            [Paragraph(f"<b>Action :</b> {dem['action']}", style_demo_action)],
            [Paragraph(f"<b>Payload / URL :</b> <code>{html.escape(dem['payload'])}</code>", style_demo_payload)],
            [Paragraph(dem['effet'], style_demo_effect)]
        ]
        t_dm = Table(demo_box, colWidths=[182 * mm])
        t_dm.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), HexColor("#F1F5F9")),
            ('BACKGROUND', (0,1), (-1,1), HexColor("#FFFFFF")),
            ('BACKGROUND', (0,2), (-1,2), C_CODE_BG),
            ('BACKGROUND', (0,3), (-1,3), C_SUCCESS_BG),
            ('BOX', (0,0), (-1,-1), 1, C_BORDER),
            ('LINELEFT', (0,0), (0,-1), 3, fiche['theme_color']),
            ('TOPPADDING', (0,0), (-1,-1), 2.5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(KeepTogether(t_dm))
        story.append(Spacer(1, 2 * mm))

    story.append(Spacer(1, 2 * mm))

    # 6. SECTION 3 : QUESTIONS & RÉPONSES DU JURY
    story.append(Paragraph("🧠 <b>3. Vos 3 Questions Clés du Jury (M. CAMARA) & Réponses Idéales</b>", style_sec_title))
    for q_text, a_text in fiche['qr']:
        qr_box = [
            [Paragraph(f"❓ <b>{q_text}</b>", style_qr_q)],
            [Paragraph(f"💡 <b>Réponse :</b> {a_text}", style_qr_a)]
        ]
        t_qr = Table(qr_box, colWidths=[182 * mm])
        t_qr.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), C_ALERT_BG),
            ('BOX', (0,0), (-1,-1), 1, C_ALERT_BORDER),
            ('LINEBEFORE', (0,0), (0,-1), 3, C_GOLD),
            ('TOPPADDING', (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(KeepTogether(t_qr))
        story.append(Spacer(1, 2.5 * mm))

    story.append(Spacer(1, 2 * mm))

    # 7. SECTION 4 : MÉMO DE SECOURS JOUR J
    story.append(Paragraph("🛡️ <b>4. Mémo de Secours Jour J & Relais d'Équipe</b>", style_sec_title))
    memo_bullets = "<br/>".join([f"• {m}" for m in fiche['memo']])
    memo_box = [
        [Paragraph(memo_bullets, style_memo)]
    ]
    t_memo = Table(memo_box, colWidths=[182 * mm])
    t_memo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 1, C_BORDER),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(KeepTogether(t_memo))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"    -> PDF généré : {pdf_filename.name} ({os.path.getsize(pdf_filename):,} octets)")

def main():
    print("=" * 70)
    print("GÉNÉRATION DES 5 FICHES INDIVIDUELLES ORAL & DÉMO VIA REPORTLAB")
    print("=" * 70)

    for fiche in FICHES:
        nom = fiche["nom_complet"]
        print(f"\n[+] Génération pour {nom}...")
        build_pdf_fiche(fiche)

    print("\n" + "=" * 70)
    print("Succès : Les 5 fiches individuelles sont prêtes dans :")
    print(f"  {OUTPUT_DIR}")
    print("=" * 70)

if __name__ == "__main__":
    main()
