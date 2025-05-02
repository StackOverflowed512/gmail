from typing import Dict, Optional
from .entity_extractor import EntityExtractor
from .sentiment_analyzer import SentimentAnalyzer
from .intent_classifier import IntentClassifier
from .history_manager import HistoryManager
from .reply_generator import ReplyGenerator
from .reply_approver import ReplyApprover
import spacy

class EmailProcessor:
    def __init__(self, use_streamlit: bool = False):
        # Initialize spacy with optimized settings
        spacy.prefer_gpu()
        self.nlp = spacy.load("en_core_web_sm", disable=["parser"])
        self.nlp.add_pipe("custom_entity_extractor")
        
        self.entity_extractor = EntityExtractor()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.intent_classifier = IntentClassifier()
        self.history_manager = HistoryManager()
        self.reply_generator = ReplyGenerator()
        self.reply_approver = ReplyApprover()
        self.use_streamlit = use_streamlit

    async def process_email(self, email_data: Dict) -> Optional[str]:
        """
        Process incoming email and generate approved reply.
        Returns approved reply text or None if rejected.
        """
        # Extract entities
        entities = self.entity_extractor.extract(email_data['body'])

        # Analyze sentiment
        sentiment = self.sentiment_analyzer.analyze(email_data['body'])

        # Classify intent
        intent = self.intent_classifier.classify(email_data['body'])

        # Get/update user profile
        profile = self.history_manager.get_profile(email_data['from'])
        profile = self.history_manager.update_profile(
            email_data['from'],
            sentiment=sentiment,
            intent=intent,
            entities=entities
        )

        # Generate reply
        generated_reply = await self.reply_generator.generate_reply(
            email_data['body'],
            sentiment,
            intent,
            profile,
            entities
        )

        # Get approval and return
        approved_reply = self.reply_approver.approve_reply(
            email_data,
            generated_reply,
            use_streamlit=self.use_streamlit
        )

        return approved_reply