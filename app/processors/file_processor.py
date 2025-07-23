import fitz  # PyMuPDF
import pandas as pd
from PIL import Image
import io
import os
from app.utils.config import VISION_MODEL, TEXT_MODEL
from groq import Groq

class SmartMultimodalFileProcessor:
    def __init__(self, groq_api_key):
        self.groq_client = Groq(api_key=groq_api_key)

    def analyze_pdf_content_type(self, pdf_document, text_data):
        """
        Analyzes the content of a PDF to determine if vision processing is beneficial.
        """
        has_images = False
        has_complex_layouts = False  # Placeholder for more advanced layout analysis
        image_to_page_ratio = 0.0

        if pdf_document.page_count > 0:
            image_count = 0
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                if page.get_images(full=True):
                    image_count += 1
            image_to_page_ratio = image_count / len(pdf_document)
            if image_to_page_ratio > 0.1:  # If more than 10% of pages have images
                has_images = True

        # Simple heuristics for complex layouts
        if len(text_data) < 500 and has_images:
            has_complex_layouts = True

        needs_vision = has_images or has_complex_layouts or image_to_page_ratio > 0.5
        return {
            "needs_vision": needs_vision,
            "has_images": has_images,
            "has_complex_layouts": has_complex_layouts,
            "image_to_page_ratio": image_to_page_ratio,
        }

    def process_file(self, file_bytes, filename, force_vision=False):
        """
        Process an uploaded file based on its type.
        """
        file_extension = os.path.splitext(filename)[1].lower()
        if file_extension == ".pdf":
            return self.process_pdf_smart_vision(file_bytes, filename, force_vision)
        elif file_extension in [".csv", ".xlsx"]:
            return self.process_tabular_data(file_bytes, file_extension)
        elif file_extension in [".jpg", ".jpeg", ".png"]:
            return self.analyze_image_with_vision(file_bytes, "Analyze this geological image.")
        elif file_extension in [".doc", ".docx", ".txt"]:
            return self.process_text_document(file_bytes, file_extension)
        else:
            return {"error": "Unsupported file type"}

    def process_pdf_smart_vision(self, file_bytes, filename, force_vision=False):
        """
        Process a PDF using smart vision, analyzing pages with visual content selectively.
        """
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_content = ""
        vision_content = []
        vision_calls_made = 0
        vision_calls_saved = 0

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            text_content += f"\n--- Page {page_num + 1} ---\n{text}"

            analysis = self.analyze_pdf_content_type(doc, text)
            if force_vision or analysis["needs_vision"]:
                pix = page.get_pixmap()
                img_bytes = pix.tobytes("png")
                vision_analysis = self.analyze_image_with_vision(
                    img_bytes,
                    "Analyze this geological document page, focusing on charts, graphs, and well logs."
                )
                vision_content.append(vision_analysis)
                vision_calls_made += 1
            else:
                vision_calls_saved += 1
        
        return {
            "text_content": text_content,
            "vision_content": vision_content,
            "stats": {
                "vision_calls_made": vision_calls_made,
                "vision_calls_saved": vision_calls_saved,
                "total_pages": len(doc)
            }
        }

    def analyze_image_with_vision(self, image_data, context):
        """
        Analyzes an image using Groq's vision model.
        """
        response = self.groq_client.chat.completions.create(
            model=VISION_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": context},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{io.BytesIO(image_data).read().hex()}"
                            },
                        },
                    ],
                }
            ],
        )
        return response.choices[0].message.content

    def process_tabular_data(self, file_bytes, file_extension):
        """
        Processes tabular data from CSV or Excel files.
        """
        try:
            if file_extension == ".csv":
                df = pd.read_csv(io.BytesIO(file_bytes))
            else:
                df = pd.read_excel(io.BytesIO(file_bytes))
            
            summary = df.describe().to_string()
            return {"text_content": f"Data Summary:\n{summary}\n\nFull Data:\n{df.to_string()}"}
        except Exception as e:
            return {"error": f"Failed to process tabular data: {e}"}

    def process_text_document(self, file_bytes, file_extension):
        """
        Processes text from DOCX or TXT files.
        """
        try:
            if file_extension == ".docx":
                import docx
                document = docx.Document(io.BytesIO(file_bytes))
                text_content = "\n".join([paragraph.text for paragraph in document.paragraphs])
            else:
                text_content = io.BytesIO(file_bytes).read().decode("utf-8")
            return {"text_content": text_content}
        except Exception as e:
            return {"error": f"Failed to process text document: {e}"}
