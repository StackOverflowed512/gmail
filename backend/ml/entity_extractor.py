from typing import Dict, List
import re
from spacy.tokens import Doc

class EntityExtractor:
    def __init__(self, nlp):
        self.nlp = nlp
        
        # Custom patterns for order numbers etc
        self.patterns = {
            "order": re.compile(r"(?:order|#)\s*(\d{5,})", re.I),
            "product": re.compile(r"(?:product|item)\s*:\s*([A-Za-z0-9\s]+)", re.I),
            "date": re.compile(r"\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}", re.I),
            "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        }

    def extract(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from email text."""
        doc = self.nlp(text)
        
        entities = {
            "names": [],
            "dates": [], 
            "orders": [],
            "products": [],
            "organizations": [],
            "emails": []
        }

        # Extract entities using regex patterns
        for key, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if key == "order":
                entities["orders"].extend(matches)
            elif key == "product":
                entities["products"].extend(matches)
            elif key == "date":
                entities["dates"].extend(matches)
            elif key == "email":
                entities["emails"].extend(matches)

        # Extract names and organizations using basic token analysis
        for token in doc:
            if token.is_title:  # Potential proper noun
                if len(token.text) > 1:  # Avoid single letters
                    if token.like_email:
                        continue  # Skip emails
                    if token.like_num:
                        continue  # Skip numbers
                    if token.is_punct:
                        continue  # Skip punctuation
                    
                    # Check if part of organization
                    if any(org_word in token.text.lower() for org_word in ["inc", "ltd", "corp", "company", "co"]):
                        entities["organizations"].append(token.text)
                    else:
                        entities["names"].append(token.text)

        # Clean up duplicates and empty strings
        for key in entities:
            entities[key] = list(set(entities[key]))
            entities[key] = [item.strip() for item in entities[key] if item.strip()]

        return entities