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
    def __init__(self, model_name: str = "mistral:7b-instruct-q4_K_M"):
        self.llm = ChatOllama(
            model=model_name,
            temperature=0.7,
            max_tokens=200,
            streaming=True  # enable streaming
        )

        self.system_prompt = SystemMessagePromptTemplate.from_template(
            "You are an expert in email communication and human behavior. "
            "Based on an original email and the response sent, predict the most likely reply "
            "that the recipient might send back. Consider the context, tone, and content of both emails."
        )

    def stream_reply_prediction(self, original_email: str, our_response: str):
        predict_prompt = ChatPromptTemplate.from_messages([
            self.system_prompt,
            HumanMessagePromptTemplate.from_template(
                "Original email:\n{original_email}\n\n"
                "Our response:\n{our_response}\n\n"
                "Predict the most likely reply the recipient might send back. "
                "Response should be plain text. "
                "Also provide a percentage (0-100%) indicating the likelihood of any reply."
            )
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
