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
    Now supports project-based document organization.
    """

    def __init__(self, source_dir="source_documents", metadata_file="source_documents.json"):
        self.source_dir = source_dir
        self.metadata_file = metadata_file
        self.doc_processor = DocumentProcessor()
        self._ensure_directories()
        self._ensure_metadata_file()
        self._migrate_existing_documents()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.source_dir, exist_ok=True)
        # Create global directory for any legacy documents
        os.makedirs(os.path.join(self.source_dir, "global"), exist_ok=True)

    def _ensure_metadata_file(self):
        """Create metadata file if it doesn't exist"""
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'w') as f:
                json.dump({"documents": []}, f)

    def _migrate_existing_documents(self):
        """Migrate existing documents to include project_id field"""
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)

            modified = False
            for doc in data.get("documents", []):
                if "project_id" not in doc:
                    doc["project_id"] = None  # None means global/legacy document
                    modified = True

            if modified:
                with open(self.metadata_file, 'w') as f:
                    json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error migrating documents: {e}")

    def _get_project_directory(self, project_id: Optional[str]) -> str:
        """Get the directory path for a project's documents"""
        if project_id:
            project_dir = os.path.join(self.source_dir, f"project_{project_id}")
            os.makedirs(project_dir, exist_ok=True)
            return project_dir
        else:
            return os.path.join(self.source_dir, "global")

    def upload_document(self, uploaded_file, name: str, description: str = "", project_id: Optional[str] = None) -> Dict:
        """
        Upload a new source document and extract its text

        Args:
            uploaded_file: Streamlit UploadedFile object
            name: Display name for the document
            description: Optional description of the document
            project_id: Optional project ID to associate document with

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

            # Get appropriate directory based on project
            project_dir = self._get_project_directory(project_id)
            file_path = os.path.join(project_dir, stored_filename)

            # Save the original file
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            # Save extracted text
            text_filename = f"{unique_id}_{name.replace(' ', '_')}.txt"
            text_path = os.path.join(project_dir, text_filename)
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(extracted_text)

            # Create metadata entry
            document_metadata = {
                "id": unique_id,
                "project_id": project_id,  # New field
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

    def get_documents(self, project_id: Optional[str] = None) -> List[Dict]:
        """
        Get all available source documents, optionally filtered by project

        Args:
            project_id: If provided, only return documents for this project.
                       If None, return global documents.
                       If "*", return all documents.
        """
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)

            documents = data.get("documents", [])

            if project_id == "*":
                # Return all documents
                return documents
            else:
                # Filter by project_id (None means global documents)
                return [d for d in documents if d.get("project_id") == project_id]

        except Exception as e:
            print(f"Error loading documents: {e}")
            return []

    def get_document(self, document_id: str, project_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get a specific document by ID, optionally checking project ownership

        Args:
            document_id: The document ID
            project_id: If provided, verify document belongs to this project
        """
        documents = self.get_documents("*")  # Get all documents
        doc = next((d for d in documents if d["id"] == document_id), None)

        # If project_id is specified, verify ownership
        if doc and project_id is not None and doc.get("project_id") != project_id:
            return None  # Document exists but doesn't belong to this project

        return doc

    def get_document_text(self, document_id: str, project_id: Optional[str] = None) -> Optional[str]:
        """Get the extracted text of a document"""
        document = self.get_document(document_id, project_id)
        if not document:
            return None

        try:
            with open(document["text_path"], 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading document text: {e}")
            return None

    def delete_document(self, document_id: str, project_id: Optional[str] = None) -> bool:
        """Delete a document and its files"""
        try:
            # Load metadata
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)

            # Find document
            document = None
            for d in data["documents"]:
                if d["id"] == document_id:
                    # Verify project ownership if specified
                    if project_id is not None and d.get("project_id") != project_id:
                        return False  # Can't delete - wrong project
                    document = d
                    break

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

    def search_documents(self, query: str, project_id: Optional[str] = None) -> List[Dict]:
        """Search documents by name, description, or content preview"""
        query_lower = query.lower()
        documents = self.get_documents(project_id)

        results = []
        for doc in documents:
            if (query_lower in doc.get("name", "").lower() or
                query_lower in doc.get("description", "").lower() or
                query_lower in doc.get("preview", "").lower()):
                results.append(doc)

        return results

    def get_recent_documents(self, limit: int = 5, project_id: Optional[str] = None) -> List[Dict]:
        """Get the most recently uploaded documents"""
        documents = self.get_documents(project_id)
        # Sort by upload date (newest first)
        sorted_docs = sorted(documents, 
                           key=lambda x: x.get("uploaded_at", ""), 
                           reverse=True)
        return sorted_docs[:limit]

    def get_project_document_count(self, project_id: str) -> int:
        """Get the count of documents in a project"""
        return len(self.get_documents(project_id))

    def move_document_to_project(self, document_id: str, target_project_id: Optional[str]) -> bool:
        """Move a document from one project to another"""
        try:
            # Load metadata
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)

            # Find document
            document = None
            for d in data["documents"]:
                if d["id"] == document_id:
                    document = d
                    break

            if not document:
                return False

            # Get old and new paths
            old_project_dir = self._get_project_directory(document.get("project_id"))
            new_project_dir = self._get_project_directory(target_project_id)

            # Move files if directories are different
            if old_project_dir != new_project_dir:
                for path_key in ["file_path", "text_path"]:
                    if path_key in document and os.path.exists(document[path_key]):
                        old_path = document[path_key]
                        filename = os.path.basename(old_path)
                        new_path = os.path.join(new_project_dir, filename)
                        os.rename(old_path, new_path)
                        document[path_key] = new_path

            # Update project_id
            document["project_id"] = target_project_id

            # Save metadata
            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=4)

            return True

        except Exception as e:
            print(f"Error moving document: {e}")
            return False