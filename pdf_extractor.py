import PyPDF2

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.
    :param pdf_path: Path to the PDF file
    :return: Extracted text as a string
    """
    extracted_text = ""
    try:
        with open(pdf_path, "rb") as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                extracted_text += page.extract_text()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return extracted_text
