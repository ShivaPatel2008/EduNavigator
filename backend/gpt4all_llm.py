from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from llama_index.core.llms import LLM, CompletionResponse, CompletionResponseGen
from llama_index.core.llms import ChatMessage, MessageRole
from typing import Any, List, Optional, AsyncGenerator
import os
from dotenv import load_dotenv
import asyncio
from llama_index.core.llms import LLMMetadata
import torch

# Load environment variables
load_dotenv()

class LocalLLM(LLM):
    """
    Custom LLM class for local transformers models with LlamaIndex
    """

    model_name: str = "microsoft/phi-2"
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    pipeline: Optional[Any] = None

    def __init__(self, model_name: str = "microsoft/phi-2", temperature: float = 0.1, max_tokens: Optional[int] = None):
        super().__init__()
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize the local model
        try:
            print(f"Loading model: {model_name}")
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto",
                low_cpu_mem_usage=True
            )

            self.pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=self.max_tokens or 256,
                temperature=self.temperature,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
            print("Model loaded successfully")
        except Exception as e:
            raise ValueError(f"Failed to load local model '{model_name}': {str(e)}")

    @property
    def metadata(self) -> LLMMetadata:
        return LLMMetadata(
            context_window=2048,  # Phi-2 has 2048 context window
            num_output=256,
            model_name=self.model_name
        )

    def generate(self, prompt: str) -> str:
        """
        Generate a response from the prompt using local model.
        Returns the text response directly.
        """
        try:
            outputs = self.pipeline(prompt, max_new_tokens=self.max_tokens or 256)
            response = outputs[0]['generated_text']
            # Remove the original prompt from the response
            if response.startswith(prompt):
                response = response[len(prompt):].strip()
            return response
        except Exception as e:
            raise Exception(f"Local model error: {str(e)}")

    def complete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Complete a prompt using local model (LlamaIndex compatibility)"""
        try:
            text = self.generate(prompt)
            return CompletionResponse(text=text)
        except Exception as e:
            raise Exception(f"Local model error: {str(e)}")

    async def acomplete(self, prompt: str, **kwargs: Any) -> CompletionResponse:
        """Async complete a prompt using local model"""
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
        """Chat completion using local model"""
        try:
            # Convert LlamaIndex messages to a single prompt
            prompt_parts = []
            for message in messages:
                role = "User" if message.role == MessageRole.USER else "Assistant"
                prompt_parts.append(f"{role}: {message.content}")

            # Join with newlines and add final instruction
            full_prompt = "\n".join(prompt_parts) + "\nAssistant:"

            response = self.generate(full_prompt)
            return CompletionResponse(text=response)

        except Exception as e:
            raise Exception(f"Local model error: {str(e)}")

    async def achat(self, messages: List[ChatMessage], **kwargs: Any) -> CompletionResponse:
        """Async chat completion using local model"""
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