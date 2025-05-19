from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import asyncio
from .ticket_history import TicketHistory

class FastEmailResponseGenerator:
    def __init__(self, model_name="mistral:7b-instruct-q4_K_M", **kwargs):
        self.llm = ChatOllama(
            model=model_name,
            temperature=kwargs.get('temperature', 0.7),
            streaming=True
        )
        
        self.ticket_history = TicketHistory()
        
        self.template = ChatPromptTemplate.from_messages([
            ("system", """You are an AI customer support assistant that generates professional, 
            empathetic responses. Consider the following context:
            
            Customer Profile:
            - Total tickets: {total_tickets}
            - Average satisfaction: {avg_satisfaction}
            - Common issues: {common_issues}
            
            Recent Support History:
            {customer_history}
            
            Similar Resolved Tickets:
            {similar_tickets}
            
            Guidelines:
            - Be concise but thorough
            - Maintain a {tone} tone
            - Address all key points
            - Reference relevant ticket history
            - Suggest solutions based on similar cases
            - Be empathetic to customer's {emotion} tone
            """),
            ("human", "{email_content}")
        ])

    async def detect_emotion(self, email_content: str) -> str:
        try:
            emotion_llm = ChatOllama(
                model=self.llm.model,
                temperature=0.3,
                streaming=False
            )
            
            emotion_prompt = ChatPromptTemplate.from_messages([
                ("system", "Classify the emotional tone as: positive, negative, neutral, or urgent."),
                ("human", "{email}")
            ])
            
            response = await emotion_llm.ainvoke(
                emotion_prompt.format_messages(email=email_content)
            )
            return response.content.strip().lower()
        except Exception as e:
            print(f"Error detecting emotion: {e}")
            return "neutral"

    def stream_email_response(self, email_content: str, email: str, emotion: str, context: dict = None):
        async def response_generator():
            try:
                # Extract issue details
                issue_subject = context.get('subject', 'General Issue')
                product_info = context.get('product', '')
                
                # First, try to find product-specific similar tickets
                similar_product_tickets, has_product_similar = (
                    self.ticket_history.get_similar_product_tickets(product_info, email_content)
                    if product_info else ([], False)
                )

                # If no product-specific tickets found, look for similar issues across all products
                similar_tickets = (
                    self.ticket_history.get_similar_tickets(email_content)
                    if not has_product_similar else []
                )

                # Combine similar tickets, prioritizing product-specific ones
                all_similar_tickets = similar_product_tickets + [
                    ticket for ticket in similar_tickets 
                    if ticket not in similar_product_tickets
                ][:5]  # Limit to top 5 similar tickets

                # If no similar tickets found, create a new one
                if not all_similar_tickets and product_info:
                    new_ticket = self.ticket_history.add_new_ticket(
                        email=email,
                        product=product_info,
                        description=email_content,
                        subject=issue_subject
                    )
                    print(f"Created new ticket: {new_ticket['Ticket ID']}")

                # Format similar tickets text with more detailed information
                similar_text = "\n".join([
                    f"- Similar Case {t.get('Ticket ID', 'N/A')}:\n"
                    f"  Product: {t.get('Product Purchased', 'N/A')}\n"
                    f"  Issue: {t.get('Ticket Description', 'N/A')}\n"
                    f"  Resolution: {t.get('Resolution', 'N/A')}\n"
                    f"  Status: {t.get('Ticket Status', 'N/A')}"
                    for t in all_similar_tickets
                    if t.get('Ticket Status', '').lower() == 'resolved'
                ])

                # Get ticket history and stats with error handling
                customer_history = self.ticket_history.get_customer_history(email) or []
                similar_tickets = self.ticket_history.get_similar_tickets(email_content) or []
                ticket_stats = self.ticket_history.get_ticket_stats(email) or {
                    "total_tickets": 0,
                    "avg_satisfaction": None,
                    "common_issues": {}
                }
                
                # Format history data with safety checks
                history_text = "\n".join([
                    f"- Ticket #{t.get('Ticket ID', 'N/A')}: {t.get('Ticket Subject', 'N/A')} ({t.get('Ticket Status', 'N/A')})\n"
                    f"  Description: {t.get('Ticket Description', 'N/A')}\n"
                    f"  Resolution: {t.get('Resolution', 'N/A')}"
                    for t in (customer_history[-3:] if isinstance(customer_history, list) else [])
                ])
                
                similar_text = "\n".join([
                    f"- Similar Case: {t.get('Ticket Subject', 'N/A')}\n"
                    f"  Issue: {t.get('Ticket Description', 'N/A')}\n"
                    f"  Resolution: {t.get('Resolution', 'N/A')}"
                    for t in (similar_tickets if isinstance(similar_tickets, list) else [])
                    if isinstance(t, dict) and t.get('Ticket Status', '').lower() == 'resolved'
                ])

                # Safely handle common_issues
                common_issues_text = ""
                if isinstance(ticket_stats.get('common_issues'), dict):
                    common_issues_text = ", ".join(
                        f"{k}({v})" for k, v in ticket_stats['common_issues'].items()
                    )

                # Prepare context data with type safety
                context_data = {
                    "tone": "professional",
                    "email_content": email_content,
                    "emotion": emotion or "neutral",
                    "total_tickets": ticket_stats.get("total_tickets", 0),
                    "avg_satisfaction": (
                        f"{ticket_stats.get('avg_satisfaction', 0):.1f}" 
                        if ticket_stats.get('avg_satisfaction') 
                        else "N/A"
                    ),
                    "common_issues": common_issues_text or "No common issues found",
                    "customer_history": history_text or "No previous tickets found",
                    "similar_tickets": similar_text or "No similar cases found"
                }
                
                messages = self.template.format_messages(**context_data)
                
                async for chunk in self.llm.astream(messages):
                    if chunk and hasattr(chunk, 'content') and chunk.content:
                        yield chunk.content
                    await asyncio.sleep(0)
                    
            except Exception as e:
                print(f"Error generating response: {e}")
                yield "I apologize, but I encountered an error generating the response. Please try again."
        
        return response_generator
