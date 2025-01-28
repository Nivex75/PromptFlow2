import os
from openai import OpenAI

class GPTHandler:
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def process_document(self, document_text, prompt, system_prompt=""):
        """
        Process a document with a given prompt using GPT-4
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"{prompt}\n\nDocument:\n{document_text}"}
            ]

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=1000
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error processing document: {str(e)}"