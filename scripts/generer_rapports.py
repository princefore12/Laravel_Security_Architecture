"""
Générateur unifié des rapports académiques complets (9 à 10 pages A4) pour le Groupe 5 (UT LOKO)
Thème n° 12 : La sécurité dans une application Laravel
Sans aucune mention d'oral ou de durée ; avec schémas techniques, captures d'écran réelles,
annexes de validation PHPUnit et bibliographie/webographie complète.

Produit :
  - livrables/office/Rapport_Securite_Laravel_Groupe5.docx
  - livrables/office/Rapport_Securite_Laravel_Groupe5.pdf
  - livrables/web-interactif/rapport.html
  - livrables/web-interactif/Rapport_Web_Groupe5.pdf
"""

import base64
import html
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor as DocxRGB
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
# SOURCE DE VÉRITÉ UNIQUE DU CONTENU ACADÉMIQUE
# ==============================================================================

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
    ("A03:2021 Injection (XSS)", "{!! $student->bio !!} sans CSP", "Blade {{ }} + SecurityHeadersMiddleware", "HTML échappé & CSP"),
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
    ("test_dashboard_loads_and_lists_all_five_pillars", "Tableau de bord (GET /)", "Vérifie le statut HTTP 200 et l'affichage des 5 piliers et membres."),
    ("test_pillar_1_sqli_exploits_..._and_is_blocked_...", "Pilier 1 : SQLi", "Prouve le bypass ' OR '1'='1 en mode vulnérable et le blocage PDO en mode sécurisé."),
    ("test_pillar_2_mass_assignment_escalates_..._blocked", "Pilier 2 : Mass Assignment", "Prouve l'escalade role=admin via forceFill() et son rejet par FormRequest + #[Fillable]."),
    ("test_pillar_3_xss_renders_raw_..._and_escaped_...", "Pilier 3 : XSS & CSP", "Prouve la sortie brute en vulnérable vs <img> + en-têtes CSP/nosniff/DENY en sécurisé."),
    ("test_pillar_4_csrf_exempt_route_succeeds_...", "Pilier 4 : CSRF", "Vérifie la modification sans jeton sur route exemptée et la protection sur route sécurisée."),
    ("test_pillar_5_idor_password_hashing_and_rate_limiting", "Pilier 5 : IDOR/Bcrypt/429", "Valide GradePolicy (403), Hash::check (bcrypt $2y$) et RateLimiter (429 au 6e essai)."),
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


# ==============================================================================
# PARTIE 1 : RAPPORT WORD (.DOCX) — 9 À 10 PAGES
# ==============================================================================

def docx_rgb(c):
    return DocxRGB(c[0], c[1], c[2])


def shade_cell(cell, hex_color):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=85, bottom=85, left=120, right=120):
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


def d_heading(doc, text, author=""):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    pPr = p._p.get_or_add_pPr()
    pBdr = parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="8B1518"/></w:pBdr>')
    pPr.append(pBdr)
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Segoe UI"
    r.font.size = Pt(14.5)
    r.font.color.rgb = docx_rgb(C_RED)
    if author:
        r2 = p.add_run(f"   — {author}")
        r2.bold = True
        r2.font.name = "Segoe UI"
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = docx_rgb(C_SLATE)


def d_sub(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    r.bold = True
    r.font.name = "Segoe UI"
    r.font.size = Pt(11.5)
    r.font.color.rgb = docx_rgb(C_NAVY)


def d_para(doc, text, bold_prefix=""):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(5.5)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.bold = True
        rb.font.name = "Segoe UI"
        rb.font.size = Pt(10)
        rb.font.color.rgb = docx_rgb(C_NAVY)
    r = p.add_run(text)
    r.font.name = "Segoe UI"
    r.font.size = Pt(10)
    r.font.color.rgb = docx_rgb((30, 41, 59))


def d_bullet(doc, lead, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.6)
    p.paragraph_format.space_after = Pt(3.5)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    rb = p.add_run(f"▪ {lead} : ")
    rb.bold = True
    rb.font.name = "Segoe UI"
    rb.font.size = Pt(9.8)
    rb.font.color.rgb = docx_rgb(C_RED)
    r = p.add_run(text)
    r.font.name = "Segoe UI"
    r.font.size = Pt(9.8)
    r.font.color.rgb = docx_rgb((30, 41, 59))


def d_callout(doc, title, text, bg="EFF6FF", border="2563EB"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color=border, sz="8")
    c = tbl.cell(0, 0)
    c.width = Cm(17.4)
    shade_cell(c, bg)
    set_cell_margins(c, 90, 90, 140, 140)
    p = c.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    rt = p.add_run(f"{title} — ")
    rt.bold = True
    rt.font.name = "Segoe UI"
    rt.font.size = Pt(9.8)
    rt.font.color.rgb = docx_rgb(C_NAVY)
    rb = p.add_run(text)
    rb.font.name = "Segoe UI"
    rb.font.size = Pt(9.6)
    rb.font.color.rgb = docx_rgb(C_SLATE)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)


def d_compare(doc, v_title, v_code, v_note, s_title, s_code, s_note):
    tbl = doc.add_table(rows=2, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color="CBD5E1", sz="6")
    for ci, (ht, hc, hb) in enumerate([(v_title, "991B1B", "FEE2E2"), (s_title, "065F46", "D1FAE5")]):
        cell = tbl.cell(0, ci)
        cell.width = Cm(8.7)
        shade_cell(cell, hb)
        set_cell_margins(cell, 75, 75, 110, 110)
        r = cell.paragraphs[0].add_run(ht)
        r.bold = True
        r.font.name = "Segoe UI"
        r.font.size = Pt(9.5)
        r.font.color.rgb = DocxRGB.from_string(hc)
    for ci, (cd, nt, bb) in enumerate([(v_code, v_note, "FEF2F2"), (s_code, s_note, "ECFDF5")]):
        cell = tbl.cell(1, ci)
        cell.width = Cm(8.7)
        shade_cell(cell, bb)
        set_cell_margins(cell, 85, 85, 110, 110)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(4)
        rc = p.add_run(cd)
        rc.font.name = "Consolas"
        rc.font.size = Pt(8.2)
        rc.font.color.rgb = docx_rgb(C_NAVY)
        p2 = cell.add_paragraph()
        p2.paragraph_format.space_after = Pt(0)
        rn = p2.add_run(nt)
        rn.font.name = "Segoe UI"
        rn.font.size = Pt(9)
        rn.font.color.rgb = docx_rgb(C_SLATE)
    doc.add_paragraph().paragraph_format.space_after = Pt(3)


def d_figure(doc, img_path: Path, caption: str, width_cm: float = 16.5):
    if not img_path.exists():
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(img_path), width=Cm(width_cm))
    pc = doc.add_paragraph()
    pc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pc.paragraph_format.space_after = Pt(6)
    rc = pc.add_run(caption)
    rc.italic = True
    rc.font.name = "Segoe UI"
    rc.font.size = Pt(8.8)
    rc.font.color.rgb = docx_rgb(C_SLATE)


def d_table(doc, headers, rows, widths_cm):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    for ci, h in enumerate(headers):
        c = tbl.cell(0, ci)
        c.width = Cm(widths_cm[ci])
        shade_cell(c, "8B1518")
        set_cell_margins(c, 70, 70, 90, 90)
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.name = "Segoe UI"
        r.font.size = Pt(9.2)
        r.font.color.rgb = docx_rgb(C_WHITE)
    for ri, row in enumerate(rows, start=1):
        for ci, val in enumerate(row):
            c = tbl.cell(ri, ci)
            c.width = Cm(widths_cm[ci])
            if ri % 2 == 0:
                shade_cell(c, "F8FAFC")
            set_cell_margins(c, 65, 65, 90, 90)
            r = c.paragraphs[0].add_run(val)
            r.font.name = "Segoe UI"
            r.font.size = Pt(8.8)
            r.bold = (ci == 0)
            r.font.color.rgb = docx_rgb(C_NAVY)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)


def build_docx_report() -> Path:
    doc = Document()
    for sec in doc.sections:
        sec.top_margin = Cm(1.4)
        sec.bottom_margin = Cm(1.4)
        sec.left_margin = Cm(1.6)
        sec.right_margin = Cm(1.6)
        sec.different_first_page_header_footer = True
        hdr = sec.header.paragraphs[0]
        hdr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        rh = hdr.add_run("UT LOKO • Licence 3 Informatique • Groupe 5 — La sécurité dans une application Laravel")
        rh.font.name = "Segoe UI"
        rh.font.size = Pt(8.5)
        rh.font.color.rgb = docx_rgb(C_SLATE)
        ftr = sec.footer.paragraphs[0]
        ftr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        rf = ftr.add_run("Année académique 2025–2026  |  Professeur : M. CAMARA  |  Module Base de données (XAMPP) & Framework Laravel")
        rf.font.name = "Segoe UI"
        rf.font.size = Pt(8.5)
        rf.font.color.rgb = docx_rgb(C_SLATE)

    # ---- PAGE 1 : PAGE DE GARDE UT LOKO CORRIGÉE ----
    top_tbl = doc.add_table(rows=1, cols=3)
    top_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(top_tbl, val="none")
    c0, c1, c2 = top_tbl.cell(0, 0), top_tbl.cell(0, 1), top_tbl.cell(0, 2)
    c0.width, c1.width, c2.width = Cm(3.5), Cm(10.5), Cm(3.2)
    for c in (c0, c1, c2):
        c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    if LOGO_CI.exists():
        c0.paragraphs[0].add_run().add_picture(str(LOGO_CI), width=Cm(3.0))
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
    lp0 = left_c.paragraphs[0]
    lp0.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if LOGO_UT.exists():
        lp0.add_run().add_picture(str(LOGO_UT), width=Cm(4.5))
    for lbl, val in [
        ("DÉPARTEMENT :", "ITER"),
        ("DOMAINE :", "SCIENCE ET TECHNOLOGIE"),
        ("MENTION :", "INFORMATIQUE ET TÉLÉCOMMUNICATION"),
        ("NIVEAU :", "LICENCE 3 — Module Base de Données (XAMPP) & Framework Laravel"),
    ]:
        lp = left_c.add_paragraph()
        lp.paragraph_format.space_before = Pt(16)
        lp.paragraph_format.space_after = Pt(4)
        rl = lp.add_run(lbl + " ")
        rl.bold = True
        rl.font.name = "Segoe UI"
        rl.font.size = Pt(10.5)
        rl.font.color.rgb = docx_rgb(C_RED)
        rv = lp.add_run(val)
        rv.font.name = "Segoe UI"
        rv.font.size = Pt(10.5)
        rv.font.color.rgb = docx_rgb(C_NAVY)

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

    add_rc("ANNÉE ACADÉMIQUE : 2025 - 2026", size=13, bold=True, before=6, after=14)
    add_rc("Spécialité : INFORMATIQUE", size=12.5, bold=True, before=4, after=20)
    add_rc("THÈME N° 12 :", size=13, bold=True, color=(253, 230, 138), before=12, after=4)
    add_rc("La sécurité dans une application Laravel", size=20, bold=True, color=C_WHITE, before=2, after=26)
    add_rc("TRAVAIL RÉALISÉ PAR (GROUPE 5) :", size=12.5, bold=True, color=(253, 230, 138), before=10, after=8)
    for nm in ["SIBY MODY", "SORE RAMATOU", "BOIN NAOMI", "TRAORÉ LEYLA CHARIFAT", "DJAN KOUASSI NOËL"]:
        add_rc(nm, size=12.5, bold=True, color=C_WHITE, before=3, after=3)
    add_rc("PROFESSEUR :", size=12.5, bold=True, color=(253, 230, 138), before=24, after=4)
    add_rc("M. CAMARA", size=15, bold=True, color=C_WHITE, before=0, after=12)
    doc.add_page_break()

    # ---- PAGE 2 : TABLE DES MATIÈRES & RÉSUMÉ EXÉCUTIF ----
    d_heading(doc, "Table des Matières & Résumé Exécutif")
    d_para(doc,
        "Ce dossier technique constitue l'étude approfondie réalisée par le Groupe 5 (Licence 3 Informatique, UT LOKO) sur le thème n° 12 : « La sécurité dans une application Laravel ». Il analyse les vulnérabilités critiques menaçant une application web reliée à un serveur de base de données MariaDB / MySQL sous XAMPP, puis détaille l'implémentation concrète des protections natives de Laravel à travers le laboratoire expérimental LOKO-Vault CyberLab (Laravel 13, PHP 8.5.12, MariaDB 10.11.16).")
    d_table(doc, ["Repère", "Intitulé du Chapitre / Section", "Auteur Référent"], TOC_ROWS, [2.2, 11.4, 3.8])

    d_sub(doc, "Répartition des contributions techniques au sein du Groupe 5")
    d_table(doc, ["Membre du Groupe 5", "Chapitre(s)", "Périmètre technique couvert dans le rapport"], CONTRIBUTIONS_ROWS, [4.2, 2.8, 10.4])

    d_callout(doc, "Environnement expérimental XAMPP & Laravel",
        "Les extraits de code, requêtes SQL observées et tests automatisés présentés dans ce rapport proviennent de l'application réelle LOKO-Vault CyberLab, exécutée sur PHP 8.5.12 et connectée à la base MariaDB loko_security_lab (port 3306 sous XAMPP).")
    doc.add_page_break()

    # ---- PAGE 3 : CHAPITRE 1 ----
    d_heading(doc, "1. Introduction Générale & Architecture de Défense en Profondeur", "Sore Ramatou")
    d_para(doc,
        "L'essor des frameworks PHP modernes comme Laravel a profondément structuré le développement d'applications web autour du patron architectural MVC (Modèle-Vue-Contrôleur). Toutefois, une architecture fonctionnelle — dotée de routes propres, de contrôleurs organisés, de vues Blade dynamiques et de migrations SQL — demeure exposée à des compromissions majeures dès lors qu'elle interagit avec des utilisateurs externes et une base de données relationnelle MariaDB.")
    d_para(doc,
        "Selon le référentiel international OWASP Top 10, la majorité des failles critiques touchent directement la couche applicative et son interface avec la base de données : contrôle d'accès défaillant (A01), failles cryptographiques (A02), injections SQL et XSS (A03), conception non sécurisée ou assignation de masse (A04), et mauvaise configuration serveur (A05).")
    d_sub(doc, "1.1. La philosophie « Secure by Default » et la défense en 7 couches")
    d_para(doc,
        "Laravel adopte le principe de sécurité par défaut : les mécanismes de protection essentiels sont activés dès l'installation du framework. Entre la requête HTTP émise par le navigateur et le moteur MariaDB sous XAMPP, une transaction traverse sept barrières successives :")
    for lead, desc in [
        ("Couche 1 — RateLimiter", "Limite la fréquence des requêtes par adresse IP ou utilisateur afin de neutraliser le brute-force (HTTP 429)."),
        ("Couche 2 — ValidateCsrfToken", "Vérifie l'authenticité des soumissions POST/PUT/PATCH/DELETE grâce au jeton @csrf (HTTP 419)."),
        ("Couche 3 — Authentification & Sessions", "Valide l'identité et protège le cookie laravel_session par l'attribut HttpOnly (HTTP 401)."),
        ("Couche 4 — Authorization (Policies & Gates)", "Contrôle le droit d'accès effectif sur chaque enregistrement SQL ciblé (HTTP 403)."),
        ("Couche 5 — Validation FormRequest", "Vérifie types, longueurs et formats avant d'extraire uniquement $request->validated() (HTTP 422)."),
        ("Couche 6 — Eloquent ORM & PDO", "Applique la liste blanche #[Fillable] et transmet les paramètres via requêtes préparées (?)."),
        ("Couche 7 — Moteur Blade & En-têtes CSP", "Échappe les sorties HTML via {{ }} et impose des restrictions navigateur via SecurityHeadersMiddleware."),
    ]:
        d_bullet(doc, lead, desc)
    d_figure(doc, DIAG_7, "Figure 1 : Architecture de défense en profondeur à 7 couches entre le navigateur et MariaDB (XAMPP).", 16.8)
    doc.add_page_break()

    # ---- PAGE 4 : CHAPITRE 2 (SQLi) ----
    d_heading(doc, "2. Pilier 1 : Injections SQL (SQLi), PDO & Eloquent ORM", "Sore Ramatou")
    d_sub(doc, "2.1. Mécanisme de l'injection SQL sur une base MariaDB")
    d_para(doc,
        "L'injection SQL (OWASP A03) survient lorsqu'une donnée provenant d'une requête HTTP est directement concaténée dans une chaîne SQL transmise à MariaDB. L'attaquant introduit des délimiteurs SQL (comme l'apostrophe ') suivis de clauses logiques toujours vraies (' OR '1'='1) ou d'opérateurs de jointure (UNION SELECT) permettant de lire d'autres tables de la base, notamment la table users contenant les e-mails, rôles et condensats de mots de passe.")
    d_sub(doc, "2.2. Fonctionnement en deux phases des requêtes préparées PDO")
    d_para(doc,
        "Eloquent ORM et le Query Builder de Laravel s'appuient sur l'extension PHP Data Objects (PDO) et ses requêtes préparées natives : (1) Laravel transmet d'abord à MariaDB le squelette de la requête contenant des marqueurs ? afin que le moteur compile l'arbre syntaxique SQL ; (2) Laravel envoie ensuite les valeurs saisies dans un tableau séparé (bindings). Dès lors, un payload tel que ' OR '1'='1 ne peut plus modifier la structure de la requête et est comparé littéralement.")
    d_compare(doc,
        "❌ CODE VULNÉRABLE (SqlInjectionController)",
        "$q = $request->input('matricule');\n$rows = DB::select(\n  \"SELECT id, matricule, full_name, filiere, moyenne\n   FROM students WHERE matricule = '{$q}'\"\n);\n// Payload UNION :\n// ' UNION SELECT id, email, password, role, 0 FROM users -- ",
        "MariaDB recompile le mot-clé UNION injecté et divulgue les colonnes sensibles de la table users.",
        "✅ CODE SÉCURISÉ (Eloquent ORM & Bindings PDO)",
        "$rows = Student::query()\n  ->where('matricule', $q)\n  ->get(['id', 'matricule', 'full_name', 'filiere', 'moyenne']);\n\n// Alternative SQL brut sécurisée :\n// DB::select('SELECT ... WHERE matricule = ?', [$q]);",
        "PDO isole le paramètre $q : l'inspecteur DB::listen confirme la présence du marqueur ? et du binding séparé.")
    d_callout(doc, "Vigilance sur les expressions SQL brutes",
        "Les méthodes avancées whereRaw(), selectRaw(), orderByRaw() et DB::raw() redeviennent vulnérables si une variable PHP y est concaténée. Il faut systématiquement fournir les paramètres dans un tableau en second argument : whereRaw('matricule = ?', [$q]).",
        bg="FEF3C7", border="D97706")
    d_figure(doc, SCR_SQLI, "Figure 2 : Capture réelle de LOKO-Vault — Injection SQL (' OR '1'='1) et requête capturée par SqlInspectorService.", 16.0)
    doc.add_page_break()

    # ---- PAGE 5 : CHAPITRE 3 (MASS ASSIGNMENT) ----
    d_heading(doc, "3. Pilier 2 : Mass Assignment, Intégrité BDD & FormRequest", "Siby Mody")
    d_sub(doc, "3.1. Escalade de privilèges sur la colonne users.role")
    d_para(doc,
        "Pour accélérer la persistance des formulaires, Eloquent permet de créer ou de mettre à jour une ligne SQL à partir d'un tableau associatif (User::create(...) ou $user->update(...)). Lorsque le développeur passe sans filtre l'intégralité des entrées HTTP via $request->all() ou contourne les protections avec forceFill(), un attaquant peut ajouter manuellement un champ caché role=admin dans la requête POST. Dans la table users de MariaDB, cette manipulation déclenche une escalade de privilèges immédiate.")
    d_sub(doc, "3.2. Liste blanche (#[Fillable] / $fillable) contre liste noire ($guarded)")
    d_bullet(doc, "Liste blanche (#[Fillable(['name', 'email', 'password'])] en Laravel 13 ou $fillable)",
        "Seuls les attributs explicitement listés peuvent être modifiés par assignation de masse. La colonne role est automatiquement ignorée, même si elle figure dans la requête HTTP.")
    d_bullet(doc, "Liste noire ($guarded = ['role'])",
        "Approche risquée : toute nouvelle colonne sensible ajoutée ultérieurement par migration devient immédiatement exposée si l'on oublie de mettre à jour $guarded. Quant à $guarded = [], il désactive toute protection.")
    d_sub(doc, "3.3. La double barrière : UpdateProfileRequest + Modèle Eloquent")
    d_compare(doc,
        "❌ CODE VULNÉRABLE (MassAssignmentController)",
        "public function updateVulnerable(Request $request)\n{\n    $user = User::where('email', 'mody.siby@loko.ci')\n                ->firstOrFail();\n    $user->forceFill($request->only(['name', 'email', 'role']))\n         ->save();\n}",
        "Génère UPDATE users SET role = 'admin' WHERE id = ? dans MariaDB.",
        "✅ DOUBLE BARRIÈRE (FormRequest + #[Fillable])",
        "// 1. UpdateProfileRequest::rules()\nreturn ['name' => ['required', 'string', 'max:100'],\n        'email' => ['required', 'email', 'max:150']];\n// 2. Contrôleur sécurisé + #[Fillable] sur User :\n$user->update($request->validated());",
        "validated() exclut role dès la couche HTTP, et #[Fillable] verrouille l'ORM.")
    d_callout(doc, "Modification légitime d'un rôle par l'administrateur",
        "L'exclusion de role dans #[Fillable] n'empêche pas l'administration du système : un contrôleur protégé par une Policy d'administration assigne explicitement la propriété ($user->role = 'admin'; $user->save();).",
        bg="ECFDF5", border="059669")
    doc.add_page_break()

    # ---- PAGE 6 : CHAPITRE 4 (XSS & BLADE) ----
    d_heading(doc, "4. Pilier 3 : Cross-Site Scripting (XSS), Blade & CSP", "Boin Naomi")
    d_sub(doc, "4.1. Typologie XSS et rôle de la base MariaDB comme vecteur")
    d_para(doc,
        "La faille Cross-Site Scripting (XSS) permet l'exécution de code JavaScript arbitraire dans le navigateur d'une victime. On distingue la XSS réfléchie (payload renvoyé dans l'URL), la XSS DOM-based, et surtout la XSS stockée (Stored XSS) : l'attaquant enregistre une balise malveillante dans une colonne MariaDB (comme le champ students.bio), qui infecte ensuite chaque enseignant ou administrateur consultant la fiche étudiant.")
    d_sub(doc, "4.2. Échappement automatique Blade : {{ }} contre {!! !!}")
    d_para(doc,
        "Le moteur de templates Blade compile les doubles accolades {{ $student->bio }} en un appel au helper PHP e(), qui exécute htmlspecialchars($value, ENT_QUOTES, 'UTF-8', true). Les chevrons < et > deviennent &lt; et &gt;, neutralisant toute balise HTML ou attribut événementiel (onerror, onload). À l'inverse, la syntaxe brute {!! $student->bio !!} désactive cette protection.")
    d_compare(doc,
        "❌ RENDU BLADE BRUT ({!! !!})",
        "<div class=\"bio-preview\">\n    {!! $student->bio !!}\n</div>\n<!-- Payload en BDD : -->\n<!-- <img src=\"x\" onerror=\"...\"> -->",
        "Le navigateur interprète le HTML stocké en base et exécute le JavaScript malveillant.",
        "✅ ÉCHAPPEMENT {{ }} + SECURITYHEADERSMIDDLEWARE",
        "<div class=\"bio-preview\">\n    {{ $student->bio }}\n</div>\n// En-têtes HTTP ajoutés sur /lab/xss/secure :\n// Content-Security-Policy, nosniff, X-Frame-Options: DENY",
        "Le code injecté s'affiche sous forme de texte inerte et le navigateur bloque les scripts non autorisés.")
    d_sub(doc, "4.3. Défense en profondeur : En-têtes HTTP et cookies HttpOnly")
    d_bullet(doc, "SecurityHeadersMiddleware",
        "Injecte Content-Security-Policy (restreint l'origine des scripts et interdit les objets actifs object-src 'none'), X-Content-Type-Options: nosniff et X-Frame-Options: DENY (anti-Clickjacking).")
    d_bullet(doc, "Attribut HttpOnly sur laravel_session",
        "Activé par défaut dans config/session.php ('http_only' => true), il interdit à document.cookie en JavaScript d'accéder à l'identifiant de session.")
    d_bullet(doc, "Cas du HTML riche (WYSIWYG)",
        "Lorsqu'une mise en forme HTML légitime est requise avant {!! !!}, la saisie doit impérativement être filtrée côté serveur par une liste blanche stricte (ex. HTMLPurifier).")
    doc.add_page_break()

    # ---- PAGE 7 : CHAPITRE 5 (CSRF & SESSIONS) ----
    d_heading(doc, "5. Pilier 4 : Cross-Site Request Forgery (CSRF) & Sessions", "Traoré Charifat Leyla")
    d_sub(doc, "5.1. Principe de la falsification de requête inter-sites")
    d_para(doc,
        "Lorsqu'un utilisateur est authentifié sur LOKO-Vault, son navigateur joint automatiquement le cookie laravel_session à toute requête destinée au domaine de l'application. Une attaque CSRF exploite ce comportement : un site externe piégé (illustré par la route /lab/csrf/evil-site) soumet silencieusement un formulaire caché en méthode POST vers l'application cible. Si le serveur ne vérifie pas l'origine légitime du formulaire, la modification est appliquée dans MariaDB à l'insu de l'utilisateur.")
    d_sub(doc, "5.2. Fonctionnement cryptographique de @csrf et ValidateCsrfToken")
    d_para(doc,
        "Laravel génère pour chaque session un jeton cryptographique aléatoire de 40 caractères. Dans les formulaires Blade, la directive @csrf injecte un champ caché <input type=\"hidden\" name=\"_token\" value=\"...\">. Lors de la soumission, le middleware ValidateCsrfToken compare le jeton reçu à celui de la session à l'aide de hash_equals() (comparaison en temps constant prévenant les attaques temporelles). En cas d'absence ou de divergence, Laravel lève une TokenMismatchException et retourne le code HTTP 419 Page Expired.")
    d_compare(doc,
        "❌ ROUTE EXEMPTE OU ACTION EN GET",
        "// bootstrap/app.php (exemption dangereuse)\n$middleware->validateCsrfTokens(except: [\n    'lab/csrf/vulnerable-update',\n]);\n// Ou : Route::get('/grades/reset/{id}', ...);",
        "Une page externe modifie frauduleusement la note en base MariaDB (20/20) sans jeton _token.",
        "✅ PROTECTION @csrf & SAMESITE=LAX",
        "<form method=\"POST\" action=\"{{ route('lab.csrf.secure-update') }}\">\n    @csrf\n    <input type=\"number\" name=\"score\" value=\"15.75\">\n    <button type=\"submit\">Valider</button>\n</form>",
        "Toute requête issue du site piège externe sans jeton valide est stoppée par HTTP 419.")
    d_bullet(doc, "Sémantique HTTP (RFC 9110)",
        "Les requêtes GET doivent rester strictement sûres et idempotentes (lecture seule) ; toute opération modifiant MariaDB doit employer POST, PUT, PATCH ou DELETE.")
    d_bullet(doc, "Requêtes AJAX et SameSite",
        "Les appels fetch/Axios transmettent le jeton via l'en-tête HTTP X-CSRF-TOKEN (<meta name=\"csrf-token\">), complétés par 'same_site' => 'lax' dans config/session.php.")
    doc.add_page_break()

    # ---- PAGE 8 : CHAPITRE 6 (BCRYPT, IDOR, RATE LIMITER) ----
    d_heading(doc, "6. Pilier 5 : Cryptographie, IDOR (Policies) & RateLimiter", "Djan Kouassi Noël")
    d_sub(doc, "6.1. Stockage des mots de passe : bcrypt / Argon2id contre MD5")
    d_para(doc,
        "Les fonctions de hachage rapides et non salées comme MD5 ou SHA-1 sont vulnérables aux tables arc-en-ciel (Rainbow Tables) et au cassage par GPU. Laravel impose par défaut bcrypt (ou Argon2id) via Hash::make() et le cast Eloquent 'password' => 'hashed'. Chaque condensat de 60 caractères ($2y$12$...) intègre un sel aléatoire de 128 bits et un facteur de coût BCRYPT_ROUNDS=12.")
    d_bullet(doc, "Hachage (Hash::make) vs Chiffrement (Crypt::encryptString)",
        "Le hachage est irréversible (vérifié uniquement via Hash::check) et dédié aux mots de passe ; le chiffrement AES-256-CBC (clé APP_KEY) est réversible via Crypt::decryptString pour les données sensibles devant être relues.")
    d_sub(doc, "6.2. Authentification vs Autorisation : prévenir l'IDOR avec GradePolicy")
    d_para(doc,
        "Vérifier qu'un utilisateur est connecté (HTTP 401) ne garantit pas qu'il soit autorisé à consulter un objet donné. La faille IDOR (Insecure Direct Object Reference) permet à un étudiant connecté de modifier l'identifiant d'URL (/grades/1 vers /grades/2) pour lire le relevé d'un camarade. La classe GradePolicy impose : $user->isAdmin() || $grade->student?->user_id === $user->id, renvoyant HTTP 403 Forbidden en cas de violation.")
    d_sub(doc, "6.3. Protection contre le Brute-Force via RateLimiter")
    d_para(doc,
        "Dans AccessControlController, la façade RateLimiter limite à 5 le nombre de tentatives d'authentification par minute et par adresse IP. Dès la 6e requête consécutive, Laravel bloque l'accès avec le statut HTTP 429 Too Many Requests.")
    d_figure(doc, SCR_ACCESS, "Figure 3 : Atelier 5 dans LOKO-Vault — Contrôle d'accès IDOR (GradePolicy), comparateur bcrypt et RateLimiter.", 15.8)
    doc.add_page_break()

    # ---- PAGE 9 : CHAPITRE 7 (ARCHITECTURE BDD, DURCISSEMENT & CONCLUSION) ----
    d_heading(doc, "7. Architecture MariaDB XAMPP, Durcissement & Conclusion", "Groupe 5")
    d_sub(doc, "7.1. Modèle physique de la base loko_security_lab (XAMPP)")
    d_para(doc,
        "L'application repose sur quatre tables InnoDB créées par migration Laravel dans MariaDB 10.11.16 : users (comptes et rôles), students (dossiers L3 reliés par clé étrangère user_id avec ON DELETE CASCADE), grades (relevés de notes liés par student_id) et security_logs (audit temps réel alimenté par SqlInspectorService::capture via DB::listen).")
    d_figure(doc, DIAG_BDD, "Figure 4 : Schéma relationnel MariaDB (loko_security_lab) sous XAMPP.", 15.6)
    d_figure(doc, SCR_DASH, "Figure 5 : Tableau de bord LOKO-Vault affichant les métriques et le journal MariaDB security_logs.", 15.2)

    d_sub(doc, "7.2. Passage de XAMPP (Développement) à la Production : Checklist de durcissement")
    d_table(doc, ["Paramètre", "Configuration XAMPP locale", "Obligatoire en Production", "Risque prévenu"], ENV_HARDENING, [3.2, 3.6, 4.6, 6.0])

    d_sub(doc, "7.3. Conclusion Générale")
    d_para(doc,
        "À l'issue de cette étude et de la mise en œuvre du laboratoire LOKO-Vault sous XAMPP, il apparaît que Laravel fournit un écosystème de sécurité complet contre les risques majeurs du web moderne. L'efficacité réelle de cette protection repose toutefois sur le respect rigoureux des conventions du framework par l'équipe de développement : requêtes préparées PDO, listes blanches #[Fillable] et FormRequest, échappement Blade {{ }}, jetons @csrf, hachage bcrypt, Policies d'autorisation et durcissement de l'environnement MariaDB.")
    doc.add_page_break()

    # ---- PAGE 10 : ANNEXES & BIBLIOGRAPHIE ----
    d_heading(doc, "8. Annexes Techniques & Bibliographie")
    d_sub(doc, "Annexe A — Matrice de synthèse OWASP Top 10 ↔ Mécanismes Laravel")
    d_table(doc, ["Menace OWASP", "Pratique Vulnérable (❌)", "Mécanisme Laravel (✅)", "Effet / Statut"], OWASP_MATRIX, [3.8, 4.6, 5.4, 3.6])

    d_sub(doc, "Annexe B — Protocole de validation automatisée (PHPUnit 12)")
    d_para(doc,
        "L'intégralité des scénarios vulnérables et sécurisés est vérifiée automatiquement par la commande php artisan test (8 tests, 50 assertions validées dans tests/Feature/SecurityLabTest.php et ExampleTest.php) :")
    d_table(doc, ["Méthode de Test", "Atelier vérifié", "Assertions validées"], TEST_CASES, [6.2, 3.6, 7.6])

    d_sub(doc, "Bibliographie & Webographie Officielle")
    for auth, title, url in BIBLIOGRAPHY:
        d_bullet(doc, auth, f"{title} Disponible sur : {url}")

    out_docx = OFFICE_DIR / "Rapport_Securite_Laravel_Groupe5.docx"
    doc.save(str(out_docx))
    print("Saved 10-page DOCX:", out_docx)
    return out_docx


# ==============================================================================
# PARTIE 2 : RAPPORT PDF REPORTLAB (10 PAGES CALIBRÉES)
# ==============================================================================

def build_pdf_report(pdf_path: Path):
    col_red = colors.HexColor("#8B1518")
    col_gold = colors.HexColor("#D97706")
    col_navy = colors.HexColor("#0F172A")
    col_slate = colors.HexColor("#334155")
    col_vuln_bg = colors.HexColor("#FEF2F2")
    col_vuln_bd = colors.HexColor("#DC2626")
    col_sec_bg = colors.HexColor("#ECFDF5")
    col_sec_bd = colors.HexColor("#059669")

    from reportlab.pdfgen import canvas as rl_canvas

    class NumberedCanvas(rl_canvas.Canvas):
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
                if self._pageNumber > 1:
                    self.saveState()
                    self.setStrokeColor(col_red)
                    self.setLineWidth(1)
                    self.line(1.4 * cm, A4[1] - 1.15 * cm, A4[0] - 1.4 * cm, A4[1] - 1.15 * cm)
                    self.setFont("Helvetica", 8)
                    self.setFillColor(col_slate)
                    self.drawString(1.4 * cm, A4[1] - 0.95 * cm, "UT LOKO • Licence 3 Informatique • Groupe 5")
                    self.drawRightString(A4[0] - 1.4 * cm, A4[1] - 0.95 * cm, "La sécurité dans une application Laravel")
                    self.line(1.4 * cm, 1.15 * cm, A4[0] - 1.4 * cm, 1.15 * cm)
                    self.drawString(1.4 * cm, 0.78 * cm, "Module : Base de Données (XAMPP / MariaDB) & Framework Laravel | Prof. M. CAMARA")
                    self.drawRightString(A4[0] - 1.4 * cm, 0.78 * cm, f"Page {self._pageNumber} / {num_pages}")
                    self.restoreState()
                super().showPage()
            super().save()

    styles = getSampleStyleSheet()
    st_h1 = ParagraphStyle("LH1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=13.2,
                           textColor=col_red, spaceBefore=3, spaceAfter=5)
    st_h2 = ParagraphStyle("LH2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.6,
                           textColor=col_navy, spaceBefore=6, spaceAfter=3)
    st_body = ParagraphStyle("LB", parent=styles["Normal"], fontName="Helvetica", fontSize=9.3,
                             leading=13.0, textColor=colors.HexColor("#1E293B"), alignment=TA_JUSTIFY, spaceAfter=4.5)
    st_bullet = ParagraphStyle("LBul", parent=styles["Normal"], fontName="Helvetica", fontSize=9.0,
                               leading=12.2, leftIndent=12, textColor=colors.HexColor("#1E293B"), alignment=TA_JUSTIFY, spaceAfter=3)
    st_bib = ParagraphStyle("LBib", parent=styles["Normal"], fontName="Helvetica", fontSize=8.1,
                            leading=10.5, leftIndent=10, textColor=colors.HexColor("#1E293B"), spaceAfter=2.2)
    st_code = ParagraphStyle("LC", parent=styles["Code"], fontName="Courier", fontSize=7.7,
                             leading=10, textColor=col_navy)
    st_tbl = ParagraphStyle("LT", parent=styles["Normal"], fontName="Helvetica", fontSize=8.0, leading=10.4)
    st_tbl_hdr = ParagraphStyle("LTH", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.3, textColor=colors.white)
    st_cap = ParagraphStyle("LCap", parent=styles["Normal"], fontName="Helvetica-Oblique", fontSize=8.2,
                            alignment=TA_CENTER, textColor=col_slate, spaceBefore=2, spaceAfter=4)

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=1.4 * cm,
        rightMargin=1.4 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
    )
    story = []

    def p_h1(title, author=""):
        suffix = f" <font size='9.5' color='#475569'>— {esc(author)}</font>" if author else ""
        story.append(Paragraph(f"{esc(title)}{suffix}", st_h1))

    def p_tbl(headers, rows, col_widths, pad_v=3.5):
        data = [[Paragraph(esc(h), st_tbl_hdr) for h in headers]]
        for r in rows:
            data.append([Paragraph(f"<b>{esc(r[0])}</b>" if i == 0 else esc(c), st_tbl) for i, c in enumerate(r)])
        t = Table(data, colWidths=[w * cm for w in col_widths])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), col_red),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), pad_v),
            ("BOTTOMPADDING", (0, 0), (-1, -1), pad_v),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.16 * cm))

    def p_cmp(v_title, v_code, v_note, s_title, s_code, s_note):
        tbl = Table([
            [Paragraph(f"<b>{esc(v_title)}</b>", ParagraphStyle("VT", fontSize=8.6, textColor=col_vuln_bd)),
             Paragraph(f"<b>{esc(s_title)}</b>", ParagraphStyle("ST", fontSize=8.6, textColor=col_sec_bd))],
            [Paragraph(esc(v_code).replace("\n", "<br/>") + f"<br/><br/><font size='8' color='#475569'>{esc(v_note)}</font>", st_code),
             Paragraph(esc(s_code).replace("\n", "<br/>") + f"<br/><br/><font size='8' color='#475569'>{esc(s_note)}</font>", st_code)],
        ], colWidths=[9.0 * cm, 9.0 * cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), col_vuln_bg),
            ("BACKGROUND", (1, 0), (1, -1), col_sec_bg),
            ("BOX", (0, 0), (0, -1), 1, col_vuln_bd),
            ("BOX", (1, 0), (1, -1), 1, col_sec_bd),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 7),
            ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ]))
        story.append(tbl)
        story.append(Spacer(1, 0.2 * cm))

    def p_callout(title, body, bg="#EFF6FF", bd="#2563EB"):
        t = Table([[Paragraph(f"<b>{esc(title)} :</b> {esc(body)}",
                              ParagraphStyle("CO", fontSize=8.8, leading=12.2, textColor=col_navy))]],
                  colWidths=[18.0 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor(bd)),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.2 * cm))

    def p_img(path: Path, caption: str, w_cm: float, h_cm: float):
        if not path.exists():
            return
        im = RlImage(str(path), width=w_cm * cm, height=h_cm * cm)
        im.hAlign = "CENTER"
        story.append(im)
        story.append(Paragraph(esc(caption), st_cap))

    # --- PAGE 1 : COUVERTURE OFFICIELLE ---
    ci_img = RlImage(str(LOGO_CI), width=2.8 * cm, height=1.55 * cm) if LOGO_CI.exists() else Paragraph("", st_body)
    gl_img = RlImage(str(LOGO_GL), width=2.1 * cm, height=1.9 * cm) if LOGO_GL.exists() else Paragraph("", st_body)
    ministry_p = Paragraph(
        "<b>Ministère de l'Enseignement Supérieur<br/>et de la Recherche Scientifique</b>",
        ParagraphStyle("Min", fontName="Helvetica-Bold", fontSize=11, alignment=TA_CENTER, leading=14, textColor=col_navy),
    )
    top_banner = Table([[ci_img, ministry_p, gl_img]], colWidths=[3.5 * cm, 11.2 * cm, 3.5 * cm])
    top_banner.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (2, 0), (2, 0), "RIGHT")]))
    story.append(top_banner)
    story.append(Spacer(1, 0.55 * cm))

    ut_img = RlImage(str(LOGO_UT), width=4.4 * cm, height=3.9 * cm) if LOGO_UT.exists() else Paragraph("UT LOKO", st_h1)
    left_flow = [
        ut_img,
        Spacer(1, 0.9 * cm),
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
        Spacer(1, 1.1 * cm),
        Paragraph("<u>TRAVAIL RÉALISÉ PAR (GROUPE 5) :</u>", st_r_gold),
        Spacer(1, 0.3 * cm),
        Paragraph("SIBY MODY<br/>SORE RAMATOU<br/>BOIN NAOMI<br/>TRAORÉ LEYLA CHARIFAT<br/>DJAN KOUASSI NOËL",
                  ParagraphStyle("Auth", fontName="Helvetica-Bold", fontSize=12, leading=20, alignment=TA_CENTER, textColor=colors.white)),
        Spacer(1, 1.1 * cm),
        Paragraph("PROFESSEUR :", st_r_gold),
        Paragraph("M. CAMARA", ParagraphStyle("Prof", fontName="Helvetica-Bold", fontSize=14, alignment=TA_CENTER, textColor=colors.white)),
    ]
    cover_tbl = Table([[left_flow, right_flow]], colWidths=[6.5 * cm, 11.7 * cm], rowHeights=[22.4 * cm])
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

    # --- PAGE 2 : TABLE DES MATIÈRES & RÉSUMÉ ---
    p_h1("Table des Matières & Résumé Exécutif")
    story.append(Paragraph(
        "Ce document technique présente l'étude approfondie menée par le <b>Groupe 5</b> (Licence 3 Informatique, UT LOKO) sur <b>la sécurité dans une application Laravel</b>. Il examine comment les failles web majeures ciblent l'interface entre le code PHP et le serveur de base de données <b>MariaDB / MySQL (XAMPP)</b>, et détaille l'implémentation des boucliers natifs de Laravel au sein du laboratoire applicatif expérimental <b>LOKO-Vault CyberLab</b> (Laravel 13, PHP 8.5.12).",
        st_body))
    p_tbl(["Repère", "Intitulé du Chapitre / Section", "Auteur Référent"], TOC_ROWS, [2.2, 11.8, 4.0])
    story.append(Paragraph("Répartition des contributions techniques du Groupe 5", st_h2))
    p_tbl(["Membre du Groupe 5", "Chapitre(s)", "Périmètre technique couvert"], CONTRIBUTIONS_ROWS, [4.2, 2.8, 11.0])
    p_callout("Validation expérimentale sous XAMPP",
        "Chaque chapitre s'appuie sur des contrôles réels exécutés sur la base MariaDB loko_security_lab (port 3306) ainsi que sur une batterie de tests automatisés PHPUnit (8 tests, 50 assertions).")
    story.append(PageBreak())

    # --- PAGE 3 : CHAPITRE 1 ---
    p_h1("1. Introduction Générale & Défense en Profondeur", "Sore Ramatou")
    story.append(Paragraph(
        "Le développement d'une application web robuste sous Laravel ne se limite pas à l'organisation MVC, au routage, aux contrôleurs, aux gabarits Blade et aux migrations SQL. Dès qu'un système informatique traite des comptes étudiants, des relevés académiques ou des droits d'administration dans une base MariaDB sous XAMPP, sa surface d'attaque devient critique. Selon le référentiel <b>OWASP Top 10</b>, les vulnérabilités liées au contrôle d'accès (A01), à la cryptographie (A02), aux injections SQL/XSS (A03), à la conception (A04) et aux mauvaises configurations (A05) représentent les vecteurs de compromission les plus fréquents.",
        st_body))
    story.append(Paragraph("1.1. Le principe « Secure by Default » et les 7 couches Laravel", st_h2))
    story.append(Paragraph(
        "Laravel adopte une approche de défense en profondeur (Defense in Depth) : aucune requête HTTP n'atteint directement les tables InnoDB de MariaDB sans avoir franchi sept couches de filtrage successives :",
        st_body))
    for lead, txt in [
        ("Couche 1 — RateLimiter", "Limite le nombre de requêtes par IP/session et stoppe les attaques par force brute (HTTP 429)."),
        ("Couche 2 — ValidateCsrfToken", "Valide le jeton cryptographique @csrf sur toute méthode d'écriture HTTP (HTTP 419)."),
        ("Couche 3 — Authentification & Sessions", "Identifie l'utilisateur et protège le cookie laravel_session par l'attribut HttpOnly (HTTP 401)."),
        ("Couche 4 — Policies & Gates", "Vérifie la propriété de la ressource SQL ciblée pour bloquer les failles IDOR (HTTP 403)."),
        ("Couche 5 — FormRequest", "Valide les types, longueurs et n'extrait que $request->validated() (HTTP 422)."),
        ("Couche 6 — Eloquent ORM & PDO", "Verrouille les colonnes via #[Fillable] et isole les données par requêtes préparées (?)."),
        ("Couche 7 — Moteur Blade & CSP", "Échappe les sorties HTML {{ }} et applique les en-têtes SecurityHeadersMiddleware."),
    ]:
        story.append(Paragraph(f"<b>• {esc(lead)} :</b> {esc(txt)}", st_bullet))
    story.append(Spacer(1, 0.2 * cm))
    p_img(DIAG_7, "Figure 1 : Parcours d'une requête HTTP à travers les 7 couches de sécurité Laravel jusqu'à MariaDB (XAMPP).", 18.0, 6.9)
    story.append(PageBreak())

    # --- PAGE 4 : CHAPITRE 2 (SQLi) ---
    p_h1("2. Pilier 1 : Injections SQL (SQLi), PDO & Eloquent ORM", "Sore Ramatou")
    story.append(Paragraph("2.1. Nature de l'attaque et impact direct sur MariaDB", st_h2))
    story.append(Paragraph(
        "L'injection SQL se produit lorsque des paramètres saisis par l'utilisateur sont concaténés directement dans une requête SQL envoyée à MariaDB. Un attaquant peut fermer le littéral texte au moyen d'une apostrophe et injecter une condition toujours vraie (' OR '1'='1) pour extraire l'ensemble d'une table, ou détourner la requête via UNION SELECT afin de lire la table users (adresses e-mail, rôles et condensats de mots de passe).",
        st_body))
    story.append(Paragraph("2.2. Compilation en deux étapes via PDO et Eloquent ORM", st_h2))
    story.append(Paragraph(
        "Pour éliminer ce risque, Eloquent ORM et le Query Builder utilisent les requêtes préparées de l'extension PHP Data Objects (PDO). Dans un premier temps, Laravel transmet à MariaDB l'instruction SQL compilable avec des marqueurs ? ; dans un second temps, il transmet les valeurs saisies (bindings) séparément. MariaDB n'interprète jamais le contenu des paramètres comme du code SQL.",
        st_body))
    p_cmp(
        "[VULNÉRABLE] SqlInjectionController",
        "$q = $request->input('matricule');\n$rows = DB::select(\n  \"SELECT id, matricule, full_name, filiere, moyenne\n   FROM students WHERE matricule = '{$q}'\"\n);",
        "Vulnérable au bypass (' OR '1'='1) et à l'exfiltration UNION SELECT sur users.",
        "[SÉCURISÉ] Eloquent ORM & Bindings PDO",
        "$rows = Student::query()\n  ->where('matricule', $q)\n  ->get(['id', 'matricule', 'full_name', 'filiere', 'moyenne']);\n// Ou : DB::select('SELECT ... WHERE matricule = ?', [$q]);",
        "PDO isole $q dans un binding préparé : toute charge SQL devient un texte inoffensif."
    )
    p_callout("Attention aux méthodes brutes (whereRaw, selectRaw, orderByRaw)",
        "Eloquent ne protège pas les expressions brutes mal écrites comme whereRaw(\"matricule = '$q'\"). Il est impératif d'utiliser un tableau de bindings : whereRaw('matricule = ?', [$q]).",
        bg="#FEF3C7", bd="#D97706")
    p_img(SCR_SQLI, "Figure 2 : Capture de LOKO-Vault — Exploitation SQLi (' OR '1'='1) et trace SQL réelle capturée par DB::listen().", 16.5, 11.4)
    story.append(PageBreak())

    # --- PAGE 5 : CHAPITRE 3 (MASS ASSIGNMENT) ---
    p_h1("3. Pilier 2 : Mass Assignment, Intégrité BDD & FormRequest", "Siby Mody")
    story.append(Paragraph("3.1. Escalade de privilèges par assignation de masse", st_h2))
    story.append(Paragraph(
        "L'assignation de masse permet d'hydrater et de sauvegarder un modèle Eloquent en une instruction à partir d'un tableau HTTP ($user->update($request->all())). Dans la base MariaDB loko_security_lab, la table users contient une colonne sensible role ('student' ou 'admin'). Bien que le formulaire HTML visible ne propose que les champs name et email, un utilisateur malveillant peut ajouter un paramètre POST caché role=admin et obtenir ainsi les privilèges d'administrateur.",
        st_body))
    story.append(Paragraph("3.2. Liste blanche (#[Fillable] / $fillable) contre liste noire ($guarded)", st_h2))
    story.append(Paragraph(
        "<b>• Approche Liste Blanche (#[Fillable(['name', 'email', 'password'])] en Laravel 13 ou $fillable) :</b> Seules les colonnes explicitement autorisées peuvent être remplies en masse. L'attribut role reste strictement inaccessible par cette voie.",
        st_bullet))
    story.append(Paragraph(
        "<b>• Approche Liste Noire ($guarded = ['role']) :</b> Déconseillée, car toute nouvelle colonne critique ajoutée ultérieurement par migration reste vulnérable en cas d'oubli. Définir $guarded = [] ou appeler forceFill() annule toute barrière.",
        st_bullet))
    story.append(Paragraph("3.3. La double barrière de défense en profondeur", st_h2))
    p_cmp(
        "[VULNÉRABLE] forceFill non filtré",
        "$user = User::where('email', 'mody.siby@loko.ci')->firstOrFail();\n$user->forceFill($request->only(['name', 'email', 'role']))->save();",
        "Modifie directement la colonne users.role en 'admin' dans MariaDB.",
        "[SÉCURISÉ] UpdateProfileRequest + #[Fillable]",
        "// UpdateProfileRequest::rules() -> 'name' et 'email' uniquement\n$user->update($request->validated());",
        "validated() écarte 'role' en amont et #[Fillable] protège le modèle en aval."
    )
    p_callout("Attribution légitime d'un rôle par un administrateur",
        "Lorsqu'un administrateur autorisé par une Policy doit promouvoir un compte, il procède par assignation directe d'attribut : $user->role = 'admin'; $user->save();.",
        bg="#ECFDF5", bd="#059669")
    story.append(PageBreak())

    # --- PAGE 6 : CHAPITRE 4 (XSS & BLADE) ---
    p_h1("4. Pilier 3 : Cross-Site Scripting (XSS), Blade & Headers CSP", "Boin Naomi")
    story.append(Paragraph("4.1. Du stockage en base MariaDB à l'exécution navigateur (XSS Stockée)", st_h2))
    story.append(Paragraph(
        "Une faille Cross-Site Scripting (XSS) permet d'injecter du code JavaScript exécutable dans les pages affichées aux utilisateurs. Dans sa forme stockée (Stored XSS), la base MariaDB sert de vecteur persistant : une charge malveillante enregistrée dans students.bio (telle qu'une balise &lt;img src='x' onerror='...'&gt;) s'exécute automatiquement chez tout professeur ou administrateur qui ouvre la fiche de l'étudiant.",
        st_body))
    story.append(Paragraph("4.2. Échappement automatique Blade : {{ }} contre {!! !!}", st_h2))
    story.append(Paragraph(
        "Par défaut, la syntaxe Blade {{ $student->bio }} se compile en &lt;?php echo e($student->bio); ?&gt;, qui appelle htmlspecialchars(..., ENT_QUOTES, 'UTF-8', true). Tous les chevrons et guillemets sont convertis en entités HTML inertes (&amp;lt;, &amp;gt;). À l'opposé, la directive {!! $student->bio !!} affiche la chaîne brute sans filtrage et ne doit jamais être employée sur des saisies utilisateurs non purifiées.",
        st_body))
    p_cmp(
        "[VULNÉRABLE] Vue Blade ({!! !!})",
        "<div class=\"bio-preview\">\n  {!! $student->bio !!}\n</div>",
        "Exécute le JavaScript stocké dans MariaDB dès le chargement du DOM.",
        "[SÉCURISÉ] Vue Blade ({{ }}) + CSP",
        "<div class=\"bio-preview\">\n  {{ $student->bio }}\n</div>\n// + SecurityHeadersMiddleware",
        "Convertit les balises en texte inerte et applique Content-Security-Policy."
    )
    story.append(Paragraph("4.3. Défense en profondeur côté HTTP et Cookies", st_h2))
    for lead, txt in [
        ("En-têtes HTTP (SecurityHeadersMiddleware)", "Content-Security-Policy restreint les sources de scripts ; X-Content-Type-Options: nosniff empêche le MIME-sniffing ; X-Frame-Options: DENY bloque le Clickjacking."),
        ("Protection du cookie de session (HttpOnly)", "Configuré à 'http_only' => true dans config/session.php, le cookie laravel_session reste invisible pour document.cookie même si du JavaScript était injecté."),
        ("Assainissement HTML riche (WYSIWYG)", "Si du HTML enrichi doit être rendu avec {!! !!}, il doit être nettoyé côté serveur par une bibliothèque sur liste blanche comme HTMLPurifier."),
    ]:
        story.append(Paragraph(f"<b>• {esc(lead)} :</b> {esc(txt)}", st_bullet))
    story.append(PageBreak())

    # --- PAGE 7 : CHAPITRE 5 (CSRF) ---
    p_h1("5. Pilier 4 : Cross-Site Request Forgery (CSRF) & Sessions", "Traoré Charifat Leyla")
    story.append(Paragraph("5.1. Anatomie d'une attaque par falsification inter-sites", st_h2))
    story.append(Paragraph(
        "Une attaque CSRF exploite la confiance accordée par une application au navigateur d'un utilisateur déjà authentifié. Tant que la session est ouverte, le navigateur transmet automatiquement le cookie laravel_session vers le domaine cible, y compris lorsque la requête HTTP est déclenchée depuis un site tiers malveillant (simulé dans LOKO-Vault via la page piège /lab/csrf/evil-site qui poste silencieusement score=20).",
        st_body))
    story.append(Paragraph("5.2. Jeton cryptographique @csrf et ValidateCsrfToken (HTTP 419)", st_h2))
    story.append(Paragraph(
        "Laravel attribue à chaque session un jeton secret aléatoire que tout site externe est incapable de deviner. La directive Blade @csrf génère un champ caché _token dans chaque formulaire. À la réception d'une requête POST, PUT, PATCH ou DELETE, le middleware ValidateCsrfToken vérifie ce jeton en temps constant via hash_equals() (protection contre les attaques temporelles). En l'absence de jeton valide, Laravel bloque l'opération avant d'atteindre MariaDB et renvoie le code <b>HTTP 419 Page Expired</b>.",
        st_body))
    p_cmp(
        "[VULNÉRABLE] Route exempte ou GET",
        "// bootstrap/app.php :\n$middleware->validateCsrfTokens(except: ['lab/csrf/vulnerable-update']);\n// Ou : Route::get('/grades/reset/{id}', ...);",
        "Le site piège externe modifie la note en base MariaDB sans jeton _token.",
        "[SÉCURISÉ] Protection @csrf & SameSite=Lax",
        "<form method=\"POST\" action=\"{{ route('lab.csrf.secure-update') }}\">\n  @csrf\n  <input type=\"number\" name=\"score\" value=\"15.75\">\n</form>",
        "Une soumission externe sans _token échoue immédiatement avec HTTP 419."
    )
    story.append(Paragraph("<b>• Idempotence HTTP (RFC 9110) :</b> Les routes GET ne doivent jamais modifier la base de données ; elles sont réservées à la lecture.", st_bullet))
    story.append(Paragraph("<b>• AJAX &amp; Cookie SameSite :</b> Les requêtes fetch/Axios incluent l'en-tête X-CSRF-TOKEN, tandis que 'same_site' => 'lax' bloque l'envoi automatique des cookies lors de POST inter-sites.", st_bullet))
    story.append(PageBreak())

    # --- PAGE 8 : CHAPITRE 6 (BCRYPT, IDOR, RATE LIMITER) ---
    p_h1("6. Pilier 5 : Cryptographie, IDOR (Policies) & RateLimiter", "Djan Kouassi Noël")
    story.append(Paragraph("6.1. Hachage adaptatif bcrypt / Argon2id contre MD5", st_h2))
    story.append(Paragraph(
        "Stocker des mots de passe en clair ou avec MD5/SHA-1 dans MariaDB expose les comptes aux attaques par Rainbow Tables et GPU (plusieurs milliards d'empreintes par seconde, sans sel). Laravel impose le hachage unidirectionnel salé <b>bcrypt</b> (ou Argon2id) via Hash::make() et le cast 'password' => 'hashed' : un sel aléatoire de 128 bits et un facteur de coût (BCRYPT_ROUNDS=12) garantissent que deux mots de passe identiques produisent deux empreintes $2y$12$... distinctes. Contrairement à Crypt::encryptString() (chiffrement réversible AES-256-CBC), le hachage ne peut jamais être déchiffré et se vérifie via Hash::check().",
        st_body))
    story.append(Paragraph("6.2. Autorisation granulaire : bloquer l'IDOR avec GradePolicy", st_h2))
    story.append(Paragraph(
        "L'authentification (HTTP 401) vérifie l'identité de l'utilisateur, mais seule l'autorisation empêche la faille <b>IDOR (Insecure Direct Object Reference)</b> où un étudiant consulte les notes d'un autre en modifiant l'ID dans l'URL. Notre classe GradePolicy::view(User $user, Grade $grade) vérifie $user->isAdmin() || $grade->student?->user_id === $user->id et renvoie <b>HTTP 403 Forbidden</b> en cas d'accès illicite.",
        st_body))
    story.append(Paragraph("6.3. Anti-Brute-Force avec RateLimiter (HTTP 429)", st_h2))
    story.append(Paragraph(
        "La façade RateLimiter restreint les tentatives d'authentification à 5 essais par minute par IP et verrouille la 6e tentative via <b>HTTP 429 Too Many Requests</b>.",
        st_body))
    p_img(SCR_ACCESS, "Figure 3 : Capture de LOKO-Vault — Atelier 5 (GradePolicy IDOR, comparateur MD5/bcrypt et RateLimiter).", 16.5, 10.6)
    story.append(PageBreak())

    # --- PAGE 9 : CHAPITRE 7 (ARCHITECTURE BDD, DURCISSEMENT & CONCLUSION) ---
    p_h1("7. Architecture MariaDB XAMPP, Durcissement & Conclusion", "Groupe 5")
    story.append(Paragraph(
        "La base MariaDB 10.11.16 s'articule autour de quatre tables InnoDB liées par contraintes référentielles : <b>users</b> (comptes et rôles), <b>students</b> (dossiers liés par user_id FK), <b>grades</b> (notes liées par student_id FK) et <b>security_logs</b> (traçabilité SQL temps réel capturée par SqlInspectorService).",
        st_body))
    p_img(DIAG_BDD, "Figure 4 : Schéma relationnel MariaDB (loko_security_lab) sous XAMPP.", 12.2, 6.3)
    p_img(SCR_DASH, "Figure 5 : Tableau de bord LOKO-Vault et journalisation temps réel dans security_logs.", 10.2, 6.6)
    story.append(Paragraph("7.2. Checklist de durcissement XAMPP vers Production", st_h2))
    p_tbl(["Paramètre", "Développement XAMPP", "Exigence Production", "Risque prévenu"], ENV_HARDENING, [3.3, 3.6, 4.9, 6.2], pad_v=3.0)
    story.append(Paragraph(
        "<b>Conclusion générale :</b> Laravel offre une architecture de sécurité complète et éprouvée face aux menaces majeures recensées par l'OWASP. Combinée à une conception rigoureuse de la base MariaDB, au respect strict de ses conventions (Eloquent PDO, #[Fillable], FormRequest, Blade {{ }}, @csrf, bcrypt et Policies) et à une configuration serveur durcie, elle garantit la fiabilité et la confidentialité des applications modernes.",
        st_body))
    story.append(PageBreak())

    # --- PAGE 10 : ANNEXES & BIBLIOGRAPHIE ---
    p_h1("8. Annexes Techniques & Bibliographie")
    story.append(Paragraph("Annexe A — Matrice de synthèse OWASP Top 10 <-> Protections Laravel", st_h2))
    p_tbl(["Menace OWASP", "Pratique Vulnérable", "Mécanisme Laravel", "Effet / Statut"], OWASP_MATRIX, [4.0, 4.7, 5.7, 3.6], pad_v=3.0)
    story.append(Paragraph("Annexe B — Validation automatisée par suite de tests PHPUnit 12 (8 tests / 50 assertions)", st_h2))
    p_tbl(["Méthode de Test", "Atelier vérifié", "Assertions validées"], TEST_CASES, [6.4, 3.4, 8.2], pad_v=3.0)
    story.append(Paragraph("Bibliographie & Webographie Officielle", st_h2))
    for auth, title, url in BIBLIOGRAPHY:
        story.append(Paragraph(f"<b>• {esc(auth)} :</b> {esc(title)} <font color='#1D4ED8'>{esc(url)}</font>", st_bib))

    doc.build(story, canvasmaker=NumberedCanvas)
    print("Saved calibrated ReportLab PDF:", pdf_path)


# ==============================================================================
# PARTIE 3 : RAPPORT WEB INTERACTIF (rapport.html) + PDF EDGE
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

    bib_items = "".join(
        f'<li><strong>{esc(a)}</strong> — {esc(t)} <a href="{esc(u)}" target="_blank">{esc(u)}</a></li>'
        for a, t, u in BIBLIOGRAPHY
    )
    tbl_toc = html_table(["Repère", "Intitulé du Chapitre / Section", "Auteur Référent"], TOC_ROWS)
    tbl_contrib = html_table(["Membre du Groupe 5", "Chapitre(s)", "Périmètre technique couvert"], CONTRIBUTIONS_ROWS)
    tbl_env = html_table(["Paramètre", "Développement XAMPP", "Exigence Production", "Risque prévenu"], ENV_HARDENING)
    tbl_owasp = html_table(["Menace OWASP", "Pratique Vulnérable (❌)", "Mécanisme Laravel (✅)", "Effet / Statut"], OWASP_MATRIX)
    tbl_tests = html_table(["Méthode de Test", "Atelier vérifié", "Assertions validées"], TEST_CASES)

    cmp_sqli = html_cmp(
        "❌ Code Vulnérable (SqlInjectionController)",
        "$q = $request->input('matricule');\n$rows = DB::select(\n  \"SELECT id, matricule, full_name, filiere, moyenne\n   FROM students WHERE matricule = '{$q}'\"\n);",
        "Vulnérable au bypass (' OR '1'='1) et à l'exfiltration UNION SELECT sur users.",
        "✅ Solution Eloquent ORM & Bindings PDO",
        "$rows = Student::query()\n  ->where('matricule', $q)\n  ->get(['id', 'matricule', 'full_name', 'filiere', 'moyenne']);\n// SQL brut préparé : DB::select('... WHERE matricule = ?', [$q]);",
        "PDO isole $q dans un binding préparé : 0 fuite de données."
    )
    cmp_ma = html_cmp(
        "❌ Code Vulnérable (forceFill non filtré)",
        "$user = User::where('email', 'mody.siby@loko.ci')->firstOrFail();\n$user->forceFill($request->only(['name', 'email', 'role']))->save();",
        "Exécute UPDATE users SET role = 'admin' dans MariaDB.",
        "✅ Double Barrière (UpdateProfileRequest + #[Fillable])",
        "// UpdateProfileRequest::rules() : 'name' et 'email' uniquement\n$user->update($request->validated());",
        "validated() écarte 'role' en couche HTTP, #[Fillable] verrouille l'ORM."
    )
    cmp_xss = html_cmp(
        "❌ Rendu Blade Brut ({!! !!})",
        "<div class=\"bio-preview\">\n    {!! $student->bio !!}\n</div>",
        "Interprète <img src='x' onerror='...'> et exécute le JavaScript.",
        "✅ Rendu Échappé ({{ }}) + CSP",
        "<div class=\"bio-preview\">\n    {{ $student->bio }}\n</div>",
        "Transforme les balises en texte inerte (<img...>)."
    )
    cmp_csrf = html_cmp(
        "❌ Route Exempte ou Action en GET",
        "// bootstrap/app.php :\n$middleware->validateCsrfTokens(except: ['lab/csrf/vulnerable-update']);",
        "Un site tiers modifie frauduleusement la note en base MariaDB.",
        "✅ Protection @csrf & SameSite=Lax",
        "<form method=\"POST\" action=\"{{ route('lab.csrf.secure-update') }}\">\n    @csrf\n    <input type=\"number\" name=\"score\" value=\"15.75\">\n</form>",
        "Le site piège externe est bloqué par HTTP 419 Page Expired."
    )

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
  body { font-family: 'Segoe UI', system-ui, sans-serif; color: var(--slate-900); background: #E2E8F0; line-height: 1.56; font-size: 13.8px; }
  .toolbar { position: sticky; top: 0; z-index: 100; background: var(--slate-900); color: #FFF; padding: 10px 28px; display: flex; align-items: center; justify-content: space-between; border-bottom: 3px solid var(--loko-red); }
  .toolbar .btn { background: var(--loko-red); color: #FFF; border: none; padding: 7px 15px; border-radius: 6px; font-weight: 700; cursor: pointer; text-decoration: none; font-size: 13px; }
  .document-container { max-width: 920px; margin: 24px auto; display: flex; flex-direction: column; gap: 22px; }
  .page { background: #FFFFFF; padding: 38px 46px; border-radius: 6px; box-shadow: 0 10px 28px rgba(15, 23, 42, 0.12); page-break-after: always; }
  .page:last-child { page-break-after: auto; }
  .cover-page { padding: 0; overflow: hidden; min-height: 1030px; display: flex; flex-direction: column; }
  .cover-top-logos { display: flex; align-items: center; justify-content: space-between; padding: 20px 38px; border-bottom: 2px solid #E2E8F0; }
  .cover-ministry { text-align: center; font-size: 14px; font-weight: 700; color: var(--slate-800); }
  .cover-split { flex: 1; display: grid; grid-template-columns: 315px 1fr; }
  .cover-col-left { background: #FFF; padding: 38px 28px; display: flex; flex-direction: column; justify-content: space-between; border-right: 4px solid var(--loko-red); }
  .ut-emblem { text-align: center; padding: 14px; border: 1px solid #E2E8F0; border-radius: 10px; }
  .left-meta { display: flex; flex-direction: column; gap: 18px; font-size: 13.5px; }
  .cover-col-right { background: var(--loko-red); color: #FFF; padding: 48px 40px; display: flex; flex-direction: column; justify-content: space-between; text-align: center; }
  .cover-theme-box { border-top: 2px solid rgba(255,255,255,0.35); border-bottom: 2px solid rgba(255,255,255,0.35); padding: 24px 16px; }
  .cover-theme-box .label { font-size: 15px; letter-spacing: 2px; font-weight: 700; color: #FDE68A; margin-bottom: 8px; }
  .cover-theme-box h1 { font-size: 30px; font-weight: 900; line-height: 1.25; }
  .cover-authors { list-style: none; display: flex; flex-direction: column; gap: 8px; font-size: 16px; font-weight: 800; margin-top: 12px; }
  .cover-authors li { padding: 6px 12px; background: rgba(0, 0, 0, 0.18); border-radius: 6px; }
  h2.chap-title { font-size: 19px; font-weight: 900; color: var(--loko-red); border-bottom: 2.5px solid var(--loko-red); padding-bottom: 6px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; gap: 10px; }
  h2.chap-title .author-tag { font-size: 11.5px; background: var(--slate-900); color: #FDE68A; padding: 3px 11px; border-radius: 999px; font-weight: 700; white-space: nowrap; }
  h3 { font-size: 15px; font-weight: 800; color: var(--slate-800); margin: 13px 0 6px; }
  p { margin-bottom: 9px; text-align: justify; }
  ul, ol { padding-left: 22px; margin-bottom: 10px; }
  li { margin-bottom: 4px; }
  .compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin: 10px 0; }
  .box-vuln { background: var(--vuln-bg); border: 1px solid #FCA5A5; border-left: 5px solid var(--vuln-red); border-radius: 7px; padding: 11px 13px; }
  .box-sec { background: var(--sec-bg); border: 1px solid #6EE7B7; border-left: 5px solid var(--sec-green); border-radius: 7px; padding: 11px 13px; }
  .box-title { font-weight: 800; font-size: 12.5px; margin-bottom: 6px; text-transform: uppercase; }
  .box-vuln .box-title { color: #991B1B; }
  .box-sec .box-title { color: #065F46; }
  .box-note { font-size: 12.2px; color: var(--slate-700); margin-top: 6px; margin-bottom: 0; }
  pre { background: #0F172A; color: #F8FAFC; padding: 9px 11px; border-radius: 6px; font-family: 'Cascadia Code', Consolas, monospace; font-size: 11.2px; line-height: 1.42; overflow-x: auto; white-space: pre-wrap; }
  code { font-family: 'Cascadia Code', Consolas, monospace; background: #F1F5F9; padding: 1px 4px; border-radius: 3px; font-size: 12px; color: #991B1B; }
  pre code { background: transparent; color: inherit; padding: 0; }
  table.report-table { width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 12.4px; }
  table.report-table th { background: var(--loko-red); color: #FFF; text-align: left; padding: 7px 10px; font-weight: 700; }
  table.report-table td { padding: 6.5px 10px; border: 1px solid #CBD5E1; vertical-align: top; }
  table.report-table tr:nth-child(even) td { background: #F8FAFC; }
  .callout-info { background: #EFF6FF; border-left: 4px solid #2563EB; padding: 10px 14px; border-radius: 6px; margin: 10px 0; font-size: 12.8px; }
  figure { margin: 10px 0; text-align: center; }
  figure img { max-width: 100%; height: auto; border: 1px solid #CBD5E1; border-radius: 6px; }
  figcaption { font-size: 11.8px; color: var(--slate-600); font-style: italic; margin-top: 4px; }
  .page-foot { margin-top: 14px; padding-top: 6px; border-top: 1px solid #E2E8F0; display: flex; justify-content: space-between; font-size: 11px; color: var(--slate-600); }
  @page { size: A4; margin: 8mm; }
  @media print {
    body { background: #FFF; font-size: 12.2px; }
    .toolbar { display: none !important; }
    .document-container { max-width: 100%; margin: 0; gap: 0; }
    .page { box-shadow: none; border-radius: 0; padding: 10mm 11mm; page-break-after: always; }
    .cover-page { padding: 0; min-height: 274mm; }
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
      <img src="__CI_U__" alt="Côte d'Ivoire" style="height:64px; object-fit:contain;">
      <div class="cover-ministry">Ministère de l'Enseignement Supérieur<br>et de la Recherche Scientifique</div>
      <img src="__GL_U__" alt="Groupe LOKO" style="height:64px; object-fit:contain;">
    </div>
    <div class="cover-split">
      <div class="cover-col-left">
        <div class="ut-emblem"><img src="__UT_U__" alt="UT LOKO" style="max-width:205px; max-height:140px; object-fit:contain;"></div>
        <div class="left-meta">
          <div><strong>DÉPARTEMENT : ITER</strong></div>
          <div><strong>DOMAINE : SCIENCE ET TECHNOLOGIE</strong></div>
          <div><strong>MENTION : INFORMATIQUE ET TÉLÉCOMMUNICATION</strong></div>
          <div><strong>NIVEAU : LICENCE 3</strong><br><span style="color:#475569; font-size:12.5px;">Module : Base de données (XAMPP) &amp; Framework Laravel</span></div>
        </div>
        <div style="font-size:12px; color:#64748B; border-top:1px solid #E2E8F0; padding-top:10px;">Groupe 5 • Thème n° 12<br>Laboratoire expérimental : <strong>LOKO-Vault CyberLab</strong></div>
      </div>
      <div class="cover-col-right">
        <div>
          <div style="font-size:17px; font-weight:700;">ANNÉE ACADÉMIQUE : 2025-2026</div>
          <div style="font-size:16px; font-weight:700; margin-top:18px;">Spécialité : INFORMATIQUE</div>
        </div>
        <div class="cover-theme-box">
          <div class="label">THÈME N° 12 :</div>
          <h1>La sécurité dans une application Laravel</h1>
          <div style="font-size:13.5px; color:#FDE68A; margin-top:8px;">Protection de la base de données MySQL/MariaDB (XAMPP) et défense multicouche du framework</div>
        </div>
        <div>
          <div style="font-size:15px; font-weight:700; text-decoration:underline;">TRAVAIL RÉALISÉ PAR (GROUPE 5) :</div>
          <ul class="cover-authors">
            <li>SIBY MODY</li>
            <li>SORE RAMATOU</li>
            <li>BOIN NAOMI</li>
            <li>TRAORÉ LEYLA CHARIFAT</li>
            <li>DJAN KOUASSI NOËL</li>
          </ul>
        </div>
        <div>
          <div style="font-size:15px; font-weight:700;">PROFESSEUR :</div>
          <div style="font-size:21px; font-weight:900; color:#FDE68A; margin-top:4px;">M. CAMARA</div>
        </div>
      </div>
    </div>
  </section>

  <!-- PAGE 2 -->
  <section class="page">
    <h2 class="chap-title"><span>Table des Matières &amp; Résumé Exécutif</span><span class="author-tag">Groupe 5 • Licence 3</span></h2>
    <p>Ce dossier technique présente l'étude approfondie menée par le <strong>Groupe 5</strong> (Licence 3 Informatique, UT LOKO) sur <strong>la sécurité dans une application Laravel</strong>. Il analyse comment les vulnérabilités web majeures menacent l'interface entre PHP et le serveur <strong>MariaDB / MySQL (XAMPP)</strong>, puis détaille l'implémentation des boucliers natifs de Laravel au sein du laboratoire <strong>LOKO-Vault CyberLab</strong> (Laravel 13, PHP 8.5.12, MariaDB 10.11.16).</p>
    __TBL_TOC__
    <h3>Répartition des contributions techniques</h3>
    __TBL_CONTRIB__
    <div class="callout-info"><strong>Validation expérimentale sous XAMPP :</strong> Tous les extraits de code, captures et tests proviennent de l'application réelle <em>LOKO-Vault CyberLab</em> connectée à la base MariaDB <code>loko_security_lab</code>.</div>
    <div class="page-foot"><span>UT LOKO • Base de Données (XAMPP) &amp; Laravel</span><span>Page 2 / 10</span></div>
  </section>

  <!-- PAGE 3 -->
  <section class="page">
    <h2 class="chap-title"><span>1. Introduction Générale &amp; Défense en Profondeur</span><span class="author-tag">Sore Ramatou</span></h2>
    <p>Concevoir une application Laravel fonctionnelle avec une architecture MVC, des routes, des contrôleurs, des vues Blade et des migrations ne suffit pas : dès qu'elle est connectée à une base de données MariaDB sous XAMPP, chaque requête HTTP constitue une surface d'attaque potentielle. Le référentiel <strong>OWASP Top 10</strong> rappelle que les défaillances de contrôle d'accès (A01), la cryptographie faible (A02), les injections SQL/XSS (A03), l'assignation de masse (A04) et la mauvaise configuration (A05) sont responsables de la grande majorité des compromissions.</p>
    <h3>1.1. La philosophie « Secure by Default » en 7 couches</h3>
    <p>Laravel applique une architecture de <strong>défense en profondeur</strong> : aucune requête HTTP n'interroge directement MariaDB sans franchir sept barrières successives :</p>
    <ol>
      <li><strong>RateLimiter</strong> : limite les requêtes par IP/session contre le brute-force (<code>HTTP 429</code>).</li>
      <li><strong>ValidateCsrfToken</strong> : authentifie l'origine des formulaires d'écriture via <code>@csrf</code> (<code>HTTP 419</code>).</li>
      <li><strong>Authentification &amp; Session</strong> : identifie l'utilisateur et protège <code>laravel_session</code> avec <code>HttpOnly</code> (<code>HTTP 401</code>).</li>
      <li><strong>Authorization (Policies &amp; Gates)</strong> : contrôle les droits sur la ressource SQL ciblée contre l'IDOR (<code>HTTP 403</code>).</li>
      <li><strong>Validation FormRequest</strong> : vérifie les formats et filtre strictement <code>$request-&gt;validated()</code> (<code>HTTP 422</code>).</li>
      <li><strong>Eloquent ORM &amp; PDO</strong> : protège les colonnes via <code>#[Fillable]</code> et isole les paramètres SQL (<code>?</code>).</li>
      <li><strong>Blade &amp; SecurityHeadersMiddleware</strong> : échappe le HTML via <code>{{ }}</code> et impose des en-têtes <code>CSP</code>.</li>
    </ol>
    <figure><img src="__D7_U__" alt="Architecture 7 couches Laravel"><figcaption>Figure 1 : Parcours sécurisé d'une requête HTTP à travers les 7 couches Laravel jusqu'à MariaDB (XAMPP).</figcaption></figure>
    <div class="page-foot"><span>UT LOKO • Base de Données (XAMPP) &amp; Laravel</span><span>Page 3 / 10</span></div>
  </section>

  <!-- PAGE 4 -->
  <section class="page">
    <h2 class="chap-title"><span>2. Pilier 1 : Injections SQL (SQLi), PDO &amp; Eloquent ORM</span><span class="author-tag">Sore Ramatou</span></h2>
    <h3>2.1. Mécanisme de l'attaque et compilation PDO en deux temps</h3>
    <p>L'injection SQL survient lorsque des données saisies par l'utilisateur sont concaténées directement dans une requête SQL envoyée à MariaDB. Un attaquant peut fermer le littéral avec <code>'</code> pour injecter une condition toujours vraie (<code>' OR '1'='1</code>) ou détourner la requête via <code>UNION SELECT</code> pour lire la table <code>users</code>.</p>
    <p>Eloquent ORM et le Query Builder s'appuient sur les <strong>requêtes préparées PDO</strong> : MariaDB reçoit d'abord la structure SQL avec des marqueurs <code>?</code> puis reçoit séparément le tableau de paramètres (<em>bindings</em>), rendant toute injection SQL impossible.</p>
    __CMP_SQLI__
    <figure><img src="__SS_U__" alt="Capture SQLi LOKO-Vault" style="max-height:360px;"><figcaption>Figure 2 : Capture réelle de LOKO-Vault — Injection SQL et requête capturée par <code>SqlInspectorService</code>.</figcaption></figure>
    <div class="page-foot"><span>UT LOKO • Base de Données (XAMPP) &amp; Laravel</span><span>Page 4 / 10</span></div>
  </section>

  <!-- PAGE 5 -->
  <section class="page">
    <h2 class="chap-title"><span>3. Pilier 2 : Mass Assignment, Intégrité BDD &amp; FormRequest</span><span class="author-tag">Siby Mody</span></h2>
    <h3>3.1. Escalade de privilèges sur la colonne <code>users.role</code></h3>
    <p>Eloquent facilite l'écriture en base en acceptant un tableau associatif (<code>$user-&gt;update(...)</code>). Si le contrôleur transmet aveuglément <code>$request-&gt;all()</code> ou appelle <code>forceFill()</code>, un étudiant malveillant peut ajouter un paramètre caché <code>role=admin</code> dans sa requête POST afin de s'octroyer les droits d'administrateur dans MariaDB.</p>
    <h3>3.2. Liste blanche (<code>#[Fillable]</code>) contre liste noire (<code>$guarded</code>)</h3>
    <ul>
      <li><strong>Liste blanche (<code>#[Fillable(['name', 'email', 'password'])]</code> en Laravel 13 ou <code>$fillable</code>) :</strong> Seuls ces attributs sont modifiables en masse ; la colonne <code>role</code> est strictement ignorée.</li>
      <li><strong>Liste noire (<code>$guarded = ['role']</code>) :</strong> Risquée dès qu'une migration ajoute une nouvelle colonne sensible oubliée ; <code>$guarded = []</code> désactive toute protection.</li>
    </ul>
    __CMP_MA__
    <div class="callout-info"><strong>Modification légitime par un administrateur :</strong> Un contrôleur réservé à l'administration assigne explicitement la propriété (<code>$user-&gt;role = 'admin'; $user-&gt;save();</code>), ce qui contourne volontairement <code>#[Fillable]</code> de manière maîtrisée.</div>
    <div class="page-foot"><span>UT LOKO • Base de Données (XAMPP) &amp; Laravel</span><span>Page 5 / 10</span></div>
  </section>

  <!-- PAGE 6 -->
  <section class="page">
    <h2 class="chap-title"><span>4. Pilier 3 : Cross-Site Scripting (XSS), Blade &amp; CSP</span><span class="author-tag">Boin Naomi</span></h2>
    <h3>4.1. XSS Stockée dans MariaDB et échappement Blade</h3>
    <p>Dans une attaque <strong>XSS Stockée</strong>, la base MariaDB enregistre un script JavaScript malveillant (ex. dans <code>students.bio</code>), qui s'exécute chez tous les administrateurs ou enseignants ouvrant la fiche. Blade protège nativement la vue via les doubles accolades <code>{{ $student-&gt;bio }}</code>, compilées avec <code>e()</code> (<code>htmlspecialchars</code>), tandis que la syntaxe brute <code>{!! $student-&gt;bio !!}</code> désactive cette barrière.</p>
    __CMP_XSS__
    <h3>4.2. Défense en profondeur : En-têtes HTTP &amp; Cookies <code>HttpOnly</code></h3>
    <ul>
      <li><strong><code>SecurityHeadersMiddleware</code> :</strong> envoie <code>Content-Security-Policy</code>, <code>X-Content-Type-Options: nosniff</code> et <code>X-Frame-Options: DENY</code> (anti-Clickjacking).</li>
      <li><strong>Cookies <code>HttpOnly</code> :</strong> réglé par défaut à <code>true</code> dans <code>config/session.php</code>, empêchant <code>document.cookie</code> en JavaScript de lire le jeton de session.</li>
      <li><strong>Contenu HTML riche :</strong> si un éditeur WYSIWYG exige <code>{!! !!}</code>, la donnée doit d'abord être assainie côté serveur via <em>HTMLPurifier</em>.</li>
    </ul>
    <div class="page-foot"><span>UT LOKO • Base de Données (XAMPP) &amp; Laravel</span><span>Page 6 / 10</span></div>
  </section>

  <!-- PAGE 7 -->
  <section class="page">
    <h2 class="chap-title"><span>5. Pilier 4 : Cross-Site Request Forgery (CSRF) &amp; Sessions</span><span class="author-tag">Traoré Charifat Leyla</span></h2>
    <h3>5.1. Usurpation d'action inter-sites et bouclier <code>@csrf</code></h3>
    <p>Lorsqu'un utilisateur connecté visite un site externe piégé (simulé via <code>/lab/csrf/evil-site</code>), son navigateur envoie automatiquement son cookie <code>laravel_session</code> avec la requête forgée. Pour empêcher toute modification non consentie en base MariaDB, Laravel associe un jeton cryptographique secret à la session, inséré via <code>@csrf</code> et vérifié en temps constant par <code>hash_equals()</code> dans <code>ValidateCsrfToken</code>. Toute requête dépourvue de jeton valide échoue immédiatement avec le code <strong>HTTP 419 Page Expired</strong>.</p>
    __CMP_CSRF__
    <ul>
      <li><strong>Règle RFC 9110 :</strong> les routes <code>GET</code> doivent rester en lecture seule ; toute écriture en BDD exige <code>POST</code>, <code>PUT</code>, <code>PATCH</code> ou <code>DELETE</code>.</li>
      <li><strong>AJAX &amp; SameSite :</strong> transmission via l'en-tête <code>X-CSRF-TOKEN</code> et attribut <code>'same_site' =&gt; 'lax'</code> dans <code>config/session.php</code>.</li>
    </ul>
    <div class="page-foot"><span>UT LOKO • Base de Données (XAMPP) &amp; Laravel</span><span>Page 7 / 10</span></div>
  </section>

  <!-- PAGE 8 -->
  <section class="page">
    <h2 class="chap-title"><span>6. Pilier 5 : Cryptographie, IDOR (Policies) &amp; RateLimiter</span><span class="author-tag">Djan Kouassi Noël</span></h2>
    <h3>6.1. Hachage adaptatif <code>bcrypt</code> contre <code>MD5</code></h3>
    <p>Contrairement à MD5/SHA-1 (rapides, non salés et vulnérables aux Rainbow Tables), Laravel chiffre les mots de passe de manière irréversible via <code>Hash::make()</code> et le cast <code>'password' =&gt; 'hashed'</code> (sel aléatoire 128 bits, coût <code>BCRYPT_ROUNDS=12</code>, format <code>$2y$12$...</code>). Pour des données sensibles devant être relues, Laravel fournit séparément le chiffrement symétrique AES-256-CBC via <code>Crypt::encryptString()</code>.</p>
    <h3>6.2. Prévenir l'IDOR avec <code>GradePolicy</code> &amp; Brute-Force avec <code>RateLimiter</code></h3>
    <p>L'authentification (<code>HTTP 401</code>) doit être complétée par l'autorisation (<code>HTTP 403</code>) afin qu'un étudiant ne puisse pas lire la note d'un autre en changeant l'ID dans l'URL. <code>GradePolicy::view()</code> vérifie <code>$user-&gt;isAdmin() || $grade-&gt;student?-&gt;user_id === $user-&gt;id</code>. En parallèle, <code>RateLimiter</code> bloque toute attaque par force brute dès la 6<sup>e</sup> tentative (<strong>HTTP 429 Too Many Requests</strong>).</p>
    <figure><img src="__SA_U__" alt="Atelier 5 LOKO-Vault" style="max-height:365px;"><figcaption>Figure 3 : Capture de LOKO-Vault — Atelier 5 (Contrôle IDOR, comparateur MD5/bcrypt et RateLimiter).</figcaption></figure>
    <div class="page-foot"><span>UT LOKO • Base de Données (XAMPP) &amp; Laravel</span><span>Page 8 / 10</span></div>
  </section>

  <!-- PAGE 9 -->
  <section class="page">
    <h2 class="chap-title"><span>7. Architecture MariaDB XAMPP, Durcissement &amp; Conclusion</span><span class="author-tag">Groupe 5 (Collectif)</span></h2>
    <p>La base MariaDB <code>loko_security_lab</code> regroupe quatre tables InnoDB liées par clés étrangères avec suppression en cascade (<code>users</code>, <code>students</code>, <code>grades</code>) et journalisation d'audit temps réel (<code>security_logs</code>).</p>
    <figure><img src="__DB_U__" alt="Schéma BDD MariaDB" style="max-height:260px;"><figcaption>Figure 4 : Modèle relationnel de la base <code>loko_security_lab</code> sous MariaDB XAMPP.</figcaption></figure>
    <figure><img src="__SD_U__" alt="Dashboard LOKO-Vault" style="max-height:260px;"><figcaption>Figure 5 : Tableau de bord LOKO-Vault et table d'audit <code>security_logs</code>.</figcaption></figure>
    <h3>Durcissement XAMPP → Serveur de Production</h3>
    __TBL_ENV__
    <p><strong>Conclusion générale :</strong> Laravel offre une armure native remarquable face aux vulnérabilités OWASP Top 10, dont l'efficacité dépend directement de l'application disciplinée des requêtes préparées PDO, de <code>#[Fillable]</code>, de <code>FormRequest</code>, de l'échappement Blade, des jetons <code>@csrf</code>, du hachage <code>bcrypt</code> et des <code>Policies</code>.</p>
    <div class="page-foot"><span>UT LOKO • Base de Données (XAMPP) &amp; Laravel</span><span>Page 9 / 10</span></div>
  </section>

  <!-- PAGE 10 -->
  <section class="page">
    <h2 class="chap-title"><span>8. Annexes Techniques &amp; Bibliographie</span><span class="author-tag">Groupe 5 (Collectif)</span></h2>
    <h3>Annexe A — Matrice de synthèse OWASP Top 10 ↔ Protections Laravel</h3>
    __TBL_OWASP__
    <h3>Annexe B — Validation automatisée par suite de tests PHPUnit 12 (8 tests / 50 assertions)</h3>
    __TBL_TESTS__
    <h3>Bibliographie &amp; Webographie Officielle</h3>
    <ol style="font-size:12.2px;">__BIB__</ol>
    <div class="page-foot"><span>UT LOKO • Base de Données (XAMPP) &amp; Laravel</span><span>Page 10 / 10</span></div>
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
        "__TBL_TOC__": tbl_toc,
        "__TBL_CONTRIB__": tbl_contrib,
        "__TBL_ENV__": tbl_env,
        "__TBL_OWASP__": tbl_owasp,
        "__TBL_TESTS__": tbl_tests,
        "__CMP_SQLI__": cmp_sqli,
        "__CMP_MA__": cmp_ma,
        "__CMP_XSS__": cmp_xss,
        "__CMP_CSRF__": cmp_csrf,
        "__BIB__": bib_items,
    }
    for k, v in replacements.items():
        content = content.replace(k, v)

    out_html = WEB_DIR / "rapport.html"
    out_html.write_text(content, encoding="utf-8")
    print("Saved 10-page HTML report:", out_html)
    return out_html


def export_web_pdf_edge(html_path: Path, pdf_path: Path) -> bool:
    pdf_path.unlink(missing_ok=True)
    edge = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    if edge.exists():
        subprocess.run([
            str(edge),
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            html_path.as_uri(),
        ], capture_output=True, text=True, check=False)
        if pdf_path.exists() and pdf_path.stat().st_size > 10000:
            print("Saved Web PDF via Edge:", pdf_path)
            return True
    build_pdf_report(pdf_path)
    return False


def generate_all_reports():
    OFFICE_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DIR.mkdir(parents=True, exist_ok=True)
    build_docx_report()
    build_pdf_report(OFFICE_DIR / "Rapport_Securite_Laravel_Groupe5.pdf")
    html_file = build_web_report_html()
    export_web_pdf_edge(html_file, WEB_DIR / "Rapport_Web_Groupe5.pdf")


if __name__ == "__main__":
    generate_all_reports()
