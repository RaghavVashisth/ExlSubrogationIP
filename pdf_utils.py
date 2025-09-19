import os, datetime, tempfile
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from PIL import Image

def generate_exhibit_title(file_path, index):
    base = os.path.basename(file_path)
    name, _ = os.path.splitext(base)
    return f"Exhibit {index}: {name.replace('_',' ').replace('-',' ').title()}"

def create_enhanced_cover_page(pdf_path, title, claim_id, prepared_by, prepared_for, logo_path=None):
    c = canvas.Canvas(pdf_path, pagesize=LETTER)
    width, height = LETTER
    border_margin = 0.5 * inch
    c.setStrokeColorRGB(0.1, 0.1, 0.1)
    c.setLineWidth(1)
    c.rect(border_margin, border_margin, width - 2*border_margin, height - 2*border_margin)

    if logo_path and os.path.exists(logo_path):
        c.drawImage(logo_path, 1*inch, height - 2*inch, width=1.5*inch, preserveAspectRatio=True)

    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 2.5 * inch, title)

    text = f"""
    Claim ID: {claim_id}
    Prepared For: {prepared_for}
    Prepared By: {prepared_by}
    Date: {datetime.date.today().strftime("%B %d, %Y")}
    """
    c.setFont("Helvetica", 14)
    for i, line in enumerate(text.strip().split("\n")):
        c.drawCentredString(width/2, height - 4*inch - i*20, line.strip())

    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(HexColor("#666666"))
    c.drawCentredString(width/2, 1*inch, "This document is confidential.")
    c.showPage()
    c.save()

def convert_to_temp_pdf(file_path, extract_text_fn):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return file_path, False
    tmp_pdf_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    styles = getSampleStyleSheet()
    if ext in [".docx", ".txt"]:
        text = extract_text_fn(file_path).replace('\n', '<br/>')
        doc = SimpleDocTemplate(tmp_pdf_path, pagesize=LETTER)
        doc.build([Paragraph(text, styles["Normal"])])
    elif ext in [".png", ".jpg", ".jpeg"]:
        c = canvas.Canvas(tmp_pdf_path, pagesize=LETTER)
        width, height = LETTER
        img = Image.open(file_path)
        img_width, img_height = img.size
        aspect = img_height / float(img_width)
        new_width = width - 2*inch
        new_height = new_width * aspect
        if new_height > height - 2*inch:
            new_height = height - 2*inch
            new_width = new_height / aspect
        c.drawImage(file_path, (width-new_width)/2, (height-new_height)/2,
                    width=new_width, height=new_height, preserveAspectRatio=True)
        c.showPage()
        c.save()
    else:
        doc = SimpleDocTemplate(tmp_pdf_path, pagesize=LETTER)
        doc.build([Paragraph("Unsupported file type", styles["Normal"])])
    return tmp_pdf_path, True
