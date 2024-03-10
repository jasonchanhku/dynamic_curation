import openai, os
import json
from dotenv import load_dotenv
from typing import Generator
import re

load_dotenv()

# Azure OpenAI on your own data is only supported by the 2023-08-01-preview API version
api_type = os.getenv("OPENAI_API_TYPE")
api_version = os.getenv("OPENAI_API_VERSION")

# Azure OpenAI setup
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") # Add your endpoint here
api_key = os.getenv("AZURE_OPENAI_API_KEY") # Add your OpenAI API key here
deployment_id = os.getenv("AZURE_OPENAI_MODEL_NAME") # Add your deployment ID here

# Add your Azure AI Search index name here
search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT"); # Add your Azure AI Search endpoint here
search_key = os.getenv("AZURE_SEARCH_ADMIN_KEY"); # Add your Azure AI Search admin key here


# system message
system_message = os.getenv("AZURE_OPENAI_SYSTEM_MESSAGE")

class AzureChatbot(object):
    # constructor for client
    def __init__(self, idx_var:str, conversation: list[dict]):
        print("Azure Chatbot Initialized")
        self.client :openai.lib.azure.AzureOpenAI = openai.AzureOpenAI(
            base_url=f"{endpoint}/openai/deployments/{deployment_id}/extensions",
            api_key=api_key,
            api_version=api_version,
        )
        self.search_index_name = os.getenv(idx_var)

        self.conversation :list[dict] = conversation
        self.llm_model: str = None
        # to be developed [TBD]
        self.citations :list[dict] = None

    @staticmethod
    def get_name():
        return "AzureChatbot"
    
    @staticmethod
    def preprocess_response(text):
        # This regex pattern looks for [docN] where N is any integer.
        pattern = r'\[doc(\d+)\]'
        
        # The substitution function uses the number captured in the regex.
        # It applies the subscript HTML tag to the number N.
        def subscript_replacement(match):
            return f'<sub>[{match.group(1)}]</sub>'
        
        # Perform the actual replacement using the regex pattern and substitution function.
        processed_text = re.sub(pattern, subscript_replacement, text)
        
        return processed_text
    

    # conversation is list of dicts
    def response_stream(self) -> Generator[str, None, None]:
        for response in self.client.chat.completions.create(
                model=deployment_id,
                messages=self.conversation,
                stream=True,
                extra_body={
                    "dataSources": [
                        {
                            "type": "AzureCognitiveSearch",
                            "parameters": {
                                "endpoint": search_endpoint,
                                "key": search_key,
                                "indexName": self.search_index_name,
                                "inScope": True,
                                "topNDocuments": 1,
                                "queryType": "semantic",
                                "semanticConfiguration": "default",
                                "roleInformation": system_message,
                                "strictness": 3
                            }
                        }
                    ]
                }
            ):

            response_dumps = response.model_dump()
            self.llm_model = response_dumps['model']
            delta = response_dumps['choices'][0]['delta']
            if "context" in delta.keys():
                self.citations: list[dict] = json.loads(delta['context']['messages'][0]['content'])['citations']

            yield delta['content']
