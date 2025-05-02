from fastapi.responses import StreamingResponse
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
import re
import random
import asyncio

class ResponsePredictor:
    """
    AI-powered predictor for email conversations.
    Given an original email and a sent response, predicts the most likely reply
    the recipient might send back, considering context, tone, and content.
    """

    def __init__(
        self,
        model_name: str = "mistral:7b-instruct-q4_K_M",
        temperature: float = 0.7,
        max_tokens: int = 200,
        streaming: bool = True,
        system_prompt: str = (
            "You are an expert in email communication and human behavior. "
            "Based on an original email and the response sent, predict the most likely reply "
            "that the recipient might send back. Consider the context, tone, and content of both emails."
        ),
        human_prompt_template: str = (
            "Original email:\n{original_email}\n\n"
            "Our response:\n{our_response}\n\n"
            "Predict the most likely reply the recipient might send back. "
            "Response should be plain text. "
            "Also provide a percentage (0-100%) indicating the likelihood of any reply."
        )
    ):
        """
        Initialize the ResponsePredictor with model and prompt configuration.

        Args:
            model_name (str): Name of the LLM model to use.
            temperature (float): Sampling temperature for response randomness.
            max_tokens (int): Maximum tokens to generate in the reply.
            streaming (bool): Whether to stream the response.
            system_prompt (str): System prompt for the LLM.
            human_prompt_template (str): Template for the human message prompt.
        """
        self.llm = ChatOllama(
            model=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            streaming=streaming
        )

        self.system_prompt = SystemMessagePromptTemplate.from_template(system_prompt)
        self.human_prompt_template = human_prompt_template

    def stream_reply_prediction(self, original_email: str, our_response: str):
        """
        Streams the predicted reply to an email conversation.

        Args:
            original_email (str): The original email content.
            our_response (str): The response sent to the original email.

        Returns:
            StreamingResponse: An async streaming response with the predicted reply.
        """
        predict_prompt = ChatPromptTemplate.from_messages([
            self.system_prompt,
            HumanMessagePromptTemplate.from_template(self.human_prompt_template)
        ])
        predict_chain = predict_prompt | self.llm

        async def generator():
            async for chunk in predict_chain.astream({
                "original_email": original_email,
                "our_response": our_response
            }):
                yield chunk.content
                await asyncio.sleep(0)  # let other tasks run

        return StreamingResponse(generator(), media_type="text/plain")
