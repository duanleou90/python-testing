import os
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key="",
    azure_endpoint="https://hfai-llm-test.openai.azure.com/",
    api_version="2025-04-01-preview"
)

response = client.responses.create(
  model="o3-mini",
  input="compare gdp of thailand and vietnam in 2023",
  reasoning={
            "effort": "medium",
            "summary": "detailed"
        }
)

print(response)
#Your organization must be verified to generate reasoning summaries. Please go to: https://platform.openai.com/settings/organization/general and click on Verify Organization. If you just verified, it can take up to 15 minutes for access to propagate.
#https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/reasoning?tabs=python-secure%2Cpy
