"""
面试问题 PDF 导出
使用 PyMuPDF 生成包含题目和标准答案的 PDF 文档
"""
import io
import fitz  # PyMuPDF


# === 字体配置 ===
# PyMuPDF 内置中文支持，使用系统字体
FONT_CN = "china-s"  # 简体中文 serif
FONT_CN_SANS = "china-ss"  # 简体中文 sans-serif

# === 颜色 ===
COLOR_TITLE = (0.12, 0.12, 0.15)       # 深色标题
COLOR_SUBTITLE = (0.40, 0.40, 0.42)    # 灰色副标题
COLOR_BODY = (0.25, 0.25, 0.27)        # 正文色
COLOR_ACCENT = (0.91, 0.66, 0.22)      # Amber 强调色
COLOR_TAG_BG = (0.91, 0.66, 0.22, 0.12)  # 标签背景
COLOR_DIVIDER = (0.85, 0.85, 0.83)     # 分隔线


def generate_interview_pdf(session: dict) -> bytes:
    """
    生成面试问题 PDF
    :param session: 面试会话文档（包含 questions, evaluations, overall_evaluation）
    :return: PDF 字节内容
    """
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4
    rect = page.rect
    margin = 50
    content_width = rect.width - 2 * margin
    y = margin

    # === 标题区 ===
    y = _draw_header(page, session, margin, y, content_width)

    # === 问题列表 ===
    questions = session.get("questions", [])
    evaluations = session.get("evaluations", [])
    eval_map = {e["question_id"]: e for e in evaluations}

    cat_labels = {
        "technical": "技术类",
        "behavioral": "行为类",
        "situational": "情景类",
        "gap_followup": "追问类",
    }
    diff_labels = {"easy": "简单", "medium": "中等", "hard": "困难"}

    for i, q in enumerate(questions):
        qid = q.get("question_id", "")
        eval_data = eval_map.get(qid)

        # 如果空间不够，换页
        if y > rect.height - 120:
            page = doc.new_page(width=595, height=842)
            y = margin

        # 问题编号 + 类别 + 难度
        category = cat_labels.get(q.get("category", ""), q.get("category", ""))
        difficulty = diff_labels.get(q.get("difficulty", ""), "")
        header_text = f"Q{i+1}"
        tag_text = f"{category} · {difficulty}"

        # 画编号
        tw = fitz.get_text_length(header_text, fontname=FONT_CN_SANS, fontsize=16)
        page.insert_text(
            (margin, y + 16), header_text,
            fontname=FONT_CN_SANS, fontsize=16,
            color=COLOR_ACCENT,
        )

        # 画标签
        tag_x = margin + tw + 10
        tag_rect = fitz.Rect(tag_x, y + 3, tag_x + fitz.get_text_length(tag_text, fontname=FONT_CN, fontsize=9) + 12, y + 18)
        page.draw_rect(tag_rect, color=COLOR_TAG_BG, fill=COLOR_TAG_BG)
        page.insert_text(
            (tag_x + 6, y + 15), tag_text,
            fontname=FONT_CN, fontsize=9,
            color=COLOR_SUBTITLE,
        )

        y += 24

        # 问题内容
        question_text = q.get("question", "")
        y = _draw_wrapped_text(page, question_text, margin, y, content_width,
                               fontname=FONT_CN, fontsize=11, color=COLOR_BODY, line_spacing=5)
        y += 4

        # 评分和反馈（如果有）
        if eval_data:
            score = eval_data.get("score", 0)
            feedback = eval_data.get("feedback", "")

            # 评分
            score_text = f"评分: {score}/10"
            page.insert_text(
                (margin + 4, y + 12), score_text,
                fontname=FONT_CN_SANS, fontsize=10,
                color=COLOR_ACCENT,
            )
            score_x = margin + 4 + fitz.get_text_length(score_text, fontname=FONT_CN_SANS, fontsize=10) + 12

            # strengths
            for s in eval_data.get("strengths", []):
                s_text = f"+ {s}"
                page.insert_text(
                    (score_x, y + 12), s_text,
                    fontname=FONT_CN, fontsize=9,
                    color=(0.30, 0.55, 0.35),
                )
                score_x += fitz.get_text_length(s_text, fontname=FONT_CN, fontsize=9) + 8

            y += 16

            # 反馈
            if feedback:
                y = _draw_wrapped_text(page, f"反馈: {feedback}", margin + 4, y, content_width - 8,
                                       fontname=FONT_CN, fontsize=9, color=COLOR_SUBTITLE, line_spacing=3)
                y += 2

        # 出题理由
        rationale = q.get("rationale", "")
        if rationale:
            y = _draw_wrapped_text(page, f"出题理由: {rationale}", margin + 4, y, content_width - 8,
                                   fontname=FONT_CN, fontsize=9, color=COLOR_SUBTITLE, line_spacing=3)

        # 分隔线
        y += 10
        page.draw_line(fitz.Point(margin, y), fitz.Point(margin + content_width, y),
                       color=COLOR_DIVIDER, width=0.5)
        y += 12

    # === 总评 ===
    overall = session.get("overall_evaluation")
    if overall:
        if y > rect.height - 180:
            page = doc.new_page(width=595, height=842)
            y = margin

        y = _draw_overall_evaluation(page, overall, margin, y, content_width)

    # 输出
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _draw_header(page, session: dict, margin: int, y: int, width: int) -> int:
    """画页头"""
    # 标题
    page.insert_text(
        (margin, y + 20), "AI 预面试 — 问题报告",
        fontname=FONT_CN_SANS, fontsize=22,
        color=COLOR_TITLE,
    )
    y += 30

    # 信息行
    info_parts = []
    info_parts.append(f"会话ID: {session.get('id', 'N/A')[:12]}")
    info_parts.append(f"状态: {'进行中' if session.get('status') == 'in_progress' else '已完成'}")
    info_parts.append(f"题目数: {len(session.get('questions', []))}")

    info_text = "  |  ".join(info_parts)
    page.insert_text(
        (margin, y + 14), info_text,
        fontname=FONT_CN, fontsize=10,
        color=COLOR_SUBTITLE,
    )
    y += 20

    # 分隔线
    page.draw_line(fitz.Point(margin, y), fitz.Point(margin + width, y),
                   color=COLOR_ACCENT, width=1.5)
    y += 16

    return y


def _draw_wrapped_text(page, text: str, x: int, y: int, width: int,
                       fontname: str, fontsize: int, color: tuple, line_spacing: int = 4) -> int:
    """自动换行绘制文本"""
    # 使用 PyMuPDF 的 TextWriter 实现换行
    words = list(text)
    line = ""
    line_height = fontsize + line_spacing

    for char in words:
        test_line = line + char
        tw = fitz.get_text_length(test_line, fontname=fontname, fontsize=fontsize)
        if tw > width and line:
            page.insert_text(
                (x, y + fontsize), line,
                fontname=fontname, fontsize=fontsize,
                color=color,
            )
            y += line_height
            line = char
        else:
            line = test_line

    if line:
        page.insert_text(
            (x, y + fontsize), line,
            fontname=fontname, fontsize=fontsize,
            color=color,
        )
        y += line_height

    return y


def _draw_overall_evaluation(page, overall: dict, margin: int, y: int, width: int) -> int:
    """画总评区域"""
    # 标题
    page.insert_text(
        (margin, y + 16), "面试总评",
        fontname=FONT_CN_SANS, fontsize=16,
        color=COLOR_TITLE,
    )
    y += 24

    # 分隔线
    page.draw_line(fitz.Point(margin, y), fitz.Point(margin + width, y),
                   color=COLOR_ACCENT, width=1.5)
    y += 14

    # 评分
    scores_text = (
        f"总分: {overall.get('total_score', 0)}    "
        f"技术: {overall.get('technical_score', 0)}    "
        f"沟通: {overall.get('communication_score', 0)}    "
        f"文化: {overall.get('cultural_fit_score', 0)}"
    )
    page.insert_text(
        (margin, y + 14), scores_text,
        fontname=FONT_CN_SANS, fontsize=12,
        color=COLOR_ACCENT,
    )
    y += 22

    # 推荐等级
    rec = overall.get("recommendation", "")
    rec_labels = {
        "strongly_recommend": "强烈推荐",
        "recommend_interview": "推荐面试",
        "needs_further_evaluation": "需进一步评估",
        "not_recommended": "不推荐",
    }
    rec_text = f"推荐: {rec_labels.get(rec, rec)}"
    page.insert_text(
        (margin, y + 14), rec_text,
        fontname=FONT_CN_SANS, fontsize=11,
        color=COLOR_BODY,
    )
    y += 20

    # 综合评价
    summary = overall.get("summary", "")
    if summary:
        y = _draw_wrapped_text(page, summary, margin, y, width,
                               fontname=FONT_CN, fontsize=10, color=COLOR_BODY, line_spacing=4)
        y += 6

    # 亮点
    highlights = overall.get("highlights", [])
    if highlights:
        page.insert_text(
            (margin, y + 14), "亮点:",
            fontname=FONT_CN_SANS, fontsize=10,
            color=(0.30, 0.55, 0.35),
        )
        y += 14
        for h in highlights:
            y = _draw_wrapped_text(page, f"+ {h}", margin + 12, y, width - 12,
                                   fontname=FONT_CN, fontsize=10, color=(0.30, 0.55, 0.35), line_spacing=3)
        y += 4

    # 关注点
    concerns = overall.get("key_concerns", [])
    if concerns:
        page.insert_text(
            (margin, y + 14), "关注点:",
            fontname=FONT_CN_SANS, fontsize=10,
            color=(0.83, 0.40, 0.29),
        )
        y += 14
        for c in concerns:
            y = _draw_wrapped_text(page, f"! {c}", margin + 12, y, width - 12,
                                   fontname=FONT_CN, fontsize=10, color=(0.83, 0.40, 0.29), line_spacing=3)

    return y
