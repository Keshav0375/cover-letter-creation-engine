from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from io import BytesIO


def create_pdf(cover_letter_text: str) -> bytes:
    """
    Create a professionally formatted PDF from cover letter text.
    Uses 1 line spacing and 1.3 cm margins with justified text.

    Args:
        cover_letter_text: The cover letter content as string

    Returns:
        PDF file as bytes

    Raises:
        Exception: If PDF generation fails
    """
    try:
        # Create a BytesIO buffer to store PDF
        buffer = BytesIO()

        # Create PDF document with 1.3 cm margins
        margin = 1.3 * cm
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=margin,
            leftMargin=margin,
            topMargin=margin,
            bottomMargin=margin
        )

        # Container for PDF elements
        elements = []

        # Define styles
        styles = getSampleStyleSheet()

        # Custom style for header/contact information (each line separate)
        header_style = ParagraphStyle(
            'CoverLetterHeader',
            parent=styles['Normal'],
            fontSize=11,
            leading=16.5,
            alignment=TA_LEFT,
            spaceAfter=2,
            spaceBefore=0,
            fontName='Times-Roman'
        )

        # Custom style for body paragraphs - JUSTIFIED
        body_style = ParagraphStyle(
            'CoverLetterBody',
            parent=styles['Normal'],
            fontSize=11,
            leading=16.5,
            alignment=TA_JUSTIFY,
            spaceAfter=11,
            spaceBefore=0,
            fontName='Times-Roman',
            firstLineIndent=0
        )

        # Custom style for date and employer info
        info_style = ParagraphStyle(
            'InfoStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=16.5,
            alignment=TA_LEFT,
            spaceAfter=2,
            spaceBefore=0,
            fontName='Times-Roman'
        )

        # Custom style for greeting
        greeting_style = ParagraphStyle(
            'GreetingStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=16.5,
            alignment=TA_LEFT,
            spaceAfter=11,
            spaceBefore=0,
            fontName='Times-Roman'
        )

        # Custom style for closing
        closing_style = ParagraphStyle(
            'ClosingStyle',
            parent=styles['Normal'],
            fontSize=11,
            leading=16.5,
            alignment=TA_LEFT,
            spaceAfter=2,
            spaceBefore=11,
            fontName='Times-Roman'
        )

        # Split the cover letter into paragraphs
        paragraphs = cover_letter_text.split('\n\n')

        greeting_found = False
        closing_found = False

        # Process each paragraph
        for i, para_text in enumerate(paragraphs):
            para_text = para_text.strip()

            if not para_text:
                continue

            # Detect section types
            has_email = '@' in para_text
            has_phone = any(char.isdigit() for char in para_text) and ('-' in para_text or '(' in para_text)
            has_url = 'http' in para_text.lower() or 'www.' in para_text.lower()

            is_header = i == 0 and (has_email or has_phone or has_url)

            is_date = any(month in para_text for month in [
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]) and len(para_text) < 50

            is_subject = para_text.startswith('Subject:')
            is_greeting = para_text.startswith('Dear')
            is_closing = para_text.startswith('Sincerely')

            # Employer info: comes after date, before subject/greeting, and is short
            is_employer_info = (not is_header and not is_date and not is_subject
                                and not is_greeting and not is_closing
                                and not greeting_found and i > 0 and len(para_text) < 200
                                and '\n' in para_text)

            # Handle header section (contact info with line breaks)
            if is_header:
                lines = para_text.split('\n')
                for line in lines:
                    if line.strip():
                        para = Paragraph(line.strip(), header_style)
                        elements.append(para)
                elements.append(Spacer(1, 0.4 * cm))
                continue

            # Handle date
            if is_date:
                para = Paragraph(para_text, info_style)
                elements.append(para)
                elements.append(Spacer(1, 0.4 * cm))
                continue

            # Handle employer info (multiple lines)
            if is_employer_info:
                lines = para_text.split('\n')
                for line in lines:
                    if line.strip():
                        para = Paragraph(line.strip(), info_style)
                        elements.append(para)
                elements.append(Spacer(1, 0.4 * cm))
                continue

            # Handle subject line
            if is_subject:
                para = Paragraph(para_text, info_style)
                elements.append(para)
                elements.append(Spacer(1, 0.4 * cm))
                continue

            # Handle greeting
            if is_greeting:
                para = Paragraph(para_text, greeting_style)
                elements.append(para)
                greeting_found = True
                continue

            # Handle closing
            if is_closing:
                closing_found = True
                lines = para_text.split('\n')
                for line in lines:
                    if line.strip():
                        para = Paragraph(line.strip(), closing_style)
                        elements.append(para)
                continue

            # Everything else after greeting and before closing is body text
            if greeting_found and not closing_found:
                # Replace newlines within paragraph with space for proper flow
                para_text = para_text.replace('\n', ' ')
                para = Paragraph(para_text, body_style)
                elements.append(para)

        # Build PDF
        doc.build(elements)

        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    except Exception as e:
        raise Exception(f"Failed to generate PDF: {str(e)}")


def create_pdf_advanced(cover_letter_text: str, candidate_name: str = None) -> bytes:
    """
    Create a more advanced PDF with better formatting and optional watermark.
    This is an alternative function with more features.

    Args:
        cover_letter_text: The cover letter content as string
        candidate_name: Optional candidate name for metadata

    Returns:
        PDF file as bytes
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.units import cm

        buffer = BytesIO()

        # Create canvas
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Set metadata
        if candidate_name:
            c.setAuthor(candidate_name)
            c.setTitle(f"Cover Letter - {candidate_name}")
        c.setSubject("Professional Cover Letter")

        # Set margins (1.3 cm)
        margin = 1.3 * cm
        left_margin = margin
        right_margin = width - margin
        top_margin = height - margin
        bottom_margin = margin

        # Starting position
        y_position = top_margin

        # Set font (11pt)
        c.setFont("Times-Roman", 11)
        line_height = 13.2  # 1.2x spacing for readability

        # Split text into lines and paragraphs
        paragraphs = cover_letter_text.split('\n\n')

        for para_idx, para in enumerate(paragraphs):
            if not para.strip():
                y_position -= 11
                continue

            # Split paragraph into lines
            lines = para.split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    y_position -= 13.2
                    continue

                # Word wrap
                words = line.split()
                current_line = ""

                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    text_width = c.stringWidth(test_line, "Times-Roman", 11)

                    if text_width <= (right_margin - left_margin):
                        current_line = test_line
                    else:
                        # Draw current line
                        c.drawString(left_margin, y_position, current_line)
                        y_position -= line_height
                        current_line = word

                        # Check if we need a new page
                        if y_position < bottom_margin + 2 * cm:
                            c.showPage()
                            c.setFont("Times-Roman", 11)
                            y_position = top_margin

                # Draw remaining text
                if current_line:
                    c.drawString(left_margin, y_position, current_line)
                    y_position -= line_height

            # Space between paragraphs
            y_position -= 11

            # Check if we need a new page
            if y_position < bottom_margin + 2 * cm:
                c.showPage()
                c.setFont("Times-Roman", 11)
                y_position = top_margin

        # Save PDF
        c.save()

        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    except Exception as e:
        # Fallback to simple version
        return create_pdf(cover_letter_text)