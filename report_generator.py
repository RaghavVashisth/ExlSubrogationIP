import os, datetime, tempfile
from tqdm import tqdm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from PyPDF2 import PdfMerger
from llm_processing import process_file_with_llm, llm_for_highlights
from pdf_utils import generate_exhibit_title, create_enhanced_cover_page, convert_to_temp_pdf
from text_extraction import extract_text_from_file
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from PyPDF2 import PdfMerger
import tempfile
import os
import csv



    


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


# def llm_for_highlights(prompt):
#     try:
    
#         # 1) factual summary (low randomness)
#         resp_sum = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[
#                 {"role": "system", "content": "You are an insurance claims assistant. your job is to only keep most important key highlights from summary, followups and recommendations from the given witness statement, repair estimates and photo estimates. Make sure that key highlights are short and crisp."},
#                 {"role": "user", "content": prompt }
                
#             ],
#             temperature=0.2,
#             top_p=0.1,
#             max_tokens=600
#         )
#         summary = resp_sum.choices[0].message.content.strip()

#         return summary

#     except Exception as err:
#         # Return safe fallback strings (so create_final_reports won't crash)
#         return f"[LLM error: {err}]", "N/A", "N/A"

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




# def create_internal_final_reports(exhibit_files, output_internal_pdf,
#                                   claim_id, prepared_by, logo_path=None):
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

#     # Prepare highlights directory
#     highlights_dir = os.path.join(os.getcwd(), "highlights")
#     os.makedirs(highlights_dir, exist_ok=True)
#     highlights_csv_path = os.path.join(highlights_dir, f"{claim_id}_highlights.csv")

#     # CSV setup
#     with open(highlights_csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(["Claim_ID", "Exhibit_Title", "Key_Highlights"])

#         # Process each exhibit
#         for i, file_path in enumerate(unique_files, 1):
#             exhibit_title = generate_exhibit_title(file_path, i)
#             if exhibit_title in seen_titles:
#                 continue
#             seen_titles.add(exhibit_title)

#             summary, followups, recommendations = process_file_with_llm(file_path)
#             pdf_path, is_temp = convert_to_temp_pdf(file_path, extract_text_from_file)
#             if is_temp:
#                 temp_files_to_clean.append(pdf_path)

#             # Generate highlights using LLM
#             highlight_prompt = (
#                 f"Summary: {summary}\n\nFollow-Ups: {followups}\n\nRecommendations: {recommendations}"
#             )
#             key_highlights = llm_for_highlights(highlight_prompt)

#             # Write to CSV
#             writer.writerow([claim_id, exhibit_title, key_highlights])

#             # Store processed info for PDF
#             processed_exhibits.append({
#                 "title": exhibit_title,
#                 "summary": summary,
#                 "followups": followups,
#                 "recommendations": recommendations,
#                 "pdf_path": pdf_path,
#             })

#     # --- Create Cover Page ---
#     internal_cover_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
#     temp_files_to_clean.append(internal_cover_pdf)
#     create_enhanced_cover_page(
#         internal_cover_pdf,
#         "Internal Adjuster Report [CONFIDENTIAL]",
#         claim_id, prepared_by, "Internal Use Only", logo_path
#     )

#     # --- Build Internal Notes PDF ---
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

#     # --- Merge All PDFs ---
#     internal_merger = PdfMerger()
#     internal_merger.append(internal_cover_pdf)
#     internal_merger.append(internal_notes_pdf)
#     for exhibit in processed_exhibits:
#         internal_merger.append(exhibit["pdf_path"])
#     internal_merger.write(output_internal_pdf)
#     internal_merger.close()

#     # --- Cleanup Temporary Files ---
#     for f in temp_files_to_clean:
#         if os.path.exists(f):
#             os.remove(f)

#     print(f"✅ Internal report created: {output_internal_pdf}")
#     print(f"✅ Highlights saved: {highlights_csv_path}")
















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
