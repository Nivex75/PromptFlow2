import docx
import io
import logging

class DocumentProcessor:
    def extract_text(self, uploaded_file):
        """
        Extract text from an uploaded Word document
        """
        try:
            if uploaded_file is None:
                raise ValueError("No file was uploaded")

            # Log file details for debugging
            logging.info(f"Processing file: {uploaded_file.name}, type: {uploaded_file.type}")

            # Read the file content
            file_content = uploaded_file.read()
            if not file_content:
                raise ValueError("Uploaded file is empty")

            # Create a BytesIO object
            doc_bytes = io.BytesIO(file_content)

            # Open document with python-docx
            doc = docx.Document(doc_bytes)

            # Extract text from paragraphs
            full_text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():  # Only add non-empty paragraphs
                    full_text.append(paragraph.text)

            # Extract text from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = []
                    for cell in row.cells:
                        if cell.text.strip():
                            row_text.append(cell.text.strip())
                    if row_text:
                        full_text.append(" | ".join(row_text))

            # Reset the file pointer for future reads
            uploaded_file.seek(0)

            return "\n".join(full_text)
        except Exception as e:
            logging.error(f"Error processing document: {str(e)}")
            raise Exception(f"Error processing document: {str(e)}")