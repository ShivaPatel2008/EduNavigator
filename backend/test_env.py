#!/usr/bin/env python3
import os
from dotenv import load_dotenv

load_dotenv()

print("Environment variables:")
print(f"MAX_ANSWER_LENGTH: {os.getenv('MAX_ANSWER_LENGTH', 'Not set')}")
print(f"MAX_SOURCES: {os.getenv('MAX_SOURCES', 'Not set')}")
print(f"MAX_HIGHLIGHTED_CHUNKS: {os.getenv('MAX_HIGHLIGHTED_CHUNKS', 'Not set')}")

# Test import
try:
    import query_engine
    print("query_engine imported successfully")
    print(f"MAX_ANSWER_LENGTH in module: {query_engine.MAX_ANSWER_LENGTH}")
    print(f"MAX_SOURCES in module: {query_engine.MAX_SOURCES}")
    print(f"MAX_HIGHLIGHTED_CHUNKS in module: {query_engine.MAX_HIGHLIGHTED_CHUNKS}")
except Exception as e:
    print(f"Error importing query_engine: {e}")