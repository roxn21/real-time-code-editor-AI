from celery import Celery
from decouple import config
from app.redis_client import RedisClient  # Correct import
import json
import ollama

REDIS_URL = f"redis://{config('REDIS_HOST', default='localhost')}:{config('REDIS_PORT', default=6380)}/0"

celery_app = Celery(
    "tasks",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True
)

# Move the task registration here, after the Celery app is defined
from app.services.ai_service import analyze_code_task  # Import the function from ai_service

@celery_app.task
def analyze_code_task(code: str) -> dict:
    """
    Checks Redis for a cached response before calling the AI model.
    Stores new responses in Redis for faster retrieval.
    """
    cache_key = f"ai_debug:{hash(code)}"
    
    # Instantiate Redis client
    redis_client = RedisClient()
    redis_conn = redis_client.get_redis_connection()

    # Check if result is already cached
    cached_result = redis_conn.get(cache_key)
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

    try:
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])

        # Try parsing the response
        structured_output = json.loads(response["message"]["content"])
        
        # Cache the result for 1 hour
        redis_conn.setex(cache_key, 3600, json.dumps(structured_output))
        
        return structured_output
    
    except json.JSONDecodeError:
        # Log error for debugging and return a fallback response
        print(f"Failed to parse AI response: {response}")
        return {"errors": [], "warnings": [], "optimizations": ["Failed to parse AI response"]}
    
    except Exception as e:
        # Catch any unexpected exceptions
        print(f"Unexpected error: {str(e)}")
        return {"errors": [], "warnings": [], "optimizations": ["Unexpected error"]}