#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Local LLM integration...")

try:
    from gpt4all_llm import LocalLLM
    print("✓ LocalLLM import successful")

    # Test model loading
    model_name = os.getenv("LLM_MODEL", "microsoft/phi-2")
    print(f"Testing model: {model_name}")

    print("Loading model (this may take a while on first run)...")
    llm = LocalLLM(model_name=model_name, temperature=0.1)
    print("✓ Local model loaded successfully")

    # Test a simple generation
    test_prompt = "What is AI?"
    print(f"Testing prompt: {test_prompt}")

    response = llm.generate(test_prompt)
    print(f"Response: {response[:200]}...")
    print("✓ Local model generation successful")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()