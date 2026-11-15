"""
Converts Financial_Inclusion_Analytics.pdf into 5 high-resolution PNG screenshots.
Saves to docs/screenshots/ with exact required filenames:
- 01_portfolio_health.png
- 02_collection_performance.png
- 03_repayment_vintage.png
- 04_digital_collections.png
- 05_data_quality.png
"""

import os
import pypdfium2 as pdfium

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(PROJECT_ROOT, "docs", "Financial_Inclusion_Analytics.pdf")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "docs", "screenshots")

PAGE_FILENAMES = [
    "01_portfolio_health.png",
    "02_collection_performance.png",
    "03_repayment_vintage.png",
    "04_digital_collections.png",
    "05_data_quality.png"
]

def convert():
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"PDF not found at: {PDF_PATH}")
        
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    pdf = pdfium.PdfDocument(PDF_PATH)
    page_count = len(pdf)
    print(f"Loaded PDF: {PDF_PATH}")
    print(f"Total Pages: {page_count}")
    
    if page_count != 5:
        raise ValueError(f"Expected exactly 5 pages, but found {page_count}")
        
    # Render at ~200 DPI (scale = 200 / 72 = 2.778)
    scale = 200 / 72
    
    for i in range(page_count):
        page = pdf.get_page(i)
        bitmap = page.render(scale=scale)
        pil_image = bitmap.to_pil()
        
        target_name = PAGE_FILENAMES[i]
        target_path = os.path.join(OUTPUT_DIR, target_name)
        pil_image.save(target_path, format="PNG")
        
        fsize_kb = os.path.getsize(target_path) / 1024
        print(f"Page {i+1} saved to {target_name} | Size: {pil_image.size} | File size: {fsize_kb:.1f} KB")

if __name__ == "__main__":
    convert()
