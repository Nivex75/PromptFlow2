import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import io
from document_processor import DocumentProcessor

class SourceDocumentManager:
    """
    Manages source documents (contracts, leases, etc.) that will be analyzed.
    Provides persistent storage and retrieval of documents for analysis workflows.
    """

    def __init__(self, source_dir="source_documents", metadata_file="source_documents.json"):
        self.source_dir = source_dir
        self.metadata_file = metadata_file
        self.doc_processor = DocumentProcessor()
        self._ensure_directories()
        self._ensure_metadata_file()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.source_dir, exist_ok=True)

    def _ensure_metadata_file(self):
        """Create metadata file if it doesn't exist"""
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'w') as f:
                json.dump({"documents": []}, f)

    def upload_document(self, uploaded_file, name: str, description: str = "") -> Dict:
        """
        Upload a new source document and extract its text

        Args:
            uploaded_file: Streamlit UploadedFile object
            name: Display name for the document
            description: Optional description of the document

        Returns:
            Dict containing document metadata and extracted text
        """
        try:
            # Extract text first to ensure document is valid
            uploaded_file.seek(0)  # Reset file pointer
            extracted_text = self.doc_processor.extract_text(uploaded_file)
            uploaded_file.seek(0)  # Reset again for saving

            # Generate unique filename with microseconds and counter for uniqueness
            import time
            import random
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = f"{timestamp}_{int(time.time() * 1000000) % 1000000}_{random.randint(1000, 9999)}"
            file_extension = os.path.splitext(uploaded_file.name)[1]
            stored_filename = f"{unique_id}_{name.replace(' ', '_')}{file_extension}"
            file_path = os.path.join(self.source_dir, stored_filename)

            # Save the original file
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            # Save extracted text
            text_filename = f"{unique_id}_{name.replace(' ', '_')}.txt"
            text_path = os.path.join(self.source_dir, text_filename)
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(extracted_text)

            # Create metadata entry
            document_metadata = {
                "id": unique_id,
                "name": name,
                "description": description,
                "original_filename": uploaded_file.name,
                "stored_filename": stored_filename,
                "file_path": file_path,
                "text_path": text_path,
                "uploaded_at": datetime.now().isoformat(),
                "file_size": uploaded_file.size,
                "file_type": uploaded_file.type,
                "text_length": len(extracted_text),
                "preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
            }

            # Update metadata file
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)

            data["documents"].append(document_metadata)

            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=4)

            return document_metadata

        except Exception as e:
            print(f"Error uploading document: {e}")
            raise

    def get_documents(self) -> List[Dict]:
        """Get all available source documents"""
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
            return data.get("documents", [])
        except Exception as e:
            print(f"Error loading documents: {e}")
            return []

    def get_document(self, document_id: str) -> Optional[Dict]:
        """Get a specific document by ID"""
        documents = self.get_documents()
        return next((d for d in documents if d["id"] == document_id), None)

    def get_document_text(self, document_id: str) -> Optional[str]:
        """Get the extracted text of a document"""
        document = self.get_document(document_id)
        if not document:
            return None

        try:
            with open(document["text_path"], 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading document text: {e}")
            return None

    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its files"""
        try:
            # Load metadata
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)

            # Find document
            document = next((d for d in data["documents"] if d["id"] == document_id), None)
            if not document:
                return False

            # Delete files
            for path_key in ["file_path", "text_path"]:
                if path_key in document and os.path.exists(document[path_key]):
                    os.remove(document[path_key])

            # Remove from metadata
            data["documents"] = [d for d in data["documents"] if d["id"] != document_id]

            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=4)

            return True

        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

    def search_documents(self, query: str) -> List[Dict]:
        """Search documents by name, description, or content preview"""
        query_lower = query.lower()
        documents = self.get_documents()

        results = []
        for doc in documents:
            if (query_lower in doc.get("name", "").lower() or
                query_lower in doc.get("description", "").lower() or
                query_lower in doc.get("preview", "").lower()):
                results.append(doc)

        return results

    def get_recent_documents(self, limit: int = 5) -> List[Dict]:
        """Get the most recently uploaded documents"""
        documents = self.get_documents()
        # Sort by upload date (newest first)
        sorted_docs = sorted(documents, 
                           key=lambda x: x.get("uploaded_at", ""), 
                           reverse=True)
        return sorted_docs[:limit]