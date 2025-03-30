"""
GitGains Model Guide - March 2025
Author: Rob

This file helps you choose and use the best OpenAI models for your RAG project.
Supports chat, embeddings, and scalable inference.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

### MODEL OPTIONS ###

# Chat models
CHAT_MODELS = {
    "default": "gpt-4o",
    "deep_reasoning": "o1-preview",
    "fast_cost_saving": "o1-mini",
    "experimental": "o3-mini",  # Use if you have access
}

# Embedding models
EMBEDDING_MODELS = {
    "default": "text-embedding-3-large",
    "fast": "text-embedding-3-small",
}

### SELECTION TIPS ###

def choose_chat_model(goal: str, context_size: int = 4096) -> str:
    """
    Choose a chat model based on task goal and expected context window size.
    """
    if "reasoning" in goal.lower() or "periodization" in goal.lower():
        return CHAT_MODELS["deep_reasoning"]
    elif context_size > 100000:
        return CHAT_MODELS["experimental"]
    elif "fast" in goal.lower() or "batch" in goal.lower():
        return CHAT_MODELS["fast_cost_saving"]
    return CHAT_MODELS["default"]


def choose_embedding_model(high_accuracy: bool = True) -> str:
    """
    Choose an embedding model based on accuracy/speed needs.
    """
    return EMBEDDING_MODELS["default"] if high_accuracy else EMBEDDING_MODELS["fast"]


### EMBEDDING CALL ###

def embed_text(text: str, model: str = None) -> list[float]:
    """
    Get embedding vector from OpenAI.
    """
    model = model or choose_embedding_model()
    response = client.embeddings.create(input=text, model=model)
    return response.data[0].embedding


### CHAT COMPLETION CALL ###

def generate_chat_response(
    messages: list[dict], model: str = None, temperature: float = 0.7
) -> str:
    """
    Get chat completion from OpenAI.
    Messages should be in OpenAI format:
        [{"role": "system", "content": "You are..."}, {"role": "user", "content": "Hi"}]
    """
    model = model or choose_chat_model(goal="default")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


### USAGE EXAMPLES ###

if __name__ == "__main__":
    # Example usage
    print("=== EMBEDDING EXAMPLE ===")
    vec = embed_text("Progressive overload over 8 weeks")
    print(f"Vector (first 5): {vec[:5]}")

    print("\n=== CHAT EXAMPLE ===")
    prompt = [
        {"role": "system", "content": "You are a fitness coach specializing in strength programming."},
        {"role": "user", "content": "Create a 4-week intermediate deadlift program."},
    ]
    reply = generate_chat_response(prompt, temperature=0.5)
    print("AI Reply:\n", reply)
