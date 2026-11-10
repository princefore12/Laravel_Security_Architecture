"""
Génère les deux schémas techniques haute résolution pour le rapport académique du Groupe 5 :
  1. scripts/assets/diagram_7_couches.png : Architecture de défense en profondeur (7 couches)
  2. scripts/assets/diagram_bdd_loko.png : Schéma relationnel MariaDB XAMPP (loko_security_lab)
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)


def load_font(size: int, bold: bool = False, mono: bool = False):
    candidates = []
    if mono:
        candidates = ["C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf"]
    elif bold:
        candidates = ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]
    else:
        candidates = ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def draw_rounded_box(draw, xy, radius, fill, outline=None, width=3):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def build_7_layers_diagram():
    W, H = 2400, 920
    img = Image.new("RGB", (W, H), "#F8FAFC")
    d = ImageDraw.Draw(img)

    f_title = load_font(40, bold=True)
    f_sub = load_font(23, bold=False)
    f_card_num = load_font(20, bold=True)
    f_card_title = load_font(22, bold=True)
    f_card_body = load_font(18, bold=False)
    f_badge = load_font(19, bold=True)

    # Header bar
    d.rectangle([0, 0, W, 130], fill="#8B1518")
    d.rectangle([0, 126, W, 134], fill="#F59E0B")
    d.text((55, 24), "Architecture de Défense en Profondeur — Laravel 13 & MariaDB (XAMPP)", font=f_title, fill="#FFFFFF")
    d.text((55, 78), "Parcours sécurisé d'une requête HTTP entrante jusqu'au moteur de base de données loko_security_lab", font=f_sub, fill="#FDE68A")

    # Left Actor: Client / Attacker
    draw_rounded_box(d, [40, 210, 305, 780], 22, fill="#0F172A", outline="#38BDF8", width=4)
    d.text((66, 245), "NAVIGATEUR", font=f_card_title, fill="#38BDF8")
    d.text((66, 282), "Client HTTP(S)", font=f_card_body, fill="#E2E8F0")
    draw_rounded_box(d, [60, 345, 285, 455], 14, fill="#1E293B", outline="#64748B", width=2)
    d.text((76, 368), "Requêtes légitimes\n(GET / POST / Form)", font=f_card_body, fill="#A7F3D0")
    draw_rounded_box(d, [60, 495, 285, 710], 14, fill="#450A0A", outline="#EF4444", width=2)
    d.text((76, 518), "Menaces ciblées :\n• SQL Injection\n• Mass Assignment\n• XSS / CSRF\n• IDOR / Brute-Force", font=f_card_body, fill="#FECACA")

    # Arrow from Browser to Pipeline
    d.line([305, 495, 348, 495], fill="#8B1518", width=6)
    d.polygon([(348, 480), (372, 495), (348, 510)], fill="#8B1518")

    # 7 Layers
    layers = [
        ("COUCHE 1", "RateLimiter", "Max 5 essais / min\nAnti Brute-Force\n& Anti-DoS", "HTTP 429", "#DC2626"),
        ("COUCHE 2", "Middleware CSRF", "Jeton secret @csrf\nhash_equals()\nCookie SameSite", "HTTP 419", "#D97706"),
        ("COUCHE 3", "Auth & Session", "Identité vérifiée\nCookies HttpOnly\nHachage bcrypt", "HTTP 401", "#0284C7"),
        ("COUCHE 4", "Policies / Gates", "GradePolicy::view()\nPropriété ressource\nPrévention IDOR", "HTTP 403", "#7C3AED"),
        ("COUCHE 5", "FormRequest", "Règles strictes\nvalidated() uniquement\nFiltrage champs", "HTTP 422", "#DB2777"),
        ("COUCHE 6", "Eloquent & PDO", "Attribut #[Fillable]\nRequêtes préparées\nMarqueurs SQL (?)", "PDO Bind", "#059669"),
        ("COUCHE 7", "Blade & CSP", "Échappement {{ }}\nhtmlspecialchars()\nCSP & X-Frame DENY", "Anti-XSS", "#0D9488"),
    ]

    start_x = 378
    card_w = 224
    gap = 16
    for idx, (num, title, desc, http_tag, col) in enumerate(layers):
        x0 = start_x + idx * (card_w + gap)
        x1 = x0 + card_w
        y0, y1 = 200, 790
        draw_rounded_box(d, [x0, y0, x1, y1], 18, fill="#FFFFFF", outline=col, width=4)
        draw_rounded_box(d, [x0, y0, x1, y0 + 58], 14, fill=col)
        d.text((x0 + 16, y0 + 16), num, font=f_card_num, fill="#FFFFFF")
        d.text((x0 + 14, y0 + 78), title, font=f_card_title, fill="#0F172A")
        d.line([x0 + 14, y0 + 118, x1 - 14, y0 + 118], fill="#E2E8F0", width=2)
        d.text((x0 + 14, y0 + 140), desc, font=f_card_body, fill="#334155")

        # Status badge at bottom
        draw_rounded_box(d, [x0 + 20, y1 - 72, x1 - 20, y1 - 22], 12, fill="#0F172A", outline=col, width=2)
        d.text((x0 + 54, y1 - 58), http_tag, font=f_badge, fill="#FDE68A")

        if idx < len(layers) - 1:
            ax = x1
            d.line([ax, 495, ax + gap, 495], fill="#475569", width=5)

    # Arrow to MariaDB
    last_x = start_x + 7 * card_w + 6 * gap
    d.line([last_x, 495, last_x + 26, 495], fill="#059669", width=6)
    d.polygon([(last_x + 26, 480), (last_x + 48, 495), (last_x + 26, 510)], fill="#059669")

    # Right Node: MariaDB XAMPP
    mx0, mx1 = last_x + 52, W - 36
    draw_rounded_box(d, [mx0, 210, mx1, 780], 22, fill="#064E3B", outline="#10B981", width=4)
    d.text((mx0 + 22, 245), "MARIADB", font=f_card_title, fill="#6EE7B7")
    d.text((mx0 + 22, 282), "XAMPP :3306", font=f_badge, fill="#FDE68A")
    d.text((mx0 + 22, 345), "Base :\nloko_security_lab\n\nTables :\n• users\n• students\n• grades\n• security_logs\n\nCompte prod :\nMoindre privilège", font=f_card_body, fill="#ECFDF5")

    d.text((55, 862), "UT LOKO • Licence 3 Informatique • Groupe 5 — Schéma d'architecture de sécurité multicouche", font=f_sub, fill="#475569")

    out = ASSETS / "diagram_7_couches.png"
    img.save(str(out), dpi=(300, 300))
    print("Saved:", out)


def build_db_schema_diagram():
    W, H = 2250, 1180
    img = Image.new("RGB", (W, H), "#F8FAFC")
    d = ImageDraw.Draw(img)

    f_title = load_font(40, bold=True)
    f_sub = load_font(24, bold=False)
    f_tbl_hdr = load_font(26, bold=True)
    f_col = load_font(20, bold=False, mono=True)
    f_col_b = load_font(20, bold=True, mono=True)
    f_fk = load_font(20, bold=True)

    d.rectangle([0, 0, W, 130], fill="#0F172A")
    d.rectangle([0, 126, W, 134], fill="#8B1518")
    d.text((55, 24), "Schéma Relationnel MariaDB (XAMPP) — Base : loko_security_lab", font=f_title, fill="#FFFFFF")
    d.text((55, 78), "Contraintes d'intégrité InnoDB, clés étrangères (ON DELETE CASCADE) et journalisation d'audit", font=f_sub, fill="#FDE68A")

    def draw_table(x, y, w, h, name, subtitle, cols, hdr_col="#8B1518", type_offset=295):
        draw_rounded_box(d, [x, y, x + w, y + h], 16, fill="#FFFFFF", outline=hdr_col, width=4)
        draw_rounded_box(d, [x, y, x + w, y + 78], 12, fill=hdr_col)
        d.text((x + 20, y + 12), name, font=f_tbl_hdr, fill="#FFFFFF")
        d.text((x + 20, y + 46), subtitle, font=load_font(18), fill="#FDE68A")
        cy = y + 96
        for tag, cname, ctype in cols:
            if tag == "PK":
                draw_rounded_box(d, [x + 16, cy, x + 64, cy + 28], 6, fill="#FEF3C7", outline="#D97706", width=2)
                d.text((x + 24, cy + 2), "PK", font=load_font(17, bold=True), fill="#92400E")
            elif tag == "FK":
                draw_rounded_box(d, [x + 16, cy, x + 64, cy + 28], 6, fill="#DBEAFE", outline="#2563EB", width=2)
                d.text((x + 24, cy + 2), "FK", font=load_font(17, bold=True), fill="#1E40AF")
            elif tag == "SEC":
                draw_rounded_box(d, [x + 16, cy, x + 64, cy + 28], 6, fill="#D1FAE5", outline="#059669", width=2)
                d.text((x + 19, cy + 2), "SEC", font=load_font(16, bold=True), fill="#065F46")
            d.text((x + 76, cy), cname, font=f_col_b if tag else f_col, fill="#0F172A")
            d.text((x + type_offset, cy), ctype, font=f_col, fill="#475569")
            cy += 42

    draw_table(60, 190, 640, 410, "users", "Comptes & Rôles (Eloquent #[Fillable])", [
        ("PK", "id", "BIGINT UNSIGNED AI"),
        ("", "name", "VARCHAR(255)"),
        ("SEC", "email", "VARCHAR(255) UNIQUE"),
        ("SEC", "password", "VARCHAR(255) bcrypt"),
        ("SEC", "role", "VARCHAR(30) 'student'"),
        ("", "remember_token", "VARCHAR(100) NULL"),
        ("", "timestamps", "CREATED / UPDATED_AT"),
    ], hdr_col="#8B1518", type_offset=295)

    draw_table(820, 190, 660, 445, "students", "Dossiers Étudiants L3 UT LOKO (XSS / SQLi)", [
        ("PK", "id", "BIGINT UNSIGNED AI"),
        ("FK", "user_id", "BIGINT -> users.id"),
        ("SEC", "matricule", "VARCHAR(32) UNIQUE"),
        ("", "full_name", "VARCHAR(120)"),
        ("", "filiere", "VARCHAR(120)"),
        ("", "moyenne", "DECIMAL(4,2)"),
        ("SEC", "bio", "TEXT (Cible XSS Blade)"),
        ("", "timestamps", "CREATED / UPDATED_AT"),
    ], hdr_col="#0284C7", type_offset=295)

    draw_table(1585, 190, 605, 405, "grades", "Relevés & Notes (IDOR Policy / CSRF)", [
        ("PK", "id", "BIGINT UNSIGNED AI"),
        ("FK", "student_id", "BIGINT -> students.id"),
        ("", "course_code", "VARCHAR(24)"),
        ("", "course_name", "VARCHAR(140)"),
        ("SEC", "score", "DECIMAL(4,2) (CSRF)"),
        ("", "jury_remark", "VARCHAR(160)"),
        ("", "timestamps", "CREATED / UPDATED_AT"),
    ], hdr_col="#059669", type_offset=275)

    draw_table(60, 680, 1420, 410, "security_logs", "Journal d'Audit Temps Réel (Inspecteur SqlInspectorService::capture)", [
        ("PK", "id", "BIGINT UNSIGNED AI"),
        ("", "pillar", "VARCHAR(60)  -- 1. SQLi | 2. Mass Assignment | 3. XSS | 4. CSRF | 5. IDOR"),
        ("SEC", "mode", "VARCHAR(20)  -- 'vulnerable' | 'secure'"),
        ("", "actor", "VARCHAR(100) -- Intervenant ou utilisateur actif"),
        ("", "payload", "TEXT NULL    -- Charge d'attaque injectée ou action"),
        ("SEC", "executed_sql", "TEXT NULL    -- Requête SQL réelle exécutée par MariaDB XAMPP"),
        ("SEC", "outcome", "VARCHAR(40)  -- 'exploited' | 'blocked' | 'info'"),
    ], hdr_col="#1E293B", type_offset=275)

    draw_rounded_box(d, [1585, 680, 2190, 1090], 16, fill="#FEF2F2", outline="#8B1518", width=3)
    d.text((1615, 706), "Mécanismes d'Intégrité BDD", font=f_tbl_hdr, fill="#8B1518")
    notes_bdd = (
        "• Clés étrangères FK avec\n"
        "  ON DELETE CASCADE (InnoDB).\n\n"
        "• Colonne users.role absente de\n"
        "  #[Fillable] -> Anti-escalade.\n\n"
        "• users.password haché en\n"
        "  bcrypt (BCRYPT_ROUNDS=12).\n\n"
        "• En production : compte dédié\n"
        "  GRANT SELECT,INSERT,UPDATE,\n"
        "  DELETE (jamais root XAMPP)."
    )
    d.text((1615, 760), notes_bdd, font=load_font(21), fill="#1E293B")

    # Relations arrows
    d.line([700, 290, 820, 290], fill="#2563EB", width=5)
    d.polygon([(802, 278), (820, 290), (802, 302)], fill="#2563EB")
    d.text((725, 255), "1 : 1", font=f_fk, fill="#1E40AF")

    d.line([1480, 290, 1585, 290], fill="#059669", width=5)
    d.polygon([(1567, 278), (1585, 290), (1567, 302)], fill="#059669")
    d.text((1500, 255), "1 : N", font=f_fk, fill="#065F46")

    d.text((60, 1125), "UT LOKO • Licence 3 Informatique • Base de données MariaDB 10.11.16 (XAMPP) — Modèle physique de données", font=f_sub, fill="#475569")

    out = ASSETS / "diagram_bdd_loko.png"
    img.save(str(out), dpi=(300, 300))
    print("Saved:", out)


if __name__ == "__main__":
    build_7_layers_diagram()
    build_db_schema_diagram()
