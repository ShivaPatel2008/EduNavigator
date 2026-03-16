import json
from typing import Dict

def reflect_on_answer(question: str, answer: str, retrieved_context: str, llm) -> Dict:
    """
    Use LLM to evaluate the answer and determine if it needs improvement.
    
    Args:
        question: The user's question
        answer: The generated answer
        retrieved_context: The retrieved context used to generate the answer
        llm: The LLM instance to use for reflection
    
    Returns:
        Dict with keys: is_sufficient (bool), reason (str), needs_more_retrieval (bool)
    """
    prompt = f"""
Evaluate the following answer to the question based on the retrieved context.

Question: {question}

Answer: {answer}

Retrieved Context: {retrieved_context}

Determine:
1. Does the answer fully address the user question?
2. Is the answer grounded in retrieved context?
3. Is important information missing?

Return a JSON object with the following structure:
{{
 "is_sufficient": true/false,
 "reason": "brief explanation of your evaluation",
 "needs_more_retrieval": true/false
}}

Only return the JSON object, no additional text.
"""
    
    try:
        response = llm.complete(prompt).text.strip()
        # Remove any markdown formatting if present
        if response.startswith('```json'):
            response = response[7:]
        if response.endswith('```'):
            response = response[:-3]
        response = response.strip()
        
        result = json.loads(response)
        
        # Validate the structure
        required_keys = ['is_sufficient', 'reason', 'needs_more_retrieval']
        if not all(key in result for key in required_keys):
            raise ValueError("Missing required keys in reflection response")
        
        return result
    except Exception as e:
        # Fallback in case of parsing error
        return {
            "is_sufficient": True,
            "reason": f"Reflection failed: {str(e)}. Assuming answer is sufficient.",
            "needs_more_retrieval": False
        }