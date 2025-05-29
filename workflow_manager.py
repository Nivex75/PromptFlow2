import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import copy

class WorkflowManager:
    def __init__(self, filename="workflows.json", project_filename="project_workflows.json"):
        self.filename = filename  # Global workflows
        self.project_filename = project_filename  # Project-specific workflows
        self._ensure_workflows_file()
        self._ensure_project_workflows_file()
        self._migrate_existing_workflows()

    def _ensure_workflows_file(self):
        """Ensure global workflows file exists"""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump({"workflows": []}, f)

    def _ensure_project_workflows_file(self):
        """Ensure project workflows file exists"""
        if not os.path.exists(self.project_filename):
            with open(self.project_filename, 'w') as f:
                json.dump({"workflows": []}, f)

    def _migrate_existing_workflows(self):
        """Add is_global flag to existing workflows"""
        try:
            # Migrate global workflows
            with open(self.filename, 'r') as f:
                data = json.load(f)

            modified = False
            for workflow in data.get("workflows", []):
                if "is_global" not in workflow:
                    workflow["is_global"] = True
                    workflow["project_id"] = None
                    modified = True

            if modified:
                with open(self.filename, 'w') as f:
                    json.dump(data, f, indent=4)

        except Exception as e:
            print(f"Error migrating workflows: {e}")

    def create_workflow(self, name: str, description: str = "", template_id: str = None, 
                       project_id: Optional[str] = None, source_workflow_id: Optional[str] = None) -> bool:
        """
        Create a new workflow, either global or project-specific

        Args:
            name: Workflow name
            description: Workflow description
            template_id: Associated template ID
            project_id: If provided, create as project workflow
            source_workflow_id: If provided, this is a copy of another workflow
        """
        try:
            # Determine which file to use
            filename = self.project_filename if project_id else self.filename

            with open(filename, 'r') as f:
                data = json.load(f)

            # Check if workflow with same name exists in the same context
            existing_workflows = [w for w in data["workflows"] 
                                if w.get("project_id") == project_id]
            if any(w["name"] == name for w in existing_workflows):
                return False

            workflow = {
                "name": name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "status": "draft",
                "prompts": [],
                "template": None,
                "template_id": template_id,
                "output_format": "markdown",
                "is_global": project_id is None,
                "project_id": project_id,
                "source_workflow_id": source_workflow_id
            }

            data["workflows"].append(workflow)

            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)

            return True
        except Exception as e:
            print(f"Error creating workflow: {e}")
            return False

    def copy_workflow_to_project(self, workflow_name: str, project_id: str, new_name: Optional[str] = None) -> bool:
        """Copy a global workflow to a project"""
        try:
            # Get the source workflow
            source_workflow = self.get_workflow(workflow_name, is_global=True)
            if not source_workflow:
                return False

            # Create a deep copy
            new_workflow = copy.deepcopy(source_workflow)

            # Update workflow properties
            new_workflow["name"] = new_name or f"{workflow_name} (Copy)"
            new_workflow["is_global"] = False
            new_workflow["project_id"] = project_id
            new_workflow["source_workflow_id"] = workflow_name
            new_workflow["created_at"] = datetime.now().isoformat()
            new_workflow["status"] = "draft"

            # Add to project workflows
            with open(self.project_filename, 'r') as f:
                data = json.load(f)

            data["workflows"].append(new_workflow)

            with open(self.project_filename, 'w') as f:
                json.dump(data, f, indent=4)

            return True
        except Exception as e:
            print(f"Error copying workflow: {e}")
            return False

    def get_workflows(self, project_id: Optional[str] = None, include_global: bool = False) -> List[Dict]:
        """
        Get workflows filtered by project

        Args:
            project_id: If provided, get workflows for this project
            include_global: If True and project_id is provided, also include global workflows
        """
        workflows = []

        try:
            # Always load global workflows
            with open(self.filename, 'r') as f:
                global_data = json.load(f)
                global_workflows = global_data.get("workflows", [])

            # Load project workflows
            with open(self.project_filename, 'r') as f:
                project_data = json.load(f)
                project_workflows = project_data.get("workflows", [])

            if project_id is None:
                # Return only global workflows
                workflows = global_workflows
            else:
                # Get project-specific workflows
                workflows = [w for w in project_workflows if w.get("project_id") == project_id]

                # Optionally include global workflows
                if include_global:
                    workflows.extend(global_workflows)

        except Exception as e:
            print(f"Error loading workflows: {e}")

        return workflows

    def get_workflow(self, name: str, project_id: Optional[str] = None, is_global: bool = False) -> Optional[Dict]:
        """Get a specific workflow by name"""
        if is_global or project_id is None:
            # Look in global workflows
            workflows = self.get_workflows(project_id=None)
        else:
            # Look in project workflows
            workflows = self.get_workflows(project_id=project_id)

        return next((w for w in workflows if w["name"] == name), None)

    def update_workflow_template_id(self, workflow_name: str, template_id: str, project_id: Optional[str] = None) -> bool:
        """Update a workflow's template document reference"""
        try:
            # Determine which file to use
            workflow = self.get_workflow(workflow_name, project_id=project_id)
            if not workflow:
                return False

            filename = self.project_filename if workflow.get("project_id") else self.filename

            with open(filename, 'r') as f:
                data = json.load(f)

            for w in data["workflows"]:
                if w["name"] == workflow_name and w.get("project_id") == project_id:
                    w["template_id"] = template_id
                    break

            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)

            return True
        except Exception as e:
            print(f"Error updating workflow template ID: {e}")
            return False

    def add_prompt_to_workflow(self, workflow_name: str, prompt_data: Dict, project_id: Optional[str] = None) -> bool:
        """Add a prompt to a workflow"""
        try:
            workflow = self.get_workflow(workflow_name, project_id=project_id)
            if not workflow:
                return False

            filename = self.project_filename if workflow.get("project_id") else self.filename

            with open(filename, 'r') as f:
                data = json.load(f)

            for w in data["workflows"]:
                if w["name"] == workflow_name and w.get("project_id") == project_id:
                    w["prompts"].append(prompt_data)
                    break

            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)

            return True
        except Exception as e:
            print(f"Error adding prompt to workflow: {e}")
            return False

    def update_workflow_prompt(self, workflow_name: str, prompt_index: int, updated_prompt: Dict, 
                             project_id: Optional[str] = None) -> bool:
        """Update a specific prompt in a workflow"""
        try:
            workflow = self.get_workflow(workflow_name, project_id=project_id)
            if not workflow:
                return False

            filename = self.project_filename if workflow.get("project_id") else self.filename

            with open(filename, 'r') as f:
                data = json.load(f)

            for w in data["workflows"]:
                if w["name"] == workflow_name and w.get("project_id") == project_id:
                    if 0 <= prompt_index < len(w["prompts"]):
                        w["prompts"][prompt_index] = updated_prompt
                        break

            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)

            return True
        except Exception as e:
            print(f"Error updating workflow prompt: {e}")
            return False

    def complete_workflow(self, workflow_name: str, project_id: Optional[str] = None) -> bool:
        """Mark a workflow as completed"""
        try:
            workflow = self.get_workflow(workflow_name, project_id=project_id)
            if not workflow:
                return False

            filename = self.project_filename if workflow.get("project_id") else self.filename

            with open(filename, 'r') as f:
                data = json.load(f)

            for w in data["workflows"]:
                if w["name"] == workflow_name and w.get("project_id") == project_id:
                    w["status"] = "completed"
                    break

            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)

            return True
        except Exception as e:
            print(f"Error completing workflow: {e}")
            return False

    def delete_workflow(self, workflow_name: str, project_id: Optional[str] = None) -> bool:
        """Delete a workflow"""
        try:
            workflow = self.get_workflow(workflow_name, project_id=project_id)
            if not workflow:
                return False

            filename = self.project_filename if workflow.get("project_id") else self.filename

            with open(filename, 'r') as f:
                data = json.load(f)

            data["workflows"] = [w for w in data["workflows"] 
                               if not (w["name"] == workflow_name and w.get("project_id") == project_id)]

            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)

            return True
        except Exception as e:
            print(f"Error deleting workflow: {e}")
            return False

    def get_workflow_template(self, workflow_name: str, project_id: Optional[str] = None) -> Optional[Dict]:
        """Get a workflow's template configuration"""
        workflow = self.get_workflow(workflow_name, project_id=project_id)
        if workflow:
            return {
                "template": workflow.get("template"),
                "output_format": workflow.get("output_format", "markdown")
            }
        return None

    def update_workflow_template(self, workflow_name: str, template_content: str, 
                               output_format: str = "markdown", project_id: Optional[str] = None) -> bool:
        """Update a workflow's template"""
        try:
            workflow = self.get_workflow(workflow_name, project_id=project_id)
            if not workflow:
                return False

            filename = self.project_filename if workflow.get("project_id") else self.filename

            with open(filename, 'r') as f:
                data = json.load(f)

            for w in data["workflows"]:
                if w["name"] == workflow_name and w.get("project_id") == project_id:
                    w["template"] = template_content
                    w["output_format"] = output_format
                    break

            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)

            return True
        except Exception as e:
            print(f"Error updating workflow template: {e}")
            return False

    def process_workflow_with_template(self, workflow_name: str, source_document_id: str, 
                                     template_manager, source_manager, gpt_handler, prompt_manager,
                                     project_id: Optional[str] = None) -> Dict:
        """
        Process a workflow using a source document and populate a template

        Returns:
            Dict containing the populated template content and metadata
        """
        workflow = self.get_workflow(workflow_name, project_id=project_id)
        if not workflow:
            return {"error": "Workflow not found"}

        # Get source document text (verify it belongs to the project if project_id is specified)
        source_text = source_manager.get_document_text(source_document_id, project_id)
        if not source_text:
            return {"error": "Source document not found or access denied"}

        # Process all prompts
        results = {}
        for prompt_data in workflow['prompts']:
            try:
                result = gpt_handler.process_document(
                    source_text,
                    prompt_data['prompt'],
                    prompt_manager.get_system_prompt()
                )
                # Store with the marker format expected in templates
                marker_name = f"{prompt_data['name'].upper().replace(' ', '_')}_OUTPUT"
                results[marker_name] = result
            except Exception as e:
                results[f"{prompt_data['name']}_OUTPUT"] = f"Error: {str(e)}"

        # Get template content
        template_content = None
        if workflow.get('template_id'):
            template_content = template_manager.read_template_content(workflow['template_id'])
        elif workflow.get('template'):
            # Fallback to inline template
            template_content = workflow['template']

        if not template_content:
            return {"error": "No template associated with workflow"}

        # Replace markers in template
        populated_content = template_content
        for marker, value in results.items():
            populated_content = populated_content.replace(f"{{{marker}}}", value)

        return {
            "content": populated_content,
            "format": workflow.get('output_format', 'markdown'),
            "results": results,
            "template_id": workflow.get('template_id'),
            "source_document_id": source_document_id,
            "project_id": project_id
        }

    def _save_data(self, data: Dict):
        """Legacy method for compatibility"""
        # This method is referenced in old code, so we keep it for compatibility
        # It saves to the global workflows file
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")