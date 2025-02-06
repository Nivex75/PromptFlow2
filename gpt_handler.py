
import os
from openai import OpenAI

class GPTHandler:
    def __init__(self):
        self.model = "gpt-4o"
        
        # Configure based on environment
        use_azure = os.getenv('USE_AZURE_OPENAI', 'false').lower() == 'true'
        
        if use_azure:
            self.client = OpenAI(
                api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                base_url=os.getenv('AZURE_OPENAI_ENDPOINT'),
                api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-01'),
                azure_deployed_model=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4'),
                azure_ad_token=os.getenv('AZURE_AD_TOKEN'),  # For Azure AD authentication
                default_headers={'Ocp-Apim-Subscription-Key': os.getenv('AZURE_OPENAI_API_KEY')}
            )
        else:
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
