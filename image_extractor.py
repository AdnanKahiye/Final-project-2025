from PIL import Image
import pytesseract # type: ignore

# Set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = "C:/Program Files/Tesseract-OCR/tesseract.exe"

def extract_text_from_image(image_path):
    """
    Extract text from an image file.
    :param image_path: Path to the image file
    :return: Extracted text as a string
    """
    try:
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""

# Testing the function
if __name__ == "__main__":
    # Provide the path to your test image
    image_path = "sample_image.png"  # Replace with your actual image file path
    text = extract_text_from_image(image_path)  # Call the function, do not pass it as a reference
    print("Extracted text:", text)
