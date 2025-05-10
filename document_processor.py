import docx
import io
import logging
import PyPDF2 

class DocumentProcessor:
    def extract_text(self, uploaded_file):
        """
        Extract text from an uploaded document (Word or PDF)
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

            # Determine file type based on extension
            file_extension = uploaded_file.name.split('.')[-1].lower()

            # Process based on file type
            if file_extension == 'docx':
                return self._extract_from_docx(file_content)
            elif file_extension == 'pdf':
                return self._extract_from_pdf(file_content)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}. Only .docx and .pdf files are supported.")

        except Exception as e:
            logging.error(f"Error processing document: {str(e)}")
            raise Exception(f"Error processing document: {str(e)}")
        finally:
            # Reset the file pointer for future reads
            uploaded_file.seek(0)

    def _extract_from_docx(self, file_content):
        """Extract text from docx content"""
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

        return "\n".join(full_text)

    def _extract_from_pdf(self, file_content):
        """Extract text from PDF content"""
        # Create a BytesIO object from file content
        pdf_bytes = io.BytesIO(file_content)

        # Create a PDF reader object
        pdf_reader = PyPDF2.PdfReader(pdf_bytes)

        # Extract text from all pages
        full_text = []
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:  # Skip empty pages
                full_text.append(page_text)

        # If no text was extracted, the PDF might be scanned or image-based
        if not full_text:
            return "The PDF appears to contain no extractable text. It may be a scanned document or image-based PDF."

        return "\n\n".join(full_text)