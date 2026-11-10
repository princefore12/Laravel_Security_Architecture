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

1. **Démarrer l'environnement en 1 clic** : Double-cliquer sur `scripts\lancer-demo.bat`.
   - Vérifie et démarre automatiquement **MariaDB (XAMPP)** sur le port `3306`.
   - Démarre le serveur Laravel (`http://127.0.0.1:8000`).
2. **Préparer les 3 onglets du navigateur (plein écran `F11`)** :
   - **Onglet 1** : Le diaporama (`livrables/web-interactif/slides.html` ou PowerPoint `Expose_Securite_Laravel_Groupe5.pptx`).
   - **Onglet 2** : L'application de démonstration **LOKO-Vault CyberLab** (`http://127.0.0.1:8000`) — cliquer sur **« 🔄 Réinitialiser le Laboratoire »** en haut à droite pour remettre la base MariaDB dans son état initial propre.
   - **Onglet 3 (optionnel mais très impressionnant)** : `http://localhost/phpmyadmin` ouvert sur la base `loko_security_lab` (tables `users`, `students`, `grades`, `security_logs`).
3. **Lancer le chronomètre intégré** : Dans `slides.html`, cliquer sur **« ▶ Démarrer 20:00 »** en bas à droite dès que M. CAMARA donne le top départ.

---

## ⏱️ Script Oral Mot-à-Mot & Chorégraphie de Démonstration (20 Minutes)

---

### 👤 PARTIE 1 — SORE RAMATOU (00:00 → 04:00)
**Sujets** : Accroche, Architecture de sécurité multicouche de Laravel & **Atelier 1 : Injection SQL (SQLi)**  
**Slides** : Diapositives 1 à 5

#### 🗣️ Discours (00:00 – 02:15)
> « Bonjour Monsieur CAMARA, bonjour chers camarades. Nous sommes le **Groupe 5**, composé de **Sore Ramatou, Siby Mody, Boin Naomi, Traoré Charifat Leyla et Djan Kouassi Noël**. Aujourd'hui, nous avons l'honneur de vous présenter le **Thème n° 12 : La sécurité dans une application Laravel**, reliée à une base de données **MySQL / MariaDB sous XAMPP**.
>
> Pourquoi ce thème est-il central ? Parce que dans les exposés précédents, nous avons découvert l'architecture MVC, le routage, les contrôleurs, Blade et les migrations. Mais **une application fonctionnelle qui n'est pas sécurisée est une porte ouverte sur sa base de données**. Selon le référentiel mondial **OWASP Top 10**, plus de 70 % des compromissions web ciblent directement la couche applicative et ses requêtes SQL.
>
> La philosophie de Laravel tient en un principe : **"Secure by Default"** (sécurisé par défaut). Cependant, comme nous allons le prouver en direct, un développeur qui contourne les mécanismes natifs du framework peut réintroduire des failles critiques.
>
> Pour rendre cet exposé concret, notre groupe a développé **LOKO-Vault**, un laboratoire de cybersécurité complet connecté en temps réel à **MariaDB sous XAMPP**, équipé d'un **Inspecteur SQL en direct** et d'un commutateur permettant de comparer, en un clic, le **Code Vulnérable** et le **Code Sécurisé par Laravel**.
>
> Je commence immédiatement avec le **Pilier n° 1 : l'Injection SQL (SQLi)**, la menace la plus directe contre notre base de données. »

#### 💻 Démonstration en direct — Atelier 1 : Injection SQL (02:15 – 04:00)
1. **Basculer sur l'application LOKO-Vault** → Cliquer sur **« Pilier 1 : Injection SQL (SQLi) »**.
2. **En 🔴 Mode Vulnérable** :
   - Montrer le code affiché à droite : `DB::select("SELECT * FROM students WHERE matricule = '$q'")`. Expliquer que la variable `$q` est concaténée directement dans la chaîne SQL.
   - Cliquer sur le bouton rapide **« ⚡ Payload 1 : Bypass total (`' OR '1'='1`) »** puis **Exécuter**.
   - **Effet WAHOU** : L'inspecteur SQL montre la requête réellement exécutée par MariaDB (`WHERE matricule = '' OR '1'='1'`). Comme `'1'='1'` est toujours vrai, **tous les dossiers confidentiels et moyennes des étudiants de L3 s'affichent !**
   - Cliquer ensuite sur **« 💀 Payload 2 : Attaque UNION (Exfiltration table `users`) »**.
   - **Effet WAHOU** : L'attaquant détourne la requête sur la table `students` pour lire la table `users` (emails, rôles et condensats de mots de passe) !
3. **Passer en 🟢 Mode Sécurisé (1 clic)** :
   - Relancer exactement le même payload `' OR '1'='1`.
   - **Résultat** : **0 résultat trouvé — Attaque bloquée !**
   - Pointer l'Inspecteur SQL : Laravel (via **Eloquent ORM** et **PDO**) a séparé l'instruction SQL (`WHERE matricule = ?`) des données (`Bindings : ["' OR '1'='1"]`). MariaDB traite désormais l'attaque comme une simple chaîne de texte inoffensive.
4. **Transition** :
   > « Protéger la requête SQL de lecture est indispensable, mais que se passe-t-il lorsqu'un attaquant manipule les colonnes écrites en base de données ? Je passe la parole à **Siby Mody** pour le **Mass Assignment**. »

---

### 👤 PARTIE 2 — SIBY MODY (04:00 → 08:00)
**Sujets** : **Atelier 2 : Mass Assignment (Assignation de masse), Escalade de privilèges en BDD & Validation `FormRequest`**  
**Slides** : Diapositives 6 et 7

#### 🗣️ Discours (04:00 – 05:45)
> « Merci Ramatou. Bonjour Monsieur le Professeur, bonjour à tous. Je suis **Siby Mody**, et je vais vous présenter une vulnérabilité redoutable propre aux frameworks ORM modernes comme Eloquent : le **Mass Assignment** (ou assignation de masse) et son impact direct sur l'intégrité de notre base de données MariaDB.
>
> Pour accélérer le développement, Laravel permet d'enregistrer ou de mettre à jour une ligne en base en une seule instruction grâce à `$request->all()`. C'est très pratique… mais extrêmement dangereux si le modèle n'est pas verrouillé !
>
> Pourquoi ? Dans notre table `users` sous XAMPP, nous avons les colonnes `name`, `email`, `password`, mais aussi une colonne sensible : **`role`** (`student` ou `admin`). Sur le formulaire HTML de profil, seuls le nom et l'email sont affichés. Mais un attaquant peut inspecter la page (F12) ou intercepter la requête HTTP pour **ajouter un champ caché `role=admin`**. Si le contrôleur passe aveuglément `$request->all()` à la base de données, l'étudiant s'auto-octroie les pleins pouvoirs d'administrateur !
>
> Regardons cette attaque d'escalade de privilèges en direct dans **LOKO-Vault**. »

#### 💻 Démonstration en direct — Atelier 2 : Mass Assignment (05:45 – 08:00)
1. **Ouvrir « Pilier 2 : Mass Assignment & Validation »** dans LOKO-Vault.
2. **Montrer l'état initial du compte** de **Siby Mody** : badge bleu **`Rôle actuel en BDD : STUDENT (Étudiant L3)`**.
3. **En 🔴 Mode Vulnérable** :
   - Pointer le code : `$user->forceFill($request->all())->save()` (ou modèle avec `$guarded = []`).
   - Cliquer sur le bouton **« 💀 Injecter un champ caché `role=admin` dans la requête HTTP »** puis soumettre.
   - **Effet WAHOU** : Une alerte critique s'affiche, l'Inspecteur SQL montre `UPDATE users SET name = ?, email = ?, role = 'admin' WHERE id = ?`, et le badge du profil passe en rouge clignotant : **« ⚠️ COMPROMIS : RÔLE PASSÉ À ADMIN EN BASE MARIADB ! »**.
4. **Cliquer sur « Réinitialiser en Étudiant » puis basculer en 🟢 Mode Sécurisé** :
   - Tenter exactement la même attaque avec `role=admin`.
   - **Résultat** : Le nom et l'email sont mis à jour, mais le rôle reste strictement **`student`** !
   - Expliquer la **double barrière Laravel** visible dans le comparateur de code :
     1. **Au niveau du Contrôleur (`UpdateProfileRequest`)** : on utilise `$request->validated()`, qui ne laisse passer que les champs explicitement déclarés dans les règles de validation.
     2. **Au niveau du Modèle Eloquent (`User.php`)** : la liste blanche `protected $fillable = ['name', 'email', 'password'];` interdit à Eloquent de modifier la colonne `role` en masse, même par erreur.
5. **Transition** :
   > « Nous avons sécurisé la lecture et l'écriture des colonnes SQL. Mais que se passe-t-il si un étudiant enregistre du code JavaScript piégé dans un champ texte valide comme sa biographie ? **Boin Naomi** vous présente le **Pilier n° 3 : la faille XSS**. »

---

### 👤 PARTIE 3 — BOIN NAOMI (08:00 → 12:00)
**Sujets** : **Atelier 3 : Cross-Site Scripting (XSS Stocké), Moteur Blade (`{{ }}` vs `{!! !!}`) & En-têtes HTTP (`CSP`)**  
**Slides** : Diapositives 8 et 9

#### 🗣️ Discours (08:00 – 09:45)
> « Merci Mody. Bonjour à tous. Je suis **Boin Naomi** et j'aborde le **Pilier n° 3 : le Cross-Site Scripting (XSS)** et la protection du moteur de templates **Blade**.
>
> Contrairement à l'injection SQL qui attaque le serveur de base de données, la faille **XSS Stockée (Stored XSS)** utilise la base de données MariaDB comme **vecteur de propagation**. L'attaquant enregistre un script JavaScript malveillant dans un champ légitime — par exemple la biographie d'un étudiant ou un commentaire. Dès que l'administrateur ou le professeur consulte la page, le navigateur exécute ce script avec les privilèges de la victime : vol de cookie de session, modification des notes affichées à l'écran ou redirection vers un faux portail UT LOKO.
>
> Dans Laravel, tout se joue entre deux syntaxes dans les vues `.blade.php` :
> - `{!! $variable !!}` affiche la donnée brute **sans aucun filtrage** : c'est la porte ouverte au XSS.
> - `{{ $variable }}` passe automatiquement la donnée dans la fonction PHP `htmlspecialchars(..., ENT_QUOTES, 'UTF-8')`, transformant `<` et `>` en entités HTML inoffensives (`&lt;` et `&gt;`).
>
> Passons tout de suite à la démonstration en direct. »

#### 💻 Démonstration en direct — Atelier 3 : XSS Stocké & Blade (09:45 – 12:00)
1. **Ouvrir « Pilier 3 : Faille XSS & Moteur Blade »**.
2. **En 🔴 Mode Vulnérable (`{!! $student->bio !!}`)** :
   - Cliquer sur **« ⚡ Payload XSS : Défiguration & Capture de Session »** puis enregistrer en base MariaDB.
   - **Effet WAHOU** : L'Inspecteur SQL confirme que le script a été stocké dans la table `students`. À l'affichage de la page, le script s'exécute immédiatement dans la zone de prévisualisation : une bannière pirate rouge apparaît (**« ⚡ EXÉCUTION JS RÉUSSIE : DOM COMPROMIS & JETON CAPTURÉ »**).
3. **Passer en 🟢 Mode Sécurisé (`{{ $student->bio }}` + CSP)** :
   - La même biographie issue de MariaDB est maintenant affichée littéralement sous forme de texte (`<div class=...>`), sans aucune exécution !
   - Montrer le panneau **« En-têtes HTTP de Défense en Profondeur (`SecurityHeadersMiddleware`) »** :
     - `Content-Security-Policy (CSP)` : interdit l'exécution de scripts inline non autorisés.
     - `X-Content-Type-Options: nosniff` et `X-Frame-Options: DENY`.
     - Cookie de session Laravel configuré avec `http_only = true` (invisible pour `document.cookie` en JavaScript).
4. **Transition** :
   > « Même si aucun script malveillant ne s'exécute sur notre site, un attaquant peut forcer le navigateur d'un utilisateur connecté à envoyer une requête à son insu depuis un autre site. **Traoré Charifat Leyla** vous explique le **Pilier n° 4 : la faille CSRF**. »

---

### 👤 PARTIE 4 — TRAORÉ CHARIFAT LEYLA (12:00 → 16:00)
**Sujets** : **Atelier 4 : Cross-Site Request Forgery (CSRF), Sécurité des Sessions & Jeton `@csrf`**  
**Slides** : Diapositives 10 et 11

#### 🗣️ Discours (12:00 – 13:45)
> « Merci Naomi. Bonjour Monsieur CAMARA, bonjour à tous. Je suis **Traoré Charifat Leyla**, et je vais vous présenter le **Pilier n° 4 : le Cross-Site Request Forgery (CSRF)**, ou falsification de requête inter-sites.
>
> Le scénario est très fréquent : un enseignant ou un administrateur est connecté sur le portail **LOKO-Vault**. Son navigateur possède donc un cookie de session actif. Sans fermer sa session, il ouvre dans un autre onglet un site externe piégé — par exemple une fausse page de concours ou un lien reçu par email.
>
> Ce site externe contient un formulaire caché qui pointe vers l'URL de modification des notes de notre application Laravel. Comme le navigateur joint automatiquement le cookie de session aux requêtes vers notre domaine, si Laravel ne vérifie pas **l'origine réelle de l'intention**, la base de données MariaDB exécute l'ordre du pirate !
>
> Pour contrer cela, Laravel intègre le middleware `ValidateCsrfToken` (anciennement `VerifyCsrfToken`) et la directive Blade `@csrf`. À chaque session, Laravel génère un **jeton cryptographique secret** que le site externe est incapable de deviner. Vérifions-le en direct. »

#### 💻 Démonstration en direct — Atelier 4 : CSRF & Site Piège (13:45 – 16:00)
1. **Ouvrir « Pilier 4 : Faille CSRF & Protection `@csrf` »**.
2. Montrer à gauche **la note officielle en base MariaDB** (ex. *Base de données & Laravel : 12/20*) et à droite le **Simulateur de Site Externe Piégé (« 🎁 Concours Bourse d'Excellence »)**.
3. **En 🔴 Mode Vulnérable (Route sans vérification CSRF)** :
   - Cliquer sur le bouton appât **« 🎁 Réclamer ma récompense »** sur le faux site externe.
   - **Effet WAHOU** : En arrière-plan, le site piège envoie un `POST` caché (`score=20`). Sans jeton CSRF requis, Laravel accepte la requête : la note dans MariaDB passe frauduleusement à **20/20** à l'insu de l'utilisateur !
4. **Passer en 🟢 Mode Sécurisé (Middleware `ValidateCsrfToken` + `@csrf`)** :
   - Cliquer à nouveau sur le piège externe (qui envoie une requête sans jeton `_token` valide) :
   - **Effet WAHOU** : Laravel intercepte immédiatement la requête avant même de toucher à MariaDB et renvoie le bouclier officiel **HTTP 419 — Page Expired (Token CSRF manquant ou invalide)** !
   - Effectuer ensuite la modification depuis le **formulaire légitime** contenant `@csrf` (et montrer l'`<input type="hidden" name="_token" value="...">`) : la mise à jour légitime fonctionne parfaitement.
5. **Transition** :
   > « Il nous reste enfin à protéger l'authentification des utilisateurs, le chiffrement des mots de passe en base, l'accès aux dossiers privés et la configuration du serveur XAMPP. Je passe la parole à **Djan Kouassi Noël** pour le **5e pilier et la conclusion**. »

---

### 👤 PARTIE 5 — DJAN KOUASSI NOËL (16:00 → 20:00)
**Sujets** : **Atelier 5 : Authentification, Hachage `bcrypt`, Contrôle d'accès (`IDOR` / `Policies`), `Rate Limiting`, Hygiène `.env`/XAMPP & Conclusion**  
**Slides** : Diapositives 12 à 16

#### 🗣️ Discours & Démonstration combinée (16:00 – 19:00)
> « Merci Leyla. Bonjour Monsieur le Professeur, bonjour chers camarades. Je suis **Djan Kouassi Noël**, et je clôture notre parcours avec le **Pilier n° 5 : Authentification, Cryptographie en base de données, Contrôle d'accès (IDOR) et Durcissement de l'infrastructure XAMPP/Laravel**.
>
> Même lorsqu'un étudiant est légalement connecté, trois questions critiques se posent :
> 1. **Comment son mot de passe est-il stocké dans MariaDB ?**
> 2. **Peut-il consulter le bulletin de notes d'un autre étudiant en changeant simplement l'identifiant dans l'URL (faille IDOR) ?**
> 3. **Un robot peut-il tester 10 000 mots de passe par minute sur notre formulaire de connexion (Brute-Force) ?** »

#### 💻 Démonstration en direct — Atelier 5 : IDOR, Bcrypt & Rate Limiting (16:45 – 18:45)
1. **Ouvrir « Pilier 5 : Auth, Bcrypt, IDOR & Rate Limit »** dans LOKO-Vault :
   - **Sous-atelier A — Faille IDOR vs Laravel `GradePolicy`** :
     - Nous sommes connectés en tant qu'**Étudiant #1**.
     - En **🔴 Mode Vulnérable**, cliquer sur **« 🔍 Tenter d'accéder au relevé privé de l'Étudiant #2 (`/grades/2`) »** : le contrôleur fait un simple `Grade::findOrFail(2)` sans vérifier le propriétaire → **Fuite de données confidentielles !**
     - En **🟢 Mode Sécurisé**, refaire le même clic : Laravel exécute `$this->authorize('view', $grade)` via notre classe `GradePolicy` (`$grade->student->user_id === $user->id`) → **Bouclier HTTP 403 Forbidden (Accès non autorisé)** !
   - **Sous-atelier B — Laboratoire de Hachage (`MD5` vs `bcrypt` / `Argon2id`)** :
     - Tester un mot de passe dans le comparateur : montrer que `MD5` produit toujours le même condensat sans sel (cassable en 0,001s), tandis que `Hash::make()` (ou le cast `'password' => 'hashed'`) génère un hash **`bcrypt` (`$2y$12$...`) de 60 caractères avec un sel aléatoire unique à chaque exécution**.
   - **Sous-atelier C — Anti-Brute-Force (`RateLimiter`)** :
     - Cliquer sur **« 🚀 Simuler une attaque Brute-Force (6 tentatives rapides) »** : les 5 premières tentatives échouent normalement, et dès la 6e tentative, la façade `RateLimiter` de Laravel verrouille l'accès avec le code **HTTP 429 Too Many Requests** !

#### 🗣️ Bonnes pratiques `.env` / XAMPP & Conclusion générale (18:45 – 20:00)
> « enfin, sur la diapositive 15, nous rappelons les **3 règles d'or entre Laravel et XAMPP/MySQL** avant toute mise en production :
> 1. **Protection du fichier `.env`** : ne jamais le versionner sur Git (`.gitignore`), et passer impérativement `APP_DEBUG=false` et `APP_ENV=production` pour ne jamais exposer la trace d'erreur ni les identifiants MySQL aux visiteurs.
> 2. **Moindre privilège sur MariaDB/XAMPP** : en développement nous utilisons `root` sans mot de passe, mais en production l'application Laravel doit utiliser un utilisateur MySQL dédié ayant uniquement `SELECT, INSERT, UPDATE, DELETE` sur sa base, sans `DROP` ni `GRANT`.
> 3. **Audit continu** : utiliser `composer audit` pour détecter les failles dans les librairies tierces.
>
> **En conclusion** (Diapositive 16), Laravel offre une armure native exceptionnelle contre le Top 10 de l'OWASP — **PDO/Eloquent contre SQLi, `$fillable` et `FormRequest` contre le Mass Assignment, `{{ }}` contre le XSS, `@csrf` contre le CSRF, et `bcrypt`/`Policies`/`RateLimiter` pour le contrôle d'accès** — à une condition essentielle : que le développeur comprenne et respecte l'architecture du framework.
>
> Nous vous remercions pour votre attention et sommes prêts pour vos questions ! »

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
