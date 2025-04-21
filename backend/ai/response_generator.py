from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate
)

class FastEmailResponseGenerator:
    def __init__(self, model_name: str = "mistral:7b-instruct-q4_K_M"):
        self.llm = ChatOllama(
            model=model_name,
            max_tokens=150,
            temperature=0.3,
            num_thread=10,
            num_gpu=10,
            streaming=True  # Enable streaming
        )

        self.emotion_system_prompt = SystemMessagePromptTemplate.from_template(
            "You are an expert in emotion analysis. Classify the given email "
            "into one of these emotions: joy, sadness, anger, neutral. Respond with only the category."
        )

        self.response_system_prompt = SystemMessagePromptTemplate.from_template(
            "You are an AI that generates professional, empathetic email responses. "
            "Ensure the response is concise and solution-focused."
        )

    async def detect_emotion(self, email_content: str) -> str:
        """Run non-streaming emotion detection first."""
        # Use a fresh non-streaming instance for classification
        classification_llm = ChatOllama(model=self.llm.model, temperature=0.3, streaming=False)

        emotion_prompt = ChatPromptTemplate.from_messages([
            self.emotion_system_prompt,
            HumanMessagePromptTemplate.from_template("{email}")
        ])
        
        emotion_chain = emotion_prompt | classification_llm | StrOutputParser()
        emotion = await emotion_chain.ainvoke({"email": email_content})
        return emotion.strip().lower()

    def stream_email_response(self, email_content: str, emotion: str):
        """Stream the response tokens asynchronously."""

        response_prompt = ChatPromptTemplate.from_messages([
            self.response_system_prompt,
            HumanMessagePromptTemplate.from_template(
                f"""Generate a professional email body response (no subject, no greetings/signatures) based on the following email. 
                The sender's emotional tone is **{emotion}**. Follow these rules strictly:
                1. **Acknowledge the emotion**: Recognize the sender's tone ({emotion}) in a professional way.
                2. **Address concerns**: Directly respond to key issues raised.
                3. **Provide solutions**: Offer clear, actionable steps.
                4. **Be concise**: Keep it brief (2-3 sentences max).

                Email: {{email}}

                Respond with ONLY the email body text, formatted professionally. Do not include labels like "Response:".
                """
            )
        ])

        response_chain = response_prompt | self.llm

        async def generator():
            async for chunk in response_chain.astream({"email": email_content}):
                yield chunk.content

        return generator
