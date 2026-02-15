"""
Growth Profile PDF Generator - 成长档案PDF生成
生成面试作品集PDF，用于向目标学校展示
"""

import os
import io
import base64
from datetime import datetime
from services.growth_profile_service import (
    get_growth_profile,
    generate_portfolio_summary,
)

# 尝试导入PDF库
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, mm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle,
        Image,
    )
    from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, String
    from reportlab.graphics import renderPDF

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("⚠️ ReportLab not installed, using HTML fallback")

try:
    from fpdf import FPDF

    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    print("⚠️ FPDF not installed")


def generate_growth_profile_pdf(user_id, profile_data=None):
    """
    生成成长档案PDF

    Args:
        user_id: 用户ID
        profile_data: 孩子画像数据

    Returns:
        bytes: PDF文件内容
    """
    # 获取成长档案数据
    growth_profile = get_growth_profile(user_id, profile_data)
    portfolio = generate_portfolio_summary(growth_profile)

    # 尝试使用ReportLab生成PDF
    if REPORTLAB_AVAILABLE:
        return _generate_pdf_with_reportlab(growth_profile, portfolio)
    elif FPDF_AVAILABLE:
        return _generate_pdf_with_fpdf(growth_profile, portfolio)
    else:
        # 返回HTML格式的报告（备用方案）
        return _generate_html_fallback(growth_profile, portfolio)


def _generate_pdf_with_reportlab(growth_profile, portfolio):
    """使用ReportLab生成PDF"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    story = []

    # 标题
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        spaceAfter=30,
        alignment=1,
        textColor=colors.HexColor("#1a56db"),
    )
    story.append(Paragraph(portfolio["title"], title_style))
    story.append(Spacer(1, 10))

    # 生成日期
    date_text = f"生成日期: {datetime.now().strftime('%Y年%m月%d日')}"
    story.append(Paragraph(date_text, styles["Normal"]))
    story.append(Spacer(1, 20))

    # 综合评分
    score_style = ParagraphStyle(
        "Score",
        parent=styles["Heading2"],
        fontSize=18,
        textColor=colors.HexColor("#059669"),
    )
    story.append(
        Paragraph(f"综合成长评分: {portfolio['overall_score']}分", score_style)
    )
    story.append(Spacer(1, 20))

    # 练习统计
    stats = portfolio["practice_stats"]
    stats_data = [
        ["练习次数", "总时长", "连续天数", "完成主题"],
        [
            f"{stats['total_practices']}次",
            f"{stats['total_minutes']}分钟",
            f"{stats['streak_days']}天",
            f"{stats['topics_completed']}/{stats['total_topics']}",
        ],
    ]
    stats_table = Table(stats_data, colWidths=[80, 80, 80, 80])
    stats_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e0e7ff")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#c7d2fe")),
            ]
        )
    )
    story.append(stats_table)
    story.append(Spacer(1, 20))

    # 能力维度
    story.append(Paragraph("能力雷达图数据", styles["Heading2"]))
    story.append(Spacer(1, 10))

    radar = portfolio["radar"]
    capability_data = [["能力维度", "当前得分", "参考标准"]]
    for i, label in enumerate(radar["labels"]):
        capability_data.append(
            [label, f"{radar['scores'][i]}分", f"{radar['expected'][i]}分"]
        )

    cap_table = Table(capability_data, colWidths=[80, 80, 80])
    cap_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dcfce7")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#166534")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 11),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#bbf7d0")),
            ]
        )
    )
    story.append(cap_table)
    story.append(Spacer(1, 20))

    # 成长里程碑
    if portfolio["milestones"]:
        story.append(Paragraph("成长里程碑", styles["Heading2"]))
        story.append(Spacer(1, 10))

        for milestone in portfolio["milestones"][:6]:
            icon = "✓" if milestone.get("achieved") else "○"
            text = f"{icon} {milestone['title']} - {milestone['description']}"
            story.append(Paragraph(text, styles["Normal"]))
            story.append(Spacer(1, 5))

    # 优势总结
    if portfolio["strengths"]:
        story.append(Spacer(1, 15))
        story.append(Paragraph("能力优势", styles["Heading2"]))
        story.append(Spacer(1, 10))

        strength_names = {
            "communication": "沟通表达",
            "logic": "逻辑思维",
            "creativity": "创意思维",
            "confidence": "自信心",
            "eye_contact": "眼神接触",
            "manners": "礼貌礼仪",
        }

        strength_text = "、".join(
            [strength_names.get(s, s) for s in portfolio["strengths"]]
        )
        story.append(Paragraph(f"在 {strength_text} 方面表现优秀", styles["Normal"]))

    # 页脚
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.grey,
        alignment=1,
    )
    story.append(Paragraph("此报告由AI面霸导师生成 | 仅供参考", footer_style))

    # 生成PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def _generate_pdf_with_fpdf(growth_profile, portfolio):
    """使用FPDF生成PDF"""
    pdf = FPDF()
    pdf.add_page()

    # 标题
    pdf.set_font("Arial", "B", 20)
    pdf.set_text_color(26, 86, 219)
    pdf.cell(0, 20, portfolio["title"], 0, 1, "C")

    pdf.set_font("Arial", "", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 10, f"生成日期: {datetime.now().strftime('%Y年%m月%d日')}", 0, 1, "C")

    pdf.ln(10)

    # 综合评分
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(5, 150, 105)
    pdf.cell(0, 10, f"综合成长评分: {portfolio['overall_score']}分", 0, 1)

    pdf.ln(10)

    # 练习统计
    pdf.set_font("Arial", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(40, 10, "练习次数", 1)
    pdf.cell(40, 10, "总时长", 1)
    pdf.cell(40, 10, "连续天数", 1)
    pdf.cell(40, 10, "完成主题", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 11)
    stats = portfolio["practice_stats"]
    pdf.cell(40, 10, f"{stats['total_practices']}次", 1)
    pdf.cell(40, 10, f"{stats['total_minutes']}分钟", 1)
    pdf.cell(40, 10, f"{stats['streak_days']}天", 1)
    pdf.cell(40, 10, f"{stats['topics_completed']}/{stats['total_topics']}", 1)

    pdf.ln(20)

    # 能力维度
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "能力维度评估", 0, 1)

    radar = portfolio["radar"]
    pdf.set_font("Arial", "", 10)
    for i, label in enumerate(radar["labels"]):
        pdf.cell(60, 8, label, 1)
        pdf.cell(40, 8, f"{radar['scores'][i]}分", 1)
        pdf.cell(40, 8, f"参考: {radar['expected'][i]}分", 1)
        pdf.ln()

    # 成长里程碑
    if portfolio["milestones"]:
        pdf.ln(10)
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "成长里程碑", 0, 1)

        pdf.set_font("Arial", "", 10)
        for milestone in portfolio["milestones"][:6]:
            icon = "[已达成]" if milestone.get("achieved") else "[未达成]"
            pdf.cell(
                0, 8, f"{icon} {milestone['title']} - {milestone['description']}", 0, 1
            )

    # 页脚
    pdf.set_y(-20)
    pdf.set_font("Arial", "I", 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "此报告由AI面霸导师生成 | 仅供参考", 0, 0, "C")

    return pdf.output(dest="S").encode("latin-1")


def _generate_html_fallback(growth_profile, portfolio):
    """生成HTML格式的报告（备用方案）"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{portfolio["title"]}</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 40px; max-width: 800px; margin: 0 auto; }}
            h1 {{ color: #1a56db; text-align: center; }}
            h2 {{ color: #059669; border-bottom: 2px solid #e0e7ff; padding-bottom: 10px; }}
            .score {{ font-size: 24px; color: #059669; text-align: center; margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ border: 1px solid #c7d2fe; padding: 12px; text-align: center; }}
            th {{ background: #e0e7ff; color: #1e40af; }}
            .milestone {{ margin: 10px 0; padding: 10px; background: #f0fdf4; border-left: 4px solid #22c55e; }}
            .strength {{ color: #166534; font-weight: bold; }}
            .footer {{ text-align: center; color: #999; margin-top: 40px; font-size: 12px; }}
        </style>
    </head>
    <body>
        <h1>{portfolio["title"]}</h1>
        <p style="text-align: center; color: #666;">生成日期: {datetime.now().strftime("%Y年%m月%d日")}</p>
        
        <div class="score">综合成长评分: {portfolio["overall_score"]}分</div>
        
        <h2>练习统计</h2>
        <table>
            <tr><th>练习次数</th><th>总时长</th><th>连续天数</th><th>完成主题</th></tr>
            <tr>
                <td>{portfolio["practice_stats"]["total_practices"]}次</td>
                <td>{portfolio["practice_stats"]["total_minutes"]}分钟</td>
                <td>{portfolio["practice_stats"]["streak_days"]}天</td>
                <td>{portfolio["practice_stats"]["topics_completed"]}/{portfolio["practice_stats"]["total_topics"]}</td>
            </tr>
        </table>
        
        <h2>能力维度评估</h2>
        <table>
            <tr><th>能力维度</th><th>当前得分</th><th>参考标准</th></tr>
    """

    radar = portfolio["radar"]
    for i, label in enumerate(radar["labels"]):
        html += f"""
            <tr>
                <td>{label}</td>
                <td>{radar["scores"][i]}分</td>
                <td>{radar["expected"][i]}分</td>
            </tr>
        """

    if portfolio["milestones"]:
        html += """
        <h2>成长里程碑</h2>
        """
        for milestone in portfolio["milestones"][:6]:
            icon = "✓" if milestone.get("achieved") else "○"
            html += f"""
            <div class="milestone">{icon} {milestone["title"]} - {milestone["description"]}</div>
            """

    if portfolio["strengths"]:
        strength_names = {
            "communication": "沟通表达",
            "logic": "逻辑思维",
            "creativity": "创意思维",
            "confidence": "自信心",
            "eye_contact": "眼神接触",
            "manners": "礼貌礼仪",
        }
        strength_text = "、".join(
            [strength_names.get(s, s) for s in portfolio["strengths"]]
        )
        html += f"""
        <h2>能力优势</h2>
        <p class="strength">在 {strength_text} 方面表现优秀</p>
        """

    html += """
        <div class="footer">此报告由AI面霸导师生成 | 仅供参考</div>
    </body>
    </html>
    """

    return html.encode("utf-8")


def save_pdf_to_file(pdf_content, user_id):
    """保存PDF到文件"""
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data", "portfolios")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    filename = (
        f"{data_dir}/portfolio_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )

    if isinstance(pdf_content, str):
        # HTML fallback
        filename += ".html"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(pdf_content)
    else:
        filename += ".pdf"
        with open(filename, "wb") as f:
            f.write(pdf_content)

    return filename
