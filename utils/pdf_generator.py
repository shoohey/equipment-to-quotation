"""PDF生成モジュール（日本語対応）"""

import io
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 日本語フォント登録
_font_registered = False


def _register_japanese_font():
    """日本語フォントを登録する"""
    global _font_registered
    if _font_registered:
        return

    # macOS のヒラギノフォント
    font_paths = [
        "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
        "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
    ]

    for path in font_paths:
        if os.path.exists(path):
            try:
                if "W6" in path:
                    pdfmetrics.registerFont(TTFont("JapaneseBold", path, subfontIndex=0))
                else:
                    pdfmetrics.registerFont(TTFont("Japanese", path, subfontIndex=0))
                    if not _check_font("JapaneseBold"):
                        pdfmetrics.registerFont(TTFont("JapaneseBold", path, subfontIndex=0))
                _font_registered = True
            except Exception:
                continue

    if not _font_registered:
        # フォールバック: Helvetica（日本語表示不可だが動作する）
        _font_registered = True


def _check_font(name):
    try:
        pdfmetrics.getFont(name)
        return True
    except KeyError:
        return False


def _get_font_name():
    if _check_font("Japanese"):
        return "Japanese"
    return "Helvetica"


def _get_bold_font_name():
    if _check_font("JapaneseBold"):
        return "JapaneseBold"
    if _check_font("Japanese"):
        return "Japanese"
    return "Helvetica-Bold"


def generate_pdf(quotation_data):
    """見積書PDFを生成してバイトデータを返す"""
    _register_japanese_font()

    buffer = io.BytesIO()
    font = _get_font_name()
    bold_font = _get_bold_font_name()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=15 * mm,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="JpTitle",
        fontName=bold_font,
        fontSize=20,
        alignment=1,
        spaceAfter=6 * mm,
        leading=28,
    ))
    styles.add(ParagraphStyle(
        name="JpNormal",
        fontName=font,
        fontSize=9,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name="JpSmall",
        fontName=font,
        fontSize=8,
        leading=12,
    ))
    styles.add(ParagraphStyle(
        name="JpBold",
        fontName=bold_font,
        fontSize=10,
        leading=14,
    ))
    styles.add(ParagraphStyle(
        name="JpRight",
        fontName=font,
        fontSize=9,
        alignment=2,
        leading=14,
    ))

    elements = []

    # タイトル
    elements.append(Paragraph("見　積　書", styles["JpTitle"]))

    # ヘッダー（左: 宛先、右: 会社情報）
    company = quotation_data["company_info"]
    header_data = [
        [
            Paragraph(f'{quotation_data["client_name"]} 御中', styles["JpBold"]),
            Paragraph(
                f'見積番号: {quotation_data["estimate_number"]}<br/>'
                f'見積日: {quotation_data["estimate_date_jp"]}',
                styles["JpRight"],
            ),
        ],
        [
            Paragraph(f'件名: {quotation_data["project_name"]} 設備機器', styles["JpNormal"]),
            Paragraph(
                f'<b>{company["name"]}</b><br/>'
                f'{company["postal_code"]}<br/>'
                f'{company["address"]}<br/>'
                f'TEL: {company["tel"]}<br/>'
                f'FAX: {company["fax"]}',
                styles["JpSmall"],
            ),
        ],
    ]
    header_table = Table(header_data, colWidths=[90 * mm, 90 * mm])
    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 6 * mm))

    # 合計金額
    total_str = f'¥{quotation_data["total"]:,.0f}'
    total_data = [[
        Paragraph(f'合計金額（税込）　　<b>{total_str}</b>', ParagraphStyle(
            name="TotalStyle",
            fontName=bold_font,
            fontSize=14,
            alignment=1,
            leading=20,
        ))
    ]]
    total_table = Table(total_data, colWidths=[180 * mm])
    total_table.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 2, colors.HexColor("#1a3a5c")),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8f9fa")),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 6 * mm))

    # 明細テーブル
    table_header = ["No.", "品名", "型番", "メーカー", "数量", "単位", "単価", "金額"]
    table_data = [[Paragraph(h, ParagraphStyle(
        name=f"TH_{h}",
        fontName=bold_font,
        fontSize=7,
        textColor=colors.white,
        alignment=1,
        leading=10,
    )) for h in table_header]]

    for item in quotation_data["items"]:
        table_data.append([
            Paragraph(str(item["no"]), styles["JpSmall"]),
            Paragraph(str(item["name"]), styles["JpSmall"]),
            Paragraph(str(item["model"]), styles["JpSmall"]),
            Paragraph(str(item["maker"]), styles["JpSmall"]),
            Paragraph(str(item["quantity"]), ParagraphStyle(
                name="Qty", fontName=font, fontSize=8, alignment=2, leading=12)),
            Paragraph(str(item["unit"]), styles["JpSmall"]),
            Paragraph(f'¥{item["unit_price"]:,.0f}', ParagraphStyle(
                name="Price", fontName=font, fontSize=8, alignment=2, leading=12)),
            Paragraph(f'¥{item["amount"]:,.0f}', ParagraphStyle(
                name="Amount", fontName=font, fontSize=8, alignment=2, leading=12)),
        ])

    col_widths = [10 * mm, 48 * mm, 30 * mm, 22 * mm, 14 * mm, 12 * mm, 22 * mm, 24 * mm]
    detail_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    detail_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a5c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, 0), 0.5, colors.white),
        ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
        ("TOPPADDING", (0, 1), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 3),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8f9fa")]),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 4 * mm))

    # 合計欄
    summary_data = [
        ["", "小計", f'¥{quotation_data["subtotal"]:,.0f}'],
        ["", "消費税（10%）", f'¥{quotation_data["tax"]:,.0f}'],
        ["", "合計", f'¥{quotation_data["total"]:,.0f}'],
    ]
    summary_table = Table(summary_data, colWidths=[100 * mm, 40 * mm, 40 * mm])
    summary_table.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("FONTNAME", (0, 0), (-1, -1), font),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 2), (-1, 2), bold_font),
        ("FONTSIZE", (0, 2), (-1, 2), 11),
        ("LINEABOVE", (1, 2), (-1, 2), 2, colors.HexColor("#333333")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 8 * mm))

    # 備考
    remarks = (
        "【備考】<br/>"
        "・本見積書の有効期限は発行日より30日間とします。<br/>"
        "・上記金額には工事費は含まれておりません。<br/>"
        "・納期は別途ご相談ください。"
    )
    elements.append(Paragraph(remarks, styles["JpSmall"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
