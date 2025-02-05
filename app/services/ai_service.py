from app.database import redis_client
import json
import ollama

def analyze_code(code: str) -> dict:
    """
    Checks Redis for a cached response before calling the AI model.
    Stores new responses in Redis for faster retrieval.
    """
    cache_key = f"ai_debug:{hash(code)}"
    
    # Check if result is already cached
    cached_result = redis_client.get(cache_key)
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
        redis_client.setex(cache_key, 3600, json.dumps(structured_output))
        
        return structured_output
    
    except json.JSONDecodeError:
        # Log error for debugging and return a fallback response
        print(f"Failed to parse AI response: {response}")
        return {"errors": [], "warnings": [], "optimizations": ["Failed to parse AI response"]}
    
    except Exception as e:
        # Catch any unexpected exceptions
        print(f"Unexpected error occurred: {str(e)}")
        return {"errors": [], "warnings": [], "optimizations": ["Unexpected error"]}