import ollama

def analyze_code(code: str) -> str:
    """
    Sends code to DeepSeek-Coder for analysis and debugging suggestions.
    """
    model = "deepseek-coder:6.7b"
    prompt = f"Analyze the following Python code and provide debugging suggestions:\n\n{code}"
    
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    
    return response['message']['content']
