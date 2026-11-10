"""
Générateur complet des supports d'exposé pour le Groupe 5 (UT LOKO - Licence 3)
Thème n° 12 : La sécurité dans une application Laravel
Génère :
  1. livrables/office/Expose_Securite_Laravel_Groupe5.pptx
  2. livrables/office/Rapport_Securite_Laravel_Groupe5.docx
  3. livrables/office/Rapport_Securite_Laravel_Groupe5.pdf (via Microsoft Word)
  4. Mise à jour de livrables/web-interactif/slides.html & rapport.html (avec logos officiels intégrés)
  5. livrables/web-interactif/Rapport_Web_Groupe5.pdf (via Edge headless)
"""

import base64
import os
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Inches, Pt, RGBColor as DocxRGB
from pptx import Presentation
from pptx.dml.color import RGBColor as PptRGB
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches as PptIn, Pt as PptPt

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "scripts" / "assets"
OFFICE_DIR = ROOT / "livrables" / "office"
WEB_DIR = ROOT / "livrables" / "web-interactif"

LOGO_CI = ASSETS / "logo_ci.png"
LOGO_GL = ASSETS / "logo_groupe_loko.png"
LOGO_UT = ASSETS / "logo_ut_loko.png"

# Palette UT LOKO & CyberLab
C_RED = (139, 21, 24)        # #8B1518 Bordeaux UT LOKO
C_RED_DARK = (91, 11, 13)    # #5B0B0D
C_GOLD = (245, 158, 11)      # #F59E0B Or
C_NAVY = (15, 23, 42)        # #0F172A Slate 900
C_DARK_CARD = (23, 33, 54)   # #172136
C_SLATE = (51, 65, 85)       # #334155
C_MUTED = (148, 163, 184)    # #94A3B8
C_LIGHT = (248, 250, 252)    # #F8FAFC
C_WHITE = (255, 255, 255)
C_VULN = (220, 38, 38)       # #DC2626
C_VULN_BG = (69, 10, 10)
C_SEC = (16, 185, 129)       # #10B981
C_SEC_BG = (6, 78, 59)
C_BLUE = (56, 189, 248)      # #38BDF8

MEMBERS = [
    ("01 • 00:00–04:00", "SORE RAMATOU", "Intro & Injection SQL (PDO / Eloquent)"),
    ("02 • 04:00–08:00", "SIBY MODY", "Mass Assignment & Validation FormRequest"),
    ("03 • 08:00–12:00", "BOIN NAOMI", "Faille XSS Stockée, Blade & Headers CSP"),
    ("04 • 12:00–16:00", "TRAORÉ CHARIFAT LEYLA", "Faille CSRF, Sessions & Jeton @csrf"),
    ("05 • 16:00–20:00", "DJAN KOUASSI NOËL", "Auth, Bcrypt, IDOR, RateLimit & .env"),
]


def ppt_rgb(c):
    return PptRGB(c[0], c[1], c[2])


def docx_rgb(c):
    return DocxRGB(c[0], c[1], c[2])


# ==============================================================================
# PARTIE 1 : GENERATION DU DIAPORAMA POWERPOINT (.PPTX)
# ==============================================================================

def set_slide_bg(slide, color_tuple):
    bg = slide.background
    fill = bg.fill
    fill.solid()
    fill.fore_color.rgb = ppt_rgb(color_tuple)


def add_rect(slide, left, top, width, height, fill_color, border_color=None, border_pt=1.0, rounded=False):
    shape_type = MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE
    shape = slide.shapes.add_shape(shape_type, PptIn(left), PptIn(top), PptIn(width), PptIn(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = ppt_rgb(fill_color)
    if border_color:
        shape.line.color.rgb = ppt_rgb(border_color)
        shape.line.width = PptPt(border_pt)
    else:
        shape.line.fill.background()
    if rounded:
        try:
            shape.adjustments[0] = 0.06
        except Exception:
            pass
    return shape


def add_textbox(slide, left, top, width, height, text, font_size=14, color=C_WHITE,
                bold=False, italic=False, align=PP_ALIGN.LEFT, font_name="Segoe UI",
                valign=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(PptIn(left), PptIn(top), PptIn(width), PptIn(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = valign
    tf.margin_left = PptIn(0.06)
    tf.margin_right = PptIn(0.06)
    tf.margin_top = PptIn(0.04)
    tf.margin_bottom = PptIn(0.04)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = PptPt(font_size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = ppt_rgb(color)
    return tb


def add_bullets(slide, left, top, width, height, items, font_size=13.5, color=C_NAVY, space_after=6, lead_color=C_RED):
    tb = slide.shapes.add_textbox(PptIn(left), PptIn(top), PptIn(width), PptIn(height))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = PptPt(space_after)
        if isinstance(item, tuple):
            lead, body = item
            r1 = p.add_run()
            r1.text = f"▸ {lead} : "
            r1.font.name = "Segoe UI"
            r1.font.size = PptPt(font_size)
            r1.font.bold = True
            r1.font.color.rgb = ppt_rgb(lead_color)
            r2 = p.add_run()
            r2.text = body
            r2.font.name = "Segoe UI"
            r2.font.size = PptPt(font_size)
            r2.font.color.rgb = ppt_rgb(color)
        else:
            r = p.add_run()
            r.text = f"▸ {item}"
            r.font.name = "Segoe UI"
            r.font.size = PptPt(font_size)
            r.font.color.rgb = ppt_rgb(color)
    return tb


def add_header_footer(slide, kicker, title, slide_num, total_slides, badge_text=""):
    set_slide_bg(slide, C_LIGHT)
    # Top accent bar
    add_rect(slide, 0, 0, 13.333, 0.12, C_RED)
    add_rect(slide, 0, 0.12, 13.333, 0.03, C_GOLD)

    add_textbox(slide, 0.55, 0.25, 9.2, 0.3, kicker.upper(), font_size=11, color=C_RED, bold=True)
    add_textbox(slide, 0.55, 0.52, 9.6, 0.55, title, font_size=24, color=C_NAVY, bold=True)

    if badge_text:
        add_rect(slide, 10.2, 0.38, 2.6, 0.45, C_RED, (180, 83, 9), 1.0, rounded=True)
        add_textbox(slide, 10.2, 0.41, 2.6, 0.4, badge_text, font_size=11, color=C_WHITE,
                    bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)

    # Divider
    add_rect(slide, 0.55, 1.15, 12.23, 0.02, (203, 213, 225))

    # Footer
    add_rect(slide, 0, 7.06, 13.333, 0.02, (226, 232, 240))
    add_rect(slide, 0, 7.08, 13.333, 0.42, C_WHITE)
    add_textbox(slide, 0.55, 7.12, 7.5, 0.32,
                "UT LOKO • Licence 3 Informatique • Groupe 5 — La sécurité dans une application Laravel",
                font_size=10, color=(71, 85, 105))
    add_textbox(slide, 11.4, 7.12, 1.4, 0.32, f"Slide {slide_num} / {total_slides}",
                font_size=10, color=C_RED, bold=True, align=PP_ALIGN.RIGHT)


def add_code_card(slide, left, top, width, height, header_title, code_text, caption_text, is_vuln=True):
    bg = (254, 226, 226) if is_vuln else (209, 250, 229)
    border = (220, 38, 38) if is_vuln else (5, 150, 105)
    head_fg = (153, 27, 27) if is_vuln else (6, 95, 70)
    add_rect(slide, left, top, width, height, C_WHITE, border, 1.5, rounded=True)
    add_rect(slide, left, top, width, 0.48, bg, border, 1.0, rounded=False)
    add_textbox(slide, left + 0.12, top + 0.06, width - 0.24, 0.36, header_title,
                font_size=13.5, color=head_fg, bold=True)

    # Light code area
    code_h = height - 1.35
    add_rect(slide, left + 0.14, top + 0.60, width - 0.28, code_h, (248, 250, 252), (203, 213, 225), 0.75, rounded=True)
    add_textbox(slide, left + 0.22, top + 0.68, width - 0.44, code_h - 0.14, code_text,
                font_size=11.2, color=C_NAVY, font_name="Consolas")

    add_textbox(slide, left + 0.14, top + height - 0.66, width - 0.28, 0.56, caption_text,
                font_size=11.5, color=head_fg, bold=True)


def add_notes(slide, text):
    notes_slide = slide.notes_slide
    notes_slide.notes_text_frame.text = text


def build_pptx():
    prs = Presentation()
    prs.slide_width = PptIn(13.333)
    prs.slide_height = PptIn(7.5)
    blank = prs.slide_layouts[6]
    total = 16

    # ---------------- SLIDE 1 : PAGE DE GARDE ----------------
    s1 = prs.slides.add_slide(blank)
    set_slide_bg(s1, C_WHITE)
    # Left white panel + right crimson panel matching UT LOKO cover
    add_rect(s1, 4.15, 0, 9.183, 7.5, C_RED)
    add_rect(s1, 4.10, 0, 0.08, 7.5, C_GOLD)

    # Logos on left panel
    if LOGO_CI.exists():
        s1.shapes.add_picture(str(LOGO_CI), PptIn(0.35), PptIn(0.28), width=PptIn(1.35))
    if LOGO_GL.exists():
        s1.shapes.add_picture(str(LOGO_GL), PptIn(2.65), PptIn(0.25), width=PptIn(1.05))
    if LOGO_UT.exists():
        s1.shapes.add_picture(str(LOGO_UT), PptIn(0.85), PptIn(1.35), width=PptIn(2.35))

    add_textbox(s1, 0.35, 3.85, 3.55, 0.35, "DÉPARTEMENT : ITER", font_size=11.5, color=C_NAVY, bold=True)
    add_textbox(s1, 0.35, 4.25, 3.55, 0.55, "DOMAINE :\nSCIENCE ET TECHNOLOGIE", font_size=11.5, color=C_SLATE, bold=True)
    add_textbox(s1, 0.35, 4.92, 3.55, 0.65, "MENTION :\nINFORMATIQUE & TÉLÉCOM (L3)", font_size=11.5, color=C_SLATE, bold=True)
    add_textbox(s1, 0.35, 5.70, 3.55, 0.55, "MODULE :\nBase de Données (XAMPP) & Laravel", font_size=11.5, color=C_RED, bold=True)

    add_rect(s1, 0.35, 6.45, 3.45, 0.78, (254, 242, 242), C_RED, 1.0, rounded=True)
    add_textbox(s1, 0.45, 6.50, 3.25, 0.68, "PROFESSEUR ENCADRANT :\nM. CAMARA",
                font_size=12, color=C_RED, bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)

    # Right crimson panel content
    add_rect(s1, 4.65, 0.40, 8.2, 0.42, (91, 11, 13), C_GOLD, 1.0, rounded=True)
    add_textbox(s1, 4.65, 0.43, 8.2, 0.36,
                "ANNÉE ACADÉMIQUE : 2025 – 2026  •  GROUPE 5  •  THÈME N° 12",
                font_size=11.5, color=(253, 230, 138), bold=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)

    add_textbox(s1, 4.65, 1.15, 8.2, 1.45,
                "La Sécurité dans une\nApplication Laravel",
                font_size=38, color=C_WHITE, bold=True)
    add_textbox(s1, 4.65, 2.70, 8.1, 0.75,
                "Architecture de défense multicouche, protection de la base MariaDB (XAMPP)\net démonstration en direct sur le laboratoire LOKO-Vault.",
                font_size=14.5, color=(241, 245, 249))

    add_textbox(s1, 4.65, 3.70, 8.0, 0.35, "EXPOSÉ RÉALISÉ ET PRÉSENTÉ PAR :", font_size=12, color=(253, 230, 138), bold=True)

    for idx, (slot, name, role) in enumerate(MEMBERS):
        y = 4.10 + idx * 0.56
        add_rect(s1, 4.65, y, 8.2, 0.48, (74, 10, 12), (253, 230, 138) if "SIBY" in name else (180, 60, 65), 1.0, rounded=True)
        add_textbox(s1, 4.78, y + 0.06, 2.6, 0.36, name, font_size=12.5, color=C_WHITE, bold=True)
        add_textbox(s1, 7.45, y + 0.06, 3.8, 0.36, role, font_size=11.5, color=(226, 232, 240))
        add_textbox(s1, 11.2, y + 0.06, 1.5, 0.36, slot.split("•")[1].strip(), font_size=11, color=(253, 230, 138), bold=True, align=PP_ALIGN.RIGHT)

    add_textbox(s1, 4.65, 7.05, 8.2, 0.35, "Format : 20 min d'exposé avec démonstration live XAMPP + 10 min de questions",
                font_size=11, color=(253, 230, 138), align=PP_ALIGN.RIGHT)
    add_notes(s1, "Accueil par Sore Ramatou : présenter le Groupe 5, M. CAMARA, le thème 12 et annoncer la démo live LOKO-Vault sur MariaDB XAMPP.")

    # ---------------- SLIDE 2 : PLAN & RÉPARTITION ----------------
    s2 = prs.slides.add_slide(blank)
    add_header_footer(s2, "Organisation • 20 Minutes + 10 Minutes Q&R", "Plan de l'Exposé & Répartition des 5 Piliers", 2, total, "1 Membre = 1 Démo")
    col_w = 2.32
    colors = [(220, 38, 38), (217, 119, 6), (2, 132, 199), (124, 58, 237), (5, 150, 105)]
    text_colors = [(185, 28, 28), (180, 83, 9), (3, 105, 161), (109, 40, 217), (4, 120, 87)]
    descs = [
        ["Philosophie Secure by Default", "SQL brut vs PDO préparé", "Démo Bypass & UNION SELECT sur MariaDB"],
        ["Escalade de rôle (role=admin)", "$fillable vs $guarded", "Validation stricte via FormRequest"],
        ["XSS stockée dans MariaDB", "Danger de {!! !!} vs {{ }}", "En-têtes CSP & cookie HttpOnly"],
        ["Usurpation d'action inter-sites", "Middleware ValidateCsrfToken", "Jeton @csrf & erreur HTTP 419"],
        ["Hachage bcrypt vs MD5", "IDOR vs GradePolicy (HTTP 403)", "RateLimiter (429) & .env XAMPP"],
    ]
    for i, ((slot, name, role), col, tcol, pts) in enumerate(zip(MEMBERS, colors, text_colors, descs)):
        x = 0.55 + i * 2.48
        add_rect(s2, x, 1.45, col_w, 4.55, C_WHITE, (203, 213, 225), 1.2, rounded=True)
        add_rect(s2, x, 1.45, col_w, 0.10, col)
        add_textbox(s2, x + 0.1, 1.65, col_w - 0.2, 0.3, slot, font_size=10.5, color=tcol, bold=True)
        add_textbox(s2, x + 0.1, 1.98, col_w - 0.2, 0.55, name, font_size=14, color=C_NAVY, bold=True)
        add_textbox(s2, x + 0.1, 2.55, col_w - 0.2, 0.75, role, font_size=12, color=C_RED, bold=True)
        add_bullets(s2, x + 0.1, 3.35, col_w - 0.2, 2.4, pts, font_size=11.5, color=C_SLATE, space_after=8)

    add_rect(s2, 0.55, 6.20, 12.23, 0.65, (254, 242, 242), C_RED, 1.2, rounded=True)
    add_textbox(s2, 0.75, 6.28, 11.8, 0.48,
                "🧪 Laboratoire LOKO-Vault : Chaque atelier dispose d'un commutateur 🔴 Mode Vulnérable / 🟢 Mode Sécurisé + Inspecteur SQL (DB::listen) branché sur MariaDB (loko_security_lab).",
                font_size=12.5, color=C_NAVY, valign=MSO_ANCHOR.MIDDLE)
    add_notes(s2, "Présenter la structure chronométrée : 4 minutes par membre, intégrant théorie et preuve en direct.")

    # ---------------- SLIDE 3 : POURQUOI SÉCURISER LARAVEL + BDD ----------------
    s3 = prs.slides.add_slide(blank)
    add_header_footer(s3, "Introduction • Intervenante : Sore Ramatou", "Pourquoi la Sécurité est Indissociable de Laravel + MySQL ?", 3, total, "OWASP Top 10")
    cards_s3 = [
        ("⚠️ 1. La Base de Données est la Cible N°1", (185, 28, 28), [
            ("Données critiques", "Comptes, mots de passe, notes académiques et journaux résident dans MariaDB XAMPP."),
            ("Impact immédiat", "Une seule requête SQL concaténée expose toute la base via UNION SELECT."),
            ("Risque serveur", "Un compte root sans mot de passe permet DROP DATABASE ou lecture globale."),
        ]),
        ("🛡️ 2. « Secure by Default » dans Laravel", (180, 83, 9), [
            ("Modèle (M)", "Requêtes préparées PDO, $fillable, hachage bcrypt natif."),
            ("Vue (V)", "Échappement automatique Blade {{ }} et jeton @csrf."),
            ("Contrôleur (C)", "Validation FormRequest, Policies et RateLimiter intégrés."),
        ]),
        ("⚡ 3. Le Facteur Humain Reste Décisif", (4, 120, 87), [
            ("Contournements", "DB::raw() concaténé ou {!! $bio !!} réintroduisent les failles."),
            ("Oublis fréquents", "$guarded = [] ou absence de Policy (faille IDOR)."),
            ("Erreur de prod", "Laisser APP_DEBUG=true expose le code et les identifiants .env."),
        ]),
    ]
    for i, (ctitle, ccol, cpts) in enumerate(cards_s3):
        x = 0.55 + i * 4.18
        add_rect(s3, x, 1.45, 3.88, 4.45, C_WHITE, ccol, 1.5, rounded=True)
        add_textbox(s3, x + 0.18, 1.65, 3.52, 0.55, ctitle, font_size=15.5, color=ccol, bold=True)
        add_bullets(s3, x + 0.18, 2.35, 3.52, 3.3, cpts, font_size=12.5, color=C_SLATE, space_after=12, lead_color=ccol)

    add_rect(s3, 0.55, 6.12, 12.23, 0.72, (239, 246, 255), (3, 105, 161), 1.2, rounded=True)
    add_textbox(s3, 0.75, 6.20, 11.8, 0.55,
                "« La sécurité n'est pas une option ajoutée à la fin : c'est une architecture qui traverse chaque requête HTTP jusqu'au moteur MariaDB. »",
                font_size=13.5, color=C_NAVY, italic=True, align=PP_ALIGN.CENTER, valign=MSO_ANCHOR.MIDDLE)
    add_notes(s3, "Sore Ramatou fait le lien avec les groupes précédents (MVC, routes, contrôleurs, Blade, migrations).")

    # ---------------- SLIDE 4 : CYCLE DE VIE SÉCURISÉ ----------------
    s4 = prs.slides.add_slide(blank)
    add_header_footer(s4, "Architecture Multicouche • Sore Ramatou", "Cycle de Vie Sécurisé d'une Requête HTTP dans Laravel", 4, total, "7 Couches")
    layers = [
        ("1. Rate Limiter", "Anti Brute-Force\n(HTTP 429)", (220, 38, 38)),
        ("2. Middleware CSRF", "Jeton secret @csrf\n(HTTP 419)", (217, 119, 6)),
        ("3. Auth & Session", "Cookie HttpOnly\n(HTTP 401)", (2, 132, 199)),
        ("4. Policy / Gate", "Anti-IDOR objet\n(HTTP 403)", (124, 58, 237)),
        ("5. FormRequest", "Validation stricte\n(HTTP 422)", (219, 39, 119)),
        ("6. Eloquent & PDO", "$fillable + Bindings ?\n(MariaDB)", (5, 150, 105)),
        ("7. Blade & CSP", "Échappement {{ }}\n(Anti-XSS)", (8, 145, 178)),
    ]
    for i, (lname, ldesc, lcol) in enumerate(layers):
        x = 0.55 + i * 1.77
        add_rect(s4, x, 1.65, 1.62, 2.25, C_WHITE, lcol, 1.5, rounded=True)
        add_rect(s4, x, 1.65, 1.62, 0.42, lcol)
        add_textbox(s4, x + 0.05, 1.70, 1.52, 0.34, lname, font_size=11.5, color=C_WHITE, bold=True, align=PP_ALIGN.CENTER)
        add_textbox(slide=s4, left=x + 0.08, top=2.25, width=1.46, height=1.4, text=ldesc, font_size=11.5, color=C_NAVY, align=PP_ALIGN.CENTER)

    add_rect(s4, 0.55, 4.25, 5.95, 2.50, C_WHITE, (2, 132, 199), 1.2, rounded=True)
    add_textbox(s4, 0.75, 4.40, 5.55, 0.4, "🔗 Lien avec l'Architecture MVC (Groupe 1)", font_size=15, color=(3, 105, 161), bold=True)
    add_bullets(s4, 0.75, 4.90, 5.55, 1.6, [
        "Toute requête passe par public/index.php et le Kernel HTTP.",
        "Les Middlewares filtrent les attaques AVANT le Contrôleur.",
        "Si une couche échoue, MariaDB n'est jamais sollicitée.",
    ], font_size=12.5, color=C_SLATE)

    add_rect(s4, 6.83, 4.25, 5.95, 2.50, C_WHITE, (217, 119, 6), 1.2, rounded=True)
    add_textbox(s4, 7.03, 4.40, 5.55, 0.4, "🗄️ Lien avec les Migrations & BDD (Groupe 6)", font_size=15, color=(180, 83, 9), bold=True)
    add_bullets(s4, 7.03, 4.90, 5.55, 1.6, [
        "Les contraintes SQL (foreignId()->constrained(), unique()) protègent l'intégrité physique dans MariaDB.",
        "Les types stricts et index empêchent la corruption des données.",
    ], font_size=12.5, color=C_SLATE)
    add_notes(s4, "Expliquer la défense en profondeur : même si une barrière faiblit, les couches suivantes bloquent l'attaque.")

    # ---------------- SLIDE 5 : PILIER 1 - SQLi ----------------
    s5 = prs.slides.add_slide(blank)
    add_header_footer(s5, "Pilier N°1 (00:00 – 04:00) • Sore Ramatou", "Injection SQL (SQLi) : SQL Brut vs PDO & Eloquent ORM", 5, total, "Démo Atelier 1")
    add_code_card(s5, 0.55, 1.40, 5.95, 4.65,
                  "🔴 CODE VULNÉRABLE (Concaténation directe)",
                  "// DANGER : $q injecté directement dans le SQL\n$q = $request->input('matricule');\n\n$students = DB::select(\n  \"SELECT id, matricule, full_name, filiere\n   FROM students WHERE matricule = '$q'\"\n);\n\n// Payload 1 : ' OR '1'='1  --> Toute la table !\n// Payload 2 : ' UNION SELECT id, email,\n//   password, role FROM users --  --> Exfiltration !",
                  "Conséquence XAMPP : MariaDB compile les mots-clés SQL injectés par l'attaquant.", is_vuln=True)
    add_code_card(s5, 6.83, 1.40, 5.95, 4.65,
                  "🟢 CODE SÉCURISÉ (Eloquent ORM & Bindings PDO)",
                  "// SÉCURISÉ : Eloquent ORM (Requête préparée)\n$students = Student::where('matricule', $q)\n    ->get(['id', 'matricule', 'full_name', 'filiere']);\n\n// SÉCURISÉ : SQL brut avec marqueur ? et binding\n$students = DB::select(\n  \"SELECT id, matricule, full_name, filiere\n   FROM students WHERE matricule = ?\",\n  [$q]\n);",
                  "Protection : MariaDB traite $q comme une simple chaîne littérale inoffensive.", is_vuln=False)
    add_rect(s5, 0.55, 6.20, 12.23, 0.65, (255, 251, 235), (217, 119, 6), 1.2, rounded=True)
    add_textbox(s5, 0.75, 6.28, 11.8, 0.48,
                "⚠️ Piège avancé : whereRaw(\"matricule = '$q'\") reste vulnérable ! Utiliser impérativement whereRaw('matricule = ?', [$q]).",
                font_size=12.5, color=(146, 64, 14), bold=True, valign=MSO_ANCHOR.MIDDLE)
    add_notes(s5, "Sore Ramatou lance la démo live sur http://127.0.0.1:8000/lab/sqli : payload OR 1=1 et UNION SELECT, puis bascule en Mode Sécurisé.")

    # ---------------- SLIDE 6 : PILIER 2 - MASS ASSIGNMENT CONCEPT ----------------
    s6 = prs.slides.add_slide(blank)
    add_header_footer(s6, "Pilier N°2 (04:00 – 08:00) • SIBY MODY", "Mass Assignment : Escalade de Privilèges en Base de Données", 6, total, "OWASP A01 / A04")
    add_code_card(s6, 0.55, 1.40, 5.95, 5.35,
                  "💥 MÉCANISME D'ATTAQUE SUR MARIADB",
                  "-- Structure de la table `users` sous XAMPP :\nCREATE TABLE users (\n  id BIGINT PRIMARY KEY,\n  name VARCHAR(255),\n  email VARCHAR(255),\n  password VARCHAR(255),\n  role VARCHAR(30) DEFAULT 'student' -- CIBLE !\n);\n\n-- L'attaquant ajoute un champ caché POST :\n-- name=Siby+Mody&email=...&role=admin",
                  "Si le contrôleur passe $request->all(), l'étudiant devient ADMIN en base MariaDB !", is_vuln=True)
    add_rect(s6, 6.83, 1.40, 5.95, 5.35, C_WHITE, (5, 150, 105), 1.5, rounded=True)
    add_textbox(s6, 7.05, 1.60, 5.5, 0.45, "🛡️ Liste Blanche ($fillable) vs Liste Noire ($guarded)", font_size=16, color=(4, 120, 87), bold=True)
    add_bullets(s6, 7.05, 2.25, 5.5, 4.2, [
        ("protected $fillable = ['name', 'email', 'password']", "LISTE BLANCHE (Recommandée) : Eloquent n'autorise que ces 3 colonnes en assignation de masse. La colonne 'role' est bloquée."),
        ("protected $guarded = ['role']", "LISTE NOIRE (Risquée) : si une nouvelle colonne sensible (ex. is_super_admin) est ajoutée par migration, elle devient vulnérable par oubli."),
        ("protected $guarded = [] ou Model::unguard()", "À PROSCRIRE : désactive totalement la protection Eloquent sur toute la table."),
    ], font_size=13, color=C_NAVY, space_after=14, lead_color=(4, 120, 87))
    add_notes(s6, "SIBY MODY explique le concept d'assignation de masse et pourquoi $fillable (liste blanche) est toujours supérieur à $guarded.")

    # ---------------- SLIDE 7 : PILIER 2 - MASS ASSIGNMENT CODE ----------------
    s7 = prs.slides.add_slide(blank)
    add_header_footer(s7, "Pilier N°2 (Suite) • SIBY MODY", "La Double Barrière : FormRequest + $fillable", 7, total, "Démo Atelier 2")
    add_code_card(s7, 0.55, 1.40, 5.95, 4.65,
                  "🔴 CODE VULNÉRABLE (forceFill / $request->all())",
                  "// ❌ Contrôleur vulnérable :\npublic function updateVulnerable(Request $request)\n{\n    $user = User::where('email', 'mody.siby@loko.ci')\n                ->firstOrFail();\n\n    // Écrit directement role='admin' en BDD !\n    $user->forceFill(\n        $request->only(['name', 'email', 'role'])\n    )->save();\n}",
                  "Résultat : le compte étudiant est immédiatement promu Administrateur dans MariaDB.", is_vuln=True)
    add_code_card(s7, 6.83, 1.40, 5.95, 4.65,
                  "🟢 DOUBLE BARRIÈRE LARAVEL (FormRequest + $fillable)",
                  "// ✅ 1. UpdateProfileRequest.php (Validation HTTP)\npublic function rules(): array {\n    return [\n        'name'  => ['required', 'string', 'max:100'],\n        'email' => ['required', 'email', 'max:150'],\n    ]; // 'role' est absent -> exclu !\n}\n\n// ✅ 2. Contrôleur + User::$fillable\n$user->update($request->validated());",
                  "Même si l'attaquant envoie role=admin, la valeur est ignorée à 100 %.", is_vuln=False)
    add_rect(s7, 0.55, 6.20, 12.23, 0.65, (255, 251, 235), (217, 119, 6), 1.2, rounded=True)
    add_textbox(s7, 0.75, 6.28, 11.8, 0.48,
                "💡 Pour changer légitimement un rôle côté Admin : assignation explicite après Policy ($user->role = 'admin'; $user->save();).",
                font_size=12.5, color=(146, 64, 14), bold=True, valign=MSO_ANCHOR.MIDDLE)
    add_notes(s7, "SIBY MODY passe sur LOKO-Vault Atelier 2 (/lab/mass-assignment), injecte role=admin en mode vulnérable puis prouve le blocage en mode sécurisé.")

    # ---------------- SLIDE 8 : PILIER 3 - XSS & BLADE ----------------
    s8 = prs.slides.add_slide(blank)
    add_header_footer(s8, "Pilier N°3 (08:00 – 12:00) • Boin Naomi", "Cross-Site Scripting (XSS Stocké) & Échappement Blade", 8, total, "Démo Atelier 3")
    add_code_card(s8, 0.55, 1.40, 5.95, 4.65,
                  "🔴 RENDU BLADE BRUT : {!! $student->bio !!}",
                  "<!-- ❌ Vue Blade vulnérable -->\n<div class=\"bio\">\n    {!! $student->bio !!}\n</div>\n\n<!-- Payload stocké en table `students` : -->\n<img src=\"x\" onerror=\"\n  document.getElementById('xss-banner')\n          .style.display='block'\">",
                  "Danger : le script stocké en BDD s'exécute chez tous les administrateurs et professeurs !", is_vuln=True)
    add_code_card(s8, 6.83, 1.40, 5.95, 4.65,
                  "🟢 ÉCHAPPEMENT AUTOMATIQUE : {{ $student->bio }}",
                  "<!-- ✅ Vue Blade sécurisée par défaut -->\n<div class=\"bio\">\n    {{ $student->bio }}\n</div>\n\n<!-- Traduction PHP compilée par Blade : -->\n<?php echo e($student->bio); ?>\n\n<!-- Sortie envoyée au navigateur (inerte) : -->\n&lt;img src=&quot;x&quot; onerror=&quot;...&quot;&gt;",
                  "htmlspecialchars(..., ENT_QUOTES, 'UTF-8') neutralise toute balise HTML/JS.", is_vuln=False)
    add_rect(s8, 0.55, 6.20, 12.23, 0.65, (239, 246, 255), (2, 132, 199), 1.2, rounded=True)
    add_textbox(s8, 0.75, 6.28, 11.8, 0.48,
                "📌 Exception HTML riche (WYSIWYG) : nettoyer impérativement côté serveur via HTMLPurifier avant d'utiliser {!! !!}.",
                font_size=12.5, color=(30, 58, 138), bold=True, valign=MSO_ANCHOR.MIDDLE)
    add_notes(s8, "Boin Naomi présente la faille XSS stockée dans MariaDB puis montre en direct dans l'Atelier 3 l'exécution JS vs l'échappement Blade.")

    # ---------------- SLIDE 9 : PILIER 3 - CSP & COOKIES ----------------
    s9 = prs.slides.add_slide(blank)
    add_header_footer(s9, "Pilier N°3 (Suite) • Boin Naomi", "Défense en Profondeur : En-têtes HTTP (CSP) & Cookies HttpOnly", 9, total, "SecurityHeaders")
    add_code_card(s9, 0.55, 1.45, 6.15, 5.25,
                  "🟢 MIDDLEWARE DE SÉCURITÉ HTTP",
                  "// app/Http/Middleware/SecurityHeadersMiddleware.php\n$response = $next($request);\n\n$response->headers->set(\n  'Content-Security-Policy',\n  \"default-src 'self'; script-src 'self'; object-src 'none';\"\n);\n$response->headers->set('X-Content-Type-Options', 'nosniff');\n$response->headers->set('X-Frame-Options', 'DENY');\n$response->headers->set('Referrer-Policy', 'strict-origin-when-cross-origin');\n\nreturn $response;",
                  "Blinde le navigateur contre l'exécution de scripts tiers et le Clickjacking.", is_vuln=False)
    add_rect(s9, 7.0, 1.45, 5.78, 5.25, C_WHITE, (2, 132, 199), 1.5, rounded=True)
    add_textbox(s9, 7.22, 1.65, 5.34, 0.45, "🔒 Protection des Cookies (config/session.php)", font_size=16, color=(3, 105, 161), bold=True)
    add_bullets(s9, 7.22, 2.30, 5.34, 4.2, [
        ("'http_only' => true (Défaut Laravel)", "Empêche JavaScript de lire le cookie de session via document.cookie."),
        ("'same_site' => 'lax'", "Restreint l'envoi automatique des cookies lors de requêtes inter-sites."),
        ("'secure' => true (en HTTPS)", "Empêche le transit du cookie de session en clair sur le réseau Wi-Fi."),
        ("X-Frame-Options: DENY", "Interdit d'embarquer le portail UT LOKO dans une iframe piégée."),
    ], font_size=13, color=C_NAVY, space_after=14, lead_color=(3, 105, 161))
    add_notes(s9, "Boin Naomi explique comment CSP + HttpOnly protègent la session même face à une faille JS.")

    # ---------------- SLIDE 10 : PILIER 4 - CSRF CONCEPT ----------------
    s10 = prs.slides.add_slide(blank)
    add_header_footer(s10, "Pilier N°4 (12:00 – 16:00) • Traoré Charifat Leyla", "Cross-Site Request Forgery (CSRF) : L'Usurpation d'Action", 10, total, "Sessions & Jetons")
    steps_csrf = [
        ("1️⃣ Session Active", (3, 105, 161), [
            "L'enseignant est connecté sur LOKO-Vault.",
            "Son navigateur garde le cookie laravel_session.",
        ]),
        ("2️⃣ Site Piège Externe", (185, 28, 28), [
            "Il ouvre un faux lien (« Bourse d'Excellence »).",
            "Un formulaire caché envoie POST score=20 vers LOKO-Vault avec son cookie automatique !",
        ]),
        ("3️⃣ Bouclier @csrf", (4, 120, 87), [
            "Laravel exige le jeton secret _token stocké en session.",
            "Le site tiers ne peut pas le deviner -> HTTP 419 Page Expired !",
        ]),
    ]
    for i, (st, sc, sb) in enumerate(steps_csrf):
        x = 0.55 + i * 4.18
        add_rect(s10, x, 1.55, 3.88, 3.55, C_WHITE, sc, 1.5, rounded=True)
        add_textbox(s10, x + 0.18, 1.75, 3.52, 0.45, st, font_size=16, color=sc, bold=True)
        add_bullets(s10, x + 0.18, 2.35, 3.52, 2.5, sb, font_size=13, color=C_SLATE, space_after=12)

    add_rect(s10, 0.55, 5.35, 12.23, 1.40, (255, 251, 235), (217, 119, 6), 1.2, rounded=True)
    add_textbox(s10, 0.78, 5.50, 11.8, 1.1,
                "⚡ Principe clé : Les requêtes GET ne doivent JAMAIS modifier la base de données (pas de Route::get('/grades/delete/{id}')).\nToute modification (POST, PUT, PATCH, DELETE) doit inclure le jeton cryptographique vérifié par hash_equals().",
                font_size=13, color=(120, 53, 15), bold=True, valign=MSO_ANCHOR.MIDDLE)
    add_notes(s10, "Traoré Charifat Leyla explique le scénario complet de l'attaque CSRF entre deux onglets du navigateur.")

    # ---------------- SLIDE 11 : PILIER 4 - CSRF CODE & DÉMO ----------------
    s11 = prs.slides.add_slide(blank)
    add_header_footer(s11, "Pilier N°4 (Suite) • Traoré Charifat Leyla", "Implémentation de @csrf, ValidateCsrfToken & HTTP 419", 11, total, "Démo Atelier 4")
    add_code_card(s11, 0.55, 1.40, 5.95, 4.65,
                  "🔴 CONFIGURATION VULNÉRABLE (Exemption CSRF)",
                  "// ❌ bootstrap/app.php : exception imprudente\n$middleware->validateCsrfTokens(except: [\n    'lab/csrf/vulnerable-update',\n]);\n\n<!-- ❌ Formulaire piège externe sans _token -->\n<form action=\"http://127.0.0.1:8000/lab/csrf/vulnerable-update\"\n      method=\"POST\">\n  <input type=\"hidden\" name=\"score\" value=\"20\">\n</form>",
                  "Résultat : la note passe à 20/20 dans MariaDB à l'insu de l'enseignant !", is_vuln=True)
    add_code_card(s11, 6.83, 1.40, 5.95, 4.65,
                  "🟢 PROTECTION NATIVE LARAVEL (@csrf)",
                  "<!-- ✅ Formulaire légitime dans Blade -->\n<form method=\"POST\" action=\"{{ route('lab.csrf.secure') }}\">\n    @csrf\n    <input type=\"number\" name=\"score\" value=\"15\">\n    <button type=\"submit\">Enregistrer</button>\n</form>\n\n<!-- Génère automatiquement : -->\n<input type=\"hidden\" name=\"_token\" value=\"9xK4m...\">",
                  "Toute soumission depuis le site piège déclenche immédiatement HTTP 419 Page Expired.", is_vuln=False)
    add_rect(s11, 0.55, 6.20, 12.23, 0.65, (239, 246, 255), (2, 132, 199), 1.2, rounded=True)
    add_textbox(s11, 0.75, 6.28, 11.8, 0.48,
                "🌐 Appels JavaScript / AJAX : utiliser <meta name=\"csrf-token\" content=\"{{ csrf_token() }}\"> dans l'en-tête X-CSRF-TOKEN.",
                font_size=12.5, color=(30, 58, 138), bold=True, valign=MSO_ANCHOR.MIDDLE)
    add_notes(s11, "Traoré Charifat Leyla exécute la démo de l'Atelier 4 (/lab/csrf) : bouton appât du site piège en mode vulnérable vs blocage 419 en mode sécurisé.")

    # ---------------- SLIDE 12 : PILIER 5 - BCRYPT ----------------
    s12 = prs.slides.add_slide(blank)
    add_header_footer(s12, "Pilier N°5 (16:00 – 20:00) • Djan Kouassi Noël", "Cryptographie en Base de Données : bcrypt / Argon2id vs MD5", 12, total, "OWASP A02")
    add_code_card(s12, 0.55, 1.45, 5.95, 5.15,
                  "🔴 STOCKAGE EN CLAIR OU MD5 / SHA-1 (Obsolète)",
                  "// ❌ À BANNIR ABSOLUMENT !\n$user->password = md5($request->password);\n\n// Problèmes critiques :\n// 1. Pas de sel (Salt) : deux utilisateurs avec '123456'\n//    ont le MÊME hash : e10adc3949ba59abbe56e057f20f883e\n// 2. Calcul ultra-rapide : > 50 milliards/s sur GPU\n// 3. Cassable instantanément par Rainbow Tables.",
                  "En cas de fuite SQL, tous les mots de passe sont révélés en quelques secondes.", is_vuln=True)
    add_code_card(s12, 6.83, 1.45, 5.95, 5.15,
                  "🟢 HACHAGE ADAPTATIF SALÉ LARAVEL (bcrypt / Argon2id)",
                  "// ✅ Cast automatique dans app/Models/User.php\nprotected function casts(): array {\n    return ['password' => 'hashed'];\n}\n\n// ✅ Création & Vérification manuelles :\n$hash = Hash::make($plainPassword);\n$ok   = Hash::check($plainPassword, $user->password);\n\n// Exemple stocké dans MariaDB (60 car. avec sel unique) :\n// $2y$12$8K9mP4x...vR2qZ1n...",
                  "Sel aléatoire 128 bits + facteur de coût BCRYPT_ROUNDS=12 rendant le Brute-Force vain.", is_vuln=False)
    add_notes(s12, "Djan Kouassi Noël compare MD5 et bcrypt puis fait le test en direct dans l'onglet Hachage de l'Atelier 5.")

    # ---------------- SLIDE 13 : PILIER 5 - IDOR, POLICIES & RATE LIMIT ----------------
    s13 = prs.slides.add_slide(blank)
    add_header_footer(s13, "Pilier N°5 (Suite) • Djan Kouassi Noël", "Contrôle d'Accès (IDOR vs Policies) & RateLimiter", 13, total, "Démo Atelier 5")
    add_code_card(s13, 0.55, 1.40, 5.95, 4.65,
                  "🔴 FAILLE IDOR (Insecure Direct Object Reference)",
                  "// ❌ Vérifie la connexion (auth), mais PAS la propriété !\npublic function showVulnerable(int $id)\n{\n    $grade = Grade::with('student')->findOrFail($id);\n    return view('lab.grade', compact('grade'));\n}\n\n// L'étudiant #1 change l'URL /grades/1 en /grades/2\n// -> Lit les notes confidentielles d'un camarade !",
                  "Vulnérabilité N°1 du classement OWASP Top 10 (Broken Access Control).", is_vuln=True)
    add_code_card(s13, 6.83, 1.40, 5.95, 4.65,
                  "🟢 AUTHORIZATION POLICY & RATE LIMITER",
                  "// ✅ app/Policies/GradePolicy.php\npublic function view(User $user, Grade $grade): bool {\n    return $user->role === 'admin'\n        || $grade->student->user_id === $user->id;\n}\n// Contrôleur : $this->authorize('view', $grade); // 403\n\n// ✅ Anti Brute-Force (5 essais / min -> HTTP 429)\nRateLimiter::hit($key, 60);",
                  "Bouclier double : HTTP 403 Forbidden (IDOR) + HTTP 429 Too Many Requests (Brute-Force).", is_vuln=False)
    add_rect(s13, 0.55, 6.20, 12.23, 0.65, (236, 253, 245), (5, 150, 105), 1.2, rounded=True)
    add_textbox(s13, 0.75, 6.28, 11.8, 0.48,
                "💡 Rappel clé : Authentification (401 : Qui êtes-vous ?) ≠ Autorisation (403 : Avez-vous le droit sur CETTE ligne SQL ?).",
                font_size=12.5, color=(6, 95, 70), bold=True, valign=MSO_ANCHOR.MIDDLE)
    add_notes(s13, "Djan Kouassi Noël démontre l'IDOR (accès /grades/2 bloqué à 403) et la simulation Brute-Force bloquée à 429.")

    # ---------------- SLIDE 14 : DURCISSEMENT .ENV & MARIADB XAMPP ----------------
    s14 = prs.slides.add_slide(blank)
    add_header_footer(s14, "Infrastructure & Déploiement • Djan Kouassi Noël", "Durcissement du Fichier .env et de MariaDB (XAMPP → Production)", 14, total, "OWASP A05")
    add_rect(s14, 0.55, 1.45, 5.95, 5.20, C_WHITE, C_VULN, 1.5, rounded=True)
    add_textbox(s14, 0.78, 1.65, 5.5, 0.45, "🔴 Erreurs Critiques à Éviter", font_size=16, color=(185, 28, 28), bold=True)
    add_bullets(s14, 0.78, 2.25, 5.5, 4.2, [
        ("APP_DEBUG=true en production", "Expose la trace PHP, le code source, les requêtes SQL et les clés secrètes aux visiteurs."),
        ("Compte DB_USERNAME=root (XAMPP)", "Possède tous les droits (DROP DATABASE, lecture des autres bases)."),
        ("Fichier .env versionné sur Git", "Fuite immédiate d'APP_KEY et des mots de passe MySQL."),
        ("DocumentRoot Apache mal pointé", "Doit pointer sur /public et jamais sur la racine du projet."),
    ], font_size=13, color=C_NAVY, space_after=14, lead_color=(185, 28, 28))

    add_code_card(s14, 6.83, 1.45, 5.95, 5.20,
                  "🟢 BONNES PRATIQUES PRODUCTION & MARIADB",
                  "# .env durci en production\nAPP_ENV=production\nAPP_DEBUG=false\nSESSION_SECURE_COOKIE=true\nDB_USERNAME=loko_app_user\nDB_PASSWORD=\"Str0ng!Pass#2026\"\n\n-- Privilèges minimaux dans MariaDB :\nGRANT SELECT, INSERT, UPDATE, DELETE\nON loko_security_lab.* TO 'loko_app_user'@'localhost';\n\n# Audit régulier des dépendances :\ncomposer audit",
                  "Principe du moindre privilège : même en cas de faille, le compte SQL ne peut pas détruire le serveur.", is_vuln=False)
    add_notes(s14, "Expliquer la transition entre le développement sous XAMPP et un déploiement réel en production.")

    # ---------------- SLIDE 15 : MATRICE RÉCAPITULATIVE ----------------
    s15 = prs.slides.add_slide(blank)
    add_header_footer(s15, "Synthèse Technique • Groupe 5", "Matrice Récapitulative des 5 Piliers de Sécurité Laravel", 15, total, "Vue Globale")
    rows_data = [
        ("Pilier / Menace", "Intervenant", "Pratique Vulnérable (❌)", "Protection Laravel (✅)", "Effet / Code"),
        ("1. Injection SQL (SQLi)", "Sore Ramatou", "DB::select(\"... '$q'\")", "Eloquent ORM & PDO (?)", "Paramètre littéral"),
        ("2. Mass Assignment", "Siby Mody", "forceFill($request->all())", "$fillable + FormRequest", "Filtrage strict / 422"),
        ("3. XSS Stockée", "Boin Naomi", "{!! $student->bio !!}", "Blade {{ }} + CSP + HttpOnly", "HTML échappé"),
        ("4. Faille CSRF", "Traoré C. Leyla", "Exemption CSRF / route GET", "@csrf + ValidateCsrfToken", "HTTP 419 Expired"),
        ("5. Auth / IDOR / Brute", "Djan K. Noël", "MD5 + find($id) direct", "bcrypt + Policy + RateLimiter", "HTTP 403 & 429"),
    ]
    tbl_shape = s15.shapes.add_table(len(rows_data), 5, PptIn(0.55), PptIn(1.55), PptIn(12.23), PptIn(4.95))
    tbl = tbl_shape.table
    col_widths = [2.35, 1.85, 2.75, 3.15, 2.13]
    for ci, cw in enumerate(col_widths):
        tbl.columns[ci].width = PptIn(cw)

    for ri, rdata in enumerate(rows_data):
        for ci, val in enumerate(rdata):
            cell = tbl.cell(ri, ci)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if ri == 0:
                cell.fill.fore_color.rgb = ppt_rgb(C_RED)
            elif ri % 2 == 1:
                cell.fill.fore_color.rgb = ppt_rgb(C_WHITE)
            else:
                cell.fill.fore_color.rgb = ppt_rgb((241, 245, 249))
            p = cell.text_frame.paragraphs[0]
            r = p.add_run()
            r.text = val
            r.font.name = "Segoe UI"
            r.font.size = PptPt(12.5 if ri == 0 else 12)
            r.font.bold = (ri == 0 or ci == 0 or ci == 4 or val == "Siby Mody")
            r.font.color.rgb = ppt_rgb(C_WHITE if ri == 0 else (C_RED if ci == 4 else C_NAVY))
    add_notes(s15, "Vue synthétique idéale à laisser affichée si le jury pose des questions transversales.")

    # ---------------- SLIDE 16 : CONCLUSION & Q&R ----------------
    s16 = prs.slides.add_slide(blank)
    add_header_footer(s16, "Conclusion & Session Questions-Réponses (10 Min)", "Merci pour votre Attention ! Place aux Questions", 16, total, "Groupe 5 • UT LOKO")
    cols_s16 = [
        ("✅ Architecture Native Solide", (4, 120, 87), "Laravel protège nativement contre l'OWASP Top 10 (PDO, $fillable, Blade {{ }}, @csrf, bcrypt, Policies) dès lors que ses conventions sont respectées."),
        ("🗄️ Intégrité Base MariaDB", (180, 83, 9), "Les requêtes préparées, les validations FormRequest et les comptes MySQL à privilèges limités préservent la confidentialité des données XAMPP."),
        ("🧪 Vérification Automatisée", (3, 105, 161), "Notre suite PHPUnit (SecurityLabTest) valide en continu les 5 piliers en mode vulnérable et sécurisé sur la base de données."),
    ]
    for i, (t, c, body) in enumerate(cols_s16):
        x = 0.55 + i * 4.18
        add_rect(s16, x, 1.55, 3.88, 3.15, C_WHITE, c, 1.5, rounded=True)
        add_textbox(s16, x + 0.2, 1.75, 3.48, 0.45, t, font_size=15.5, color=c, bold=True)
        add_textbox(s16, x + 0.2, 2.35, 3.48, 2.1, body, font_size=13, color=C_SLATE)

    add_rect(s16, 0.55, 5.05, 12.23, 1.65, (254, 242, 242), C_RED, 2.0, rounded=True)
    add_textbox(s16, 0.85, 5.22, 8.6, 0.45, "GROUPE 5 — LICENCE 3 INFORMATIQUE (UT LOKO)", font_size=17, color=C_RED, bold=True)
    add_textbox(s16, 0.85, 5.75, 8.8, 0.7,
                "SORE RAMATOU  •  SIBY MODY  •  BOIN NAOMI  •  TRAORÉ CHARIFAT LEYLA  •  DJAN KOUASSI NOËL",
                font_size=13, color=C_NAVY, bold=True)
    add_textbox(s16, 9.6, 5.25, 2.9, 1.2, "Professeur :\nM. CAMARA\n\nDémo : 127.0.0.1:8000",
                font_size=13, color=C_RED, bold=True, align=PP_ALIGN.RIGHT)
    add_notes(s16, "Clôturer l'exposé et inviter M. CAMARA et les camarades à poser leurs questions (10 min).")

    out_pptx = OFFICE_DIR / "Expose_Securite_Laravel_Groupe5.pptx"
    prs.save(str(out_pptx))
    print("Saved PPTX:", out_pptx)


# ==============================================================================
# PARTIE 2 : GENERATION DU RAPPORT WORD (.DOCX) + PDF
# ==============================================================================

def shade_cell(cell, hex_color):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
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


def add_doc_heading(doc, text, speaker=""):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="8B1518"/></w:pBdr>')
    pPr.append(pBdr)
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Segoe UI"
    r.font.size = Pt(15)
    r.font.color.rgb = docx_rgb(C_RED)
    if speaker:
        r2 = p.add_run(f"   [{speaker}]")
        r2.bold = True
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = docx_rgb(C_SLATE)
    return p


def add_doc_sub(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Segoe UI"
    r.font.size = Pt(12)
    r.font.color.rgb = docx_rgb(C_NAVY)
    return p


def add_doc_para(doc, text, bold_prefix=""):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.bold = True
        rb.font.name = "Segoe UI"
        rb.font.size = Pt(10.5)
        rb.font.color.rgb = docx_rgb(C_NAVY)
    r = p.add_run(text)
    r.font.name = "Segoe UI"
    r.font.size = Pt(10.5)
    r.font.color.rgb = docx_rgb((30, 41, 59))
    return p


def add_compare_table(doc, vuln_title, vuln_code, vuln_note, sec_title, sec_code, sec_note):
    tbl = doc.add_table(rows=2, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color="CBD5E1", sz="6")

    headers = [(vuln_title, "991B1B", "FEE2E2"), (sec_title, "065F46", "D1FAE5")]
    bodies = [(vuln_code, vuln_note, "FEF2F2"), (sec_code, sec_note, "ECFDF5")]

    for ci, (htitle, hcol, hbg) in enumerate(headers):
        cell = tbl.cell(0, ci)
        cell.width = Cm(8.5)
        shade_cell(cell, hbg)
        set_cell_margins(cell, 90, 90, 120, 120)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(htitle)
        r.bold = True
        r.font.name = "Segoe UI"
        r.font.size = Pt(10)
        r.font.color.rgb = DocxRGB.from_string(hcol)

    for ci, (code, note, bbg) in enumerate(bodies):
        cell = tbl.cell(1, ci)
        cell.width = Cm(8.5)
        shade_cell(cell, bbg)
        set_cell_margins(cell, 100, 100, 120, 120)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(5)
        rc = p.add_run(code)
        rc.font.name = "Consolas"
        rc.font.size = Pt(8.5)
        rc.font.color.rgb = docx_rgb(C_NAVY)

        p2 = cell.add_paragraph()
        p2.paragraph_format.space_after = Pt(0)
        rn = p2.add_run(note)
        rn.font.name = "Segoe UI"
        rn.font.size = Pt(9.2)
        rn.font.color.rgb = docx_rgb(C_SLATE)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(4)


def build_docx():
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Cm(1.4)
        sec.bottom_margin = Cm(1.4)
        sec.left_margin = Cm(1.6)
        sec.right_margin = Cm(1.6)
        sec.different_first_page_header_footer = True

        # Header & Footer on subsequent pages
        hdr = sec.header.paragraphs[0]
        hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        rh = hdr.add_run("UT LOKO • Licence 3 Informatique • Groupe 5 — La sécurité dans une application Laravel")
        rh.font.name = "Segoe UI"
        rh.font.size = Pt(8.5)
        rh.font.color.rgb = docx_rgb(C_SLATE)

        ftr = sec.footer.paragraphs[0]
        ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rf = ftr.add_run("Année académique 2025–2026  |  Professeur : M. CAMARA  |  Base de données XAMPP & Laravel")
        rf.font.name = "Segoe UI"
        rf.font.size = Pt(8.5)
        rf.font.color.rgb = docx_rgb(C_SLATE)

    # ---------------- PAGE 1 : PAGE DE GARDE OFFICIELLE CORRIGÉE (SIBY MODY) ----------------
    top_tbl = doc.add_table(rows=1, cols=3)
    top_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(top_tbl, val="none")
    c0, c1, c2 = top_tbl.cell(0, 0), top_tbl.cell(0, 1), top_tbl.cell(0, 2)
    c0.width, c1.width, c2.width = Cm(3.5), Cm(10.5), Cm(3.2)
    for c in (c0, c1, c2):
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    if LOGO_CI.exists():
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p0.add_run().add_picture(str(LOGO_CI), width=Cm(3.0))

    p1 = c1.paragraphs[0]
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_min = p1.add_run("Ministère de l'Enseignement Supérieur\net de la Recherche Scientifique")
    r_min.font.name = "Segoe UI"
    r_min.font.size = Pt(12.5)
    r_min.bold = True
    r_min.font.color.rgb = docx_rgb(C_NAVY)

    if LOGO_GL.exists():
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p2.add_run().add_picture(str(LOGO_GL), width=Cm(2.4))

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    cover_tbl = doc.add_table(rows=1, cols=2)
    cover_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(cover_tbl, color="8B1518", sz="8")
    left_c, right_c = cover_tbl.cell(0, 0), cover_tbl.cell(0, 1)
    left_c.width, right_c.width = Cm(6.4), Cm(11.0)
    set_cell_margins(left_c, 220, 220, 180, 180)
    set_cell_margins(right_c, 280, 280, 220, 220)
    shade_cell(right_c, "9B1C1C")

    # Left column
    lp0 = left_c.paragraphs[0]
    lp0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if LOGO_UT.exists():
        lp0.add_run().add_picture(str(LOGO_UT), width=Cm(4.5))

    for label, val in [
        ("DÉPARTEMENT :", "ITER"),
        ("DOMAINE :", "SCIENCE ET TECHNOLOGIE"),
        ("MENTION :", "INFORMATIQUE ET TÉLÉCOMMUNICATION"),
        ("NIVEAU :", "LICENCE 3 — Module Base de Données (XAMPP) & Framework Laravel"),
    ]:
        lp = left_c.add_paragraph()
        lp.paragraph_format.space_before = Pt(18)
        lp.paragraph_format.space_after = Pt(4)
        rl = lp.add_run(label + " ")
        rl.bold = True
        rl.font.name = "Segoe UI"
        rl.font.size = Pt(10.5)
        rl.font.color.rgb = docx_rgb(C_RED)
        rv = lp.add_run(val)
        rv.font.name = "Segoe UI"
        rv.font.size = Pt(10.5)
        rv.font.color.rgb = docx_rgb(C_NAVY)

    # Right column
    def add_rc(text, size=12, bold=False, color=C_WHITE, before=8, after=8):
        rp = right_c.add_paragraph() if len(right_c.paragraphs[0].text) > 0 or len(right_c.paragraphs) > 1 else right_c.paragraphs[0]
        rp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rp.paragraph_format.space_before = Pt(before)
        rp.paragraph_format.space_after = Pt(after)
        rr = rp.add_run(text)
        rr.font.name = "Segoe UI"
        rr.font.size = Pt(size)
        rr.bold = bold
        rr.font.color.rgb = docx_rgb(color)
        return rp

    add_rc("ANNÉE ACADÉMIQUE : 2025 - 2026", size=13, bold=True, before=6, after=14)
    add_rc("Spécialité : INFORMATIQUE", size=12.5, bold=True, before=4, after=20)
    add_rc("THÈME N° 12 :", size=13, bold=True, color=(253, 230, 138), before=12, after=4)
    add_rc("La sécurité dans une application Laravel", size=20, bold=True, color=C_WHITE, before=2, after=26)
    add_rc("EXPOSÉ RÉALISÉ PAR (GROUPE 5) :", size=12.5, bold=True, color=(253, 230, 138), before=10, after=8)

    for nm in ["SIBY MODY", "SORE RAMATOU", "BOIN NAOMI", "TRAORÉ LEYLA CHARIFAT", "DJAN KOUASSI NOËL"]:
        add_rc(nm, size=12.5, bold=True, color=C_WHITE, before=3, after=3)

    add_rc("PROFESSEUR :", size=12.5, bold=True, color=(253, 230, 138), before=24, after=4)
    add_rc("M. CAMARA", size=15, bold=True, color=C_WHITE, before=0, after=12)

    doc.add_page_break()

    # ---------------- SOMMAIRE & RÉPARTITION ----------------
    add_doc_heading(doc, "Sommaire Exécutif & Répartition du Groupe 5")
    add_doc_para(doc,
        "Ce rapport accompagne l'exposé oral (20 minutes avec démonstration en direct) et la séance de questions-réponses (10 minutes) du Groupe 5 pour le module Base de Données (XAMPP / MariaDB) & Framework Laravel.")

    sum_tbl = doc.add_table(rows=6, cols=4)
    sum_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(sum_tbl)
    sum_headers = ["Pilier / Section", "Intervenant", "Mécanismes Laravel & MariaDB étudiés", "Minutage"]
    for ci, h in enumerate(sum_headers):
        c = sum_tbl.cell(0, ci)
        shade_cell(c, "8B1518")
        set_cell_margins(c, 80, 80, 100, 100)
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.name = "Segoe UI"
        r.font.size = Pt(9.5)
        r.font.color.rgb = docx_rgb(C_WHITE)

    sum_rows = [
        ("1. Intro & Injection SQL (SQLi)", "Sore Ramatou", "Architecture 7 couches, PDO préparé (?) vs DB::select concaténé", "00:00 – 04:00"),
        ("2. Mass Assignment & Validation", "Siby Mody", "Escalade role=admin en BDD, $fillable vs $guarded, FormRequest", "04:00 – 08:00"),
        ("3. Faille XSS Stockée & Blade", "Boin Naomi", "Stockage JS en BDD, {{ }} vs {!! !!}, headers CSP & HttpOnly", "08:00 – 12:00"),
        ("4. Faille CSRF & Sessions", "Traoré Charifat Leyla", "Faux site externe, ValidateCsrfToken, @csrf (HTTP 419), SameSite", "12:00 – 16:00"),
        ("5. Auth, Bcrypt, IDOR & .env", "Djan Kouassi Noël", "bcrypt vs MD5, GradePolicy (HTTP 403), RateLimiter (429), XAMPP", "16:00 – 20:00"),
    ]
    for ri, row in enumerate(sum_rows, start=1):
        for ci, val in enumerate(row):
            c = sum_tbl.cell(ri, ci)
            if ri % 2 == 0:
                shade_cell(c, "F8FAFC")
            set_cell_margins(c, 70, 70, 100, 100)
            r = c.paragraphs[0].add_run(val)
            r.font.name = "Segoe UI"
            r.font.size = Pt(9.2)
            r.bold = (ci in (0, 1))
            r.font.color.rgb = docx_rgb(C_NAVY)

    # ---------------- CHAPITRE 1 : INTRO & ARCHITECTURE ----------------
    add_doc_heading(doc, "1. Introduction Générale & Défense en Profondeur", "Sore Ramatou")
    add_doc_para(doc,
        "Dans une architecture web moderne reposant sur XAMPP (serveur Apache, PHP 8.5, moteur relationnel MariaDB 10.11) et le framework Laravel, la sécurité n'est pas un module optionnel : elle conditionne la confidentialité, l'intégrité et la disponibilité des données académiques et métiers.")
    add_doc_para(doc,
        "Laravel suit la philosophie « Secure by Default » (sécurisé par défaut) et implémente une architecture de défense en profondeur en 7 couches successives entre le navigateur et MariaDB : RateLimiter (HTTP 429) → Middleware CSRF (HTTP 419) → Authentification & Session HttpOnly (HTTP 401) → Authorization Policies/Gates (HTTP 403) → Validation FormRequest (HTTP 422) → Eloquent ORM & PDO préparé → Échappement Blade & En-têtes CSP.")

    # ---------------- CHAPITRE 2 : PILIER 1 - SQLI ----------------
    add_doc_heading(doc, "2. Pilier n° 1 : Injection SQL (SQLi), PDO & Eloquent ORM", "Sore Ramatou")
    add_doc_para(doc,
        "L'injection SQL se produit lorsque des paramètres utilisateurs sont concaténés directement dans une requête SQL envoyée à MariaDB. Un attaquant peut fermer le littéral texte pour modifier la logique de la clause WHERE (' OR '1'='1) ou exfiltrer d'autres tables via UNION SELECT.",
        bold_prefix="Problématique Base de Données : ")
    add_compare_table(
        doc,
        "❌ CODE VULNÉRABLE (Concaténation SQL)",
        "$q = $request->input('matricule');\n$rows = DB::select(\n  \"SELECT id, matricule, full_name, filiere\n   FROM students WHERE matricule = '$q'\"\n);",
        "Un payload tel que ' UNION SELECT id, email, password, role FROM users --  retourne la table users.",
        "✅ SOLUTION LARAVEL (Eloquent & Bindings PDO)",
        "$rows = Student::where('matricule', $q)->get();\n// Ou en SQL brut paramétré :\n$rows = DB::select(\n  'SELECT id, matricule, full_name, filiere\n   FROM students WHERE matricule = ?', [$q]\n);",
        "PDO compile d'abord la requête avec ?, puis transmet $q séparément comme donnée littérale."
    )

    # ---------------- CHAPITRE 3 : PILIER 2 - MASS ASSIGNMENT ----------------
    add_doc_heading(doc, "3. Pilier n° 2 : Mass Assignment & Validation FormRequest", "Siby Mody")
    add_doc_para(doc,
        "L'assignation de masse permet de remplir un modèle Eloquent directement depuis un tableau de requête ($request->all()). Si le développeur ne définit pas de liste blanche ($fillable) ou utilise forceFill(), un étudiant peut ajouter un champ caché role=admin dans sa requête POST pour s'octroyer les droits administrateur dans la table users de MariaDB.",
        bold_prefix="Escalade de privilèges en BDD : ")
    add_compare_table(
        doc,
        "❌ CODE VULNÉRABLE ($guarded = [] / forceFill)",
        "// Aucune restriction sur les colonnes\n$user->forceFill($request->all())->save();",
        "La requête SQL UPDATE générée inclut SET role = 'admin', compromettant l'intégrité des rôles.",
        "✅ DOUBLE BARRIÈRE (FormRequest + $fillable)",
        "// User.php :\nprotected $fillable = ['name', 'email', 'password'];\n// Contrôleur :\n$user->update($request->validated());",
        "Seuls les champs explicitement validés par UpdateProfileRequest et listés dans $fillable sont écrits."
    )

    # ---------------- CHAPITRE 4 : PILIER 3 - XSS & BLADE ----------------
    add_doc_heading(doc, "4. Pilier n° 3 : Faille XSS Stockée, Moteur Blade & CSP", "Boin Naomi")
    add_doc_para(doc,
        "Dans une attaque XSS stockée, du code JavaScript malveillant est enregistré dans une colonne de la base MariaDB (par exemple la biographie d'un étudiant), puis exécuté par le navigateur des autres visiteurs si la vue Blade affiche la donnée avec la syntaxe non échappée {!! $student->bio !!}.",
        bold_prefix="Vecteur Base de Données → Navigateur : ")
    add_compare_table(
        doc,
        "❌ BLADE NON ÉCHAPPÉ ({!! !!})",
        "<div class=\"bio\">{!! $student->bio !!}</div>",
        "Exécute <img src=x onerror=...> dans le navigateur de chaque administrateur consultant la fiche.",
        "✅ BLADE ÉCHAPPÉ ({{ }}) + HEADERS CSP",
        "<div class=\"bio\">{{ $student->bio }}</div>\n// + SecurityHeadersMiddleware (CSP, nosniff, DENY)",
        "Le helper e() convertit < et > en &lt; et &gt;. Les cookies HttpOnly restent inaccessibles en JS."
    )

    # ---------------- CHAPITRE 5 : PILIER 4 - CSRF ----------------
    add_doc_heading(doc, "5. Pilier n° 4 : Faille CSRF, Sessions & Directive @csrf", "Traoré Charifat Leyla")
    add_doc_para(doc,
        "Le Cross-Site Request Forgery consiste à amener un utilisateur connecté sur un site externe piégé qui soumet silencieusement un formulaire caché vers l'application Laravel en réutilisant automatiquement son cookie de session. Sans jeton secret, la base MariaDB exécute une modification non consentie.",
        bold_prefix="Usurpation de session : ")
    add_compare_table(
        doc,
        "❌ ROUTE SANS PROTECTION CSRF",
        "// bootstrap/app.php :\n$middleware->validateCsrfTokens(except: [\n  'lab/csrf/vulnerable-update',\n]);",
        "Un site externe peut modifier une note en base de données dès qu'un enseignant visite une page appât.",
        "✅ JETON @csrf & MIDDLEWARE VALIDATECSRFTOKEN",
        "<form method=\"POST\" action=\"{{ route('lab.csrf.secure') }}\">\n  @csrf\n  <input type=\"number\" name=\"score\">\n</form>",
        "En l'absence d'un _token valide vérifié par hash_equals(), Laravel bloque l'attaque avec HTTP 419."
    )

    # ---------------- CHAPITRE 6 : PILIER 5 - AUTH, BCRYPT, IDOR, .ENV ----------------
    add_doc_heading(doc, "6. Pilier n° 5 : Auth, Bcrypt, IDOR (Policies), RateLimiter & Hygiène XAMPP", "Djan Kouassi Noël")
    add_doc_sub(doc, "6.1. Hachage adaptatif des mots de passe (bcrypt / Argon2id)")
    add_doc_para(doc,
        "Contrairement à MD5 ou SHA-1 (non salés et vulnérables aux Rainbow Tables), Laravel chiffre les mots de passe à sens unique via Hash::make() (bcrypt avec sel aléatoire de 128 bits et coût configurable BCRYPT_ROUNDS=12) et le cast 'password' => 'hashed' dans User.php.")

    add_doc_sub(doc, "6.2. Prévention de la faille IDOR via les Policies & Rate Limiting")
    add_compare_table(
        doc,
        "❌ CONTRÔLEUR VULNÉRABLE À L'IDOR",
        "public function showVulnerable(int $id) {\n  // Ne vérifie pas le propriétaire !\n  return Grade::findOrFail($id);\n}",
        "Un étudiant modifie /grades/1 en /grades/2 et lit le relevé confidentiel d'un camarade.",
        "✅ GRADEPOLICY (HTTP 403) + RATELIMITER (HTTP 429)",
        "$this->authorize('view', $grade);\n// GradePolicy : $user->role === 'admin'\n// || $grade->student->user_id === $user->id",
        "Renvoie HTTP 403 Forbidden sur accès non autorisé et HTTP 429 après 5 essais de login/min."
    )

    add_doc_sub(doc, "6.3. Sécurisation de l'infrastructure XAMPP / MariaDB et du fichier .env")
    add_doc_para(doc,
        "Pour passer du laboratoire XAMPP local à la production, 4 règles impératives s'appliquent : (1) Définir APP_ENV=production et APP_DEBUG=false ; (2) Créer un utilisateur MariaDB dédié possédant uniquement SELECT, INSERT, UPDATE, DELETE (jamais root sans mot de passe) ; (3) Pointer la racine Apache uniquement sur le répertoire /public afin que .env soit inaccessible ; (4) Exécuter composer audit pour détecter les vulnérabilités des dépendances.")

    add_doc_heading(doc, "7. Conclusion Générale", "Groupe 5")
    add_doc_para(doc,
        "Le laboratoire applicatif LOKO-Vault connecté à MariaDB sous XAMPP démontre concrètement que la sécurité d'une application Laravel repose sur la synergie entre les mécanismes natifs du framework (PDO, $fillable, Blade {{ }}, @csrf, bcrypt, Policies, RateLimiter) et la vigilance constante du développeur tout au long du cycle de vie logiciel.")

    out_docx = OFFICE_DIR / "Rapport_Securite_Laravel_Groupe5.docx"
    doc.save(str(out_docx))
    print("Saved DOCX:", out_docx)
    return out_docx


def build_pdf_report(pdf_path: Path):
    """Génère un rapport PDF académique A4 complet via ReportLab (autonome, avec logos UT LOKO)."""
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Image as RlImage,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    col_red = colors.HexColor("#8B1518")
    col_gold = colors.HexColor("#D97706")
    col_navy = colors.HexColor("#0F172A")
    col_slate = colors.HexColor("#334155")
    col_vuln_bg = colors.HexColor("#FEF2F2")
    col_vuln_bd = colors.HexColor("#DC2626")
    col_sec_bg = colors.HexColor("#ECFDF5")
    col_sec_bd = colors.HexColor("#059669")

    styles = getSampleStyleSheet()
    st_h1 = ParagraphStyle("LokoH1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=14,
                           textColor=col_red, spaceBefore=12, spaceAfter=6)
    st_h2 = ParagraphStyle("LokoH2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.5,
                           textColor=col_navy, spaceBefore=8, spaceAfter=4)
    st_body = ParagraphStyle("LokoBody", parent=styles["Normal"], fontName="Helvetica", fontSize=9.8,
                             leading=14, textColor=colors.HexColor("#1E293B"), alignment=TA_JUSTIFY, spaceAfter=6)
    st_code = ParagraphStyle("LokoCode", parent=styles["Code"], fontName="Courier", fontSize=8,
                             leading=10.5, textColor=col_navy)
    st_tbl = ParagraphStyle("LokoTbl", parent=styles["Normal"], fontName="Helvetica", fontSize=8.8, leading=11.5)
    st_tbl_hdr = ParagraphStyle("LokoTblHdr", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9,
                                textColor=colors.white)

    def draw_page_chrome(canvas, doc):
        if doc.page == 1:
            return
        canvas.saveState()
        canvas.setStrokeColor(col_red)
        canvas.setLineWidth(1)
        canvas.line(1.5 * cm, A4[1] - 1.2 * cm, A4[0] - 1.5 * cm, A4[1] - 1.2 * cm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(col_slate)
        canvas.drawString(1.5 * cm, A4[1] - 1.0 * cm, "UT LOKO • Licence 3 Informatique • Groupe 5")
        canvas.drawRightString(A4[0] - 1.5 * cm, A4[1] - 1.0 * cm, "La sécurité dans une application Laravel")
        canvas.line(1.5 * cm, 1.2 * cm, A4[0] - 1.5 * cm, 1.2 * cm)
        canvas.drawString(1.5 * cm, 0.8 * cm, "Module : Base de Données (XAMPP / MariaDB) & Laravel | Prof. M. CAMARA")
        canvas.drawRightString(A4[0] - 1.5 * cm, 0.8 * cm, f"Page {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
    )
    story = []

    # --- PAGE 1 : PAGE DE GARDE UT LOKO CORRIGÉE (SIBY MODY) ---
    ci_img = RlImage(str(LOGO_CI), width=2.8 * cm, height=1.55 * cm) if LOGO_CI.exists() else Paragraph("", st_body)
    gl_img = RlImage(str(LOGO_GL), width=2.1 * cm, height=1.9 * cm) if LOGO_GL.exists() else Paragraph("", st_body)
    ministry_p = Paragraph(
        "<b>Ministère de l'Enseignement Supérieur<br/>et de la Recherche Scientifique</b>",
        ParagraphStyle("Min", fontName="Helvetica-Bold", fontSize=11, alignment=TA_CENTER, leading=14, textColor=col_navy),
    )
    top_banner = Table([[ci_img, ministry_p, gl_img]], colWidths=[3.5 * cm, 11.0 * cm, 3.5 * cm])
    top_banner.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (2, 0), (2, 0), "RIGHT")]))
    story.append(top_banner)
    story.append(Spacer(1, 0.6 * cm))

    ut_img = RlImage(str(LOGO_UT), width=4.4 * cm, height=3.9 * cm) if LOGO_UT.exists() else Paragraph("UT LOKO", st_h1)
    left_flow = [
        ut_img,
        Spacer(1, 1.0 * cm),
        Paragraph("<b>DÉPARTEMENT :</b> ITER", ParagraphStyle("LM", fontSize=10, leading=15, spaceAfter=10, textColor=col_navy)),
        Paragraph("<b>DOMAINE :</b><br/>SCIENCE ET TECHNOLOGIE", ParagraphStyle("LM2", fontSize=10, leading=15, spaceAfter=10, textColor=col_navy)),
        Paragraph("<b>MENTION :</b><br/>INFORMATIQUE ET TÉLÉCOMMUNICATION", ParagraphStyle("LM3", fontSize=10, leading=15, spaceAfter=10, textColor=col_navy)),
        Paragraph("<b>NIVEAU :</b><br/>LICENCE 3 — Module Base de Données (XAMPP) &amp; Laravel", ParagraphStyle("LM4", fontSize=9.5, leading=14, textColor=col_red)),
    ]

    st_r_title = ParagraphStyle("RT", fontName="Helvetica-Bold", fontSize=19, leading=24, alignment=TA_CENTER, textColor=colors.white)
    st_r_txt = ParagraphStyle("RX", fontName="Helvetica-Bold", fontSize=11.5, leading=16, alignment=TA_CENTER, textColor=colors.white)
    st_r_gold = ParagraphStyle("RG", fontName="Helvetica-Bold", fontSize=11.5, leading=16, alignment=TA_CENTER, textColor=colors.HexColor("#FDE68A"))

    right_flow = [
        Paragraph("ANNÉE ACADÉMIQUE : 2025 – 2026", st_r_txt),
        Spacer(1, 0.5 * cm),
        Paragraph("Spécialité : INFORMATIQUE", st_r_txt),
        Spacer(1, 1.0 * cm),
        Paragraph("THÈME N° 12 :", st_r_gold),
        Spacer(1, 0.25 * cm),
        Paragraph("La sécurité dans une application Laravel", st_r_title),
        Spacer(1, 1.2 * cm),
        Paragraph("<u>EXPOSÉ RÉALISÉ PAR (GROUPE 5) :</u>", st_r_gold),
        Spacer(1, 0.3 * cm),
        Paragraph("SIBY MODY<br/>SORE RAMATOU<br/>BOIN NAOMI<br/>TRAORÉ LEYLA CHARIFAT<br/>DJAN KOUASSI NOËL",
                  ParagraphStyle("Auth", fontName="Helvetica-Bold", fontSize=12, leading=20, alignment=TA_CENTER, textColor=colors.white)),
        Spacer(1, 1.2 * cm),
        Paragraph("PROFESSEUR :", st_r_gold),
        Paragraph("M. CAMARA", ParagraphStyle("Prof", fontName="Helvetica-Bold", fontSize=14, alignment=TA_CENTER, textColor=colors.white)),
    ]

    cover_tbl = Table([[left_flow, right_flow]], colWidths=[6.5 * cm, 11.5 * cm], rowHeights=[22.2 * cm])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.white),
        ("BACKGROUND", (1, 0), (1, 0), col_red),
        ("BOX", (0, 0), (-1, -1), 1.5, col_red),
        ("LINEBEFORE", (1, 0), (1, 0), 3, col_gold),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 24),
        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
    ]))
    story.append(cover_tbl)
    story.append(PageBreak())

    # --- PAGES SUIVANTES : CORPS DU RAPPORT ---
    story.append(Paragraph("Sommaire Exécutif &amp; Répartition du Groupe 5", st_h1))
    story.append(Paragraph(
        "Ce rapport académique accompagne la présentation orale (20 minutes avec démonstration en direct sur le laboratoire <b>LOKO-Vault</b> connecté à MariaDB/XAMPP) et la session de questions-réponses (10 minutes) devant M. CAMARA.",
        st_body))

    sum_data = [[
        Paragraph("Pilier / Chapitre", st_tbl_hdr),
        Paragraph("Intervenant", st_tbl_hdr),
        Paragraph("Mécanismes étudiés", st_tbl_hdr),
        Paragraph("Durée", st_tbl_hdr),
    ]]
    for ch, spk, mech, tm in [
        ("1. Intro &amp; Injection SQL", "Sore Ramatou", "Défense en 7 couches, PDO préparé (?) vs SQL concaténé", "00:00–04:00"),
        ("2. Mass Assignment", "Siby Mody", "Escalade role=admin en BDD, #[Fillable] &amp; FormRequest", "04:00–08:00"),
        ("3. XSS Stockée &amp; Blade", "Boin Naomi", "JS stocké en BDD, {{ }} vs {!! !!}, headers CSP &amp; HttpOnly", "08:00–12:00"),
        ("4. Faille CSRF", "Traoré C. Leyla", "Site piège externe, @csrf, ValidateCsrfToken (HTTP 419)", "12:00–16:00"),
        ("5. Auth, Bcrypt &amp; IDOR", "Djan K. Noël", "bcrypt vs MD5, GradePolicy (403), RateLimiter (429), .env", "16:00–20:00"),
    ]:
        sum_data.append([Paragraph(f"<b>{ch}</b>", st_tbl), Paragraph(f"<b>{spk}</b>", st_tbl),
                         Paragraph(mech, st_tbl), Paragraph(tm, st_tbl)])

    t_sum = Table(sum_data, colWidths=[4.2 * cm, 3.3 * cm, 8.0 * cm, 2.5 * cm])
    t_sum.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), col_red),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t_sum)
    story.append(Spacer(1, 0.3 * cm))

    def add_cmp_box(v_title, v_code, s_title, s_code):
        tbl = Table([
            [Paragraph(f"<b>{v_title}</b>", ParagraphStyle("VT", fontSize=9, textColor=col_vuln_bd)),
             Paragraph(f"<b>{s_title}</b>", ParagraphStyle("ST", fontSize=9, textColor=col_sec_bd))],
            [Paragraph(v_code.replace("\n", "<br/>"), st_code),
             Paragraph(s_code.replace("\n", "<br/>"), st_code)],
        ], colWidths=[8.9 * cm, 8.9 * cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), col_vuln_bg),
            ("BACKGROUND", (1, 0), (1, -1), col_sec_bg),
            ("BOX", (0, 0), (0, -1), 1, col_vuln_bd),
            ("BOX", (1, 0), (1, -1), 1, col_sec_bd),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.25 * cm))

    sections = [
        ("1. Introduction Générale &amp; Architecture de Défense en Profondeur", "Sore Ramatou",
         "Laravel adopte la philosophie <i>Secure by Default</i>. Entre la requête HTTP du navigateur et le moteur MariaDB sous XAMPP, toute action traverse 7 couches successives : RateLimiter (HTTP 429), ValidateCsrfToken (HTTP 419), Authentification &amp; Session HttpOnly (HTTP 401), Policies/Gates (HTTP 403), FormRequest (HTTP 422), Eloquent ORM &amp; PDO préparé, puis échappement Blade &amp; CSP.",
         None),
        ("2. Pilier n° 1 : Injection SQL (SQLi), PDO &amp; Eloquent ORM", "Sore Ramatou",
         "Une injection SQL survient lorsqu'une saisie utilisateur est concaténée dans une requête envoyée à MariaDB, permettant le bypass logique (' OR '1'='1) ou l'exfiltration de la table users via UNION SELECT. L'ORM Eloquent et les bindings PDO (?) isolent les paramètres de l'instruction SQL compilée.",
         ("❌ CODE VULNÉRABLE", "DB::select(\"SELECT * FROM students\n  WHERE matricule = '$q'\");",
          "✅ SOLUTION PDO / ELOQUENT", "Student::where('matricule', $q)->get();\n// Ou : DB::select('... = ?', [$q]);")),
        ("3. Pilier n° 2 : Mass Assignment &amp; Validation FormRequest", "Siby Mody",
         "Lorsque le contrôleur écrit tous les champs HTTP ($request-&gt;all() ou forceFill) en base de données, un attaquant peut injecter role=admin pour obtenir les privilèges administrateur. La double barrière associe FormRequest::validated() et l'attribut #[Fillable] (liste blanche).",
         ("❌ CODE VULNÉRABLE", "$user->forceFill($request->all())->save();",
          "✅ DOUBLE BARRIÈRE LARAVEL", "#[Fillable(['name', 'email', 'password'])]\n$user->update($request->validated());")),
        ("4. Pilier n° 3 : Faille XSS Stockée, Moteur Blade &amp; Headers CSP", "Boin Naomi",
         "La faille XSS stockée enregistre du code JavaScript malveillant dans MariaDB et l'exécute chez les autres utilisateurs via {!! $bio !!}. La syntaxe {{ $bio }} échappe automatiquement le HTML via htmlspecialchars(), renforcée par SecurityHeadersMiddleware (CSP, nosniff, DENY) et les cookies HttpOnly.",
         ("❌ BLADE NON ÉCHAPPÉ", "&lt;div&gt;{!! $student->bio !!}&lt;/div&gt;",
          "✅ BLADE {{ }} + CSP", "&lt;div&gt;{{ $student->bio }}&lt;/div&gt;\n// + Content-Security-Policy")),
        ("5. Pilier n° 4 : Faille CSRF, Sessions &amp; Directive @csrf", "Traoré Charifat Leyla",
         "Un site piège externe peut soumettre un formulaire caché en réutilisant le cookie de session actif de la victime. Laravel impose un jeton cryptographique @csrf vérifié par hash_equals() dans ValidateCsrfToken et bloque toute requête externe avec HTTP 419 Page Expired.",
         ("❌ ROUTE EXEMPTE DE CSRF", "$middleware->validateCsrfTokens(\n  except: ['lab/csrf/vulnerable-update']);",
          "✅ PROTECTION @csrf (HTTP 419)", "&lt;form method=\"POST\"&gt;\n  @csrf\n&lt;/form&gt;")),
        ("6. Pilier n° 5 : Bcrypt, IDOR (Policies), RateLimiter &amp; Hygiène XAMPP", "Djan Kouassi Noël",
         "Les mots de passe en base MariaDB doivent être hachés avec bcrypt (sel aléatoire 128 bits, BCRYPT_ROUNDS=12) et jamais MD5. L'autorisation via GradePolicy prévient les failles IDOR (HTTP 403), et RateLimiter bloque le brute-force dès la 6e tentative (HTTP 429). En production : APP_DEBUG=false et utilisateur SQL dédié sans droit DROP.",
         ("❌ IDOR &amp; MD5 OBSOLÈTE", "$pw = md5($plain);\nreturn Grade::findOrFail($id);",
          "✅ GRADEPOLICY &amp; BCRYPT", "$this->authorize('view', $grade); // 403\nHash::make($plain); // $2y$12$...")),
    ]

    for title, spk, desc, cmp_tuple in sections:
        story.append(Paragraph(f"{title} <font size='9.5' color='#475569'>[{spk}]</font>", st_h1))
        story.append(Paragraph(desc, st_body))
        if cmp_tuple:
            add_cmp_box(*cmp_tuple)

    story.append(Paragraph("7. Conclusion Générale", st_h1))
    story.append(Paragraph(
        "À travers l'application <b>LOKO-Vault</b> reliée à MariaDB sous XAMPP, le Groupe 5 a démontré comment Laravel protège nativement contre l'OWASP Top 10 tout en soulignant la responsabilité du développeur dans le respect des conventions du framework.",
        st_body))

    doc.build(story, onFirstPage=draw_page_chrome, onLaterPages=draw_page_chrome)
    print("Saved ReportLab PDF:", pdf_path)


def convert_docx_to_pdf_word(docx_path: Path, pdf_path: Path):
    """Tente Word COM puis bascule proprement sur ReportLab pour garantir un PDF fidèle."""
    ps_script = f"""
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = 0
    $doc = $word.Documents.Open("{str(docx_path)}")
    $doc.SaveAs([ref] "{str(pdf_path)}", [ref] 17)
    $doc.Close($false)
    $word.Quit()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
    """
    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True)
    if res.returncode == 0 and pdf_path.exists():
        print("Saved Office PDF via Word:", pdf_path)
        return True
    build_pdf_report(pdf_path)
    return True


# ==============================================================================
# PARTIE 3 : INCORPORATION DES LOGOS OFFICIELS DANS WEB-INTERACTIF + EXPORT PDF
# ==============================================================================

def img_to_data_uri(path: Path) -> str:
    if not path.exists():
        return ""
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def inject_logos_into_web_html():
    ci_uri = img_to_data_uri(LOGO_CI)
    gl_uri = img_to_data_uri(LOGO_GL)
    ut_uri = img_to_data_uri(LOGO_UT)

    slides_html = WEB_DIR / "slides.html"
    if slides_html.exists() and ut_uri:
        txt = slides_html.read_text(encoding="utf-8")
        old_box = """        <div class="cover-logo-box">
          <div class="ut-title">UT LOKO</div>
          <div class="ut-sub">Université Tertiaire &amp; Technologique</div>
          <div style="font-size:11px; color:#64748B; margin-top:4px;">Science &amp; Technologie • ITER</div>
        </div>"""
        new_box = f"""        <div class="cover-logo-box">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
            <img src="{ci_uri}" alt="Côte d'Ivoire" style="height:40px; object-fit:contain;">
            <img src="{gl_uri}" alt="Groupe LOKO" style="height:40px; object-fit:contain;">
          </div>
          <img src="{ut_uri}" alt="UT LOKO" style="max-width:190px; max-height:110px; object-fit:contain; margin:4px auto; display:block;">
        </div>"""
        if old_box in txt:
            slides_html.write_text(txt.replace(old_box, new_box), encoding="utf-8")
            print("Embedded official logos into slides.html")

    rapport_html = WEB_DIR / "rapport.html"
    if rapport_html.exists() and ut_uri:
        txt = rapport_html.read_text(encoding="utf-8")
        old_ci = """      <div class="cover-badge-groupe" style="border-color:#15803D; color:#15803D;">
        RÉPUBLIQUE DE CÔTE D'IVOIRE<br>
        <span style="font-size:10px; color:#475569;">Union - Discipline - Travail</span>
      </div>"""
        new_ci = f'      <img src="{ci_uri}" alt="Côte d\'Ivoire" style="height:68px; object-fit:contain;">'
        old_gl = """      <div class="cover-badge-groupe">
        • GROUPE •<br>
        <span style="font-size:20px;">LOKO</span>
      </div>"""
        new_gl = f'      <img src="{gl_uri}" alt="Groupe LOKO" style="height:68px; object-fit:contain;">'
        old_ut = """        <div class="ut-emblem">
          <div class="big">UT<span>LOKO</span></div>
          <div class="univ">UNIVERSITÉ</div>
          <div class="sub">Tertiaire &amp; Technologique</div>
        </div>"""
        new_ut = f"""        <div class="ut-emblem" style="background:#FFF; border-color:#E2E8F0;">
          <img src="{ut_uri}" alt="UT LOKO" style="max-width:210px; max-height:145px; object-fit:contain;">
        </div>"""
        for o, n in [(old_ci, new_ci), (old_gl, new_gl), (old_ut, new_ut)]:
            txt = txt.replace(o, n)
        rapport_html.write_text(txt, encoding="utf-8")
        print("Embedded official logos into rapport.html")


def export_web_pdf():
    out_pdf = WEB_DIR / "Rapport_Web_Groupe5.pdf"
    edge = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    if edge.exists():
        html_url = (WEB_DIR / "rapport.html").as_uri()
        subprocess.run([
            str(edge),
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={out_pdf}",
            html_url,
        ], capture_output=True, check=False)
    if not out_pdf.exists():
        build_pdf_report(out_pdf)
    else:
        print("Saved Web PDF via Edge:", out_pdf)


if __name__ == "__main__":
    OFFICE_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    build_pptx()
    inject_logos_into_web_html()
    import generer_rapports
    generer_rapports.generate_all_reports()
