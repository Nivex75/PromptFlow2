import json
import os

class PromptManager:
    def __init__(self, filename="prompts.json"):
        self.filename = filename
        self._ensure_prompts_file()

    def _ensure_prompts_file(self):
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump({
                    "system_prompt": "You are a highly skilled legal document analyzer. Always be precise and thorough in your analysis. Base your responses solely on the provided document content.",
                    "prompts": []
                }, f)

    def get_prompts(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return data.get("prompts", [])
        except Exception as e:
            print(f"Error loading prompts: {e}")
            return []

    def get_system_prompt(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                return data.get("system_prompt", "")
        except Exception as e:
            print(f"Error loading system prompt: {e}")
            return ""

    def update_system_prompt(self, new_system_prompt):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
            data["system_prompt"] = new_system_prompt
            self._save_data(data)
            return True
        except Exception as e:
            print(f"Error updating system prompt: {e}")
            return False

    def add_prompt(self, name, description, prompt_text):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            prompts = data.get("prompts", [])
            # Check if prompt with same name exists
            existing_prompt = next((p for p in prompts if p["Name"] == name), None)
            if existing_prompt:
                return False

            prompts.append({
                "Name": name,
                "Description": description,
                "Prompt": prompt_text
            })

            data["prompts"] = prompts
            self._save_data(data)
            return True
        except Exception as e:
            print(f"Error adding prompt: {e}")
            return False

    def update_prompt(self, name, description, new_prompt_text):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            prompts = data.get("prompts", [])
            for prompt in prompts:
                if prompt["Name"] == name:
                    prompt["Description"] = description
                    prompt["Prompt"] = new_prompt_text
                    break

            data["prompts"] = prompts
            self._save_data(data)
        except Exception as e:
            print(f"Error updating prompt: {e}")

    def delete_prompt(self, name):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)

            prompts = data.get("prompts", [])
            prompts = [p for p in prompts if p["Name"] != name]

            data["prompts"] = prompts
            self._save_data(data)
        except Exception as e:
            print(f"Error deleting prompt: {e}")

    def _save_data(self, data):
        try:
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")