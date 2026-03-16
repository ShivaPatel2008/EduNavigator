from llama_index.llms import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AnswerValidator:
    def __init__(self, llm_model: str = None):
        if llm_model is None:
            llm_model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.llm = OpenAI(model=llm_model, temperature=0.1)

    def validate(self, question: str, answer: str, context: str) -> bool:
        """
        Validate if the answer is based on sufficient context.
        Returns True if valid, False if not.
        """
        prompt = f"""
        Question: {question}
        Context: {context}
        Answer: {answer}

        Does the answer directly address the question using information from the context?
        Answer only 'yes' or 'no'.
        """
        response = self.llm.complete(prompt).text.strip().lower()
        return response == 'yes'

    def get_final_answer(self, question: str, answer: str, context: str) -> str:
        """
        Return the answer if valid, else the not found message.
        """
        if self.validate(question, answer, context):
            return answer
        else:
            return "I could not find that information in the program documents."

if __name__ == "__main__":
    validator = AnswerValidator()
    question = "What skills will I learn?"
    answer = "You will learn Python programming."
    context = "The curriculum includes Python programming, data analysis..."
    final_answer = validator.get_final_answer(question, answer, context)
    print(f"Final Answer: {final_answer}")