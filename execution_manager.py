# Create a new file: execution_manager.py
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import uuid

class ExecutionManager:
    """Manages workflow execution history"""

    def __init__(self, filename="executions.json"):
        self.filename = filename
        self._ensure_executions_file()

    def _ensure_executions_file(self):
        """Create executions file if it doesn't exist"""
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump({"executions": []}, f)

    def record_execution(self, project_id: str, workflow_name: str, document_id: str, 
                        results: Dict, template_content: str = None) -> str:
        """
        Record a workflow execution

        Returns:
            Execution ID
        """
        try:
            execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

            execution = {
                "id": execution_id,
                "project_id": project_id,
                "workflow_name": workflow_name,
                "document_id": document_id,
                "executed_at": datetime.now().isoformat(),
                "results": results,
                "template_content": template_content,
                "status": "completed"
            }

            with open(self.filename, 'r') as f:
                data = json.load(f)

            data["executions"].append(execution)

            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)

            return execution_id

        except Exception as e:
            print(f"Error recording execution: {e}")
            return None

    def get_executions(self, project_id: Optional[str] = None, 
                      workflow_name: Optional[str] = None,
                      document_id: Optional[str] = None) -> List[Dict]:
        """Get executions filtered by various criteria"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            executions = data.get("executions", [])

            # Apply filters
            if project_id:
                executions = [e for e in executions if e.get("project_id") == project_id]
            if workflow_name:
                executions = [e for e in executions if e.get("workflow_name") == workflow_name]
            if document_id:
                executions = [e for e in executions if e.get("document_id") == document_id]

            # Sort by execution time (newest first)
            executions.sort(key=lambda x: x.get("executed_at", ""), reverse=True)

            return executions

        except Exception as e:
            print(f"Error loading executions: {e}")
            return []

    def get_execution(self, execution_id: str) -> Optional[Dict]:
        """Get a specific execution by ID"""
        executions = self.get_executions()
        return next((e for e in executions if e["id"] == execution_id), None)

    def delete_execution(self, execution_id: str) -> bool:
        """Delete an execution record"""
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            data["executions"] = [e for e in data["executions"] if e["id"] != execution_id]

            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)

            return True

        except Exception as e:
            print(f"Error deleting execution: {e}")
            return False

    def get_recent_executions(self, limit: int = 10, project_id: Optional[str] = None) -> List[Dict]:
        """Get recent executions"""
        executions = self.get_executions(project_id=project_id)
        return executions[:limit]