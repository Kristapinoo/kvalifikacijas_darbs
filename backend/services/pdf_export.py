"""
PDF Export Service
Generates PDF files for tests and study materials
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
import html
import os

# Register DejaVu fonts for Unicode support (including Latvian characters)
try:
    # Try to use system fonts that support Latvian characters
    font_path = '/usr/share/fonts/truetype/dejavu/'
    if os.path.exists(font_path + 'DejaVuSans.ttf'):
        pdfmetrics.registerFont(TTFont('DejaVu', font_path + 'DejaVuSans.ttf'))
        pdfmetrics.registerFont(TTFont('DejaVu-Bold', font_path + 'DejaVuSans-Bold.ttf'))
        UNICODE_FONT = 'DejaVu'
        UNICODE_FONT_BOLD = 'DejaVu-Bold'
    else:
        # Fallback to Helvetica (won't support special characters properly)
        UNICODE_FONT = 'Helvetica'
        UNICODE_FONT_BOLD = 'Helvetica-Bold'
except:
    UNICODE_FONT = 'Helvetica'
    UNICODE_FONT_BOLD = 'Helvetica-Bold'


def generate_test_pdf(test_data, include_answers=True):
    """
    Generate PDF for a test

    Args:
        test_data: Test object with assignments and questions
        include_answers: Whether to include correct answers (default: True)

    Returns:
        BytesIO: PDF file content
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)

    elements = []


    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        fontName=UNICODE_FONT_BOLD,
        textColor=colors.black,
        spaceAfter=20,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=13,
        fontName=UNICODE_FONT_BOLD,
        textColor=colors.black,
        spaceAfter=8,
        spaceBefore=16
    )

    question_style = ParagraphStyle(
        'Question',
        parent=styles['Normal'],
        fontSize=10,
        fontName=UNICODE_FONT,
        spaceAfter=6,
        spaceBefore=6
    )

    answer_style = ParagraphStyle(
        'Answer',
        parent=styles['Normal'],
        fontSize=9,
        fontName=UNICODE_FONT,
        textColor=colors.black,
        leftIndent=20
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        fontName=UNICODE_FONT
    )

    elements.append(Paragraph(test_data['title'], title_style))
    elements.append(Spacer(1, 8))

    from datetime import datetime
    date_str = datetime.fromisoformat(test_data['created_at'].replace('Z', '+00:00')).strftime('%B %d, %Y')
    elements.append(Paragraph(f"Izveidots: {date_str}", normal_style))
    elements.append(Spacer(1, 12))

    # Instructions (only if answers are hidden)
    if not include_answers:
        instructions = Paragraph(
            "<b>Instrukcija:</b> Atbildiet uz visiem jautājumiem. Rakstiet savas atbildes skaidri.",
            normal_style
        )
        elements.append(instructions)
        elements.append(Spacer(1, 12))

    for assignment_idx, assignment in enumerate(test_data['assignments']):

        assignment_num = assignment_idx + 1
        assignment_title = f"Uzdevums {assignment_num}: {assignment['title']}"
        elements.append(Paragraph(assignment_title, heading_style))

        # Skip assignment description (usually contains AI generation prompts)
        # if assignment.get('description'):
        #     elements.append(Paragraph(assignment['description'], normal_style))
        #     elements.append(Spacer(1, 6))


        elements.append(Paragraph(f"<i>Maksimālais punktu skaits: {assignment['max_points']}</i>", normal_style))
        elements.append(Spacer(1, 10))

        for question_idx, question in enumerate(assignment['questions']):
            question_num = question_idx + 1


            q_header = f"<b>Jautājums {question_num}</b> ({question['points']} punkti)"
            elements.append(Paragraph(q_header, question_style))


            q_text = html.escape(question['question_text'])
            elements.append(Paragraph(q_text, normal_style))
            elements.append(Spacer(1, 6))

            # Options (for multiple choice, true/false, matching)
            if question.get('options') and len(question['options']) > 0:
                # Special handling for matching questions
                if question['question_type'] == 'matching':

                    table_data = []


                    table_data.append([
                        Paragraph('<b>Kreisā puse</b>', normal_style),
                        Paragraph('', normal_style),  # Empty space column
                        Paragraph('<b>Labā puse</b>', normal_style)
                    ])


                    for opt_idx, option in enumerate(question['options']):
                        option_text = option['option_text']
                        parts = option_text.split('|')
                        left_part = html.escape(parts[0]) if len(parts) > 0 else ''
                        right_part = html.escape(parts[1]) if len(parts) > 1 else ''


                        left_num = opt_idx + 1
                        right_num = opt_idx + 1

                        table_data.append([
                            Paragraph(f'{left_num}. {left_part}', normal_style),
                            Paragraph('', normal_style),  # Empty space for drawing lines
                            Paragraph(f'{right_num}. {right_part}', normal_style)
                        ])

                    # Create table with extra space in middle column
                    matching_table = Table(table_data, colWidths=[2.2*inch, 1.2*inch, 2.2*inch])
                    matching_table.setStyle(TableStyle([
                        # Header row styling
                        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), UNICODE_FONT_BOLD),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),

                        # Data cells - all columns
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                        ('TOPPADDING', (0, 1), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),

                        # Grid
                        ('GRID', (0, 0), (0, -1), 0.5, colors.grey),  # Left column border
                        ('GRID', (2, 0), (2, -1), 0.5, colors.grey),  # Right column border
                        ('LINEABOVE', (0, 0), (-1, 0), 0.5, colors.grey),
                        ('LINEBELOW', (0, -1), (-1, -1), 0.5, colors.grey),
                    ]))

                    elements.append(matching_table)
                    elements.append(Spacer(1, 8))


                    if not include_answers:
                        elements.append(Paragraph(
                            '<i>Velciet līnijas, lai saskaņotu elementus no kreisās kolonnas ar labo kolonnu.</i>',
                            answer_style
                        ))
                        elements.append(Spacer(1, 6))
                else:
                    # Regular options for multiple choice, true/false
                    for opt_idx, option in enumerate(question['options']):
                        option_letter = chr(65 + opt_idx)  # A, B, C, D
                        option_text = html.escape(option['option_text'])

                        # Mark correct answer if including answers
                        if include_answers and option['is_correct']:
                            opt_para = Paragraph(
                                f"<b>{option_letter}. {option_text} ✓</b>",
                                answer_style
                            )
                        else:
                            opt_para = Paragraph(f"{option_letter}. {option_text}", normal_style)

                        elements.append(opt_para)
                        elements.append(Spacer(1, 3))

            # Correct answer (if including answers and not multiple choice/matching)
            if include_answers and question['question_type'] not in ['matching'] and (not question.get('options') or len(question['options']) == 0):
                answer_text = html.escape(question['correct_answer'])
                elements.append(Paragraph(f"<b>Atbilde:</b> {answer_text}", answer_style))

            # Space for student answer (if not including answers)
            if not include_answers:
                if question['question_type'] in ['short_answer', 'fill_in_blank']:
                    elements.append(Spacer(1, 10))
                    elements.append(Paragraph("_" * 70, normal_style))
                elif question['question_type'] == 'long_answer':
                    elements.append(Spacer(1, 10))
                    for _ in range(4):
                        elements.append(Paragraph("_" * 70, normal_style))
                        elements.append(Spacer(1, 6))

            elements.append(Spacer(1, 12))

    doc.build(elements)

    buffer.seek(0)
    return buffer


def generate_study_material_pdf(material_data):
    """
    Generate PDF for study material

    Args:
        material_data: Study material object with summary and terms

    Returns:
        BytesIO: PDF file content
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=18)

    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        fontName=UNICODE_FONT_BOLD,
        textColor=colors.black,
        spaceAfter=30,
        alignment=TA_CENTER
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        fontName=UNICODE_FONT_BOLD,
        textColor=colors.black,
        spaceAfter=12,
        spaceBefore=12
    )

    term_style = ParagraphStyle(
        'Term',
        parent=styles['Normal'],
        fontSize=12,
        fontName=UNICODE_FONT_BOLD,
        textColor=colors.black,
        spaceAfter=6
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        fontName=UNICODE_FONT
    )

    elements.append(Paragraph(material_data['title'], title_style))
    elements.append(Spacer(1, 12))

    from datetime import datetime
    date_str = datetime.fromisoformat(material_data['created_at'].replace('Z', '+00:00')).strftime('%B %d, %Y')
    elements.append(Paragraph(f"Izveidots: {date_str}", normal_style))
    elements.append(Spacer(1, 30))

    # Summary section
    elements.append(Paragraph("Kopsavilkums", heading_style))
    elements.append(Spacer(1, 12))

    # Handle HTML content in summary (from rich text editor)
    summary_content = material_data['content'].get('summary', '')
    # Strip HTML tags for PDF (simple approach)
    from html.parser import HTMLParser

    class HTMLStripper(HTMLParser):
        def __init__(self):
            super().__init__()
            self.reset()
            self.strict = False
            self.convert_charrefs = True
            self.text = []

        def handle_data(self, d):
            self.text.append(d)

        def get_data(self):
            return ''.join(self.text)

    # For now, use the HTML content directly with Paragraph (ReportLab supports basic HTML)
    summary_para = Paragraph(summary_content, normal_style)
    elements.append(summary_para)
    elements.append(Spacer(1, 30))

    # Key Terms section
    elements.append(Paragraph("Galvenie termini", heading_style))
    elements.append(Spacer(1, 12))

    terms = material_data['content'].get('terms', [])
    for term in terms:
        # Term name
        elements.append(Paragraph(term['name'], term_style))

        # Term definition
        definition = html.escape(term['definition'])
        elements.append(Paragraph(definition, normal_style))
        elements.append(Spacer(1, 12))

    doc.build(elements)

    buffer.seek(0)
    return buffer
