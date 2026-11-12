# 🎤 Guide Oral Minuté (20 min) & Banque de Questions-Réponses (10 min)
## Thème n° 12 : La sécurité dans une application Laravel
**Établissement** : Université Tertiaire & Technologique LOKO (UT LOKO) — Département ITER  
**Module** : Base de données (XAMPP / MariaDB) & Framework Laravel — Licence 3 Informatique  
**Année académique** : 2025–2026 | **Professeur** : M. CAMARA  
**Groupe 5** :
1. **SORE RAMATOU** (00:00 – 04:00) — Introduction générale & Pilier 1 : Injection SQL (SQLi), PDO & Eloquent ORM
2. **SIBY MODY** (04:00 – 08:00) — Pilier 2 : Mass Assignment, Escalade de privilèges en BDD & Validation `FormRequest`
3. **BOIN NAOMI** (08:00 – 12:00) — Pilier 3 : Cross-Site Scripting (XSS Stocké), Moteur Blade & En-têtes HTTP (`CSP`)
4. **TRAORÉ CHARIFAT LEYLA** (12:00 – 16:00) — Pilier 4 : Cross-Site Request Forgery (CSRF), Sessions & Jeton `@csrf`
5. **DJAN KOUASSI NOËL** (16:00 – 20:00) — Pilier 5 : Authentification, Hachage `bcrypt`, Contrôle d'accès (`IDOR` / `Policies`), `Rate Limiting`, Sécurité `.env`/XAMPP & Conclusion

---

## 🛠️ Checklist Technique « Jour J » (5 minutes avant de passer)

1. **Démarrer l'environnement en 1 clic** : Double-cliquer sur `scripts\lancer-demo.bat` (ou lancer `scripts\reinitialiser-demo.bat` avant un second passage).
   - Vérifie et démarre **Apache (`:80`)** et **MariaDB (`:3306`)** sous XAMPP, puis crée/seede la base `loko_security_lab`.
   - Démarre le serveur externe tiers (`http://127.0.0.1:8001`, faux site Bourses d'Excellence) et le **Portail Académique UT LOKO** (`http://127.0.0.1:8000`, façade réaliste sans bouton spoiler).
2. **Préparer les 4 fenêtres / onglets (plein écran `F11`)** :
   - **Onglet 1** : Le diaporama (`livrables/web-interactif/slides.html` ou PowerPoint `Expose_Securite_Laravel_Groupe5.pptx`).
   - **Onglet 2** : Le **Portail Académique UT LOKO** (`http://127.0.0.1:8000`) avec `SECURITY_HARDENED=false` dans `.env`.
   - **Onglet 3** : Le site piège externe (`http://127.0.0.1:8001`) pour l'attaque CSRF de Leyla.
   - **Onglet 4 + VS Code** : `http://localhost/phpmyadmin` (`loko_security_lab` → tables `users`, `students`, `grades`, `campus_posts`, `security_logs`) et **VS Code** ouvert sur `laravel-security-lab/.env` (ligne 5 : `SECURITY_HARDENED=false`).
3. **Lancer le chronomètre intégré** : Dans `slides.html`, cliquer sur **« ▶ Démarrer 20:00 »** en bas à droite dès que M. CAMARA donne le top départ.

---

## ⏱️ Script Oral Mot-à-Mot & Chorégraphie de Démonstration (20 Minutes)

---

### 👤 PARTIE 1 — SORE RAMATOU (00:00 → 04:00)
**Sujets** : Accroche, Architecture de sécurité multicouche de Laravel & **Pilier 1 : Injection SQL (SQLi)**  
**Slides** : Diapositives 1 à 7

#### 🗣️ Discours (00:00 – 02:15)
> « Bonjour Monsieur CAMARA, bonjour chers camarades. Nous sommes le **Groupe 5**, composé de **Sore Ramatou, Siby Mody, Boin Naomi, Traoré Charifat Leyla et Djan Kouassi Noël**. Aujourd'hui, nous avons l'honneur de vous présenter le **Thème n° 12 : La sécurité dans une application Laravel**, reliée à une base de données **MySQL / MariaDB sous XAMPP**.
>
> Pourquoi ce thème est-il central ? Parce que dans les exposés précédents, nous avons découvert l'architecture MVC, le routage, les contrôleurs, Blade et les migrations. Mais **une application fonctionnelle qui n'est pas sécurisée est une porte ouverte sur sa base de données**. Selon le référentiel mondial **OWASP Top 10**, plus de 70 % des compromissions web ciblent directement la couche applicative et ses requêtes SQL.
>
> La philosophie de Laravel tient en un principe : **"Secure by Default"** (sécurisé par défaut). Cependant, comme nous allons le prouver en direct, un développeur qui contourne les mécanismes natifs du framework expose immédiatement son application à des attaquants réels.
>
> Pour le prouver devant vous sans simulation artificielle, nous avons construit le **Portail Académique UT LOKO** (`127.0.0.1:8000`) connecté à **MariaDB (XAMPP)** : aucune option de triche à l'écran ! Nous allons l'attaquer **exactement comme de vrais pirates** avec les outils du navigateur (`F12`, barre d'adresse, payloads SQL/XSS et un faux site externe sur `:8001`), puis **Djan Kouassi Noël** activera en direct les défenses natives de Laravel dans `.env` (`SECURITY_HARDENED=true`).
>
> Je commence immédiatement avec le **Pilier n° 1 : l'Injection SQL (SQLi)**, la menace la plus directe contre notre base de données. »

#### 💻 Démonstration en direct — Pilier 1 : Injection SQL (`SECURITY_HARDENED=false`) (02:15 – 04:00)
1. **Ouvrir l'onglet « Annuaire »** (`http://127.0.0.1:8000/annuaire`) :
   - Tapez une simple apostrophe `'` dans le champ *« Matricule ou nom »* → **Effet WAHOU** : avec `APP_DEBUG=true`, Laravel affiche l'exception SQL et la requête complète exécutée contre MariaDB !
   - Revenez en arrière sur `/annuaire` et collez :
     `' AND 1=0 UNION SELECT id, email, password, legacy_md5, role FROM users -- `
     *(espace obligatoire après `-- `)* → **Effet WAHOU** : la table de l'annuaire exfiltre en direct les e-mails, les empreintes **`bcrypt` (`$2y$12$...`)**, l'ancien **`MD5`** (`9c9b18b4...`) et les rôles (`admin`, `student`) !
2. **Contournement de connexion (Auth Bypass)** :
   - Cliquez sur **« Se connecter »** (`/connexion`), saisissez **`admin@loko.ci' -- `** avec un mot de passe quelconque (`123456`) → vous entrez directement dans la session **`Prof. M. Camara • Administrateur`** avec le menu **`Administration`** débloqué !
   - Cliquez sur **Déconnexion** et expliquez comment **Eloquent / PDO (`?`)** corrigera tout cela lors du durcissement `.env`.
3. **Transition** :
   > « Protéger la requête SQL de lecture est indispensable, mais que se passe-t-il lorsqu'un étudiant manipule directement le formulaire HTML dans son navigateur (`F12`) pour modifier son rôle en base de données ? Je passe la parole à **Siby Mody** pour le **Mass Assignment**. »

---

### 👤 PARTIE 2 — SIBY MODY (04:00 → 08:00)
**Sujets** : **Pilier 2 : Mass Assignment (Assignation de masse), Escalade de privilèges en BDD & Validation `FormRequest`**  
**Slides** : Diapositives 8 et 9

#### 🗣️ Discours (04:00 – 05:45)
> « Merci Ramatou. Bonjour Monsieur le Professeur, bonjour à tous. Je suis **Siby Mody**, et je vais vous présenter une vulnérabilité redoutable propre aux frameworks ORM modernes comme Eloquent : le **Mass Assignment** (ou assignation de masse) et son impact direct sur l'intégrité de notre base de données MariaDB.
>
> Pour accélérer le développement, Laravel permet d'enregistrer ou de mettre à jour une ligne en base en une seule instruction grâce à `$request->all()` ou `forceFill()`. C'est très pratique… mais extrêmement dangereux si le modèle n'est pas verrouillé !
>
> Pourquoi ? Dans notre table `users` sous XAMPP, nous avons les colonnes `name`, `email`, `password`, mais aussi une colonne sensible : **`role`** (`student` ou `admin`). Sur le formulaire HTML de profil, seuls le nom et l'email sont affichés. Mais je vais ouvrir l'inspecteur du navigateur (**`F12`**) comme un attaquant et **injecter moi-même un champ caché `role=admin`** avant de valider ! »

#### 💻 Démonstration en direct — Pilier 2 : Mass Assignment via `F12` (05:45 – 08:00)
1. **Connexion étudiant** sur `/connexion` avec **`mody.siby@loko.ci`** / **`Loko@2026!`**, puis clic sur **`Siby Mody • Étudiant`** → **Mon Profil** (`/profil`). Montrez que seul `name` et `email` sont visibles et que le badge affiche **`Étudiant (student)`**.
2. **Piratage via DevTools (`F12`)** :
   - Appuyez sur **`F12` → Éléments (Elements)**, repérez `<form method="POST" action="http://127.0.0.1:8000/profil">`, faites **Clic droit → Edit as HTML**, et ajoutez avant `<button>` :
     `<input type="hidden" name="role" value="admin">`
   - Fermez `F12` et cliquez sur **« Enregistrer mes informations »**.
   - **Effet WAHOU** : la page se recharge, Siby Mody devient **`Administrateur (admin)`**, l'onglet **`Administration`** apparaît dans le menu et **`phpMyAdmin`** confirme `role = 'admin'` dans `users` !
3. Expliquez la **double barrière Laravel (`UpdateProfileRequest::validated()` + `#[Fillable]` / `$fillable`)** qui bloquera cette manipulation dès la phase de durcissement `.env`, puis cliquez sur **Déconnexion**.
4. **Transition** :
   > « Nous venons de voir comment une requête HTTP falsifiée peut corrompre un rôle en base de données. Mais que se passe-t-il si un étudiant publie du code JavaScript piégé sur le mur collaboratif de la fac ? **Boin Naomi** vous présente le **Pilier n° 3 : la faille XSS**. »

---

### 👤 PARTIE 3 — BOIN NAOMI (08:00 → 12:00)
**Sujets** : **Pilier 3 : Cross-Site Scripting (XSS Stocké), Moteur Blade (`{{ }}` vs `{!! !!}`) & En-têtes HTTP (`CSP` + `HttpOnly`)**  
**Slides** : Diapositives 10 et 11

#### 🗣️ Discours (08:00 – 09:45)
> « Merci Mody. Bonjour à tous. Je suis **Boin Naomi** et j'aborde le **Pilier n° 3 : le Cross-Site Scripting (XSS)** et la protection du moteur de templates **Blade**.
>
> Contrairement à l'injection SQL qui attaque le serveur de base de données, la faille **XSS Stockée (Stored XSS)** utilise la base de données MariaDB (notre table `campus_posts`) comme **vecteur de propagation**. L'attaquant publie une annonce contenant une balise JavaScript malveillante. Dès qu'un professeur ou un étudiant ouvre le **Mur du Campus**, son navigateur exécute ce script — et si le cookie de session n'est pas `HttpOnly`, nous pouvons voler sa session via `document.cookie` !
>
> Dans Laravel, tout se joue entre deux syntaxes dans les vues `.blade.php` : `{!! $post->content !!}` (brut, dangereux) contre `{{ $post->content }}` (échappé automatiquement par `htmlspecialchars`). Passons tout de suite à la démonstration réelle sur `/campus`. »

#### 💻 Démonstration en direct — Pilier 3 : XSS Stocké & Cookies `F12` (09:45 – 12:00)
1. **Connexion étudiante** (`naomi.boin@loko.ci` / `Loko@2026!`) puis navigation sur **`Mur du Campus`** (`/campus`).
2. **Preuve dans DevTools (`F12`)** :
   - Ouvrez **`F12 → Application → Cookies → http://127.0.0.1:8000`** : montrez que la case **`HttpOnly`** de `laravel_session` est **décochée**, puis **`F12 → Network`** (pas d'en-tête `Content-Security-Policy`).
3. **Exploitation réelle** :
   - Publiez une annonce avec le contenu :
     `<img src="x" onerror="alert('XSS UT LOKO ! Cookie volé : ' + document.cookie)">`
   - **Effet WAHOU** : dès le rechargement de `/campus`, une vraie alerte JavaScript surgit à l'écran et affiche en clair `laravel_session=...` !
4. Expliquez les 3 barrières activées au durcissement `.env` : **`{{ }}` (`e()`)**, **cookie `HttpOnly = true`** et **`SecurityHeadersMiddleware`** (`Content-Security-Policy: script-src 'self'`, `X-Frame-Options: DENY`).
5. **Transition** :
   > « Même si aucun script malveillant ne s'exécute sur notre site, un attaquant peut forcer le navigateur d'un enseignant connecté à envoyer une requête à son insu depuis un autre site. **Traoré Charifat Leyla** vous explique le **Pilier n° 4 : la faille CSRF**. »

---

### 👤 PARTIE 4 — TRAORÉ CHARIFAT LEYLA (12:00 → 16:00)
**Sujets** : **Pilier 4 : Cross-Site Request Forgery (CSRF), Sécurité des Sessions & Jeton `@csrf`**  
**Slides** : Diapositives 12 et 13

#### 🗣️ Discours (12:00 – 13:45)
> « Merci Naomi. Bonjour Monsieur CAMARA, bonjour à tous. Je suis **Traoré Charifat Leyla**, et je vais vous présenter le **Pilier n° 4 : le Cross-Site Request Forgery (CSRF)**, ou falsification de requête inter-sites.
>
> Le scénario est très fréquent : un enseignant ou un administrateur est connecté sur le **Portail UT LOKO (`http://127.0.0.1:8000`)**. Son navigateur possède donc un cookie de session actif. Sans se déconnecter, il clique sur un lien externe piégé hébergé sur un autre domaine — ici notre second serveur indépendant **`http://127.0.0.1:8001`** déguisé en *Programme National Bourses d'Excellence*.
>
> Ce site externe contient un formulaire caché qui poste silencieusement une modification de note vers `:8000`. Pour empêcher cela, Laravel génère un **jeton cryptographique secret `@csrf` (`_token`)** vérifié par `ValidateCsrfToken` (et `DynamicCsrfMiddleware` dans notre démo) à chaque requête d'écriture. Vérifions-le entre nos deux sites en direct ! »

#### 💻 Démonstration en direct — Pilier 4 : CSRF réel depuis `:8001` (13:45 – 16:00)
1. **Session Admin sur `:8000`** : Connectez-vous avec **`admin@loko.ci`** / **`Camara@Loko2026`**, ouvrez **`Administration`** (`/admin/notes`) et montrez la note de **Traoré Charifat Leyla** (Bulletin `#4` = **`16.00 / 20`**).
2. **Bascule sur le Site Externe (`http://127.0.0.1:8001`)** :
   - Appuyez sur `Ctrl + U` (ou `F12`) pour montrer le `<form method="POST" action="http://127.0.0.1:8000/notes/4/modifier">` avec `score=20.00` et **sans `_token`**.
   - Cliquez sur **« Vérifier mon éligibilité à la Bourse »**.
   - **Effet WAHOU** : le navigateur joint automatiquement `laravel_session` et la note de Traoré Charifat Leyla passe réellement à **`20.00 / 20`** dans MariaDB !
3. Rappelez la règle d'or (**pas de mutation sur `GET` + `@csrf` sur tous les formulaires + cookie `SameSite=Lax`** → blocage **HTTP 419 Page Expired** dès la phase `.env`).
4. **Transition** :
   > « Il nous reste à protéger l'accès individuel aux bulletins, le hachage des mots de passe, le anti-Brute-Force et à activer en direct le bouclier global Laravel depuis `.env`. Je passe la parole à **Djan Kouassi Noël** pour le **5e pilier et le durcissement final**. »

---

### 👤 PARTIE 5 — DJAN KOUASSI NOËL (16:00 → 20:00)
**Sujets** : **Pilier 5 : Authentification, Hachage `bcrypt`, Contrôle d'accès (`IDOR` / `GradePolicy`), `RateLimiter`, Basculement à chaud `.env` (`SECURITY_HARDENED=true`) & Conclusion**  
**Slides** : Diapositives 14 à 19

#### 🗣️ Discours & Exploitation IDOR réelle (16:00 – 17:30)
> « Merci Leyla. Bonjour Monsieur le Professeur, bonjour chers camarades. Je suis **Djan Kouassi Noël**, et je clôture notre parcours avec le **Pilier n° 5 : Cryptographie en base, Contrôle d'accès (`IDOR`), Anti-Brute-Force et Durcissement `.env`**. »

1. **Exploitation IDOR réelle par l'URL** :
   - Déconnectez Admin, puis connectez-vous en étudiant simple : **`ramatou.sore@loko.ci`** / **`Loko@2026!`**.
   - Cliquez sur **`Mes Notes`** : l'URL affiche **`http://127.0.0.1:8000/bulletins/1`** (*Sore Ramatou*).
   - **Exploit devant la classe** : cliquez simplement dans la barre d'adresse et remplacez `/1` par **`/2`** (`http://127.0.0.1:8000/bulletins/2`) → **Effet WAHOU** : Sore Ramatou consulte librement le relevé confidentiel de **Siby Mody (`16.25 / 20`)** !
2. **Constat Crypto & Brute-Force** :
   - Rappelez la fuite SQLi de la Partie 1 : tous les étudiants partageant `Loko@2026!` ont le même `legacy_md5` (`9c9b18b4...`), alors que leurs vrais condensats `bcrypt` (`$2y$12$...`) ont chacun un sel aléatoire de 128 bits.
   - Sur `/connexion`, montrez que sans `RateLimiter`, on peut enchaîner 6 mauvais mots de passe sans aucun blocage.

#### 🛡️ Basculement à chaud `.env` & Preuve des 5 Blocages (17:30 – 19:15)
> « Regardez maintenant la magie architecturale de Laravel : nous n'allons même pas redémarrer le serveur PHP ! Je bascule simplement `SECURITY_HARDENED=false` vers `true` dans `.env`. »

1. Dans **VS Code (`laravel-security-lab/.env`)**, remplacez **`SECURITY_HARDENED=false`** par **`SECURITY_HARDENED=true`** et faites **`Ctrl + S`** (sans relancer le terminal).
2. Rejouez les gestes sur le navigateur avec un simple **`F5`** :
   - **IDOR (`/bulletins/2` comme Sore Ramatou)** + `F5` → **`403 | THIS ACTION IS UNAUTHORIZED`** (`GradePolicy`) !
   - **XSS (`/campus`)** + `F5` → plus aucune alerte, la balise s'affiche en texte brut (`{{ }}`), **`HttpOnly ✓`** coché dans `F12 → Cookies`, en-tête **`Content-Security-Policy`** présent dans `F12 → Network` !
   - **Mass Assignment (`/profil`)** → `<input name="role" value="admin">` via `F12` est silencieusement ignoré (`UpdateProfileRequest` + `#[Fillable]`).
   - **SQLi & Brute-Force (`/annuaire` & `/connexion`)** → `' UNION SELECT` retourne **0 résultat** (PDO `?`), et la 6e erreur de mot de passe renvoie **`HTTP 429 Too Many Requests`** (`RateLimiter`) !
   - **CSRF (`http://127.0.0.1:8001`)** → le bouton piège déclenche immédiatement **`419 | PAGE EXPIRED`** (`ValidateCsrfToken`) !

#### 🗣️ Bonnes pratiques `.env` / XAMPP & Conclusion générale (19:15 – 20:00)
> « Enfin, sur les diapositives 17 à 19, nous rappelons les **3 règles d'or entre Laravel et XAMPP/MariaDB** en production : `APP_DEBUG=false` & `APP_ENV=production`, un utilisateur MariaDB dédié limité à `SELECT, INSERT, UPDATE, DELETE` (jamais `root`), et la racine Apache pointée exclusivement sur `/public` avec `composer audit` régulier.
>
> **En conclusion**, notre suite automatisée **PHPUnit (`PortalSecurityTest` — 8 tests, 65 assertions)** valide en continu ces 5 boucliers. Laravel offre une armure native exceptionnelle contre l'OWASP Top 10, à condition que le développeur en respecte les conventions. Merci pour votre attention, nous sommes prêts pour vos questions ! »

---

## 🧠 Banque des 15 Questions-Réponses pour les 10 min du Jury (M. CAMARA)

> **Astuce d'équipe** : Répartissez les réponses selon le pilier de chacun pour montrer au professeur que **les 5 membres maîtrisent parfaitement leur sujet**.

### Questions sur la Base de Données (XAMPP / MariaDB) & Injection SQL *(Priorité : Sore Ramatou)*

1. **Q1 : Si j'utilise Eloquent ORM dans Laravel, suis-je protégé à 100 % contre les injections SQL ?**
   - **Réponse** : Non, pas à 100 % si le développeur utilise mal les méthodes brutes comme `whereRaw()`, `selectRaw()`, `orderByRaw()` ou `DB::raw()` en y concaténant directement une variable (`whereRaw("matricule = '$q'")`). Pour rester protégé même en SQL brut, il faut toujours passer un tableau de paramètres préparés en deuxième argument : `whereRaw('matricule = ?', [$q])`.

2. **Q2 : Comment fonctionne concrètement une requête préparée (Prepared Statement) entre Laravel (PDO) et MariaDB sous XAMPP ?**
   - **Réponse** : Cela se déroule en **deux étapes distinctes** :
     1. Laravel envoie d'abord le squelette de la requête SQL avec des marqueurs `?` à MariaDB (`SELECT * FROM students WHERE matricule = ?`). MariaDB compile l'arbre syntaxique SQL.
     2. Laravel envoie ensuite les paramètres (`bindings`) séparément. Même si le paramètre contient `' OR '1'='1`, MariaDB ne recompile plus le SQL : il compare simplement la colonne `matricule` à la chaîne littérale.

3. **Q3 : Pourquoi est-il dangereux de laisser l'utilisateur `root` sans mot de passe de XAMPP dans le fichier `.env` en production ?**
   - **Réponse** : L'utilisateur `root` de MariaDB possède tous les droits (`DROP DATABASE`, création d'utilisateurs, lecture de toutes les bases du serveur, écriture de fichiers via `INTO OUTFILE`). Si l'application subit une compromission ou une fuite du `.env`, tout le serveur de base de données tombe. Il faut appliquer le **principe du moindre privilège** en créant un utilisateur SQL restreint à la seule base de l'application.

### Questions sur le Mass Assignment & la Validation *(Priorité : Siby Mody)*

4. **Q4 : Quelle est la différence exacte entre `$fillable` et `$guarded` dans un modèle Eloquent ? Et lequel recommandez-vous ?**
   - **Réponse** :
     - `$fillable` est une **liste blanche (whitelist)** : seuls les champs listés peuvent être remplis en masse (`create()`, `update()`, `fill()`).
     - `$guarded` est une **liste noire (blacklist)** : les champs listés sont interdits en masse.
     - **Recommandation** : Toujours privilégier **`$fillable`**, car si on ajoute plus tard une nouvelle colonne sensible en base de données (ex. `is_super_admin` ou `solde_bourse`) via une migration et qu'on oublie de l'ajouter dans `$guarded`, elle devient immédiatement vulnérable ! De plus, écrire `$guarded = []` désactive toute protection.

5. **Q5 : Si j'utilise déjà `$fillable` sur mon modèle `User`, pourquoi avez-vous aussi utilisé une classe `FormRequest` (`UpdateProfileRequest`) ?**
   - **Réponse** : C'est le principe de **défense en profondeur (Defense in Depth)**. La `FormRequest` agit dès l'entrée HTTP : elle vérifie les types, longueurs, formats (`email`, `max:120`) et retourne des erreurs claires à l'utilisateur, et sa méthode `$request->validated()` ne renvoie que les champs autorisés. `$fillable` agit comme dernier rempart au niveau du modèle Eloquent juste avant la requête SQL.

6. **Q6 : Comment un administrateur légitime fait-il alors pour modifier le champ `role` d'un utilisateur si `role` n'est pas dans `$fillable` ?**
   - **Réponse** : Dans le contrôleur d'administration (protégé par un middleware/Policy admin), on assigne explicitement l'attribut propriété par propriété : `$user->role = 'admin'; $user->save();`. L'assignation directe d'attribut contourne volontairement `$fillable` car le développeur nomme explicitement la colonne.

### Questions sur Blade, XSS & Sécurité Front-End *(Priorité : Boin Naomi)*

7. **Q7 : Que fait exactement Laravel derrière les doubles accolades `{{ $variable }}` ?**
   - **Réponse** : Le compilateur Blade traduit `{{ $variable }}` en `<?php echo e($variable); ?>`, où le helper `e()` appelle `htmlspecialchars($variable, ENT_QUOTES, 'UTF-8', true)`. Cela convertit les 5 caractères spéciaux HTML (`&`, `"`, `'`, `<`, `>`) en entités HTML inertes.

8. **Q8 : Dans quel cas légitime a-t-on quand même besoin d'utiliser `{!! $variable !!}` et comment le sécuriser ?**
   - **Réponse** : Lorsqu'on doit afficher du HTML riche rédigé via un éditeur WYSIWYG (ex. TinyMCE, CKEditor). Dans ce cas, il ne faut **jamais** afficher directement la saisie utilisateur avec `{!! !!}` sans la nettoyer au préalable côté serveur avec un purificateur HTML sur liste blanche comme **HTMLPurifier** (`mews/purifier`), qui supprime toutes les balises `<script>`, `<iframe>` et les attributs `onerror=` / `onload=`.

9. **Q9 : Si un attaquant réussit malgré tout une faille XSS, comment Laravel empêche-t-il le vol du cookie de session en JavaScript (`document.cookie`) ?**
   - **Réponse** : Dans `config/session.php`, Laravel active par défaut l'option `'http_only' => true`. Cet attribut du cookie `Set-Cookie: ...; HttpOnly` ordonne au navigateur d'interdire tout accès au cookie via l'API JavaScript `document.cookie`.

### Questions sur le CSRF & les Sessions *(Priorité : Traoré Charifat Leyla)*

10. **Q10 : Pourquoi les requêtes `GET` ne sont-elles pas soumises à la vérification du jeton CSRF dans Laravel ?**
    - **Réponse** : Selon la norme HTTP (RFC 9110), les requêtes `GET` et `HEAD` doivent être **sûres (safe) et idempotentes**, c'est-à-dire utilisées uniquement pour lire des données sans jamais modifier l'état de la base de données. C'est pourquoi une action qui supprime ou modifie un enregistrement ne doit **jamais** être déclarée en `Route::get(...)`, mais toujours en `POST`, `PUT`, `PATCH` ou `DELETE` avec `@csrf`.

11. **Q11 : Que signifie exactement le code d'erreur HTTP `419 Page Expired` de Laravel ? Est-ce un code HTTP standard ?**
    - **Réponse** : Le code standard HTTP est `403 Forbidden` ou `400`, mais Laravel utilise spécifiquement le code **419** lorsqu'une exception `TokenMismatchException` est levée par le middleware `ValidateCsrfToken` (soit parce que le champ `_token` est absent/falsifié, soit parce que la session de l'utilisateur a expiré).

12. **Q12 : Qu'est-ce que l'attribut `same_site` des cookies dans `config/session.php` ?**
    - **Réponse** : Réglé par défaut sur `'lax'` dans Laravel (`'same_site' => 'lax'`), il empêche le navigateur d'envoyer le cookie de session lors de requêtes inter-sites de type `POST` (comme un formulaire caché sur un site tiers), offrant une seconde ligne de défense moderne en complément du jeton `@csrf`.

### Questions sur l'Authentification, Bcrypt, IDOR & Déploiement *(Priorité : Djan Kouassi Noël)*

13. **Q13 : Quelle est la différence entre le Hachage (`Hash::make`) et le Chiffrement (`Crypt::encryptString`) dans Laravel ?**
    - **Réponse** :
      - Le **Hachage (`Hash::make` avec `bcrypt` ou `Argon2id`)** est **à sens unique (irréversible)** : on ne peut jamais retrouver le mot de passe d'origine, on peut seulement vérifier une saisie avec `Hash::check($saisie, $hash)`. C'est obligatoire pour les mots de passe.
      - Le **Chiffrement (`Crypt::encryptString` avec `AES-256-CBC` et la clé `APP_KEY`)** est **réversible** avec `Crypt::decryptString()`. On l'utilise pour des données que l'application a besoin de relire (ex. un numéro de pièce d'identité ou un jeton API tiers stocké en BDD).

14. **Q14 : Quelle est la différence entre l'Authentification (`Authentication`) et l'Autorisation (`Authorization` / Policies) ?**
    - **Réponse** :
      - **L'Authentification (Middleware `auth`)** répond à la question : *« Qui êtes-vous ? »* (vérifier l'identité via login/mot de passe, renvoie `401 Unauthorized` ou redirige vers `/login`).
      - **L'Autorisation (`Gates` et `Policies`)** répond à la question : *« Avez-vous le droit d'effectuer cette action sur cette ressource précise ? »* (ex. l'Étudiant #1 est bien authentifié, mais la `GradePolicy` lui interdit de lire la note de l'Étudiant #2 et renvoie `403 Forbidden`, bloquant ainsi la faille **IDOR**).

15. **Q15 : Que se passe-t-il si on laisse `APP_DEBUG=true` dans le fichier `.env` sur un serveur en production ?**
    - **Réponse** : À la moindre erreur SQL ou exception PHP, Laravel affiche la page de débogage détaillée (Ignition/Whoops) contenant le code source, le chemin des fichiers sur le serveur, la structure des tables SQL et parfois les variables d'environnement ou paramètres de requête. En production, il faut impérativement `APP_ENV=production` et `APP_DEBUG=false`.
