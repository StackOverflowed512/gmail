from transformers import pipeline
import torch
from typing import Dict, List, Tuple

class IntentClassifier:
    def __init__(self):
        # Load pre-trained model for zero-shot classification
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )

        # Define possible intent categories
        self.intent_categories = [
            "complaint",
            "product inquiry",
            "support request", 
            "feedback",
            "order status",
            "refund request",
            "general question"
        ]

    def classify(self, text: str) -> Dict[str, float]:
        """
        Classify email intent using zero-shot classification.
        Returns probabilities for each intent category.
        """
        result = self.classifier(
            text,
            candidate_labels=self.intent_categories,
            multi_label=True
        )

        # Convert to dictionary of intent:probability
        intents = dict(zip(result['labels'], result['scores']))
        
        # Get primary and secondary intents
        sorted_intents = sorted(intents.items(), key=lambda x: x[1], reverse=True)
        primary_intent = sorted_intents[0][0]
        secondary_intent = sorted_intents[1][0] if len(sorted_intents) > 1 else None

        return {
            'primary_intent': primary_intent,
            'secondary_intent': secondary_intent,
            'confidence': sorted_intents[0][1],
            'all_intents': intents
        }