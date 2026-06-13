"""
report_gen.py
Generador de reportes PDF con ReportLab.
Soporta UTF-8 completo (ñ, é, ó...) usando fuentes del sistema.
"""

import os
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


COLOR_PRIMARY  = colors.HexColor("#01696f")
COLOR_DARK     = colors.HexColor("#1c1b19")
COLOR_LIGHT_BG = colors.HexColor("#f3f0ec")
COLOR_BORDER   = colors.HexColor("#d4d1ca")
COLOR_WHITE    = colors.white

FONT_NORMAL = "Helvetica"
FONT_BOLD   = "Helvetica-Bold"


def _register_fonts():
    global FONT_NORMAL, FONT_BOLD
    candidates = [
        ("C:/Windows/Fonts/arial.ttf",   "ReportNormal"),
        ("C:/Windows/Fonts/arialbd.ttf", "ReportBold"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",      "ReportNormal"),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "ReportBold"),
    ]
    normal_done = bold_done = False
    for path, name in candidates:
        if not os.path.exists(path):
            continue
        try:
            if name == "ReportNormal" and not normal_done:
                pdfmetrics.registerFont(TTFont("ReportNormal", path))
                normal_done = True
                FONT_NORMAL = "ReportNormal"
            elif name == "ReportBold" and not bold_done:
                pdfmetrics.registerFont(TTFont("ReportBold", path))
                bold_done = True
                FONT_BOLD = "ReportBold"
        except Exception:
            continue
        if normal_done and bold_done:
            break


_register_fonts()


def _ensure_reports_dir() -> Path:
    base = Path(__file__).resolve().parent.parent / "reports"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _build_styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "ReportTitle", parent=base["Title"],
            textColor=COLOR_WHITE, fontSize=22,
            leading=28, alignment=TA_CENTER, fontName=FONT_NORMAL,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle", parent=base["Normal"],
            textColor=COLOR_WHITE, fontSize=11,
            alignment=TA_CENTER, fontName=FONT_NORMAL,
        ),
        "section": ParagraphStyle(
            "SectionHeader", parent=base["Heading2"],
            textColor=COLOR_PRIMARY, fontSize=13,
            spaceBefore=14, spaceAfter=4, fontName=FONT_BOLD,
        ),
        "body": ParagraphStyle(
            "BodyText", parent=base["Normal"],
            fontSize=9, leading=13,
            alignment=TA_LEFT, fontName=FONT_NORMAL,
        ),
        "mono": ParagraphStyle(
            "MonoText", parent=base["Code"],
            fontSize=8, leading=11,
            textColor=COLOR_DARK, backColor=COLOR_LIGHT_BG,
            fontName=FONT_NORMAL,
        ),
        "label": ParagraphStyle(
            "LabelText", parent=base["Normal"],
            fontSize=8, textColor=colors.HexColor("#7a7974"),
            fontName=FONT_NORMAL,
        ),
    }


def _header_table(titulo: str, fecha: str, styles: dict) -> Table:
    data = [
        [Paragraph(titulo, styles["title"])],
        [Paragraph(
            f"Generado el: {fecha}  |  UI-AIAS — Universal IT Admin AI Suite",
            styles["subtitle"])],
    ]
    t = Table(data, colWidths=[18 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), COLOR_PRIMARY),
        ("ALIGN",         (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
    ]))
    return t


def _os_info_table(os_info: dict, styles: dict) -> Table:
    rows = [
        [Paragraph(k, styles["label"]), Paragraph(str(v), styles["body"])]
        for k, v in os_info.items()
    ]
    t = Table(rows, colWidths=[5 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("GRID",          (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("BACKGROUND",    (0, 0), (0, -1),  COLOR_LIGHT_BG),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def _text_section(content: str, styles: dict, max_chars: int = 3000) -> Paragraph:
    truncated = content[:max_chars]
    if len(content) > max_chars:
        truncated += "\n... [contenido truncado] ..."
    safe = (truncated
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace("\n", "<br/>"))
    return Paragraph(safe, styles["mono"])


def generate_pdf(diagnostics: dict, filename: str = None) -> str:
    """
    Construye y guarda el PDF de diagnóstico.
    Devuelve la ruta absoluta del archivo generado.
    """
    reports_dir = _ensure_reports_dir()
    if not filename:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"diagnostico_{ts}.pdf"
    filepath = str(reports_dir / filename)

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.5*cm,  bottomMargin=2*cm,
    )

    styles = _build_styles()
    story  = []
    fecha_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    story.append(_header_table("Reporte de Diagnostico del Sistema", fecha_str, styles))
    story.append(Spacer(1, 0.5 * cm))

    os_info = diagnostics.get("os_info", {})
    if os_info:
        story.append(Paragraph("Informacion del Sistema Operativo", styles["section"]))
        story.append(HRFlowable(width="100%", thickness=1, color=COLOR_BORDER))
        story.append(Spacer(1, 0.2 * cm))
        story.append(_os_info_table(os_info, styles))
        story.append(Spacer(1, 0.3 * cm))

    section_labels = {
        "procesos":     "Procesos en Ejecucion",
        "red":          "Conexiones de Red",
        "disco":        "Uso de Disco",
        "cpu":          "Informacion del CPU",
        "memoria":      "Memoria RAM",
        "usuarios":     "Usuarios del Sistema",
        "servicios":    "Servicios Activos",
        "logs_sistema": "Logs del Sistema",
        "analisis_ia":  "Analisis por IA",
    }

    for key, label in section_labels.items():
        content = diagnostics.get(key)
        if not content:
            continue
        story.append(Paragraph(label, styles["section"]))
        story.append(HRFlowable(width="100%", thickness=1, color=COLOR_BORDER))
        story.append(Spacer(1, 0.15 * cm))
        if isinstance(content, dict):
            for k, v in content.items():
                story.append(Paragraph(f"<b>{k}:</b> {v}", styles["body"]))
        else:
            story.append(_text_section(str(content), styles))
        story.append(Spacer(1, 0.4 * cm))

    doc.build(story)
    return filepath