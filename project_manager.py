import json
import os
from datetime import datetime
import uuid
from typing import List, Dict, Optional

class ProjectManager:
    def __init__(self, projects_file='data/projects.json'):
        self.projects_file = projects_file
        self.ensure_data_directory()
        self.projects = self.load_projects()

    def ensure_data_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.projects_file), exist_ok=True)

        # Create empty projects file if it doesn't exist
        if not os.path.exists(self.projects_file):
            self.save_projects([])

    def load_projects(self) -> List[Dict]:
        """Load projects from JSON file"""
        try:
            with open(self.projects_file, 'r') as f:
                data = json.load(f)
                return data.get('projects', [])
        except Exception:
            return []

    def save_projects(self, projects: List[Dict]):
        """Save projects to JSON file"""
        with open(self.projects_file, 'w') as f:
            json.dump({'projects': projects}, f, indent=2)

    def create_project(self, name: str, description: str = "") -> Dict:
        """Create a new project"""
        project = {
            'id': f"proj_{uuid.uuid4().hex[:8]}",
            'name': name,
            'description': description,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'document_groups': [],
            'metadata': {
                'status': 'active'
            }
        }

        self.projects.append(project)
        self.save_projects(self.projects)
        return project

    def get_project(self, project_id: str) -> Optional[Dict]:
        """Get a project by ID"""
        for project in self.projects:
            if project['id'] == project_id:
                return project
        return None

    def get_projects(self) -> List[Dict]:
        """Get all projects"""
        return self.projects

    def update_project(self, project_id: str, updates: Dict) -> Optional[Dict]:
        """Update a project"""
        for i, project in enumerate(self.projects):
            if project['id'] == project_id:
                # Update only provided fields
                for key, value in updates.items():
                    if key != 'id':  # Don't allow ID changes
                        project[key] = value
                project['updated_at'] = datetime.now().isoformat()
                self.projects[i] = project
                self.save_projects(self.projects)
                return project
        return None

    def delete_project(self, project_id: str) -> bool:
        """Delete a project (we'll add document handling later)"""
        self.projects = [p for p in self.projects if p['id'] != project_id]
        self.save_projects(self.projects)
        return True