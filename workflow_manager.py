import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class WorkflowManager:
    def __init__(self, filename="workflows.json"):
        self.filename = filename
        self._ensure_workflows_file()

    def _ensure_workflows_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump({
                    "workflows": []
                }, f)

    def create_workflow(self, name: str, description: str = "") -> bool:
        """Create a new workflow"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            # Check if workflow with same name exists
            if any(w["name"] == name for w in data["workflows"]):
                return False

            workflow = {
                "name": name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "status": "draft",  # draft, completed
                "prompts": [],  # List of prompt configurations
                "template": None,  # Template configuration
                "output_format": "markdown"  # markdown or html
            }

            data["workflows"].append(workflow)
            self._save_data(data)
            return True
        except Exception as e:
            print(f"Error creating workflow: {e}")
            return False

    def update_workflow_template(self, workflow_name: str, template_content: str, output_format: str = "markdown") -> bool:
        """Update a workflow's template"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            for workflow in data["workflows"]:
                if workflow["name"] == workflow_name:
                    workflow["template"] = template_content
                    workflow["output_format"] = output_format
                    self._save_data(data)
                    return True
            return False
        except Exception as e:
            print(f"Error updating workflow template: {e}")
            return False

    def get_workflow_template(self, workflow_name: str) -> Optional[Dict]:
        """Get a workflow's template configuration"""
        workflow = self.get_workflow(workflow_name)
        if workflow:
            return {
                "template": workflow.get("template"),
                "output_format": workflow.get("output_format", "markdown")
            }
        return None

    def get_workflows(self) -> List[Dict]:
        """Get all workflows"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return data.get("workflows", [])
        except Exception as e:
            print(f"Error loading workflows: {e}")
            return []

    def get_workflow(self, name: str) -> Optional[Dict]:
        """Get a specific workflow by name"""
        workflows = self.get_workflows()
        return next((w for w in workflows if w["name"] == name), None)

    def add_prompt_to_workflow(self, workflow_name: str, prompt_data: Dict) -> bool:
        """Add a prompt to a workflow"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            for workflow in data["workflows"]:
                if workflow["name"] == workflow_name:
                    workflow["prompts"].append(prompt_data)
                    self._save_data(data)
                    return True
            return False
        except Exception as e:
            print(f"Error adding prompt to workflow: {e}")
            return False

    def update_workflow_prompt(self, workflow_name: str, prompt_index: int, updated_prompt: Dict) -> bool:
        """Update a specific prompt in a workflow"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            for workflow in data["workflows"]:
                if workflow["name"] == workflow_name:
                    if 0 <= prompt_index < len(workflow["prompts"]):
                        workflow["prompts"][prompt_index] = updated_prompt
                        self._save_data(data)
                        return True
            return False
        except Exception as e:
            print(f"Error updating workflow prompt: {e}")
            return False

    def complete_workflow(self, workflow_name: str) -> bool:
        """Mark a workflow as completed"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            for workflow in data["workflows"]:
                if workflow["name"] == workflow_name:
                    workflow["status"] = "completed"
                    self._save_data(data)
                    return True
            return False
        except Exception as e:
            print(f"Error completing workflow: {e}")
            return False

    def delete_workflow(self, workflow_name: str) -> bool:
        """Delete a workflow"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            data["workflows"] = [w for w in data["workflows"] if w["name"] != workflow_name]
            self._save_data(data)
            return True
        except Exception as e:
            print(f"Error deleting workflow: {e}")
            return False

    def _save_data(self, data: Dict):
        """Save data to the workflows file"""
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    

    def create_workflow(self, name: str, description: str = "", template_id: str = None) -> bool:
        """Create a new workflow with optional template reference"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            # Check if workflow with same name exists
            if any(w["name"] == name for w in data["workflows"]):
                return False

            workflow = {
                "name": name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "status": "draft",  # draft, completed
                "prompts": [],  # List of prompt configurations
                "template": None,  # Template configuration (legacy)
                "template_id": template_id,  # Reference to template document
                "output_format": "markdown"  # markdown or html
            }

            data["workflows"].append(workflow)
            self._save_data(data)
            return True
        except Exception as e:
            print(f"Error creating workflow: {e}")
            return False

    def update_workflow_template_id(self, workflow_name: str, template_id: str) -> bool:
        """Update a workflow's template document reference"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            for workflow in data["workflows"]:
                if workflow["name"] == workflow_name:
                    workflow["template_id"] = template_id
                    self._save_data(data)
                    return True
            return False
        except Exception as e:
            print(f"Error updating workflow template ID: {e}")
            return False

    def process_workflow_with_template(self, workflow_name: str, source_document_id: str, 
                                     template_manager, source_manager, gpt_handler, prompt_manager) -> Dict:
        """
        Process a workflow using a source document and populate a template

        Returns:
            Dict containing the populated template content and metadata
        """
        workflow = self.get_workflow(workflow_name)
        if not workflow:
            return {"error": "Workflow not found"}

        # Get source document text
        source_text = source_manager.get_document_text(source_document_id)
        if not source_text:
            return {"error": "Source document not found"}

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
            "source_document_id": source_document_id
        }