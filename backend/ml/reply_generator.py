from typing import Dict, Optional
import json
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

class ReplyGenerator:
    def __init__(self, model_name: str = "mistral:7b-instruct-q4_K_M"):
        self.llm = ChatOllama(
            model=model_name,
            temperature=0.7
        )
        
        self.template = ChatPromptTemplate.from_messages([
            ("system", """You are a professional email response generator.
            Generate a {tone} response that is {sentiment} in tone.
            Primary intent to address: {intent}
            Context: Previous order {order_info}
            Previous interaction summary: {history}
            
            Rules:
            1. Be concise and clear
            2. Address specific issues mentioned
            3. Provide next steps if needed
            4. Maintain professional tone
            5. Include relevant order/ticket numbers
            """),
            ("human", "{email_body}")
        ])

    async def generate_reply(self,
                     email_body: str,
                     sentiment: Dict,
                     intent: Dict,
                     profile: Dict,
                     entities: Dict) -> str:
        """Generate contextual email reply."""
        
        # Format context from available data
        order_info = (f"#{entities['orders'][0]}" if entities.get('orders') 
                     else "no order mentioned")
        
        history = ""
        if profile:
            history = f"Customer has contacted {profile['interaction_count']} times. "
            if profile['frequent_issues']:
                top_issue = max(profile['frequent_issues'].items(), 
                              key=lambda x: x[1])[0]
                history += f"Frequently raises {top_issue} issues."

        # Generate reply using template
        response = await self.llm.ainvoke(
            self.template.format(
                tone=profile.get('tone_preference', 'formal'),
                sentiment=sentiment['sentiment'],
                intent=intent['primary_intent'],
                order_info=order_info,
                history=history,
                email_body=email_body
            )
        )

        return response.content