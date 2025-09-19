import os, datetime, tempfile
from tqdm import tqdm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from PyPDF2 import PdfMerger
from llm_processing import process_file_with_llm
from pdf_utils import generate_exhibit_title, create_enhanced_cover_page, convert_to_temp_pdf
from text_extraction import extract_text_from_file


# def create_final_reports(exhibit_files, output_demand_pdf, output_internal_pdf,
#                          claim_id, prepared_by, logo_path=None):
#     temp_files_to_clean = []
#     styles = getSampleStyleSheet()
#     processed_exhibits = []
#     for i, file_path in enumerate(tqdm(exhibit_files, desc="Processing Exhibits"), 1):
#         exhibit_title = generate_exhibit_title(file_path, i)
#         summary, followups, recommendations = process_file_with_llm(file_path)
#         pdf_path, is_temp = convert_to_temp_pdf(file_path, extract_text_from_file)
#         if is_temp:
#             temp_files_to_clean.append(pdf_path)
#         processed_exhibits.append({
#             "title": exhibit_title,
#             "summary": summary,
#             "followups": followups,
#             "recommendations": recommendations,
#             "pdf_path": pdf_path,
#         })

#     demand_cover_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     internal_cover_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     temp_files_to_clean += [demand_cover_pdf, internal_cover_pdf]
#     create_enhanced_cover_page(demand_cover_pdf, "Subrogation Demand Package",
#                                claim_id, prepared_by, "Adverse Carrier", logo_path)
#     create_enhanced_cover_page(internal_cover_pdf, "Internal Adjuster Notes [CONFIDENTIAL]",
#                                claim_id, prepared_by, "Internal Use Only", logo_path)

#     demand_story = []
#     for exhibit in processed_exhibits:
#         demand_story.append(Paragraph(exhibit["title"], styles["Heading2"]))
#         demand_story.append(Paragraph(exhibit["summary"].replace('\n', '<br/>'), styles["Normal"]))
#         demand_story.append(Spacer(1, 0.25*inch))
#     demand_summaries_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     temp_files_to_clean.append(demand_summaries_pdf)
#     SimpleDocTemplate(demand_summaries_pdf, pagesize=LETTER).build(demand_story)

#     internal_story = []
#     for exhibit in processed_exhibits:
#         internal_story.append(Paragraph(exhibit["title"], styles["Heading2"]))
#         internal_story.append(Paragraph("<b>Summary:</b>", styles["Normal"]))
#         internal_story.append(Paragraph(exhibit["summary"], styles["Normal"]))
#         internal_story.append(Paragraph("<b>Follow-Ups:</b>", styles["Normal"]))
#         internal_story.append(Paragraph(exhibit["followups"], styles["Normal"]))
#         internal_story.append(Paragraph("<b>Recommendations:</b>", styles["Normal"]))
#         internal_story.append(Paragraph(exhibit["recommendations"], styles["Normal"]))
#         internal_story.append(PageBreak())
#     internal_notes_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     temp_files_to_clean.append(internal_notes_pdf)
#     SimpleDocTemplate(internal_notes_pdf, pagesize=LETTER).build(internal_story)

#     demand_merger = PdfMerger()
#     demand_merger.append(demand_cover_pdf)
#     demand_merger.append(demand_summaries_pdf)
#     for exhibit in processed_exhibits:
#         demand_merger.append(exhibit["pdf_path"])
#     demand_merger.write(output_demand_pdf)
#     demand_merger.close()

#     internal_merger = PdfMerger()
#     internal_merger.append(internal_cover_pdf)
#     internal_merger.append(internal_notes_pdf)
#     for exhibit in processed_exhibits:
#         internal_merger.append(exhibit["pdf_path"])
#     internal_merger.write(output_internal_pdf)
#     internal_merger.close()

#     for f in temp_files_to_clean:
#         try:
#             os.remove(f)
#             print(f)
#         except OSError: pass

#     print(f"✅ Reports created:\n - Demand: {output_demand_pdf}\n - Internal: {output_internal_pdf}")




# def generate_demand_letter_pdf(claim_id, amount, loss_location):
#     """Generate demand letter PDF for insertion into demand package."""
#     styles = getSampleStyleSheet()
#     demand_letter_story = []
    
#     demand_letter = f"""
#         To:
#         [At-Fault Party's Insurance Carrier Name]
#         [Address]

#         Re: Subrogation Demand - Claim No. {claim_id}
#         Our Insured: [Name]
#         Your Insured: [Name]
#         Date of Loss: [MM/DD/YYYY]
#         Loss Location: {loss_location}

#         Dear [Claims Adjuster Name],

#         We represent [Insurer Name], the automobile insurance carrier for [Claimant Name]. 
#         On [Date of Loss], your insured, [Third Party Insured Name] negligently caused a motor
#         vehicle collision at [Location]. Based on the police report and supporting evidence, 
#         your insured was cited for failure to stop at a red light, thereby establishing liability.

#         As a result of this incident, [Insurer Name] indemnified our insured for the following damages:

#         Category                Amount Paid (USD)
#         ------------------------------------------------
#         [Vehicle Repairs]         $[Enter]
#         [Rental Car Expenses]     $[Enter]
#         [Towing & Storage]        $[Enter]
#         [Medical Payments]        $[Enter]
#         ------------------------------------------------
#         Total Demand            ${amount:,}

#         We hereby demand reimbursement in the amount of ${amount:,} 
#         within thirty (30) days of receipt of this letter. Enclosed please find supporting
#         documentation, including proof of payment, repair invoices, photographs, and the police report.

#         Should this matter remain unresolved, we reserve the right to pursue recovery 
#         through Arbitration Forums, Inc. or litigation as applicable under state law.

#         Please direct all correspondence and payments to the undersigned.

#         Sincerely,  
#         [Claims Representative Name]  
#         [Title]  
#         [Insurer Name]  
#         [Contact Information]  
#         """

#     demand_letter_story.append(Paragraph(demand_letter, styles["Normal"]))

#     temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     SimpleDocTemplate(temp_pdf).build(demand_letter_story)
#     return temp_pdf



# def create_final_reports(exhibit_files, output_demand_pdf, output_internal_pdf,
#                          claim_id, amount, loss_location, prepared_by, logo_path=None):
#     temp_files_to_clean = []
#     styles = getSampleStyleSheet()
#     processed_exhibits = []
#     seen_files = set()
#     seen_titles = set()

#     # Deduplicate file paths first (Option 1)
#     unique_files = []
#     for file_path in exhibit_files:
#         if file_path not in seen_files:
#             seen_files.add(file_path)
#             unique_files.append(file_path)

#     # Process unique files
#     for i, file_path in enumerate(tqdm(unique_files, desc="Processing Exhibits"), 1):
#         exhibit_title = generate_exhibit_title(file_path, i)

#         # Deduplicate based on exhibit title (Option 2)
#         if exhibit_title in seen_titles:
#             print(f"⚠️ Skipping duplicate exhibit: {exhibit_title}")
#             continue
#         seen_titles.add(exhibit_title)

#         summary, followups, recommendations = process_file_with_llm(file_path)
#         pdf_path, is_temp = convert_to_temp_pdf(file_path, extract_text_from_file)
#         if is_temp:
#             temp_files_to_clean.append(pdf_path)

#         processed_exhibits.append({
#             "title": exhibit_title,
#             "summary": summary,
#             "followups": followups,
#             "recommendations": recommendations,
#             "pdf_path": pdf_path,
#         })

#     # ---- (rest of your code unchanged) ----
#     demand_cover_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     internal_cover_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     temp_files_to_clean += [demand_cover_pdf, internal_cover_pdf]
#     create_enhanced_cover_page(demand_cover_pdf, "Subrogation Demand Package",
#                                claim_id, prepared_by, "Adverse Carrier", logo_path)
#     create_enhanced_cover_page(internal_cover_pdf, "Internal Adjuster Notes [CONFIDENTIAL]",
#                                claim_id, prepared_by, "Internal Use Only", logo_path)

#     # Build summaries
#     demand_story = []
#     for exhibit in processed_exhibits:
#         demand_story.append(Paragraph(exhibit["title"], styles["Heading2"]))
#         demand_story.append(Paragraph(exhibit["summary"].replace('\n', '<br/>'), styles["Normal"]))
#         demand_story.append(Spacer(1, 0.25*inch))
#     demand_summaries_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     temp_files_to_clean.append(demand_summaries_pdf)
#     SimpleDocTemplate(demand_summaries_pdf, pagesize=LETTER).build(demand_story)

#     internal_story = []
#     for exhibit in processed_exhibits:
#         internal_story.append(Paragraph(exhibit["title"], styles["Heading2"]))
#         internal_story.append(Paragraph("<b>Summary:</b>", styles["Normal"]))
#         internal_story.append(Paragraph(exhibit["summary"], styles["Normal"]))
#         internal_story.append(Paragraph("<b>Follow-Ups:</b>", styles["Normal"]))
#         internal_story.append(Paragraph(exhibit["followups"], styles["Normal"]))
#         internal_story.append(Paragraph("<b>Recommendations:</b>", styles["Normal"]))
#         internal_story.append(Paragraph(exhibit["recommendations"], styles["Normal"]))
#         internal_story.append(PageBreak())
#     internal_notes_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     temp_files_to_clean.append(internal_notes_pdf)
#     SimpleDocTemplate(internal_notes_pdf, pagesize=LETTER).build(internal_story)

#     # Generate demand letter PDF
#     demand_letter_pdf = generate_demand_letter_pdf(claim_id, amount, loss_location)  # replace amount/location
#     temp_files_to_clean.append(demand_letter_pdf)

#     demand_merger = PdfMerger()
#     demand_merger.append(demand_cover_pdf)       # Page 1: Cover
#     demand_merger.append(demand_letter_pdf)      # Page 2: Demand Letter
#     demand_merger.append(demand_summaries_pdf)   # Summaries
#     for exhibit in processed_exhibits:           # Exhibits
#         demand_merger.append(exhibit["pdf_path"])
#     demand_merger.write(output_demand_pdf)
#     demand_merger.close()




#     # Merge PDFs
#     # demand_merger = PdfMerger()
#     # demand_merger.append(demand_cover_pdf)
#     # demand_merger.append(demand_summaries_pdf)
#     # for exhibit in processed_exhibits:
#     #     demand_merger.append(exhibit["pdf_path"])
#     # demand_merger.write(output_demand_pdf)
#     # demand_merger.close()

#     internal_merger = PdfMerger()
#     internal_merger.append(internal_cover_pdf)
#     internal_merger.append(internal_notes_pdf)
#     for exhibit in processed_exhibits:
#         internal_merger.append(exhibit["pdf_path"])
#     internal_merger.write(output_internal_pdf)
#     internal_merger.close()

#     # Cleanup
#     for f in temp_files_to_clean:
#         try:
#             os.remove(f)
#         except OSError:
#             pass

#     print(f"✅ Reports created:\n - Demand: {output_demand_pdf}\n - Internal: {output_internal_pdf}")





from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PyPDF2 import PdfMerger
import tempfile
import os


# def generate_demand_letter_pdf(claim_id, amount, loss_location):
#     """Generate demand letter PDF for insertion into demand package."""
#     styles = getSampleStyleSheet()
#     story = []

#     # Build letter step by step with proper formatting
#     sections = [
#         "To:",
#         "[At-Fault Party's Insurance Carrier Name]",
#         "[Address]",
#         "",
#         f"Re: Subrogation Demand - Claim No. {claim_id}",
#         "Our Insured: [Name]",
#         "Your Insured: [Name]",
#         "Date of Loss: [MM/DD/YYYY]",
#         f"Loss Location: {loss_location}",
#         "",
#         "Dear [Claims Adjuster Name],",
#         "",
#         "We represent [Insurer Name], the automobile insurance carrier for [Claimant Name]. "
#         "On [Date of Loss], your insured, [Third Party Insured Name] negligently caused a motor "
#         "vehicle collision at [Location]. Based on the police report and supporting evidence, "
#         "your insured was cited for failure to stop at a red light, thereby establishing liability.",
#         "",
#         "As a result of this incident, [Insurer Name] indemnified our insured for the following damages:",
#         "",
#         "Category                Amount Paid (USD)",
#         "------------------------------------------------",
#         "[Vehicle Repairs]         $[Enter]",
#         "[Rental Car Expenses]     $[Enter]",
#         "[Towing & Storage]        $[Enter]",
#         "[Medical Payments]        $[Enter]",
#         "------------------------------------------------",
#         f"Total Demand            ${amount:,.2f}",
#         "",
#         f"We hereby demand reimbursement in the amount of ${amount:,.2f} "
#         "within thirty (30) days of receipt of this letter. Enclosed please find supporting "
#         "documentation, including proof of payment, repair invoices, photographs, and the police report.",
#         "",
#         "Should this matter remain unresolved, we reserve the right to pursue recovery "
#         "through Arbitration Forums, Inc. or litigation as applicable under state law.",
#         "",
#         "Please direct all correspondence and payments to the undersigned.",
#         "",
#         "Sincerely,",
#         "[Claims Representative Name]",
#         "[Title]",
#         "[Insurer Name]",
#         "[Contact Information]",
#     ]

#     for line in sections:
#         story.append(Paragraph(line, styles["Normal"]))
#         story.append(Spacer(1, 12))  # 12 points = ~1 line break

#     temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     SimpleDocTemplate(temp_pdf, pagesize=LETTER).build(story)
#     return temp_pdf

# def generate_demand_letter_from_text(letter_text):
#     """Convert edited demand letter text to PDF."""
#     styles = getSampleStyleSheet()
#     story = []
#     for line in letter_text.split("\n"):
#         story.append(Paragraph(line, styles["Normal"]))
#         story.append(Spacer(1, 12))

#     temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     SimpleDocTemplate(temp_pdf, pagesize=LETTER).build(story)
#     return temp_pdf




def generate_demand_letter_from_text(letter_text):
    """Convert edited demand letter text to PDF with header."""
    styles = getSampleStyleSheet()

    # Custom centered header style
    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Heading1"],
        alignment=1,  # 0=left, 1=center, 2=right
        spaceAfter=20,
    )

    story = []

    # Add header at top
    story.append(Paragraph("Demand Letter", header_style))
    story.append(Spacer(1, 24))  # add some space below header

    # Add body text
    for line in letter_text.split("\n"):
        story.append(Paragraph(line, styles["Normal"]))
        story.append(Spacer(1, 12))

    # Create temporary PDF file
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    SimpleDocTemplate(temp_pdf, pagesize=LETTER).build(story)
    return temp_pdf







# def create_final_reports(exhibit_files, output_demand_pdf, output_internal_pdf,
#                          claim_id, amount, loss_location, prepared_by, logo_path=None):
#     temp_files_to_clean = []
#     styles = getSampleStyleSheet()
#     processed_exhibits = []
#     seen_files, seen_titles = set(), set()

#     # Deduplicate file paths
#     unique_files = []
#     for file_path in exhibit_files:
#         if file_path not in seen_files:
#             seen_files.add(file_path)
#             unique_files.append(file_path)

#     # Process unique files
#     for i, file_path in enumerate(unique_files, 1):
#         exhibit_title = generate_exhibit_title(file_path, i)
#         if exhibit_title in seen_titles:
#             continue
#         seen_titles.add(exhibit_title)

#         summary, followups, recommendations = process_file_with_llm(file_path)
#         pdf_path, is_temp = convert_to_temp_pdf(file_path, extract_text_from_file)
#         if is_temp:
#             temp_files_to_clean.append(pdf_path)

#         processed_exhibits.append({
#             "title": exhibit_title,
#             "summary": summary,
#             "followups": followups,
#             "recommendations": recommendations,
#             "pdf_path": pdf_path,
#         })

#     # Create covers
#     demand_cover_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     internal_cover_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     temp_files_to_clean += [demand_cover_pdf, internal_cover_pdf]

#     create_enhanced_cover_page(demand_cover_pdf, "Subrogation Demand Package",
#                                claim_id, prepared_by, "Adverse Carrier", logo_path)
#     create_enhanced_cover_page(internal_cover_pdf, "Internal Adjuster Notes [CONFIDENTIAL]",
#                                claim_id, prepared_by, "Internal Use Only", logo_path)

#     # Build summaries (Demand)
#     demand_story = []
#     for exhibit in processed_exhibits:
#         demand_story.append(Paragraph(exhibit["title"], styles["Heading2"]))
#         demand_story.append(Paragraph(exhibit["summary"].replace('\n', '<br/>'), styles["Normal"]))
#         demand_story.append(Spacer(1, 0.25 * inch))
#     demand_summaries_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     temp_files_to_clean.append(demand_summaries_pdf)
#     SimpleDocTemplate(demand_summaries_pdf, pagesize=LETTER).build(demand_story)

#     # Build summaries (Internal)
#     internal_story = []
#     for exhibit in processed_exhibits:
#         internal_story.append(Paragraph(exhibit["title"], styles["Heading2"]))
#         internal_story.append(Paragraph("<b>Summary:</b>", styles["Normal"]))
#         internal_story.append(Paragraph(exhibit["summary"], styles["Normal"]))
#         internal_story.append(Paragraph("<b>Follow-Ups:</b>", styles["Normal"]))
#         internal_story.append(Paragraph(exhibit["followups"], styles["Normal"]))
#         internal_story.append(Paragraph("<b>Recommendations:</b>", styles["Normal"]))
#         internal_story.append(Paragraph(exhibit["recommendations"], styles["Normal"]))
#         internal_story.append(PageBreak())
#     internal_notes_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     temp_files_to_clean.append(internal_notes_pdf)
#     SimpleDocTemplate(internal_notes_pdf, pagesize=LETTER).build(internal_story)

#     # Demand letter PDF
#     demand_letter_pdf = generate_demand_letter_pdf(claim_id, amount, loss_location)
#     temp_files_to_clean.append(demand_letter_pdf)

#     # Merge final demand package
#     demand_merger = PdfMerger()
#     demand_merger.append(demand_cover_pdf)       # Page 1: Cover
#     demand_merger.append(demand_letter_pdf)      # Page 2: Demand Letter
#     demand_merger.append(demand_summaries_pdf)   # Summaries
#     for exhibit in processed_exhibits:           # Exhibits
#         demand_merger.append(exhibit["pdf_path"])
#     demand_merger.write(output_demand_pdf)
#     demand_merger.close()

#     # Merge internal notes
#     internal_merger = PdfMerger()
#     internal_merger.append(internal_cover_pdf)
#     internal_merger.append(internal_notes_pdf)
#     internal_merger.write(output_internal_pdf)
#     internal_merger.close()

#     # Cleanup temps if needed
#     for f in temp_files_to_clean:
#         if os.path.exists(f):
#             os.remove(f)


def create_internal_final_reports(exhibit_files, output_internal_pdf,
                         claim_id,prepared_by, logo_path=None):
    temp_files_to_clean = []
    styles = getSampleStyleSheet()
    processed_exhibits = []
    seen_files, seen_titles = set(), set()

    # Deduplicate file paths
    unique_files = []
    for file_path in exhibit_files:
        if file_path not in seen_files:
            seen_files.add(file_path)
            unique_files.append(file_path)

    # Process unique files
    for i, file_path in enumerate(unique_files, 1):
        exhibit_title = generate_exhibit_title(file_path, i)
        if exhibit_title in seen_titles:
            continue
        seen_titles.add(exhibit_title)

        summary, followups, recommendations = process_file_with_llm(file_path)
        pdf_path, is_temp = convert_to_temp_pdf(file_path, extract_text_from_file)
        if is_temp:
            temp_files_to_clean.append(pdf_path)

        processed_exhibits.append({
            "title": exhibit_title,
            "summary": summary,
            "followups": followups,
            "recommendations": recommendations,
            "pdf_path": pdf_path,
        })

    internal_cover_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    temp_files_to_clean += [ internal_cover_pdf]

    create_enhanced_cover_page(internal_cover_pdf, "Internal Adjuster Report [CONFIDENTIAL]",
                               claim_id, prepared_by, "Internal Use Only", logo_path)


    # Build summaries (Internal)
    internal_story = []
    for exhibit in processed_exhibits:
        internal_story.append(Paragraph(exhibit["title"], styles["Heading2"]))
        internal_story.append(Paragraph("<b>Summary:</b>", styles["Normal"]))
        internal_story.append(Paragraph(exhibit["summary"], styles["Normal"]))
        internal_story.append(Paragraph("<b>Follow-Ups:</b>", styles["Normal"]))
        internal_story.append(Paragraph(exhibit["followups"], styles["Normal"]))
        internal_story.append(Paragraph("<b>Recommendations:</b>", styles["Normal"]))
        internal_story.append(Paragraph(exhibit["recommendations"], styles["Normal"]))
        internal_story.append(PageBreak())
    internal_notes_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    temp_files_to_clean.append(internal_notes_pdf)
    SimpleDocTemplate(internal_notes_pdf, pagesize=LETTER).build(internal_story)


    # Merge internal notes
    internal_merger = PdfMerger()
    internal_merger.append(internal_cover_pdf)
    internal_merger.append(internal_notes_pdf)
    for exhibit in processed_exhibits:
        internal_merger.append(exhibit["pdf_path"])
    internal_merger.write(output_internal_pdf)
    internal_merger.close()

    # Cleanup temps if needed
    for f in temp_files_to_clean:
        if os.path.exists(f):
            os.remove(f)


def create_demand_package_final_reports(exhibit_files, output_demand_pdf,
                         claim_id, prepared_by, demand_letter_pdf, logo_path=None):
    temp_files_to_clean = []
    styles = getSampleStyleSheet()
    processed_exhibits = []
    seen_files, seen_titles = set(), set()

    # Deduplicate file paths
    unique_files = []
    for file_path in exhibit_files:
        if file_path not in seen_files:
            seen_files.add(file_path)
            unique_files.append(file_path)

    # Process unique files
    for i, file_path in enumerate(unique_files, 1):
        exhibit_title = generate_exhibit_title(file_path, i)
        if exhibit_title in seen_titles:
            continue
        seen_titles.add(exhibit_title)

        summary, followups, recommendations = process_file_with_llm(file_path)
        pdf_path, is_temp = convert_to_temp_pdf(file_path, extract_text_from_file)
        if is_temp:
            temp_files_to_clean.append(pdf_path)

        processed_exhibits.append({
            "title": exhibit_title,
            "summary": summary,
            "followups": followups,
            "recommendations": recommendations,
            "pdf_path": pdf_path,
        })

    # Create covers
    demand_cover_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    temp_files_to_clean += [demand_cover_pdf]

    create_enhanced_cover_page(demand_cover_pdf, "Subrogation Demand Package",
                               claim_id, prepared_by, "Adverse Carrier Claims Department", logo_path)

    # Build summaries (Demand)
    demand_story = []
    for exhibit in processed_exhibits:
        demand_story.append(Paragraph(exhibit["title"], styles["Heading2"]))
        demand_story.append(Paragraph(exhibit["summary"].replace('\n', '<br/>'), styles["Normal"]))
        demand_story.append(Spacer(1, 0.25 * inch))
    demand_summaries_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    temp_files_to_clean.append(demand_summaries_pdf)
    SimpleDocTemplate(demand_summaries_pdf, pagesize=LETTER).build(demand_story)


    # Demand letter PDF
    # demand_letter_pdf = generate_demand_letter_from_text(letter_text)
    temp_files_to_clean.append(demand_letter_pdf)

    # Merge final demand package
    demand_merger = PdfMerger()
    demand_merger.append(demand_cover_pdf)       # Page 1: Cover
    demand_merger.append(demand_letter_pdf)      # Page 2: Demand Letter
    demand_merger.append(demand_summaries_pdf)   # Summaries
    for exhibit in processed_exhibits:           # Exhibits
        demand_merger.append(exhibit["pdf_path"])
    demand_merger.write(output_demand_pdf)
    demand_merger.close()

    # Cleanup temps if needed
    for f in temp_files_to_clean:
        if os.path.exists(f):
            os.remove(f)
