from text_extraction import extract_text_from_file
from llm_processing import  llm_for_highlights
import os


def generate_highlights(file_path):

    ext = os.path.splitext(file_path)[1].lower()
    try:
        # -----------------------------
        # Text-based files: PDF / DOCX / TXT
        # -----------------------------
        if ext in (".pdf", ".docx", ".txt"):
            # extract_text_from_file must exist in your notebook
            raw = extract_text_from_file(file_path)
            if not raw or raw.strip() == "":
                raw = "No readable content found."


        summary = llm_for_highlights(raw[:4500])
        print("Generated Summary Text:", summary)  # Debug print


        return summary
    
    except Exception as err:
        print(f"Error generating highlights: {err}")
        return "Error generating highlights."