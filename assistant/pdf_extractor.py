import pymupdf
import re

def extract_pdf_pages(file_path):
    """
    Extracts text page by page from a PDF file using PyMuPDF.
    Returns a list of dicts:
    [
        {
            'page_number': 1,  # 1-based index
            'text': '...',
            'section_title': '...'
        },
        ...
    ]
    """
    doc = pymupdf.open(file_path)
    pages = []
    
    for i, page in enumerate(doc):
        raw_text = page.get_text()
        cleaned_text = raw_text.strip()
        
        # Extract potential section title from first line
        lines = [line.strip() for line in cleaned_text.splitlines() if line.strip()]
        section_title = lines[0] if lines else f"Page {i + 1}"
        
        pages.append({
            'page_number': i + 1,  # Strict 1-based page numbering as required
            'text': cleaned_text,
            'section_title': section_title[:100]
        })
        
    doc.close()
    return pages

