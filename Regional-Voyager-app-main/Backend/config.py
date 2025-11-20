import os

GENAI_BASE_URL = os.getenv("AZURE_MAAS_BASE_URL", "https://genailab.tcs.in")
GENAI_API_KEY = os.getenv("AZURE_MAAS_API_KEY", "")
GENAI_DEFAULT_MODEL = "azure_ai/genailab-maas-DeepSeek-V3-0324"
