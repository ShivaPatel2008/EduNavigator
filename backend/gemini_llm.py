import google.generativeai as genai
from llama_index.llms.base import LLM, CompletionResponse, CompletionResponseGen
from llama_index.llms.types import ChatMessage, MessageRole
from typing import Any, List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiLLM(LLM):
    """
    Custom LLM class for Google Gemini integration with LlamaIndex
    """

    model_name: str = "gemini-3-flash-preview"
    temperature: float = 0.1
    max_tokens: Optional[int] = None

    def __init__(self, model_name: str = "gemini-3-flash-preview", temperature: float = 0.1, max_tokens: Optional[int] = None):
        super().__init__()
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        genai.configure(api_key=api_key)

        # Initialize the model
        self.model = genai.GenerativeModel(model_name)

    @property
    def metadata(self) -> dict:
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Complete a prompt using Gemini"""
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )

            return CompletionResponse(text=response.text)

        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        """Streaming completion (not implemented for simplicity)"""
        # For now, just return the complete response
        response = self.complete(prompt, **kwargs)
        yield response

    def chat(self, messages: List[ChatMessage], **kwargs: Any) -> CompletionResponse:
        """Chat completion using Gemini"""
        try:
            # Convert LlamaIndex messages to Gemini format
            gemini_messages = []
            for message in messages:
                role = "user" if message.role == MessageRole.USER else "model"
                gemini_messages.append({"role": role, "parts": [message.content]})

            # Start chat
            chat = self.model.start_chat(history=gemini_messages[:-1])  # All but last message

            # Send the last message
            last_message = gemini_messages[-1]["parts"][0]
            response = chat.send_message(last_message)

            return CompletionResponse(text=response.text)

        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def stream_chat(self, messages: List[ChatMessage], **kwargs: Any) -> CompletionResponseGen:
        """Streaming chat (not implemented for simplicity)"""
        response = self.chat(messages, **kwargs)
        yield response