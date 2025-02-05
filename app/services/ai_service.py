from typing import Dict, Any
import logging
from app.database import RedisClient
import json
import ollama
from celery import Celery
from celery.utils.log import get_task_logger
from app.celery_worker import celery_app

logging.basicConfig(level=logging.INFO)
logger = get_task_logger(__name__)

class AIService:
    def __init__(self):
        self.redis_client = RedisClient()

    def analyze_code(self, code: str) -> Dict[str, Any]:
        """
        Checks Redis for a cached response before calling the AI model.
        Stores new responses in Redis for faster retrieval.

        Args:
            code (str): The code to be analyzed.

        Returns:
            dict: A dictionary containing analysis results.
        """

        try:
            cache_key = f"ai_debug:{hash(code)}"

            # Check if result is already cached
            cached_result = self.redis_client.get_redis_connection().get(cache_key)
            if cached_result:
                return json.loads(cached_result)

            # If not cached, call DeepSeek-Coder
            model = "deepseek-coder:6.7b"
            prompt = f"""
            Analyze the following Python code and provide debugging suggestions in JSON format.

            Categories:
            1. Errors (syntax, runtime, logical)
            2. Warnings (potential issues, anti-patterns)
            3. Performance Improvements (optimizations)

            Return JSON with this structure:
            {{
                "errors": [{{"line": int, "message": str}}],
                "warnings": [{{"line": int, "message": str}}],
                "optimizations": [{{"line": int, "message": str}}]
            }}

            Code:
            {code}
            """

            response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

            # Try parsing the response
            structured_output = json.loads(response["message"]["content"])

            # Cache the result for 1 hour
            redis_conn = self.redis_client.get_redis_connection()
            if redis_conn is not None:
                cache_key = f"ai_debug:{hash(code)}"
                redis_conn.setex(cache_key, 3600, json.dumps(structured_output))

            return structured_output

        except json.JSONDecodeError:
            # Log error for debugging and return a fallback response
            logging.error(f"Failed to parse AI response: {response}")
            return {"errors": [], "warnings": [], "optimizations": ["Failed to parse AI response"]}

        except Exception as e:
            # Catch any unexpected exceptions
            logging.error(f"Unexpected error occurred: {str(e)}")
            return {"errors": [], "warnings": [], "optimizations": ["Unexpected error"]}


@celery_app.task(bind=True, max_retries=3, default_retry_delay=5)  # Retry failed tasks 3 times with 5s delay
def analyze_code_task(self, code: str):
    """
    AI-powered debugging with automatic retries.
    """
    try:
        model = "deepseek-coder:6.7b"
        prompt = f"""
        Analyze the following Python code and provide debugging suggestions in JSON format.
        
        Categories:
        1. Errors (syntax, runtime, logical)
        2. Warnings (potential issues, anti-patterns)
        3. Performance Improvements (optimizations)
        
        Code:
        {code}
        """

        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        return json.loads(response["message"]["content"])
    
    except Exception as e:
        logger.error(f"AI Task Failed: {e}")
        raise self.retry(exc=e)
