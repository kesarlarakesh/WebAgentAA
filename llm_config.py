from browser_use import ChatGoogle

def get_llm():
    """
    Configure and return the LLM model for browser-use agent.
    Available Google models:
    - gemini-flash-latest (fastest, good for quick tasks)
    - gemini-pro-latest (more capable, better reasoning)
    - gemini-1.5-pro (very capable, large context window)
    - gemini-1.5-flash (balanced speed and capability)
    """
    model = "gemini-flash-latest"  # Change this to use different models
    return ChatGoogle(model=model)
