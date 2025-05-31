import os

llm_type = os.getenv("LLM_TYPE", "local")
gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-preview-05-20")

if llm_type == "local":
    from langchain_ollama import OllamaLLM

    model_name = os.getenv("LOCALE_OLLAMA_MODEL")

    if not model_name:
        raise ValueError("LOCALE_OLLAMA_MODEL environment variable is not set")

    client = OllamaLLM(model=model_name)

elif llm_type == "remote-gemini":
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    client = genai.Client(api_key=api_key)

else:
    raise ValueError("LLM_TYPE must be either 'local' or 'remote-gemini'")

def invoke(prompt: str) -> str:
    if llm_type == "local":
        response = client.generate(prompt)
        return response.text
    elif llm_type == "remote-gemini":
        response = client.models.generate_content(
            model=gemini_model,
            contents=prompt,
        )
        return response.text
    else:
        raise ValueError("Unsupported LLM type")