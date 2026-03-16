from gpt4all import GPT4All
from llama_index.core.llms import LLM, CompletionResponse, CompletionResponseGen
from llama_index.core.llms import ChatMessage, MessageRole
from typing import Any, List, Optional, AsyncGenerator
import os
from dotenv import load_dotenv
import asyncio
from llama_index.core.llms import LLMMetadata

# Load environment variables
load_dotenv()

class GPT4AllLLM(LLM):
    """
    Custom LLM class for GPT4All integration with LlamaIndex
    """

    model_name: str = "gpt4all-mini"
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    model: Optional[Any] = None

    def __init__(self, model_name: str = "gpt4all-mini", temperature: float = 0.1, max_tokens: Optional[int] = None):
        super().__init__()
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize the GPT4All model
        # GPT4All will automatically download the model if not present
        try:
            self.model = GPT4All(model_name, device='cpu')  # Use CPU for compatibility
        except Exception as e:
            raise ValueError(f"Failed to load GPT4All model '{model_name}': {str(e)}")

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=2048,  # GPT4All-Mini has smaller context window
            num_output=256,
            model_name=self.model_name
        )

    def generate(self, prompt: str) -> str:
        """
        Generate a response from the prompt using GPT4All.
        Returns the text response directly.
        """
        try:
            # GPT4All generate method
            response = self.model.generate(
                prompt,
                max_tokens=self.max_tokens or 256,
                temp=self.temperature
            )
            return response
        except Exception as e:
            raise Exception(f"GPT4All error: {str(e)}")

    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Complete a prompt using GPT4All (LlamaIndex compatibility)"""
        try:
            text = self.generate(prompt)
            return CompletionResponse(text=text)
        except Exception as e:
            raise Exception(f"GPT4All error: {str(e)}")

    async def acomplete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Async complete a prompt using GPT4All"""
        # For simplicity, run sync method in thread pool
        loop = asyncio.get_event_loop()
        text = await loop.run_in_executor(None, self.generate, prompt)
        return CompletionResponse(text=text)

    def stream_complete(self, prompt: str, **kwargs: Any) -> CompletionResponseGen:
        """Streaming completion (not implemented for simplicity)"""
        response = self.complete(prompt, **kwargs)
        yield response

    async def astream_complete(self, prompt: str, **kwargs: Any) -> AsyncGenerator[CompletionResponse, None]:
        """Async streaming completion"""
        response = await self.acomplete(prompt, **kwargs)
        yield response

    def chat(self, messages: List[ChatMessage], **kwargs: Any) -> CompletionResponse:
        """Chat completion using GPT4All"""
        try:
            # Convert LlamaIndex messages to a single prompt
            # GPT4All doesn't have native chat format, so we'll concatenate
            prompt_parts = []
            for message in messages:
                role = "User" if message.role == MessageRole.USER else "Assistant"
                prompt_parts.append(f"{role}: {message.content}")

            # Join with newlines and add final instruction
            full_prompt = "\n".join(prompt_parts) + "\nAssistant:"

            response = self.generate(full_prompt)
            return CompletionResponse(text=response)

        except Exception as e:
            raise Exception(f"GPT4All error: {str(e)}")

    async def achat(self, messages: List[ChatMessage], **kwargs: Any) -> CompletionResponse:
        """Async chat completion using GPT4All"""
        # For simplicity, run sync method in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.chat, messages)
        return result

    def stream_chat(self, messages: List[ChatMessage], **kwargs: Any) -> CompletionResponseGen:
        """Streaming chat (not implemented for simplicity)"""
        response = self.chat(messages, **kwargs)
        yield response

    async def astream_chat(self, messages: List[ChatMessage], **kwargs: Any) -> AsyncGenerator[CompletionResponse, None]:
        """Async streaming chat"""
        response = await self.achat(messages, **kwargs)
        yield response