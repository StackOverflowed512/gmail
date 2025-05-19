import pandas as pd
from typing import List, Dict, Tuple
from datetime import datetime
import os

class TicketHistory:
    def __init__(self, csv_path: str = "c:\\Users\\91798\\Desktop\\trial_mail\\backend\\customer_support_tickets.csv"):
        self.csv_path = csv_path
        if os.path.exists(csv_path):
            self.tickets_df = pd.read_csv(csv_path)
        else:
            self.tickets_df = pd.DataFrame(columns=[
                'Ticket ID', 'Customer Name', 'Customer Email', 'Customer Age',
                'Customer Gender', 'Product Purchased', 'Date Of Purchase',
                'Ticket Type', 'Ticket Subject', 'Ticket Description',
                'Ticket Status', 'Resolution', 'Ticket Priority',
                'Ticket Channel', 'First Response Time', 'Time to Resolution',
                'Customer Satisfaction Rating'
            ])

    def get_similar_product_tickets(self, product: str, issue_description: str) -> Tuple[List[Dict], bool]:
        """Find similar tickets for the same product with priority consideration."""
        try:
            # Filter by product
            product_tickets = self.tickets_df[
                self.tickets_df['Product Purchased'].str.lower() == product.lower()
            ]
            
            if len(product_tickets) == 0:
                return [], False

            # Calculate similarity scores
            keywords = set(issue_description.lower().split())
            
            def calculate_similarity(row):
                desc_words = set(str(row['Ticket Description']).lower().split())
                subj_words = set(str(row['Ticket Subject']).lower().split())
                all_words = desc_words.union(subj_words)
                
                # Base similarity score
                similarity = len(keywords.intersection(all_words)) / len(keywords.union(all_words))
                
                # Boost score based on priority and status
                priority_boost = {
                    'critical': 0.3,
                    'high': 0.2,
                    'medium': 0.1,
                    'low': 0
                }.get(str(row['Ticket Priority']).lower(), 0)
                
                status_boost = 0.2 if str(row['Ticket Status']).lower() == 'resolved' else 0
                
                return similarity + priority_boost + status_boost

            product_tickets.loc[:, 'similarity'] = product_tickets.apply(calculate_similarity, axis=1)
            similar_tickets = product_tickets[product_tickets['similarity'] > 0.3]
            
            return similar_tickets.to_dict('records'), len(similar_tickets) > 0
        except Exception as e:
            print(f"Error in get_similar_product_tickets: {e}")
            return [], False

    def add_new_ticket(self, email: str, product: str, description: str, subject: str) -> Dict:
        """Add a new ticket to the dataset."""
        try:
            # Get customer details if they exist
            existing_customer = self.tickets_df[self.tickets_df['Customer Email'] == email].iloc[0] if len(self.tickets_df[self.tickets_df['Customer Email'] == email]) > 0 else None
            
            new_ticket = {
                'Ticket ID': f"T{len(self.tickets_df) + 1:04d}",
                'Customer Name': existing_customer['Customer Name'] if existing_customer is not None else email.split('@')[0],
                'Customer Email': email,
                'Customer Age': existing_customer['Customer Age'] if existing_customer is not None else None,
                'Customer Gender': existing_customer['Customer Gender'] if existing_customer is not None else None,
                'Product Purchased': product,
                'Date Of Purchase': existing_customer['Date Of Purchase'] if existing_customer is not None else None,
                'Ticket Type': 'Technical Issue',
                'Ticket Subject': subject,
                'Ticket Description': description,
                'Ticket Status': 'Open',
                'Resolution': 'Pending',
                'Ticket Priority': 'Medium',
                'Ticket Channel': 'Email',
                'First Response Time': None,
                'Time to Resolution': None,
                'Customer Satisfaction Rating': None
            }
            
            self.tickets_df = pd.concat([
                self.tickets_df, 
                pd.DataFrame([new_ticket])
            ], ignore_index=True)
            
            self.tickets_df.to_csv(self.csv_path, index=False)
            return new_ticket
        except Exception as e:
            print(f"Error in add_new_ticket: {e}")
            return None

    def get_customer_history(self, email: str) -> List[Dict]:
        """Get historical support tickets for a customer with detailed information."""
        try:
            customer_tickets = self.tickets_df[self.tickets_df['Customer Email'] == email]
            return customer_tickets.sort_values('Ticket ID', ascending=False).to_dict('records')
        except Exception as e:
            print(f"Error in get_customer_history: {e}")
            return []

    def get_ticket_stats(self, email: str) -> Dict:
        """Get comprehensive statistics about customer's ticket history."""
        try:
            customer_tickets = self.tickets_df[self.tickets_df['Customer Email'] == email]
            
            if len(customer_tickets) == 0:
                return {
                    "total_tickets": 0,
                    "avg_satisfaction": None,
                    "common_issues": [],
                    "avg_resolution_time": None,
                    "priority_distribution": {},
                    "channel_preference": None
                }
            
            # Calculate priority distribution
            priority_dist = customer_tickets['Ticket Priority'].value_counts().to_dict()
            
            # Calculate average resolution time (assuming time is stored in hours)
            avg_resolution = customer_tickets['Time to Resolution'].mean()
            
            # Get most used channel
            preferred_channel = customer_tickets['Ticket Channel'].mode().iloc[0] if not customer_tickets['Ticket Channel'].empty else None
            
            stats = {
                "total_tickets": len(customer_tickets),
                "avg_satisfaction": customer_tickets['Customer Satisfaction Rating'].mean(),
                "common_issues": customer_tickets['Ticket Type'].value_counts().to_dict(),
                "avg_resolution_time": avg_resolution,
                "priority_distribution": priority_dist,
                "channel_preference": preferred_channel
            }
            
            return stats
        except Exception as e:
            print(f"Error in get_ticket_stats: {e}")
            return {
                "total_tickets": 0,
                "avg_satisfaction": None,
                "common_issues": [],
                "avg_resolution_time": None,
                "priority_distribution": {},
                "channel_preference": None
            }

    def get_similar_tickets(self, issue_description: str) -> List[Dict]:
        """Find similar tickets based on issue description regardless of product."""
        try:
            # Calculate similarity scores
            keywords = set(issue_description.lower().split())
            
            def calculate_similarity(row):
                desc_words = set(str(row['Ticket Description']).lower().split())
                subj_words = set(str(row['Ticket Subject']).lower().split())
                all_words = desc_words.union(subj_words)
                
                # Base similarity score
                similarity = len(keywords.intersection(all_words)) / len(keywords.union(all_words))
                
                # Boost score based on priority and status
                priority_boost = {
                    'critical': 0.3,
                    'high': 0.2,
                    'medium': 0.1,
                    'low': 0
                }.get(str(row['Ticket Priority']).lower(), 0)
                
                status_boost = 0.2 if str(row['Ticket Status']).lower() == 'resolved' else 0
                
                return similarity + priority_boost + status_boost

            self.tickets_df.loc[:, 'similarity'] = self.tickets_df.apply(calculate_similarity, axis=1)
            similar_tickets = self.tickets_df[self.tickets_df['similarity'] > 0.3]
            
            return similar_tickets.sort_values('similarity', ascending=False).to_dict('records')
        except Exception as e:
            print(f"Error in get_similar_tickets: {e}")
            return []