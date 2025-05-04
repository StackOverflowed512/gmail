from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import asyncio

class FastEmailResponseGenerator:
    """
    Generates professional, empathetic email responses and detects sender emotion using LLMs.
    All prompts and model parameters are configurable for flexibility and future extension.
    """
    def __init__(self, model_name="mistral:7b-instruct-q4_K_M", **kwargs):
        self.llm = ChatOllama(
            model=model_name,
            temperature=kwargs.get('temperature', 0.7),
            streaming=True
        )
        
        # Enhanced prompt template for better responses
        self.template = ChatPromptTemplate.from_messages([
            ("system", """You are an AI email assistant that generates professional, 
            empathetic responses. Consider the following guidelines:
            - Be concise but thorough
            - Maintain a {tone} tone
            - Address all key points
            - Be solution-oriented
            - Use professional language
            
            Previous context:
            - Past interactions: {interaction_count}
            - Recent replies: {previous_replies}
            - Common issues: {previous_issues}
            """),
            ("human", """Given this email, generate a helpful response:
            {email_content}
            
            The sender's emotional tone appears to be: {emotion}
            
            Generate a professional response:""")
        ])

    async def detect_emotion(self, email_content: str) -> str:
        try:
            emotion_llm = ChatOllama(
                model=self.llm.model,
                temperature=0.3,
                streaming=False
            )
            
            emotion_prompt = ChatPromptTemplate.from_messages([
                ("system", "Classify the emotional tone of this email as either: positive, negative, neutral, or urgent."),
                ("human", "{email}")
            ])
            
            response = await emotion_llm.ainvoke(
                emotion_prompt.format_messages(email=email_content)
            )
            return response.content.strip().lower()
        except Exception as e:
            print(f"Error detecting emotion: {e}")
            return "neutral"  # Default fallback

    def stream_email_response(self, email_content: str, emotion: str, context: dict = None):
        """Generate and stream the email response."""
        
        async def response_generator():
            try:
                # Prepare context data
                context_data = {
                    "tone": "professional",
                    "email_content": email_content,
                    "emotion": emotion,
                    "interaction_count": context.get("interaction_count", 0) if context else 0,
                    "previous_replies": "\n".join(context.get("previous_replies", []))[-500:] if context else "",
                    "previous_issues": ", ".join(context.get("previous_issues", [])) if context else "None"
                }
                
                messages = self.template.format_messages(**context_data)
                
                async for chunk in self.llm.astream(messages):
                    if chunk.content:
                        yield chunk.content
                    await asyncio.sleep(0)
                    
            except Exception as e:
                print(f"Error generating response: {e}")
                yield "I apologize, but I encountered an error generating the response. Please try again."
        
        return response_generator
