import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import shutil

class TemplateManager:
    """
    Manages document templates that can be populated with workflow outputs.
    Templates are stored persistently and can be reused across sessions.
    """

    def __init__(self, templates_dir="template_documents", metadata_file="templates.json"):
        self.templates_dir = templates_dir
        self.metadata_file = metadata_file
        self._ensure_directories()
        self._ensure_metadata_file()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        os.makedirs(self.templates_dir, exist_ok=True)

    def _ensure_metadata_file(self):
        """Create metadata file if it doesn't exist"""
        if not os.path.exists(self.metadata_file):
            with open(self.metadata_file, 'w') as f:
                json.dump({"templates": []}, f)
        else:
            # Clean up any duplicate IDs on startup
            self._cleanup_duplicate_ids()

    def _cleanup_duplicate_ids(self):
        """Remove any duplicate IDs that might exist from previous runs"""
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)

            seen_ids = set()
            cleaned_templates = []

            for template in data.get("templates", []):
                if template["id"] not in seen_ids:
                    seen_ids.add(template["id"])
                    cleaned_templates.append(template)

            if len(cleaned_templates) < len(data.get("templates", [])):
                data["templates"] = cleaned_templates
                with open(self.metadata_file, 'w') as f:
                    json.dump(data, f, indent=4)
                print(f"Cleaned up {len(data.get('templates', [])) - len(cleaned_templates)} duplicate templates")
        except Exception as e:
            print(f"Error cleaning up duplicates: {e}")

    def upload_template(self, uploaded_file, name: str, description: str = "") -> Dict:
        """
        Upload a new template document

        Args:
            uploaded_file: Streamlit UploadedFile object
            name: Display name for the template
            description: Optional description of the template

        Returns:
            Dict containing template metadata
        """
        try:
            # Generate unique filename with microseconds and counter for uniqueness
            import time
            import random
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = f"{timestamp}_{int(time.time() * 1000000) % 1000000}_{random.randint(1000, 9999)}"
            file_extension = os.path.splitext(uploaded_file.name)[1]
            stored_filename = f"{unique_id}_{name.replace(' ', '_')}{file_extension}"
            file_path = os.path.join(self.templates_dir, stored_filename)

            # Save the file
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())

            # Create metadata entry
            template_metadata = {
                "id": unique_id,
                "name": name,
                "description": description,
                "original_filename": uploaded_file.name,
                "stored_filename": stored_filename,
                "file_path": file_path,
                "uploaded_at": datetime.now().isoformat(),
                "file_size": uploaded_file.size,
                "file_type": uploaded_file.type
            }

            # Update metadata file
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)

            data["templates"].append(template_metadata)

            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=4)

            return template_metadata

        except Exception as e:
            print(f"Error uploading template: {e}")
            raise

    def get_templates(self) -> List[Dict]:
        """Get all available templates"""
        try:
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)
            return data.get("templates", [])
        except Exception as e:
            print(f"Error loading templates: {e}")
            return []

    def get_template(self, template_id: str) -> Optional[Dict]:
        """Get a specific template by ID"""
        templates = self.get_templates()
        return next((t for t in templates if t["id"] == template_id), None)

    def delete_template(self, template_id: str) -> bool:
        """Delete a template and its file"""
        try:
            # Load metadata
            with open(self.metadata_file, 'r') as f:
                data = json.load(f)

            # Find template
            template = next((t for t in data["templates"] if t["id"] == template_id), None)
            if not template:
                return False

            # Delete file
            if os.path.exists(template["file_path"]):
                os.remove(template["file_path"])

            # Remove from metadata
            data["templates"] = [t for t in data["templates"] if t["id"] != template_id]

            with open(self.metadata_file, 'w') as f:
                json.dump(data, f, indent=4)

            return True

        except Exception as e:
            print(f"Error deleting template: {e}")
            return False

    def read_template_content(self, template_id: str) -> Optional[str]:
        """Read the content of a template file"""
        template = self.get_template(template_id)
        if not template or not os.path.exists(template["file_path"]):
            return None

        try:
            # For now, we'll just read as text
            # In future, could use python-docx for better handling
            with open(template["file_path"], 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading template: {e}")
            return None

    def get_template_markers(self, template_id: str) -> List[str]:
        """
        Extract all markers (e.g., {MARKER_NAME}) from a template

        Returns:
            List of unique marker names found in the template
        """
        content = self.read_template_content(template_id)
        if not content:
            return []

        import re
        # Find all {SOMETHING_OUTPUT} patterns
        pattern = r'\{([A-Z_]+_OUTPUT)\}'
        markers = re.findall(pattern, content)
        return list(set(markers))  # Return unique markers

    def create_sample_templates(self):
        """Create sample templates for demonstration purposes"""
        sample_templates = [
            {
                "name": "Lease Review Letter",
                "description": "Standard letter template for lease reviews",
                "content": """Dear [Client Name],

Following our review of the proposed lease agreement, we set out below the key terms and our recommendations:

**Landlord Details:**
{LANDLORD_OUTPUT}

**Property:**
{PROPERTY_OUTPUT}

**Lease Term:**
{TERM_OUTPUT}

**Annual Rent:**
{RENT_OUTPUT}

**Repair Obligations:**
{REPAIR_OUTPUT}

**Break Clause:**
{BREAK_OUTPUT}

**Recommendations:**
{RECOMMENDATIONS_OUTPUT}

Please let us know if you would like to discuss any of these points in more detail.

Kind regards,
[Your Name]
[Your Firm]"""
            },
            {
                "name": "Executive Summary",
                "description": "Concise summary for senior stakeholders",
                "content": """EXECUTIVE SUMMARY - LEASE ANALYSIS

Property: {PROPERTY_OUTPUT}

Key Terms:
- Rent: {RENT_OUTPUT}
- Term: {TERM_OUTPUT}
- Break Rights: {BREAK_OUTPUT}

Key Risks:
{RISKS_OUTPUT}

Recommendations:
{RECOMMENDATIONS_OUTPUT}

Prepared by: [Analyst Name]
Date: [Date]"""
            }
        ]

        for i, template in enumerate(sample_templates):
            # Create a temporary file-like object
            import io
            import time
            content_bytes = template["content"].encode('utf-8')
            file_obj = io.BytesIO(content_bytes)

            # Create a mock uploaded file
            class MockUploadedFile:
                def __init__(self, name, content, size):
                    self.name = name
                    self.size = size
                    self._content = content
                    self.type = "text/plain"

                def getbuffer(self):
                    return self._content

            mock_file = MockUploadedFile(
                f"{template['name']}.txt",
                content_bytes,
                len(content_bytes)
            )

            try:
                self.upload_template(mock_file, template["name"], template["description"])
                # Add small delay to ensure unique timestamps
                time.sleep(0.1)
            except:
                pass  # Ignore if already exists