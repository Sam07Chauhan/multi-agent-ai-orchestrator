import httpx
import logging
import config

logger = logging.getLogger("m4_nexus")

class LlamaOrchestrator:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"

    async def detect_intent(self, user_query: str) -> str:
        """Classify the user's query intent using Llama 3."""
        system_instruction = (
            "You are an AI Routing Assistant. Classify the user query into exactly ONE category.\n"
            "Categories:\n"
            "- IMAGE_EDIT: If user wants to change clothes, modify images, generate photos, or look styles.\n"
            "- DATABASE_QUERY: If user asks for reports, stats, SQL queries, database info, tables, or records.\n"
            "Output ONLY the category name. No explanations, no punctuation."
        )
        try:
            payload = {
                "model": "llama3",
                "prompt": f"{system_instruction}\n\nUser Query: {user_query}\n\nIntent:",
                "stream": False,
                "options": {"temperature": 0.0, "num_predict": 10}
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(self.ollama_url, json=payload, timeout=5.0)
                if response.status_code == 200:
                    intent = response.json().get("response", "").strip().upper()
                    if "IMAGE" in intent: return "IMAGE_EDIT"
                    if "DATABASE" in intent or "SQL" in intent: return "DATABASE_QUERY"
            return "IMAGE_EDIT" # Default Fallback
        except Exception as e:
            logger.error(f"Llama Intent Detection Failed: {e}")
            return "IMAGE_EDIT"

    async def generate_sql_query(self, user_query: str, schema_str: str) -> str:
        """Run Text-to-SQL generation based on the provided schema framework."""
        system_instruction = (
            f"You are an expert SQL Generator. Use this database schema to write a clean SQL query:\n"
            f"{schema_str}\n"
            f"Output ONLY the executable raw SQL query string. No markdown, no triple backticks."
        )
        try:
            payload = {
                "model": "llama3",
                "prompt": f"{system_instruction}\n\nQuestion: {user_query}\n\nSQL:",
                "stream": False
            }
            async with httpx.AsyncClient() as client:
                response = await client.post(self.ollama_url, json=payload, timeout=15.0)
                if response.status_code == 200:
                    return response.json().get("response", "").strip()
            return "SELECT 'Error generating SQL from local Llama engine';"
        except Exception as e:
            return f"Error: {str(e)}"