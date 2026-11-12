# Guide Pas-à-Pas — Démonstration Réelle de Piratage & Basculement `.env` (Groupe 5)

Ce guide explique exactement **comment lancer le Portail Académique UT LOKO**, **comment exploiter les 5 failles en direct avec les vrais outils du navigateur (`F12`, barre d'adresse, faux site externe)** comme dans une situation réelle, puis **comment activer toutes les défenses Laravel en direct depuis `.env` dans VS Code**.

---

## 1. Préparation avant le passage (1 clic)

1. Double-cliquez sur [scripts/lancer-demo.bat](file:///c:/Users/prince/Music/Laravel_Security_Architecture/scripts/lancer-demo.bat).
   Il démarre automatiquement :
   - **Apache XAMPP (`:80`)** et **MariaDB XAMPP (`:3306`)**,
   - le **site piège externe CSRF** sur `http://127.0.0.1:8001`,
   - le **Portail Académique UT LOKO** sur `http://127.0.0.1:8000` (sans aucun bouton spoiler).
2. Gardez **4 fenêtres/onglets prêts** :
   - **Onglet 1** : `http://127.0.0.1:8000` (Portail UT LOKO)
   - **Onglet 2** : `http://127.0.0.1:8001` (Faux site *Bourses d'Excellence CI 2026*)
   - **Onglet 3** : `http://localhost/phpmyadmin` → base **`loko_security_lab`**
   - **VS Code** ouvert sur le fichier `laravel-security-lab/.env`

### Comptes de démonstration enregistrés dans MariaDB
| Compte | E-mail | Mot de passe | Rôle initial |
| :--- | :--- | :--- | :--- |
| Sore Ramatou | `ramatou.sore@loko.ci` | `Loko@2026!` | `student` |
| Siby Mody | `mody.siby@loko.ci` | `Loko@2026!` | `student` |
| Boin Naomi | `naomi.boin@loko.ci` | `Loko@2026!` | `student` |
| Traoré Charifat Leyla | `leyla.traore@loko.ci` | `Loko@2026!` | `student` |
| Djan Kouassi Noël | `noel.djan@loko.ci` | `Loko@2026!` | `student` |
| **Prof. M. Camara** | `admin@loko.ci` | `Camara@Loko2026` | `admin` |

> **Si vous voulez tout remettre à zéro avant de recommencer** : double-cliquez sur [scripts/reinitialiser-demo.bat](file:///c:/Users/prince/Music/Laravel_Security_Architecture/scripts/reinitialiser-demo.bat). Il remet `SECURITY_HARDENED=false` et réinitialise MariaDB proprement.

---

## 2. Phase 1 — Piratage Réel en Classe (`SECURITY_HARDENED=false`)

Vérifiez que dans `laravel-security-lab/.env`, vous avez bien **`SECURITY_HARDENED=false`**.

### Étape 1 — Sore Ramatou : Injection SQL (Annuaire, Erreur Debug & Connexion)
1. **Fuite de la requête SQL (`APP_DEBUG=true`)** :
   - Allez sur **`Annuaire`** (`http://127.0.0.1:8000/annuaire`).
   - Dans le champ **« Matricule ou nom »**, tapez une simple apostrophe : `'` et cliquez **Rechercher**.
   - **Constat en direct** : MariaDB rejette la requête cassée et Laravel affiche toute la trace PHP + la requête SQL complète (`SELECT id, matricule, full_name...`).
2. **Extraction des comptes & mots de passe (`UNION SELECT`)** :
   - Revenez en arrière sur `/annuaire` et saisissez ce payload dans le champ de recherche :
     ```sql
     ' AND 1=0 UNION SELECT id, email, password, legacy_md5, role FROM users -- '
     ```
     *(Attention : laissez bien l'espace après `-- ` pour MariaDB).*
   - **Constat en direct** : la table affiche tous les e-mails, les empreintes **`bcrypt` (`$2y$12$...`) uniques**, l'ancien condensat **`MD5` (`9c9b18b4b347333608b26b45b0904a4f`) identique** pour tous les étudiants, et les rôles (`admin`, `student`).
   - *(Bonus DevTools `F12`)* : Montrez aussi `/api/annuaire?sort=moyenne` dans `F12 → Network` (endpoint JSON vulnérable sur le tri `?sort=`, inspiré d'`appelsiini`).
3. **Contournement du formulaire de Connexion (SQLi Auth Bypass)** :
   - Allez sur **`Se connecter`** (`/connexion`).
   - Dans **Adresse e-mail**, tapez :
     ```text
     admin@loko.ci' -- 
     ```
     *(avec l'espace final après `-- `)* et tapez n'importe quel mot de passe bidon (`123456`).
   - **Constat en direct** : vous êtes authentifié instantanément comme **`Prof. M. Camara • Administrateur`** et le menu jaune **`Administration`** apparaît ! Cliquez sur **Déconnexion** avant l'étape 2.

---

### Étape 2 — Siby Mody : Mass Assignment en éditant le HTML via `F12`
1. Sur `/connexion`, connectez-vous normalement en tant qu'étudiant : **`mody.siby@loko.ci`** / **`Loko@2026!`**.
2. Cliquez sur votre nom en haut à droite (**`Siby Mody • Étudiant`**) pour ouvrir **`Mon Profil`** (`/profil`). Montrez à la classe qu'il n'y a que `Nom complet` et `Adresse e-mail`, et que `Rôle actif` affiche **`Étudiant (student)`**.
3. Appuyez sur **`F12`** (ou Clic droit sur « Nom complet » → **Inspecter**).
4. Dans l'onglet **Éléments (Elements)**, repérez la balise `<form method="POST" action="http://127.0.0.1:8000/profil">` (et le commentaire HTML `<!-- Table users : ... -->`).
5. Faites **Clic droit sur la balise `<form>` → Edit as HTML** (ou sur un `<input>`), et ajoutez juste avant `<button type="submit">` :
   ```html
   <input type="hidden" name="role" value="admin">
   ```
6. Validez la modification DOM (`Ctrl+Entrée` ou cliquez hors de la zone HTML), fermez `F12`, puis cliquez sur **« Enregistrer mes informations »**.
7. **Constat en direct** : la page se recharge, votre badge passe à **`Administrateur (admin)`**, le menu **`Administration`** se débloque dans la barre de navigation et la table `users` dans **`phpMyAdmin`** indique `role = 'admin'` !
8. Cliquez ensuite sur **Déconnexion** (pour tester ensuite le mode durci proprement, ou remettez `role = 'student'` plus tard avec `reinitialiser-demo.bat` — pour la phase 2, vous pourrez aussi tester sur `ramatou.sore@loko.ci` ou réinitialiser).

---

### Étape 3 — Boin Naomi : XSS Stocké + Vol de Cookie (`F12 → Cookies` & `Network`)
1. Connectez-vous avec **`naomi.boin@loko.ci`** / **`Loko@2026!`** puis allez sur **`Mur du Campus`** (`/campus`).
2. Avant d'attaquer, ouvrez **`F12 → Application → Cookies → http://127.0.0.1:8000`** : montrez à la classe que la colonne **`HttpOnly`** de `laravel_session` est **vide** ! Puis dans **`F12 → Network`**, montrez qu'aucun en-tête `Content-Security-Policy` n'est envoyé par le serveur.
3. Dans le formulaire **« Publier une annonce »** sur `/campus`, mettez n'importe quel titre (ex. `Résultats concours`) et collez ce payload dans **Contenu** :
   ```html
   <img src="x" onerror="alert('XSS UT LOKO ! Cookie volé : ' + document.cookie)">
   ```
4. Cliquez sur **« Publier sur le mur »**.
5. **Constat en direct** : le navigateur exécute immédiatement le JavaScript malveillant, ouvre une **vraie fenêtre d'alerte** contenant la valeur de `document.cookie` (`laravel_session=...`) chez tous les visiteurs de `/campus` !

---

### Étape 4 — Traoré Charifat Leyla : Attaque CSRF réelle depuis le site piège `:8001`
1. Connectez-vous sur `http://127.0.0.1:8000` avec le compte du professeur **`admin@loko.ci`** / **`Camara@Loko2026`**.
2. Cliquez sur **`Administration`** (`/admin/notes`) et montrez à la classe que la note de **`Traoré Charifat Leyla`** (Bulletin `#4`) est à **`16.00 / 20`**.
3. Basculez sur l'**Onglet 2** du navigateur : **`http://127.0.0.1:8001`** (« Programme National Bourses d'Excellence & Équipement L3 »).
4. Appuyez sur **`Ctrl + U`** (ou **`F12 → Éléments`**) pour montrer au prof le formulaire caché :
   `<form method="POST" action="http://127.0.0.1:8000/notes/4/modifier">` contenant `score=20.00` et **sans `_token`**.
5. Cliquez sur le bouton bleu **« Vérifier mon éligibilité à la Bourse »**.
6. **Constat en direct** : le navigateur envoie automatiquement le cookie `laravel_session` au portail `:8000` et la note de Traoré Charifat Leyla dans MariaDB passe réellement à **`20.00 / 20`** sous les yeux du professeur !

---

### Étape 5 — Djan Kouassi Noël : IDOR par l'URL + Brute-Force `F12` + Analyse `.env`
1. Cliquez sur **Déconnexion**, puis connectez-vous en étudiant simple **`ramatou.sore@loko.ci`** / **`Loko@2026!`**.
2. Cliquez sur **`Mes Notes`** dans la barre de navigation → l'adresse affiche `http://127.0.0.1:8000/bulletins/1` (`Sore Ramatou`).
3. **Exploit IDOR réel** : cliquez dans la **barre d'adresse du navigateur**, remplacez simplement le **`1`** final par **`2`** (`http://127.0.0.1:8000/bulletins/2`) et appuyez sur `Entrée`.
   - **Constat en direct** : vous accédez sans aucun blocage au relevé privé de **`Siby Mody`** et à sa remarque *« Confidentiel : relevé académique personnel réservé exclusivement à Siby Mody. »* !
4. **Constatation MD5 vs Bcrypt & Brute-Force** :
   - Rappelez la fuite du `UNION SELECT` (les deux étudiants partageant `Loko@2026!` avaient le même `legacy_md5 = 9c9b18b4...` alors que leurs `password` bcrypt `$2y$12$...` sont tous distincts).
   - Ouvrez `/connexion` et montrez qu'on peut saisir 6 mauvais mots de passe d'affilée sans aucun ralentissement ni code `429`.

---

## 3. Comment faire le basculement `.env` en direct (`SECURITY_HARDENED=true`)

C'est **Djan Kouassi Noël** qui clôture la prise d'assaut et active les boucliers Laravel **devant toute la classe sans redémarrer aucun serveur** :

1. Passez sur **VS Code** avec le fichier `laravel-security-lab/.env` ouvert.
2. Montrez au jury la ligne `DB_USERNAME=root`, `APP_DEBUG=true` et surtout la ligne 5 :
   ```env
   SECURITY_HARDENED=false
   ```
3. Remplacez simplement `false` par **`true`** :
   ```env
   SECURITY_HARDENED=true
   ```
4. Enregistrez avec **`Ctrl + S`**.
5. **C'est tout ! Ne redémarrez PAS le terminal.** Grâce à `App\Support\SecurityConfig`, Laravel relit `.env` en direct dès la prochaine requête (`F5`) et active simultanément :
   - Requêtes préparées PDO / Eloquent + liste blanche sur `?sort=`
   - `APP_DEBUG=false` (plus aucune trace SQL/code visible)
   - Validation `UpdateProfileRequest` + `#[Fillable]` (bloque `role`)
   - Échappement Blade `{{ }}` + cookie `HttpOnly` + en-têtes `Content-Security-Policy: script-src 'self'` et `X-Frame-Options: DENY`
   - Middleware `ValidateCsrfToken` (`HTTP 419 Page Expired`)
   - `GradePolicy` (`HTTP 403 Forbidden`) + `RateLimiter` (`HTTP 429 Too Many Requests`)

---

## 4. Phase 2 — Vérification des 5 Blocages après `F5`

Rejouez rapidement chaque geste devant le prof pour prouver la protection native Laravel :

1. **IDOR (Djan Kouassi Noël)** : Sur `http://127.0.0.1:8000/bulletins/2` (connecté en `ramatou.sore@loko.ci`), appuyez simplement sur **`F5`** → **`403 | THIS ACTION IS UNAUTHORIZED`**.
2. **XSS & Cookies (Boin Naomi)** : Allez sur `/campus` et appuyez sur **`F5`** → plus aucune alerte JS, le script s'affiche en texte brut inoffensif. Ouvrez `F12 → Application → Cookies` (**`HttpOnly ✓` coché**) et `F12 → Network → Headers` (**`Content-Security-Policy`** présent).
3. **Mass Assignment (Siby Mody)** : Connecté en étudiant (`naomi.boin@loko.ci` ou après réinitialisation sur `mody.siby@loko.ci`), injectez `<input type="hidden" name="role" value="admin">` via `F12`, validez → le badge reste strictement **`Étudiant`**.
4. **SQLi & Brute-Force (Sore & Noël)** :
   - Sur `/annuaire`, `' UNION SELECT ...` renvoie **0 résultat**, et `'` ne provoque aucune erreur SQL.
   - Sur `/connexion`, `admin@loko.ci' -- ` renvoie **Identifiant ou mot de passe incorrect (`HTTP 401`)**.
   - Validez 5 mauvais mots de passe rapides, puis au **6e essai** → **blocage `HTTP 429 Too Many Requests`** à l'écran et dans `F12 → Network`.
5. **CSRF (Traoré Charifat Leyla)** : Connecté en Admin (`admin@loko.ci`), allez sur `http://127.0.0.1:8001` et cliquez sur le bouton piège → Laravel bloque net la requête forgée avec **`419 | PAGE EXPIRED`** !

> **Après la séance / avant un nouveau test** : lancez [scripts/reinitialiser-demo.bat](file:///c:/Users/prince/Music/Laravel_Security_Architecture/scripts/reinitialiser-demo.bat) pour remettre `SECURITY_HARDENED=false` et restaurer les notes et annonces initiales dans MariaDB.
