"""
Générateur unifié des rapports académiques complets (10 pages A4) pour le Groupe 5 (UT LOKO)
Thème n° 12 : La sécurité dans une application Laravel

Architecture à Source de Vérité Unique :
  - Toutes les données et textes sont définis une seule fois dans REPORT_DATA.
  - build_docx_report() produit le fichier maître éditable :
      livrables/office/Rapport_Securite_Laravel_Groupe5.docx
  - Microsoft Word (scripts/export_word_pdf.ps1) exporte ce .docx exactement page pour page vers :
      livrables/office/Rapport_Securite_Laravel_Groupe5.pdf
    Garantissant une correspondance à 100 % entre ce qui est affiché dans le PDF et ce qui est modifiable dans Word.
  - build_web_report_html() génère la version web autonome (livrables/web-interactif/rapport.html)
    avec exactement le même contenu textuel et les mêmes schémas/captures.
"""

import base64
import html
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor as DocxRGB

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "scripts" / "assets"
OFFICE_DIR = ROOT / "livrables" / "office"
WEB_DIR = ROOT / "livrables" / "web-interactif"

LOGO_CI = ASSETS / "logo_ci.png"
LOGO_GL = ASSETS / "logo_groupe_loko.png"
LOGO_UT = ASSETS / "logo_ut_loko.png"
DIAG_7 = ASSETS / "diagram_7_couches.png"
DIAG_BDD = ASSETS / "diagram_bdd_loko.png"
SCR_DASH = ASSETS / "screen_dashboard.png"
SCR_SQLI = ASSETS / "screen_sqli.png"
SCR_ACCESS = ASSETS / "screen_access.png"

C_RED = (139, 21, 24)
C_GOLD = (217, 119, 6)
C_NAVY = (15, 23, 42)
C_SLATE = (51, 65, 85)
C_WHITE = (255, 255, 255)


def img_uri(path: Path) -> str:
    if not path.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def esc(text: str) -> str:
    return html.escape(text, quote=True)


# ==============================================================================
# SOURCE DE VÉRITÉ UNIQUE DU CONTENU ACADÉMIQUE (WORD .DOCX + WEB HTML)
# ==============================================================================

COVER_DATA = {
    "ministry": "Ministère de l'Enseignement Supérieur\net de la Recherche Scientifique",
    "dept": "ITER",
    "domain": "SCIENCE ET TECHNOLOGIE",
    "mention": "INFORMATIQUE ET TÉLÉCOMMUNICATION",
    "level": "LICENCE 3 — Module Base de Données (XAMPP) & Laravel",
    "year": "ANNÉE ACADÉMIQUE : 2025 – 2026",
    "specialty": "Spécialité : INFORMATIQUE",
    "theme_label": "THÈME N° 12 :",
    "theme_title": "La sécurité dans une application Laravel",
    "authors": [
        "SIBY MODY",
        "SORE RAMATOU",
        "BOIN NAOMI",
        "TRAORÉ LEYLA CHARIFAT",
        "DJAN KOUASSI NOËL",
    ],
    "professor": "M. CAMARA",
}

TOC_ROWS = [
    ("Page 2", "Résumé exécutif & Répartition des contributions techniques", "Groupe 5 (Collectif)"),
    ("Page 3", "1. Introduction générale & Défense en profondeur (7 couches)", "Sore Ramatou"),
    ("Page 4", "2. Pilier 1 : Injections SQL (SQLi), PDO & Eloquent ORM", "Sore Ramatou"),
    ("Page 5", "3. Pilier 2 : Mass Assignment, Intégrité BDD & Validation FormRequest", "Siby Mody"),
    ("Page 6", "4. Pilier 3 : Cross-Site Scripting (XSS), Blade & En-têtes HTTP (CSP)", "Boin Naomi"),
    ("Page 7", "5. Pilier 4 : Cross-Site Request Forgery (CSRF) & Sécurité des Sessions", "Traoré Charifat Leyla"),
    ("Page 8", "6. Pilier 5 : Cryptographie (bcrypt), Contrôle d'Accès (IDOR) & RateLimiter", "Djan Kouassi Noël"),
    ("Page 9", "7. Architecture BDD XAMPP, Durcissement Production & Conclusion", "Groupe 5 (Collectif)"),
    ("Page 10", "8. Annexes Techniques (Matrice OWASP, PHPUnit) & Bibliographie", "Groupe 5 (Collectif)"),
]

CONTRIBUTIONS_ROWS = [
    ("Sore Ramatou", "Chapitres 1 & 2", "Architecture 7 couches, OWASP Top 10, SQLi, PDO préparé & Eloquent ORM"),
    ("Siby Mody", "Chapitre 3", "Mass Assignment, escalade de privilèges sur users.role, #[Fillable] & FormRequest"),
    ("Boin Naomi", "Chapitre 4", "XSS Stockée en BDD, échappement Blade {{ }} vs {!! !!}, CSP & cookies HttpOnly"),
    ("Traoré Charifat Leyla", "Chapitre 5", "Attaques CSRF inter-sites, ValidateCsrfToken, @csrf (HTTP 419) & SameSite"),
    ("Djan Kouassi Noël", "Chapitre 6", "Hachage bcrypt vs MD5, IDOR & GradePolicy (403), RateLimiter (429) & .env"),
]

OWASP_MATRIX = [
    ("A03:2021 Injection (SQLi)", "DB::select(\"SELECT ... '$q'\")", "Eloquent ORM & PDO bindings (?)", "Paramètre littéral"),
    ("A01/A04 Mass Assignment", "$user->forceFill($request->all())", "#[Fillable] + UpdateProfileRequest", "422 / Filtrage strict"),
    ("A03:2021 Injection (XSS)", "{!! $post->content !!} sans CSP", "Blade {{ }} + SecurityHeadersMiddleware", "HTML échappé & CSP"),
    ("A01:2021 CSRF", "Route POST exempte ou action GET", "Directive @csrf + ValidateCsrfToken", "HTTP 419 Expired"),
    ("A01:2021 Broken Access (IDOR)", "Grade::findOrFail($id) sans Policy", "GradePolicy::view() + authorize()", "HTTP 403 Forbidden"),
    ("A02:2021 Cryptographic Fail.", "Stockage en clair ou MD5 / SHA-1", "Hash::make() bcrypt (cost 12) + sel", "Hash $2y$12$ unique"),
    ("A07:2021 Auth / Brute-Force", "Login sans limitation de tentatives", "RateLimiter::tooManyAttempts(..., 5)", "HTTP 429 Too Many"),
    ("A05:2021 Misconfiguration", "APP_DEBUG=true & compte SQL root", "APP_DEBUG=false & compte SQL restreint", "Surface minimale"),
]

ENV_HARDENING = [
    ("APP_ENV & APP_DEBUG", "local / true", "production / false", "Empêche l'exposition des traces PHP, requêtes SQL et variables .env."),
    ("Compte MariaDB", "root (XAMPP local)", "Utilisateur dédié restreint", "Octroyer uniquement SELECT, INSERT, UPDATE, DELETE (sans DROP ni GRANT)."),
    ("Racine Web Apache", "php artisan serve", "DocumentRoot pointant sur /public", "Empêche tout téléchargement direct de /.env ou /storage."),
    ("Cookies de Session", "SESSION_ENCRYPT=false", "http_only=true, secure=true, same_site=lax", "Protège laravel_session contre le vol XSS et les requêtes inter-sites."),
    ("Dépendances PHP", "composer install", "Exécution régulière de composer audit", "Détecte les vulnérabilités connues (CVE) dans les paquets vendor."),
]

TEST_CASES = [
    ("test_public_portal_pages_render_without_...", "Portail Public (GET /)", "Vérifie HTTP 200 et l'absence de boutons ou indices d'attaque."),
    ("test_sqli_login_bypass_and_union_...", "Pilier 1 : SQLi (/annuaire)", "Prouve le bypass ' OR '1'='1, UNION SELECT et le blocage PDO à chaud."),
    ("test_mass_assignment_escalates_role_...", "Pilier 2 : Mass Assign. (/profil)", "Prouve l'escalade role=admin via forceFill() et son rejet par FormRequest."),
    ("test_xss_cookies_httponly_and_csp_...", "Pilier 3 : XSS & CSP (/campus)", "Prouve le script stocké vs {{ }}, HttpOnly et les en-têtes CSP/DENY."),
    ("test_csrf_dynamic_middleware_allows_...", "Pilier 4 : CSRF (:8001 → :8000)", "Vérifie POST /notes/*/modifier sans jeton puis le blocage HTTP 419."),
    ("test_idor_policy_rate_limiter_and_...", "Pilier 5 : IDOR/Bcrypt/429", "Valide GradePolicy (403), bcrypt ($2y$), MD5 legacy et RateLimiter (429)."),
]

BIBLIOGRAPHY = [
    ("Laravel LLC (2026)", "Laravel 13.x Official Documentation — Security: Authentication, Authorization, CSRF Protection, Encryption & Hashing.", "https://laravel.com/docs/13.x"),
    ("Laravel LLC (2026)", "Eloquent ORM & Database: Query Builder, Mass Assignment & Prepared Statements (PDO).", "https://laravel.com/docs/13.x/eloquent"),
    ("OWASP Foundation (2021/2025)", "OWASP Top 10: The Ten Most Critical Web Application Security Risks (A01–A10).", "https://owasp.org/Top10/"),
    ("OWASP Cheat Sheet Series", "SQL Injection Prevention, Cross Site Scripting (XSS) Prevention, CSRF Prevention & Mass Assignment Cheat Sheets.", "https://cheatsheetseries.owasp.org/"),
    ("MariaDB Foundation", "MariaDB Server 10.11 Documentation — InnoDB Foreign Keys, Privilege System & Prepared Statements.", "https://mariadb.com/kb/en/documentation/"),
    ("The PHP Group", "PHP Manual — PDO (PHP Data Objects), Prepared Statements & password_hash() / bcrypt.", "https://www.php.net/manual/fr/book.pdo.php"),
    ("IETF (Fielding et al., 2022)", "RFC 9110 — HTTP Semantics (Section 9.2.1 : Safe Methods & Idempotency for GET vs POST).", "https://www.rfc-editor.org/rfc/rfc9110"),
    ("Sebastian Bergmann", "PHPUnit 12 Documentation — Automated Feature Testing for Web Applications.", "https://docs.phpunit.de/"),
]

REPORT_TEXT = {
    "p2_title": "Table des Matières & Résumé Exécutif",
    "p2_intro": (
        "Ce document technique présente l'étude approfondie menée par le Groupe 5 (Licence 3 Informatique, UT LOKO) "
        "sur la sécurité dans une application Laravel. Il examine comment les failles web majeures ciblent l'interface "
        "entre le code PHP et le serveur de base de données MariaDB / MySQL (XAMPP), et détaille l'implémentation "
        "des boucliers natifs de Laravel au sein de l'application réelle Portail Académique UT LOKO "
        "(:8000 & :8001, Laravel 13, PHP 8.5.12)."
    ),
    "p2_sub": "Répartition des contributions techniques du Groupe 5",
    "p2_callout_t": "Validation expérimentale sous XAMPP",
    "p2_callout_b": (
        "Chaque chapitre s'appuie sur des contrôles réels exécutés sur la base MariaDB loko_security_lab "
        "(port 3306) ainsi que sur une batterie de tests automatisés PHPUnit (8 tests, 65 assertions)."
    ),

    "p3_title": "1. Introduction Générale & Défense en Profondeur",
    "p3_author": "Sore Ramatou",
    "p3_intro": (
        "Le développement d'une application web robuste sous Laravel ne se limite pas à l'organisation MVC, au routage, "
        "aux contrôleurs, aux gabarits Blade et aux migrations SQL. Dès qu'un système informatique traite des comptes "
        "étudiants, des relevés académiques ou des droits d'administration dans une base MariaDB sous XAMPP, sa surface "
        "d'attaque devient critique. Selon le référentiel OWASP Top 10, les vulnérabilités liées au contrôle d'accès (A01), "
        "à la cryptographie (A02), aux injections SQL/XSS (A03), à la conception (A04) et aux mauvaises configurations "
        "(A05) représentent les vecteurs de compromission les plus fréquents."
    ),
    "p3_sub": "1.1. Le principe « Secure by Default » et les 7 couches Laravel",
    "p3_sub_intro": (
        "Laravel adopte une approche de défense en profondeur (Defense in Depth) : aucune requête HTTP n'atteint "
        "directement les tables InnoDB de MariaDB sans avoir franchi sept couches de filtrage successives :"
    ),
    "p3_layers": [
        ("Couche 1 — RateLimiter", "Limite le nombre de requêtes par IP/session et stoppe les attaques par force brute (HTTP 429)."),
        ("Couche 2 — ValidateCsrfToken", "Valide le jeton cryptographique @csrf sur toute méthode d'écriture HTTP (HTTP 419)."),
        ("Couche 3 — Authentification & Sessions", "Identifie l'utilisateur et protège le cookie laravel_session par l'attribut HttpOnly (HTTP 401)."),
        ("Couche 4 — Policies & Gates", "Vérifie la propriété de la ressource SQL ciblée pour bloquer les failles IDOR (HTTP 403)."),
        ("Couche 5 — FormRequest", "Valide les types, longueurs et n'extrait que $request->validated() (HTTP 422)."),
        ("Couche 6 — Eloquent ORM & PDO", "Verrouille les colonnes via #[Fillable] et isole les données par requêtes préparées (?)."),
        ("Couche 7 — Moteur Blade & CSP", "Échappe les sorties HTML {{ }} et applique les en-têtes SecurityHeadersMiddleware."),
    ],
    "p3_fig": "Figure 1 : Parcours d'une requête HTTP à travers les 7 couches de sécurité Laravel jusqu'à MariaDB (XAMPP).",

    "p4_title": "2. Pilier 1 : Injections SQL (SQLi), PDO & Eloquent ORM",
    "p4_author": "Sore Ramatou",
    "p4_sub1": "2.1. Nature de l'attaque et impact direct sur MariaDB",
    "p4_p1": (
        "L'injection SQL se produit lorsque des paramètres saisis par l'utilisateur sont concaténés directement dans "
        "une requête SQL envoyée à MariaDB. Un attaquant peut fermer le littéral texte au moyen d'une apostrophe et "
        "injecter une condition toujours vraie (' OR '1'='1) pour extraire l'ensemble d'une table, ou détourner la "
        "requête via UNION SELECT afin de lire la table users (adresses e-mail, rôles et condensats de mots de passe)."
    ),
    "p4_sub2": "2.2. Compilation en deux étapes via PDO et Eloquent ORM",
    "p4_p2": (
        "Pour éliminer ce risque, Eloquent ORM et le Query Builder utilisent les requêtes préparées de l'extension "
        "PHP Data Objects (PDO). Dans un premier temps, Laravel transmet à MariaDB l'instruction SQL compilable avec "
        "des marqueurs ? ; dans un second temps, il transmet les valeurs saisies (bindings) séparément. MariaDB "
        "n'interprète jamais le contenu des paramètres comme du code SQL."
    ),
    "p4_cmp": (
        "[VULNÉRABLE] DirectoryController",
        "$q = $request->input('q');\n$rows = DB::select(\n  \"SELECT id, matricule, full_name, filiere, moyenne\n   FROM students WHERE full_name LIKE '%{$q}%'\"\n);",
        "Vulnérable au bypass (' OR '1'='1) et à l'exfiltration UNION SELECT sur users.",
        "[SÉCURISÉ] Eloquent ORM & Bindings PDO",
        "$rows = Student::query()\n  ->where('matricule', $q)\n  ->get(['id', 'matricule', 'full_name', 'filiere', 'moyenne']);\n// Ou : DB::select('SELECT ... WHERE matricule = ?', [$q]);",
        "PDO isole $q dans un binding préparé : toute charge SQL devient un texte inoffensif.",
    ),
    "p4_callout_t": "Attention aux méthodes brutes (whereRaw, selectRaw, orderByRaw)",
    "p4_callout_b": (
        "Eloquent ne protège pas les expressions brutes mal écrites comme whereRaw(\"matricule = '$q'\"). "
        "Il est impératif d'utiliser un tableau de bindings : whereRaw('matricule = ?', [$q])."
    ),
    "p4_fig": "Figure 2 : Capture du Portail UT LOKO — Annuaire (/annuaire) exposé aux injections SQL (?q=) avant durcissement .env.",

    "p5_title": "3. Pilier 2 : Mass Assignment, Intégrité BDD & FormRequest",
    "p5_author": "Siby Mody",
    "p5_sub1": "3.1. Escalade de privilèges par assignation de masse",
    "p5_p1": (
        "L'assignation de masse permet d'hydrater et de sauvegarder un modèle Eloquent en une instruction à partir "
        "d'un tableau HTTP ($user->update($request->all())). Dans la base MariaDB loko_security_lab, la table users "
        "contient une colonne sensible role ('student' ou 'admin'). Bien que le formulaire HTML visible ne propose "
        "que les champs name et email, un utilisateur malveillant peut ajouter un paramètre POST caché role=admin et "
        "obtenir ainsi les privilèges d'administrateur."
    ),
    "p5_sub2": "3.2. Liste blanche (#[Fillable] / $fillable) contre liste noire ($guarded)",
    "p5_bullets": [
        ("Approche Liste Blanche (#[Fillable(['name', 'email', 'password'])] en Laravel 13 ou $fillable)",
         "Seules les colonnes explicitement autorisées peuvent être remplies en masse. L'attribut role reste strictement inaccessible par cette voie."),
        ("Approche Liste Noire ($guarded = ['role'])",
         "Déconseillée, car toute nouvelle colonne critique ajoutée ultérieurement par migration reste vulnérable en cas d'oubli. Définir $guarded = [] ou appeler forceFill() annule toute barrière."),
    ],
    "p5_sub3": "3.3. La double barrière de défense en profondeur",
    "p5_cmp": (
        "[VULNÉRABLE] forceFill non filtré",
        "$user = User::where('email', 'mody.siby@loko.ci')->firstOrFail();\n$user->forceFill($request->only(['name', 'email', 'role']))->save();",
        "Modifie directement la colonne users.role en 'admin' dans MariaDB.",
        "[SÉCURISÉ] UpdateProfileRequest + #[Fillable]",
        "// UpdateProfileRequest::rules() -> 'name' et 'email' uniquement\n$user->update($request->validated());",
        "validated() écarte 'role' en amont et #[Fillable] protège le modèle en aval.",
    ),
    "p5_callout_t": "Attribution légitime d'un rôle par un administrateur",
    "p5_callout_b": (
        "Lorsqu'un administrateur autorisé par une Policy doit promouvoir un compte, il procède par assignation "
        "directe d'attribut : $user->role = 'admin'; $user->save();."
    ),

    "p6_title": "4. Pilier 3 : Cross-Site Scripting (XSS), Blade & Headers CSP",
    "p6_author": "Boin Naomi",
    "p6_sub1": "4.1. Du stockage en base MariaDB à l'exécution navigateur (XSS Stockée)",
    "p6_p1": (
        "Une faille Cross-Site Scripting (XSS) permet d'injecter du code JavaScript exécutable dans les pages affichées "
        "aux utilisateurs. Dans sa forme stockée (Stored XSS), la base MariaDB sert de vecteur persistant : une charge "
        "malveillante enregistrée dans campus_posts.content (balise <img src='x' onerror='...'>) s'exécute "
        "automatiquement chez tout professeur ou étudiant qui consulte le mur du campus (/campus)."
    ),
    "p6_sub2": "4.2. Échappement automatique Blade : {{ }} contre {!! !!}",
    "p6_p2": (
        "Par défaut, la syntaxe Blade {{ $post->content }} se compile en <?php echo e($post->content); ?>, qui appelle "
        "htmlspecialchars(..., ENT_QUOTES, 'UTF-8', true). Tous les chevrons et guillemets sont convertis en entités "
        "HTML inertes (&lt;, &gt;). À l'opposé, la directive {!! $post->content !!} affiche la chaîne brute sans filtrage "
        "et ne doit jamais être employée sur des saisies utilisateurs non purifiées."
    ),
    "p6_cmp": (
        "[VULNÉRABLE] Vue Blade ({!! !!})",
        "<div class=\"post-body\">\n  {!! $post->content !!}\n</div>",
        "Exécute le JavaScript stocké dans MariaDB dès le chargement du DOM.",
        "[SÉCURISÉ] Vue Blade ({{ }}) + CSP",
        "<div class=\"post-body\">\n  {{ $post->content }}\n</div>\n// + SecurityHeadersMiddleware",
        "Convertit les balises en texte inerte et applique Content-Security-Policy.",
    ),
    "p6_sub3": "4.3. Défense en profondeur côté HTTP et Cookies",
    "p6_bullets": [
        ("En-têtes HTTP (SecurityHeadersMiddleware)",
         "Content-Security-Policy restreint les sources de scripts ; X-Content-Type-Options: nosniff empêche le MIME-sniffing ; X-Frame-Options: DENY bloque le Clickjacking."),
        ("Protection du cookie de session (HttpOnly)",
         "Configuré à 'http_only' => true dans config/session.php, le cookie laravel_session reste invisible pour document.cookie même si du JavaScript était injecté."),
        ("Assainissement HTML riche (WYSIWYG)",
         "Si du HTML enrichi doit être rendu avec {!! !!}, il doit être nettoyé côté serveur par une bibliothèque sur liste blanche comme HTMLPurifier."),
    ],

    "p7_title": "5. Pilier 4 : Cross-Site Request Forgery (CSRF) & Sessions",
    "p7_author": "Traoré Charifat Leyla",
    "p7_sub1": "5.1. Anatomie d'une attaque par falsification inter-sites",
    "p7_p1": (
        "Une attaque CSRF exploite la confiance accordée par une application au navigateur d'un utilisateur déjà authentifié. "
        "Tant que la session est ouverte, le navigateur transmet automatiquement le cookie laravel_session vers le domaine cible, "
        "y compris lorsque la requête HTTP est déclenchée depuis un site tiers malveillant (simulé sur le serveur externe "
        "http://127.0.0.1:8001/index.html qui poste silencieusement score=20)."
    ),
    "p7_sub2": "5.2. Jeton cryptographique @csrf et ValidateCsrfToken (HTTP 419)",
    "p7_p2": (
        "Laravel attribue à chaque session un jeton secret aléatoire que tout site externe est incapable de deviner. "
        "La directive Blade @csrf génère un champ caché _token dans chaque formulaire. À la réception d'une requête POST, "
        "PUT, PATCH ou DELETE, le middleware ValidateCsrfToken vérifie ce jeton en temps constant via hash_equals() "
        "(protection contre les attaques temporelles). En l'absence de jeton valide, Laravel bloque l'opération avant "
        "d'atteindre MariaDB et renvoie le code HTTP 419 Page Expired."
    ),
    "p7_cmp": (
        "[VULNÉRABLE] Route exempte ou GET",
        "// DynamicCsrfMiddleware (SECURITY_HARDENED=false)\nif ($request->is('notes/*/modifier')) return true;\n// Ou : Route::get('/grades/reset/{id}', ...);",
        "Le site piège :8001 modifie la note en base MariaDB sans jeton _token.",
        "[SÉCURISÉ] Protection @csrf & SameSite=Lax",
        "<form method=\"POST\" action=\"{{ route('portal.grades.update', $g) }}\">\n  @csrf\n  <input type=\"number\" name=\"score\" value=\"15.75\">\n</form>",
        "Une soumission externe sans _token échoue immédiatement avec HTTP 419.",
    ),
    "p7_bullets": [
        ("Idempotence HTTP (RFC 9110)",
         "Les routes GET ne doivent jamais modifier la base de données ; elles sont réservées à la lecture."),
        ("AJAX & Cookie SameSite",
         "Les requêtes fetch/Axios incluent l'en-tête X-CSRF-TOKEN, tandis que 'same_site' => 'lax' bloque l'envoi automatique des cookies lors de POST inter-sites."),
    ],

    "p8_title": "6. Pilier 5 : Cryptographie, IDOR (Policies) & RateLimiter",
    "p8_author": "Djan Kouassi Noël",
    "p8_sub1": "6.1. Hachage adaptatif bcrypt / Argon2id contre MD5",
    "p8_p1": (
        "Stocker des mots de passe en clair ou avec MD5/SHA-1 dans MariaDB expose les comptes aux attaques par Rainbow "
        "Tables et GPU (plusieurs milliards d'empreintes par seconde, sans sel). Laravel impose le hachage unidirectionnel "
        "salé bcrypt (ou Argon2id) via Hash::make() et le cast 'password' => 'hashed' : un sel aléatoire de 128 bits et "
        "un facteur de coût (BCRYPT_ROUNDS=12) garantissent que deux mots de passe identiques produisent deux empreintes "
        "$2y$12$... distinctes. Contrairement à Crypt::encryptString() (chiffrement réversible AES-256-CBC), le hachage "
        "ne peut jamais être déchiffré et se vérifie via Hash::check()."
    ),
    "p8_sub2": "6.2. Autorisation granulaire : bloquer l'IDOR avec GradePolicy",
    "p8_p2": (
        "L'authentification (HTTP 401) vérifie l'identité de l'utilisateur, mais seule l'autorisation empêche la faille "
        "IDOR (Insecure Direct Object Reference) où un étudiant consulte les notes d'un autre en modifiant l'ID dans "
        "l'URL. Notre classe GradePolicy::view(User $user, Grade $grade) vérifie "
        "$user->isAdmin() || $grade->student?->user_id === $user->id et renvoie HTTP 403 Forbidden en cas d'accès illicite."
    ),
    "p8_sub3": "6.3. Anti-Brute-Force avec RateLimiter (HTTP 429)",
    "p8_p3": (
        "La façade RateLimiter restreint les tentatives d'authentification à 5 essais par minute par IP et verrouille la "
        "6e tentative via HTTP 429 Too Many Requests."
    ),
    "p8_fig": "Figure 3 : Capture du Portail UT LOKO — Faille IDOR sur /bulletins/2 (Sore Ramatou lit la note de Siby Mody) avant HTTP 403.",

    "p9_title": "7. Architecture MariaDB XAMPP, Durcissement & Conclusion",
    "p9_author": "Groupe 5",
    "p9_p1": (
        "La base MariaDB 10.11.16 s'articule autour de cinq tables InnoDB liées par contraintes référentielles : "
        "users (rôles et legacy_md5), students (dossiers liés), grades (notes), campus_posts (mur XSS) et "
        "security_logs (traçabilité SQL capturée par SqlInspectorService)."
    ),
    "p9_fig1": "Figure 4 : Schéma relationnel MariaDB (loko_security_lab) sous XAMPP.",
    "p9_fig2": "Figure 5 : Accueil du Portail Académique UT LOKO (127.0.0.1:8000) connecté à MariaDB.",
    "p9_sub": "7.2. Checklist de durcissement XAMPP vers Production",
    "p9_conc_lead": "Conclusion générale : ",
    "p9_conc": (
        "Laravel offre une architecture de sécurité complète et éprouvée face aux menaces majeures recensées par l'OWASP. "
        "Combinée à une conception rigoureuse de la base MariaDB, au respect strict de ses conventions (Eloquent PDO, "
        "#[Fillable], FormRequest, Blade {{ }}, @csrf, bcrypt et Policies) et à une configuration serveur durcie, elle "
        "garantit la fiabilité et la confidentialité des applications modernes."
    ),

    "p10_title": "8. Annexes Techniques & Bibliographie",
    "p10_sub1": "Annexe A — Matrice de synthèse OWASP Top 10 <-> Protections Laravel",
    "p10_sub2": "Annexe B — Validation automatisée par suite de tests PHPUnit 12 (8 tests / 65 assertions)",
    "p10_sub3": "Bibliographie & Webographie Officielle",
}


# ==============================================================================
# PARTIE 1 : RAPPORT WORD MAÎTRE (.DOCX) — 10 PAGES A4 ÉDITABLES & IDENTIQUES AU PDF
# ==============================================================================

def docx_rgb(c):
    return DocxRGB(c[0], c[1], c[2])


def shade_cell(cell, hex_color):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=55, bottom=55, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="CBD5E1", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def set_cell_left_border(cell, color="D97706", sz="24"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)


def set_row_cant_split(row):
    trPr = row._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))


def set_row_min_height(row, height_cm: float):
    trPr = row._tr.get_or_add_trPr()
    dxa = int(height_cm * 567)
    trPr.append(parse_xml(f'<w:trHeight {nsdecls("w")} w:val="{dxa}" w:hRule="atLeast"/>'))


def add_word_field(p, field_name: str, font_size=8.2, color=C_SLATE):
    for node in [
        parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="begin"/>'),
        parse_xml(f'<w:instrText {nsdecls("w")} xml:space="preserve"> {field_name} </w:instrText>'),
        parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="separate"/>'),
    ]:
        r = p.add_run()
        r.font.name = "Arial"
        r.font.size = Pt(font_size)
        r.font.color.rgb = docx_rgb(color)
        r._r.append(node)
    rt = p.add_run("1")
    rt.font.name = "Arial"
    rt.font.size = Pt(font_size)
    rt.font.color.rgb = docx_rgb(color)
    re = p.add_run()
    re.font.name = "Arial"
    re.font.size = Pt(font_size)
    re.font.color.rgb = docx_rgb(color)
    re._r.append(parse_xml(f'<w:fldChar {nsdecls("w")} w:fldCharType="end"/>'))


def d_heading(doc, text, author="", page_break=True):
    p = doc.add_paragraph()
    if page_break:
        p.paragraph_format.page_break_before = True
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(5)
    p.paragraph_format.keep_with_next = True
    pPr = p._p.get_or_add_pPr()
    pPr.append(parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="10" w:space="3" w:color="8B1518"/></w:pBdr>'))
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(13.0)
    r.font.color.rgb = docx_rgb(C_RED)
    if author:
        r2 = p.add_run(f" — {author}")
        r2.bold = True
        r2.font.name = "Arial"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = docx_rgb(C_SLATE)


def d_sub(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2.5)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Arial"
    r.font.size = Pt(10.5)
    r.font.color.rgb = docx_rgb(C_NAVY)


def d_para(doc, text, bold_prefix="", space_after=4.5):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.bold = True
        rb.font.name = "Arial"
        rb.font.size = Pt(9.3)
        rb.font.color.rgb = docx_rgb(C_NAVY)
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(9.3)
    r.font.color.rgb = docx_rgb((30, 41, 59))


def d_bullet(doc, lead, text, url="", font_size=9.0, space_after=2.5):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.45)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.12
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rb = p.add_run(f"• {lead} : ")
    rb.bold = True
    rb.font.name = "Arial"
    rb.font.size = Pt(font_size)
    rb.font.color.rgb = docx_rgb(C_NAVY)
    r = p.add_run(text)
    r.font.name = "Arial"
    r.font.size = Pt(font_size)
    r.font.color.rgb = docx_rgb((30, 41, 59))
    if url:
        ru = p.add_run(f" {url}")
        ru.font.name = "Arial"
        ru.font.size = Pt(font_size)
        ru.font.color.rgb = DocxRGB.from_string("1D4ED8")


def d_callout(doc, title, text, bg="EFF6FF", border="2563EB"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    set_table_borders(tbl, color=border, sz="8")
    set_row_cant_split(tbl.rows[0])
    c = tbl.cell(0, 0)
    c.width = Cm(18.2)
    shade_cell(c, bg)
    set_cell_margins(c, 70, 70, 120, 120)
    p = c.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.12
    rt = p.add_run(f"{title} : ")
    rt.bold = True
    rt.font.name = "Arial"
    rt.font.size = Pt(8.9)
    rt.font.color.rgb = docx_rgb(C_NAVY)
    rb = p.add_run(text)
    rb.font.name = "Arial"
    rb.font.size = Pt(8.9)
    rb.font.color.rgb = docx_rgb(C_NAVY)
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(2)
    sp.add_run("").font.size = Pt(2)


def d_compare(doc, v_title, v_code, v_note, s_title, s_code, s_note):
    tbl = doc.add_table(rows=2, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    set_table_borders(tbl, color="CBD5E1", sz="6")
    for r in tbl.rows:
        set_row_cant_split(r)
    for ci, (ht, hc, hb) in enumerate([(v_title, "DC2626", "FEF2F2"), (s_title, "059669", "ECFDF5")]):
        cell = tbl.cell(0, ci)
        cell.width = Cm(9.1)
        shade_cell(cell, hb)
        set_cell_margins(cell, 55, 45, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(ht)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(8.8)
        r.font.color.rgb = DocxRGB.from_string(hc)
    for ci, (cd, nt, bb) in enumerate([(v_code, v_note, "FEF2F2"), (s_code, s_note, "ECFDF5")]):
        cell = tbl.cell(1, ci)
        cell.width = Cm(9.1)
        shade_cell(cell, bb)
        set_cell_margins(cell, 45, 60, 100, 100)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.08
        rc = p.add_run(cd)
        rc.font.name = "Consolas"
        rc.font.size = Pt(7.8)
        rc.font.color.rgb = docx_rgb(C_NAVY)
        p2 = cell.add_paragraph()
        p2.paragraph_format.space_before = Pt(0)
        p2.paragraph_format.space_after = Pt(0)
        p2.paragraph_format.line_spacing = 1.1
        rn = p2.add_run(nt)
        rn.font.name = "Arial"
        rn.font.size = Pt(8.1)
        rn.font.color.rgb = docx_rgb(C_SLATE)
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(2)
    sp.add_run("").font.size = Pt(2)


def d_figure(doc, img_path: Path, caption: str, width_cm: float, height_cm: float = None):
    if not img_path.exists():
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    kwargs = {"width": Cm(width_cm)}
    if height_cm is not None:
        kwargs["height"] = Cm(height_cm)
    p.add_run().add_picture(str(img_path), **kwargs)
    pc = doc.add_paragraph()
    pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pc.paragraph_format.space_before = Pt(0)
    pc.paragraph_format.space_after = Pt(4)
    rc = pc.add_run(caption)
    rc.italic = True
    rc.font.name = "Arial"
    rc.font.size = Pt(8.2)
    rc.font.color.rgb = docx_rgb(C_SLATE)


def d_table(doc, headers, rows, widths_cm, font_size=8.1, pad_v=42):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    set_table_borders(tbl)
    for row in tbl.rows:
        set_row_cant_split(row)
    for ci, h in enumerate(headers):
        c = tbl.cell(0, ci)
        c.width = Cm(widths_cm[ci])
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        shade_cell(c, "8B1518")
        set_cell_margins(c, pad_v + 8, pad_v + 8, 80, 80)
        p = c.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.name = "Arial"
        r.font.size = Pt(font_size + 0.2)
        r.font.color.rgb = docx_rgb(C_WHITE)
    for ri, row in enumerate(rows, start=1):
        for ci, val in enumerate(row):
            c = tbl.cell(ri, ci)
            c.width = Cm(widths_cm[ci])
            c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if ri % 2 == 0:
                shade_cell(c, "F8FAFC")
            set_cell_margins(c, pad_v, pad_v, 80, 80)
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.08
            r = p.add_run(val)
            r.font.name = "Arial"
            r.font.size = Pt(font_size)
            r.bold = (ci == 0)
            r.font.color.rgb = docx_rgb(C_NAVY)
    sp = doc.add_paragraph()
    sp.paragraph_format.space_before = Pt(0)
    sp.paragraph_format.space_after = Pt(2)
    sp.add_run("").font.size = Pt(2)


def build_docx_report() -> Path:
    doc = Document()
    for sec in doc.sections:
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)
        sec.top_margin = Cm(1.35)
        sec.bottom_margin = Cm(1.35)
        sec.left_margin = Cm(1.4)
        sec.right_margin = Cm(1.4)
        sec.header_distance = Cm(0.55)
        sec.footer_distance = Cm(0.55)
        sec.different_first_page_header_footer = True

        # En-tête (Pages 2 à 10) identique au PDF
        hp0 = sec.header.paragraphs[0]
        hp0.paragraph_format.space_before = Pt(0)
        hp0.paragraph_format.space_after = Pt(0)
        htbl = sec.header.add_table(rows=1, cols=2, width=Cm(18.2))
        htbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        htbl.autofit = False
        set_table_borders(htbl, val="none")
        htbl._tbl.tblPr.append(parse_xml(
            f'<w:tblBorders {nsdecls("w")}><w:bottom w:val="single" w:sz="8" w:space="0" w:color="8B1518"/></w:tblBorders>'
        ))
        hc0, hc1 = htbl.cell(0, 0), htbl.cell(0, 1)
        hc0.width, hc1.width = Cm(9.1), Cm(9.1)
        set_cell_margins(hc0, 0, 35, 0, 0)
        set_cell_margins(hc1, 0, 35, 0, 0)
        hp_l = hc0.paragraphs[0]
        hp_l.paragraph_format.space_after = Pt(0)
        rl = hp_l.add_run("UT LOKO • Licence 3 Informatique • Groupe 5")
        rl.font.name = "Arial"
        rl.font.size = Pt(8.0)
        rl.font.color.rgb = docx_rgb(C_SLATE)
        hp_r = hc1.paragraphs[0]
        hp_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hp_r.paragraph_format.space_after = Pt(0)
        rr = hp_r.add_run("La sécurité dans une application Laravel")
        rr.font.name = "Arial"
        rr.font.size = Pt(8.0)
        rr.font.color.rgb = docx_rgb(C_SLATE)

        # Pied de page (Pages 2 à 10) avec Page X / Y dynamique
        fp0 = sec.footer.paragraphs[0]
        fp0.paragraph_format.space_before = Pt(0)
        fp0.paragraph_format.space_after = Pt(0)
        ftbl = sec.footer.add_table(rows=1, cols=2, width=Cm(18.2))
        ftbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        ftbl.autofit = False
        set_table_borders(ftbl, val="none")
        ftbl._tbl.tblPr.append(parse_xml(
            f'<w:tblBorders {nsdecls("w")}><w:top w:val="single" w:sz="8" w:space="0" w:color="8B1518"/></w:tblBorders>'
        ))
        fc0, fc1 = ftbl.cell(0, 0), ftbl.cell(0, 1)
        fc0.width, fc1.width = Cm(14.0), Cm(4.2)
        set_cell_margins(fc0, 35, 0, 0, 0)
        set_cell_margins(fc1, 35, 0, 0, 0)
        fp_l = fc0.paragraphs[0]
        fp_l.paragraph_format.space_after = Pt(0)
        rfl = fp_l.add_run("Module : Base de Données (XAMPP / MariaDB) & Framework Laravel | Prof. M. CAMARA")
        rfl.font.name = "Arial"
        rfl.font.size = Pt(8.0)
        rfl.font.color.rgb = docx_rgb(C_SLATE)
        fp_r = fc1.paragraphs[0]
        fp_r.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        fp_r.paragraph_format.space_after = Pt(0)
        rfr = fp_r.add_run("Page ")
        rfr.font.name = "Arial"
        rfr.font.size = Pt(8.0)
        rfr.font.color.rgb = docx_rgb(C_SLATE)
        add_word_field(fp_r, "PAGE", 8.0, C_SLATE)
        rfr2 = fp_r.add_run(" / ")
        rfr2.font.name = "Arial"
        rfr2.font.size = Pt(8.0)
        rfr2.font.color.rgb = docx_rgb(C_SLATE)
        add_word_field(fp_r, "NUMPAGES", 8.0, C_SLATE)

    # ---- PAGE 1 : COUVERTURE OFFICIELLE UT LOKO ----
    top_tbl = doc.add_table(rows=1, cols=3)
    top_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    top_tbl.autofit = False
    set_table_borders(top_tbl, val="none")
    c0, c1, c2 = top_tbl.cell(0, 0), top_tbl.cell(0, 1), top_tbl.cell(0, 2)
    c0.width, c1.width, c2.width = Cm(3.5), Cm(11.2), Cm(3.5)
    for c in (c0, c1, c2):
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    if LOGO_CI.exists():
        c0.paragraphs[0].add_run().add_picture(str(LOGO_CI), width=Cm(2.8))
    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_min = p1.add_run(COVER_DATA["ministry"])
    r_min.font.name = "Arial"
    r_min.font.size = Pt(11.0)
    r_min.bold = True
    r_min.font.color.rgb = docx_rgb(C_NAVY)
    if LOGO_GL.exists():
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p2.add_run().add_picture(str(LOGO_GL), width=Cm(2.1))

    sp_cov = doc.add_paragraph()
    sp_cov.paragraph_format.space_before = Pt(0)
    sp_cov.paragraph_format.space_after = Pt(6)
    sp_cov.add_run("").font.size = Pt(2)

    cover_tbl = doc.add_table(rows=1, cols=2)
    cover_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cover_tbl.autofit = False
    set_table_borders(cover_tbl, color="8B1518", sz="10")
    set_row_min_height(cover_tbl.rows[0], 22.0)
    left_c, right_c = cover_tbl.cell(0, 0), cover_tbl.cell(0, 1)
    left_c.width, right_c.width = Cm(6.5), Cm(11.7)
    left_c.vertical_alignment = WD_ALIGN_VERTICAL.TOP
    right_c.vertical_alignment = WD_ALIGN_VERTICAL.TOP
    set_cell_margins(left_c, 220, 180, 180, 180)
    set_cell_margins(right_c, 260, 220, 220, 220)
    shade_cell(right_c, "8B1518")
    set_cell_left_border(right_c, color="D97706", sz="24")

    lp0 = left_c.paragraphs[0]
    lp0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    lp0.paragraph_format.space_after = Pt(18)
    if LOGO_UT.exists():
        lp0.add_run().add_picture(str(LOGO_UT), width=Cm(4.4))

    for lbl, val, col_txt, same_line in [
        ("DÉPARTEMENT : ", COVER_DATA["dept"], C_NAVY, True),
        ("DOMAINE :", COVER_DATA["domain"], C_NAVY, False),
        ("MENTION :", COVER_DATA["mention"], C_NAVY, False),
        ("NIVEAU :", COVER_DATA["level"], C_RED, False),
    ]:
        lp = left_c.add_paragraph()
        lp.paragraph_format.space_before = Pt(8)
        lp.paragraph_format.space_after = Pt(8)
        lp.paragraph_format.line_spacing = 1.25
        rl = lp.add_run(lbl if same_line else lbl + "\n")
        rl.bold = True
        rl.font.name = "Arial"
        rl.font.size = Pt(9.8)
        rl.font.color.rgb = docx_rgb(col_txt)
        rv = lp.add_run(val)
        rv.font.name = "Arial"
        rv.font.size = Pt(9.8)
        rv.font.color.rgb = docx_rgb(col_txt)

    def add_rc(text, size=11.5, bold=True, color=C_WHITE, before=4, after=6, underline=False):
        rp = right_c.add_paragraph() if len(right_c.paragraphs[0].text) > 0 or len(right_c.paragraphs) > 1 else right_c.paragraphs[0]
        rp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rp.paragraph_format.space_before = Pt(before)
        rp.paragraph_format.space_after = Pt(after)
        rp.paragraph_format.line_spacing = 1.25
        rr = rp.add_run(text)
        rr.font.name = "Arial"
        rr.font.size = Pt(size)
        rr.bold = bold
        rr.underline = underline
        rr.font.color.rgb = docx_rgb(color)

    add_rc(COVER_DATA["year"], size=11.5, before=6, after=12)
    add_rc(COVER_DATA["specialty"], size=11.5, before=4, after=22)
    add_rc(COVER_DATA["theme_label"], size=11.5, color=(253, 230, 138), before=12, after=6)
    add_rc(COVER_DATA["theme_title"], size=19.0, color=C_WHITE, before=2, after=26)
    add_rc("TRAVAIL RÉALISÉ PAR (GROUPE 5) :", size=11.5, color=(253, 230, 138), before=10, after=8, underline=True)
    for nm in COVER_DATA["authors"]:
        add_rc(nm, size=12.0, color=C_WHITE, before=2, after=3)
    add_rc("PROFESSEUR :", size=11.5, color=(253, 230, 138), before=24, after=3)
    add_rc(COVER_DATA["professor"], size=14.0, color=C_WHITE, before=0, after=8)

    # ---- PAGE 2 : TABLE DES MATIÈRES & RÉSUMÉ EXÉCUTIF ----
    d_heading(doc, REPORT_TEXT["p2_title"], page_break=True)
    d_para(doc, REPORT_TEXT["p2_intro"])
    d_table(doc, ["Repère", "Intitulé du Chapitre / Section", "Auteur Référent"], TOC_ROWS, [2.2, 11.8, 4.2])
    d_sub(doc, REPORT_TEXT["p2_sub"])
    d_table(doc, ["Membre du Groupe 5", "Chapitre(s)", "Périmètre technique couvert"], CONTRIBUTIONS_ROWS, [4.2, 2.8, 11.2])
    d_callout(doc, REPORT_TEXT["p2_callout_t"], REPORT_TEXT["p2_callout_b"])

    # ---- PAGE 3 : CHAPITRE 1 ----
    d_heading(doc, REPORT_TEXT["p3_title"], REPORT_TEXT["p3_author"], page_break=True)
    d_para(doc, REPORT_TEXT["p3_intro"])
    d_sub(doc, REPORT_TEXT["p3_sub"])
    d_para(doc, REPORT_TEXT["p3_sub_intro"])
    for lead, desc in REPORT_TEXT["p3_layers"]:
        d_bullet(doc, lead, desc)
    d_figure(doc, DIAG_7, REPORT_TEXT["p3_fig"], 17.8, 6.8)

    # ---- PAGE 4 : CHAPITRE 2 (SQLi) ----
    d_heading(doc, REPORT_TEXT["p4_title"], REPORT_TEXT["p4_author"], page_break=True)
    d_sub(doc, REPORT_TEXT["p4_sub1"])
    d_para(doc, REPORT_TEXT["p4_p1"])
    d_sub(doc, REPORT_TEXT["p4_sub2"])
    d_para(doc, REPORT_TEXT["p4_p2"])
    d_compare(doc, *REPORT_TEXT["p4_cmp"])
    d_callout(doc, REPORT_TEXT["p4_callout_t"], REPORT_TEXT["p4_callout_b"], bg="FEF3C7", border="D97706")
    d_figure(doc, SCR_SQLI, REPORT_TEXT["p4_fig"], 15.6, 9.75)

    # ---- PAGE 5 : CHAPITRE 3 (MASS ASSIGNMENT) ----
    d_heading(doc, REPORT_TEXT["p5_title"], REPORT_TEXT["p5_author"], page_break=True)
    d_sub(doc, REPORT_TEXT["p5_sub1"])
    d_para(doc, REPORT_TEXT["p5_p1"])
    d_sub(doc, REPORT_TEXT["p5_sub2"])
    for lead, desc in REPORT_TEXT["p5_bullets"]:
        d_bullet(doc, lead, desc)
    d_sub(doc, REPORT_TEXT["p5_sub3"])
    d_compare(doc, *REPORT_TEXT["p5_cmp"])
    d_callout(doc, REPORT_TEXT["p5_callout_t"], REPORT_TEXT["p5_callout_b"], bg="ECFDF5", border="059669")

    # ---- PAGE 6 : CHAPITRE 4 (XSS & BLADE) ----
    d_heading(doc, REPORT_TEXT["p6_title"], REPORT_TEXT["p6_author"], page_break=True)
    d_sub(doc, REPORT_TEXT["p6_sub1"])
    d_para(doc, REPORT_TEXT["p6_p1"])
    d_sub(doc, REPORT_TEXT["p6_sub2"])
    d_para(doc, REPORT_TEXT["p6_p2"])
    d_compare(doc, *REPORT_TEXT["p6_cmp"])
    d_sub(doc, REPORT_TEXT["p6_sub3"])
    for lead, desc in REPORT_TEXT["p6_bullets"]:
        d_bullet(doc, lead, desc)

    # ---- PAGE 7 : CHAPITRE 5 (CSRF & SESSIONS) ----
    d_heading(doc, REPORT_TEXT["p7_title"], REPORT_TEXT["p7_author"], page_break=True)
    d_sub(doc, REPORT_TEXT["p7_sub1"])
    d_para(doc, REPORT_TEXT["p7_p1"])
    d_sub(doc, REPORT_TEXT["p7_sub2"])
    d_para(doc, REPORT_TEXT["p7_p2"])
    d_compare(doc, *REPORT_TEXT["p7_cmp"])
    for lead, desc in REPORT_TEXT["p7_bullets"]:
        d_bullet(doc, lead, desc)

    # ---- PAGE 8 : CHAPITRE 6 (BCRYPT, IDOR, RATE LIMITER) ----
    d_heading(doc, REPORT_TEXT["p8_title"], REPORT_TEXT["p8_author"], page_break=True)
    d_sub(doc, REPORT_TEXT["p8_sub1"])
    d_para(doc, REPORT_TEXT["p8_p1"])
    d_sub(doc, REPORT_TEXT["p8_sub2"])
    d_para(doc, REPORT_TEXT["p8_p2"])
    d_sub(doc, REPORT_TEXT["p8_sub3"])
    d_para(doc, REPORT_TEXT["p8_p3"])
    d_figure(doc, SCR_ACCESS, REPORT_TEXT["p8_fig"], 15.8, 9.85)

    # ---- PAGE 9 : CHAPITRE 7 (ARCHITECTURE BDD, DURCISSEMENT & CONCLUSION) ----
    d_heading(doc, REPORT_TEXT["p9_title"], REPORT_TEXT["p9_author"], page_break=True)
    d_para(doc, REPORT_TEXT["p9_p1"], space_after=3.5)
    d_figure(doc, DIAG_BDD, REPORT_TEXT["p9_fig1"], 11.6, 6.0)
    d_figure(doc, SCR_DASH, REPORT_TEXT["p9_fig2"], 9.8, 6.1)
    d_sub(doc, REPORT_TEXT["p9_sub"])
    d_table(doc, ["Paramètre", "Développement XAMPP", "Exigence Production", "Risque prévenu"], ENV_HARDENING, [3.3, 3.6, 4.9, 6.4], font_size=7.9, pad_v=34)
    d_para(doc, REPORT_TEXT["p9_conc"], bold_prefix=REPORT_TEXT["p9_conc_lead"], space_after=2)

    # ---- PAGE 10 : ANNEXES & BIBLIOGRAPHIE ----
    d_heading(doc, REPORT_TEXT["p10_title"], page_break=True)
    d_sub(doc, REPORT_TEXT["p10_sub1"])
    d_table(doc, ["Menace OWASP", "Pratique Vulnérable", "Mécanisme Laravel", "Effet / Statut"], OWASP_MATRIX, [4.0, 4.7, 5.8, 3.7], font_size=7.8, pad_v=32)
    d_sub(doc, REPORT_TEXT["p10_sub2"])
    d_table(doc, ["Méthode de Test", "Atelier vérifié", "Assertions validées"], TEST_CASES, [6.4, 3.4, 8.4], font_size=7.8, pad_v=32)
    d_sub(doc, REPORT_TEXT["p10_sub3"])
    for auth, title, url in BIBLIOGRAPHY:
        d_bullet(doc, auth, title, url=url, font_size=7.9, space_after=2.0)

    out_docx = OFFICE_DIR / "Rapport_Securite_Laravel_Groupe5.docx"
    doc.save(str(out_docx))
    print("Saved unified 10-page master DOCX:", out_docx)
    return out_docx


# ==============================================================================
# PARTIE 2 : RAPPORT WEB INTERACTIF (rapport.html) — CONTENU 100 % ALIGNÉ
# ==============================================================================

def build_web_report_html() -> Path:
    ci_u = img_uri(LOGO_CI)
    gl_u = img_uri(LOGO_GL)
    ut_u = img_uri(LOGO_UT)
    d7_u = img_uri(DIAG_7)
    db_u = img_uri(DIAG_BDD)
    sd_u = img_uri(SCR_DASH)
    ss_u = img_uri(SCR_SQLI)
    sa_u = img_uri(SCR_ACCESS)

    def html_table(headers, rows):
        ths = "".join(f"<th>{esc(h)}</th>" for h in headers)
        trs = []
        for r in rows:
            tds = "".join(f"<td>{'<strong>'+esc(c)+'</strong>' if i == 0 else esc(c)}</td>" for i, c in enumerate(r))
            trs.append(f"<tr>{tds}</tr>")
        return f'<table class="report-table"><thead><tr>{ths}</tr></thead><tbody>{"".join(trs)}</tbody></table>'

    def html_cmp(vt, vc, vn, st, sc, sn):
        return f"""
        <div class="compare-grid">
          <div class="box-vuln">
            <div class="box-title">{esc(vt)}</div>
            <pre><code>{esc(vc)}</code></pre>
            <p class="box-note">{esc(vn)}</p>
          </div>
          <div class="box-sec">
            <div class="box-title">{esc(st)}</div>
            <pre><code>{esc(sc)}</code></pre>
            <p class="box-note">{esc(sn)}</p>
          </div>
        </div>"""

    def html_bullets(items):
        lis = "".join(f"<li><strong>{esc(lead)} :</strong> {esc(txt)}</li>" for lead, txt in items)
        return f"<ul>{lis}</ul>"

    bib_items = "".join(
        f'<li><strong>{esc(a)} :</strong> {esc(t)} <a href="{esc(u)}" target="_blank">{esc(u)}</a></li>'
        for a, t, u in BIBLIOGRAPHY
    )
    authors_li = "".join(f"<li>{esc(nm)}</li>" for nm in COVER_DATA["authors"])

    content = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rapport Académique — La Sécurité dans une Application Laravel (Groupe 5 - UT LOKO)</title>
<style>
  :root {
    --loko-red: #8B1518;
    --loko-gold: #D97706;
    --slate-900: #0F172A;
    --slate-800: #1E293B;
    --slate-700: #334155;
    --slate-600: #475569;
    --vuln-red: #DC2626;
    --vuln-bg: #FEF2F2;
    --sec-green: #059669;
    --sec-bg: #ECFDF5;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', Arial, sans-serif; color: var(--slate-900); background: #E2E8F0; line-height: 1.48; font-size: 13px; }
  .toolbar { position: sticky; top: 0; z-index: 100; background: #FFFFFF; color: var(--slate-900); padding: 10px 28px; display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid var(--loko-red); }
  .toolbar .btn { background: var(--loko-red); color: #FFF; border: none; padding: 7px 15px; border-radius: 6px; font-weight: 700; cursor: pointer; text-decoration: none; font-size: 13px; }
  .document-container { max-width: 900px; margin: 20px auto; display: flex; flex-direction: column; gap: 18px; }
  .page { background: #FFFFFF; padding: 30px 40px; border-radius: 6px; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.10); page-break-after: always; }
  .page:last-child { page-break-after: auto; }
  .cover-page { padding: 0; overflow: hidden; min-height: 1020px; display: flex; flex-direction: column; }
  .cover-top-logos { display: flex; align-items: center; justify-content: space-between; padding: 18px 34px; border-bottom: 2px solid #E2E8F0; }
  .cover-ministry { text-align: center; font-size: 13.5px; font-weight: 700; color: var(--slate-800); }
  .cover-split { flex: 1; display: grid; grid-template-columns: 300px 1fr; border: 2px solid var(--loko-red); margin: 16px 26px 24px; }
  .cover-col-left { background: #FFF; padding: 34px 24px; display: flex; flex-direction: column; justify-content: space-between; border-right: 4px solid var(--loko-gold); }
  .ut-emblem { text-align: center; padding: 12px; }
  .left-meta { display: flex; flex-direction: column; gap: 16px; font-size: 13px; }
  .cover-col-right { background: var(--loko-red); color: #FFF; padding: 44px 36px; display: flex; flex-direction: column; justify-content: space-between; text-align: center; }
  .cover-theme-box { border-top: 2px solid rgba(255,255,255,0.35); border-bottom: 2px solid rgba(255,255,255,0.35); padding: 20px 14px; }
  .cover-theme-box .label { font-size: 14px; letter-spacing: 1.5px; font-weight: 700; color: #FDE68A; margin-bottom: 8px; }
  .cover-theme-box h1 { font-size: 27px; font-weight: 900; line-height: 1.25; }
  .cover-authors { list-style: none; display: flex; flex-direction: column; gap: 7px; font-size: 15px; font-weight: 800; margin-top: 10px; }
  h2.chap-title { font-size: 17.5px; font-weight: 900; color: var(--loko-red); border-bottom: 2px solid var(--loko-red); padding-bottom: 5px; margin-bottom: 10px; display: flex; align-items: center; justify-content: space-between; gap: 10px; }
  h2.chap-title .author-tag { font-size: 11px; color: var(--slate-600); font-weight: 700; white-space: nowrap; }
  h3 { font-size: 14px; font-weight: 800; color: var(--slate-900); margin: 10px 0 4px; }
  p { margin-bottom: 7px; text-align: justify; }
  ul, ol { padding-left: 20px; margin-bottom: 8px; }
  li { margin-bottom: 3.5px; text-align: justify; }
  .compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 8px 0; }
  .box-vuln { background: var(--vuln-bg); border: 1px solid var(--vuln-red); border-radius: 6px; padding: 9px 11px; }
  .box-sec { background: var(--sec-bg); border: 1px solid var(--sec-green); border-radius: 6px; padding: 9px 11px; }
  .box-title { font-weight: 800; font-size: 11.8px; margin-bottom: 5px; }
  .box-vuln .box-title { color: #DC2626; }
  .box-sec .box-title { color: #059669; }
  .box-note { font-size: 11.4px; color: var(--slate-700); margin-top: 5px; margin-bottom: 0; }
  pre { background: #FFFFFF; border: 1px solid #CBD5E1; color: var(--slate-900); padding: 7px 9px; border-radius: 5px; font-family: 'Cascadia Code', Consolas, monospace; font-size: 10.6px; line-height: 1.38; white-space: pre-wrap; }
  table.report-table { width: 100%; border-collapse: collapse; margin: 8px 0; font-size: 11.6px; }
  table.report-table th { background: var(--loko-red); color: #FFF; text-align: left; padding: 6px 8px; font-weight: 700; }
  table.report-table td { padding: 5.5px 8px; border: 1px solid #CBD5E1; vertical-align: top; }
  table.report-table tr:nth-child(even) td { background: #F8FAFC; }
  .callout-info { background: #EFF6FF; border: 1px solid #2563EB; padding: 8px 12px; border-radius: 6px; margin: 8px 0; font-size: 12px; }
  .callout-warn { background: #FEF3C7; border: 1px solid #D97706; padding: 8px 12px; border-radius: 6px; margin: 8px 0; font-size: 12px; }
  .callout-sec { background: #ECFDF5; border: 1px solid #059669; padding: 8px 12px; border-radius: 6px; margin: 8px 0; font-size: 12px; }
  figure { margin: 8px 0; text-align: center; }
  figure img { max-width: 100%; height: auto; border: 1px solid #CBD5E1; border-radius: 5px; }
  figcaption { font-size: 11.2px; color: var(--slate-600); font-style: italic; margin-top: 3px; }
  .page-foot { margin-top: 10px; padding-top: 5px; border-top: 1px solid var(--loko-red); display: flex; justify-content: space-between; font-size: 10.5px; color: var(--slate-600); }
  @page { size: A4; margin: 5.5mm 6mm; }
  @media print {
    body { background: #FFF; font-size: 11.0px; line-height: 1.38; }
    .toolbar { display: none !important; }
    .document-container { max-width: 100%; margin: 0; gap: 0; }
    .page { box-shadow: none; border-radius: 0; padding: 6mm 8mm; page-break-after: always; }
    .cover-page { padding: 0; min-height: 274mm; }
    h2.chap-title { font-size: 15.5px; margin-bottom: 7px; padding-bottom: 4px; }
    h3 { font-size: 12.6px; margin: 7px 0 3px; }
    p { margin-bottom: 5px; }
    ul, ol { margin-bottom: 5px; }
    li { margin-bottom: 2px; }
    table.report-table { font-size: 10.2px; margin: 5px 0; }
    table.report-table th { padding: 4px 6px; }
    table.report-table td { padding: 3.5px 6px; }
    figure { margin: 5px 0; }
    .page-foot { margin-top: 6px; }
  }
</style>
</head>
<body>
<div class="toolbar">
  <div><strong>📘 Dossier Académique Complet (10 Pages) — Groupe 5 (UT LOKO • Licence 3)</strong></div>
  <div style="display:flex; gap:10px;">
    <a href="slides.html" class="btn" style="background:#334155;">🖥️ Ouvrir les Slides</a>
    <button class="btn" onclick="window.print()">🖨️ Imprimer / Enregistrer PDF</button>
  </div>
</div>

<div class="document-container">
  <!-- PAGE 1 -->
  <section class="page cover-page">
    <div class="cover-top-logos">
      <img src="__CI_U__" alt="Côte d'Ivoire" style="height:58px; object-fit:contain;">
      <div class="cover-ministry">Ministère de l'Enseignement Supérieur<br>et de la Recherche Scientifique</div>
      <img src="__GL_U__" alt="Groupe LOKO" style="height:58px; object-fit:contain;">
    </div>
    <div class="cover-split">
      <div class="cover-col-left">
        <div class="ut-emblem"><img src="__UT_U__" alt="UT LOKO" style="max-width:195px; max-height:140px; object-fit:contain;"></div>
        <div class="left-meta">
          <div><strong>DÉPARTEMENT :</strong> __COV_DEPT__</div>
          <div><strong>DOMAINE :</strong><br>__COV_DOMAIN__</div>
          <div><strong>MENTION :</strong><br>__COV_MENTION__</div>
          <div style="color:#8B1518;"><strong>NIVEAU :</strong><br>__COV_LEVEL__</div>
        </div>
      </div>
      <div class="cover-col-right">
        <div>
          <div style="font-size:15.5px; font-weight:700;">__COV_YEAR__</div>
          <div style="font-size:15px; font-weight:700; margin-top:14px;">__COV_SPEC__</div>
        </div>
        <div class="cover-theme-box">
          <div class="label">__COV_THEME_LBL__</div>
          <h1>__COV_THEME_TTL__</h1>
        </div>
        <div>
          <div style="font-size:14.5px; font-weight:700; color:#FDE68A; text-decoration:underline;">TRAVAIL RÉALISÉ PAR (GROUPE 5) :</div>
          <ul class="cover-authors">__AUTHORS_LI__</ul>
        </div>
        <div>
          <div style="font-size:14.5px; font-weight:700; color:#FDE68A;">PROFESSEUR :</div>
          <div style="font-size:20px; font-weight:900; color:#FFF; margin-top:3px;">__COV_PROF__</div>
        </div>
      </div>
    </div>
  </section>

  <!-- PAGE 2 -->
  <section class="page">
    <h2 class="chap-title"><span>__P2_TITLE__</span><span class="author-tag">Groupe 5 • Licence 3</span></h2>
    <p>__P2_INTRO__</p>
    __TBL_TOC__
    <h3>__P2_SUB__</h3>
    __TBL_CONTRIB__
    <div class="callout-info"><strong>__P2_CT__ :</strong> __P2_CB__</div>
    <div class="page-foot"><span>Module : Base de Données (XAMPP / MariaDB) &amp; Framework Laravel | Prof. M. CAMARA</span><span>Page 2 / 10</span></div>
  </section>

  <!-- PAGE 3 -->
  <section class="page">
    <h2 class="chap-title"><span>__P3_TITLE__</span><span class="author-tag">— __P3_AUTH__</span></h2>
    <p>__P3_INTRO__</p>
    <h3>__P3_SUB__</h3>
    <p>__P3_SUB_INTRO__</p>
    __P3_LAYERS__
    <figure><img src="__D7_U__" alt="Architecture 7 couches Laravel" style="max-height:245px;"><figcaption>__P3_FIG__</figcaption></figure>
    <div class="page-foot"><span>Module : Base de Données (XAMPP / MariaDB) &amp; Framework Laravel | Prof. M. CAMARA</span><span>Page 3 / 10</span></div>
  </section>

  <!-- PAGE 4 -->
  <section class="page">
    <h2 class="chap-title"><span>__P4_TITLE__</span><span class="author-tag">— __P4_AUTH__</span></h2>
    <h3>__P4_SUB1__</h3>
    <p>__P4_P1__</p>
    <h3>__P4_SUB2__</h3>
    <p>__P4_P2__</p>
    __CMP_SQLI__
    <div class="callout-warn"><strong>__P4_CT__ :</strong> __P4_CB__</div>
    <figure><img src="__SS_U__" alt="Capture Annuaire UT LOKO" style="max-height:335px;"><figcaption>__P4_FIG__</figcaption></figure>
    <div class="page-foot"><span>Module : Base de Données (XAMPP / MariaDB) &amp; Framework Laravel | Prof. M. CAMARA</span><span>Page 4 / 10</span></div>
  </section>

  <!-- PAGE 5 -->
  <section class="page">
    <h2 class="chap-title"><span>__P5_TITLE__</span><span class="author-tag">— __P5_AUTH__</span></h2>
    <h3>__P5_SUB1__</h3>
    <p>__P5_P1__</p>
    <h3>__P5_SUB2__</h3>
    __P5_BULLETS__
    <h3>__P5_SUB3__</h3>
    __CMP_MA__
    <div class="callout-sec"><strong>__P5_CT__ :</strong> __P5_CB__</div>
    <div class="page-foot"><span>Module : Base de Données (XAMPP / MariaDB) &amp; Framework Laravel | Prof. M. CAMARA</span><span>Page 5 / 10</span></div>
  </section>

  <!-- PAGE 6 -->
  <section class="page">
    <h2 class="chap-title"><span>__P6_TITLE__</span><span class="author-tag">— __P6_AUTH__</span></h2>
    <h3>__P6_SUB1__</h3>
    <p>__P6_P1__</p>
    <h3>__P6_SUB2__</h3>
    <p>__P6_P2__</p>
    __CMP_XSS__
    <h3>__P6_SUB3__</h3>
    __P6_BULLETS__
    <div class="page-foot"><span>Module : Base de Données (XAMPP / MariaDB) &amp; Framework Laravel | Prof. M. CAMARA</span><span>Page 6 / 10</span></div>
  </section>

  <!-- PAGE 7 -->
  <section class="page">
    <h2 class="chap-title"><span>__P7_TITLE__</span><span class="author-tag">— __P7_AUTH__</span></h2>
    <h3>__P7_SUB1__</h3>
    <p>__P7_P1__</p>
    <h3>__P7_SUB2__</h3>
    <p>__P7_P2__</p>
    __CMP_CSRF__
    __P7_BULLETS__
    <div class="page-foot"><span>Module : Base de Données (XAMPP / MariaDB) &amp; Framework Laravel | Prof. M. CAMARA</span><span>Page 7 / 10</span></div>
  </section>

  <!-- PAGE 8 -->
  <section class="page">
    <h2 class="chap-title"><span>__P8_TITLE__</span><span class="author-tag">— __P8_AUTH__</span></h2>
    <h3>__P8_SUB1__</h3>
    <p>__P8_P1__</p>
    <h3>__P8_SUB2__</h3>
    <p>__P8_P2__</p>
    <h3>__P8_SUB3__</h3>
    <p>__P8_P3__</p>
    <figure><img src="__SA_U__" alt="Capture IDOR Portail UT LOKO" style="max-height:345px;"><figcaption>__P8_FIG__</figcaption></figure>
    <div class="page-foot"><span>Module : Base de Données (XAMPP / MariaDB) &amp; Framework Laravel | Prof. M. CAMARA</span><span>Page 8 / 10</span></div>
  </section>

  <!-- PAGE 9 -->
  <section class="page">
    <h2 class="chap-title"><span>__P9_TITLE__</span><span class="author-tag">— __P9_AUTH__</span></h2>
    <p>__P9_P1__</p>
    <figure><img src="__DB_U__" alt="Schéma BDD MariaDB" style="max-height:168px;"><figcaption>__P9_FIG1__</figcaption></figure>
    <figure><img src="__SD_U__" alt="Portail Académique UT LOKO" style="max-height:175px;"><figcaption>__P9_FIG2__</figcaption></figure>
    <h3>__P9_SUB__</h3>
    __TBL_ENV__
    <p><strong>__P9_CONC_LEAD__</strong>__P9_CONC__</p>
    <div class="page-foot"><span>Module : Base de Données (XAMPP / MariaDB) &amp; Framework Laravel | Prof. M. CAMARA</span><span>Page 9 / 10</span></div>
  </section>

  <!-- PAGE 10 -->
  <section class="page">
    <h2 class="chap-title"><span>__P10_TITLE__</span><span class="author-tag">Groupe 5 (Collectif)</span></h2>
    <h3>__P10_SUB1__</h3>
    __TBL_OWASP__
    <h3>__P10_SUB2__</h3>
    __TBL_TESTS__
    <h3>__P10_SUB3__</h3>
    <ol style="font-size:10.0px; line-height:1.28;">__BIB__</ol>
    <div class="page-foot"><span>Module : Base de Données (XAMPP / MariaDB) &amp; Framework Laravel | Prof. M. CAMARA</span><span>Page 10 / 10</span></div>
  </section>
</div>
</body>
</html>"""

    replacements = {
        "__CI_U__": ci_u,
        "__GL_U__": gl_u,
        "__UT_U__": ut_u,
        "__D7_U__": d7_u,
        "__DB_U__": db_u,
        "__SD_U__": sd_u,
        "__SS_U__": ss_u,
        "__SA_U__": sa_u,
        "__COV_DEPT__": esc(COVER_DATA["dept"]),
        "__COV_DOMAIN__": esc(COVER_DATA["domain"]),
        "__COV_MENTION__": esc(COVER_DATA["mention"]),
        "__COV_LEVEL__": esc(COVER_DATA["level"]),
        "__COV_YEAR__": esc(COVER_DATA["year"]),
        "__COV_SPEC__": esc(COVER_DATA["specialty"]),
        "__COV_THEME_LBL__": esc(COVER_DATA["theme_label"]),
        "__COV_THEME_TTL__": esc(COVER_DATA["theme_title"]),
        "__COV_PROF__": esc(COVER_DATA["professor"]),
        "__AUTHORS_LI__": authors_li,
        "__P2_TITLE__": esc(REPORT_TEXT["p2_title"]),
        "__P2_INTRO__": esc(REPORT_TEXT["p2_intro"]),
        "__P2_SUB__": esc(REPORT_TEXT["p2_sub"]),
        "__P2_CT__": esc(REPORT_TEXT["p2_callout_t"]),
        "__P2_CB__": esc(REPORT_TEXT["p2_callout_b"]),
        "__TBL_TOC__": html_table(["Repère", "Intitulé du Chapitre / Section", "Auteur Référent"], TOC_ROWS),
        "__TBL_CONTRIB__": html_table(["Membre du Groupe 5", "Chapitre(s)", "Périmètre technique couvert"], CONTRIBUTIONS_ROWS),
        "__P3_TITLE__": esc(REPORT_TEXT["p3_title"]),
        "__P3_AUTH__": esc(REPORT_TEXT["p3_author"]),
        "__P3_INTRO__": esc(REPORT_TEXT["p3_intro"]),
        "__P3_SUB__": esc(REPORT_TEXT["p3_sub"]),
        "__P3_SUB_INTRO__": esc(REPORT_TEXT["p3_sub_intro"]),
        "__P3_LAYERS__": html_bullets(REPORT_TEXT["p3_layers"]),
        "__P3_FIG__": esc(REPORT_TEXT["p3_fig"]),
        "__P4_TITLE__": esc(REPORT_TEXT["p4_title"]),
        "__P4_AUTH__": esc(REPORT_TEXT["p4_author"]),
        "__P4_SUB1__": esc(REPORT_TEXT["p4_sub1"]),
        "__P4_P1__": esc(REPORT_TEXT["p4_p1"]),
        "__P4_SUB2__": esc(REPORT_TEXT["p4_sub2"]),
        "__P4_P2__": esc(REPORT_TEXT["p4_p2"]),
        "__CMP_SQLI__": html_cmp(*REPORT_TEXT["p4_cmp"]),
        "__P4_CT__": esc(REPORT_TEXT["p4_callout_t"]),
        "__P4_CB__": esc(REPORT_TEXT["p4_callout_b"]),
        "__P4_FIG__": esc(REPORT_TEXT["p4_fig"]),
        "__P5_TITLE__": esc(REPORT_TEXT["p5_title"]),
        "__P5_AUTH__": esc(REPORT_TEXT["p5_author"]),
        "__P5_SUB1__": esc(REPORT_TEXT["p5_sub1"]),
        "__P5_P1__": esc(REPORT_TEXT["p5_p1"]),
        "__P5_SUB2__": esc(REPORT_TEXT["p5_sub2"]),
        "__P5_BULLETS__": html_bullets(REPORT_TEXT["p5_bullets"]),
        "__P5_SUB3__": esc(REPORT_TEXT["p5_sub3"]),
        "__CMP_MA__": html_cmp(*REPORT_TEXT["p5_cmp"]),
        "__P5_CT__": esc(REPORT_TEXT["p5_callout_t"]),
        "__P5_CB__": esc(REPORT_TEXT["p5_callout_b"]),
        "__P6_TITLE__": esc(REPORT_TEXT["p6_title"]),
        "__P6_AUTH__": esc(REPORT_TEXT["p6_author"]),
        "__P6_SUB1__": esc(REPORT_TEXT["p6_sub1"]),
        "__P6_P1__": esc(REPORT_TEXT["p6_p1"]),
        "__P6_SUB2__": esc(REPORT_TEXT["p6_sub2"]),
        "__P6_P2__": esc(REPORT_TEXT["p6_p2"]),
        "__CMP_XSS__": html_cmp(*REPORT_TEXT["p6_cmp"]),
        "__P6_SUB3__": esc(REPORT_TEXT["p6_sub3"]),
        "__P6_BULLETS__": html_bullets(REPORT_TEXT["p6_bullets"]),
        "__P7_TITLE__": esc(REPORT_TEXT["p7_title"]),
        "__P7_AUTH__": esc(REPORT_TEXT["p7_author"]),
        "__P7_SUB1__": esc(REPORT_TEXT["p7_sub1"]),
        "__P7_P1__": esc(REPORT_TEXT["p7_p1"]),
        "__P7_SUB2__": esc(REPORT_TEXT["p7_sub2"]),
        "__P7_P2__": esc(REPORT_TEXT["p7_p2"]),
        "__CMP_CSRF__": html_cmp(*REPORT_TEXT["p7_cmp"]),
        "__P7_BULLETS__": html_bullets(REPORT_TEXT["p7_bullets"]),
        "__P8_TITLE__": esc(REPORT_TEXT["p8_title"]),
        "__P8_AUTH__": esc(REPORT_TEXT["p8_author"]),
        "__P8_SUB1__": esc(REPORT_TEXT["p8_sub1"]),
        "__P8_P1__": esc(REPORT_TEXT["p8_p1"]),
        "__P8_SUB2__": esc(REPORT_TEXT["p8_sub2"]),
        "__P8_P2__": esc(REPORT_TEXT["p8_p2"]),
        "__P8_SUB3__": esc(REPORT_TEXT["p8_sub3"]),
        "__P8_P3__": esc(REPORT_TEXT["p8_p3"]),
        "__P8_FIG__": esc(REPORT_TEXT["p8_fig"]),
        "__P9_TITLE__": esc(REPORT_TEXT["p9_title"]),
        "__P9_AUTH__": esc(REPORT_TEXT["p9_author"]),
        "__P9_P1__": esc(REPORT_TEXT["p9_p1"]),
        "__P9_FIG1__": esc(REPORT_TEXT["p9_fig1"]),
        "__P9_FIG2__": esc(REPORT_TEXT["p9_fig2"]),
        "__P9_SUB__": esc(REPORT_TEXT["p9_sub"]),
        "__TBL_ENV__": html_table(["Paramètre", "Développement XAMPP", "Exigence Production", "Risque prévenu"], ENV_HARDENING),
        "__P9_CONC_LEAD__": esc(REPORT_TEXT["p9_conc_lead"]),
        "__P9_CONC__": esc(REPORT_TEXT["p9_conc"]),
        "__P10_TITLE__": esc(REPORT_TEXT["p10_title"]),
        "__P10_SUB1__": esc(REPORT_TEXT["p10_sub1"]),
        "__TBL_OWASP__": html_table(["Menace OWASP", "Pratique Vulnérable", "Mécanisme Laravel", "Effet / Statut"], OWASP_MATRIX),
        "__P10_SUB2__": esc(REPORT_TEXT["p10_sub2"]),
        "__TBL_TESTS__": html_table(["Méthode de Test", "Atelier vérifié", "Assertions validées"], TEST_CASES),
        "__P10_SUB3__": esc(REPORT_TEXT["p10_sub3"]),
        "__BIB__": bib_items,
    }
    for k, v in replacements.items():
        content = content.replace(k, v)

    out_html = WEB_DIR / "rapport.html"
    out_html.write_text(content, encoding="utf-8")
    print("Saved unified 10-page HTML report:", out_html)
    return out_html


def generate_all_reports():
    OFFICE_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    build_docx_report()
    build_web_report_html()


if __name__ == "__main__":
    generate_all_reports()
