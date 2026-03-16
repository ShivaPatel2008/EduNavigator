#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing GPT4All integration...")

try:
    from gpt4all_llm import GPT4AllLLM
    print("✓ GPT4AllLLM import successful")

    # Test model loading
    llm_model = os.getenv("LLM_MODEL", "gpt4all-mini")
    print(f"Using model: {llm_model}")

    llm = GPT4AllLLM(model_name=llm_model, temperature=0.1)
    print("✓ GPT4All model loaded successfully")

    # Test a simple generation
    test_prompt = "What is AI?"
    print(f"Testing prompt: {test_prompt}")

    response = llm.generate(test_prompt)
    print(f"Response: {response[:100]}...")
    print("✓ GPT4All generation successful")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()