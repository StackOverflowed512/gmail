import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class HistoryManager:
    def __init__(self, profiles_path: str = "user_profiles.json"):
        self.profiles_path = profiles_path
        self.profiles = self._load_profiles()

    def _load_profiles(self) -> Dict:
        """Load existing user profiles or create new file."""
        if os.path.exists(self.profiles_path):
            with open(self.profiles_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_profiles(self):
        """Save profiles to JSON file."""
        with open(self.profiles_path, 'w') as f:
            json.dump(self.profiles, f, indent=2)

    def update_profile(self, email: str, 
                      sentiment: Dict = None,
                      intent: Dict = None,
                      entities: Dict = None,
                      reply: str = None) -> Dict:
        """Update user profile with new interaction data."""
        
        if email not in self.profiles:
            self.profiles[email] = {
                "tone_preference": "formal",
                "frequent_issues": {},
                "last_replies": [],
                "last_orders": [],
                "interaction_count": 0,
                "first_seen": datetime.now().isoformat()
            }

        profile = self.profiles[email]
        profile["last_seen"] = datetime.now().isoformat()
        profile["interaction_count"] += 1

        # Update tone preference based on formal words ratio
        if reply:
            formal_words = len([w for w in reply.lower().split() 
                              if w in {"kindly", "please", "sincerely", "regards"}])
            profile["tone_preference"] = "formal" if formal_words > 0 else "informal"

        # Update frequent issues
        if intent and "primary_intent" in intent:
            issues = profile["frequent_issues"]
            issues[intent["primary_intent"]] = issues.get(intent["primary_intent"], 0) + 1

        # Update last orders
        if entities and "orders" in entities and entities["orders"]:
            profile["last_orders"] = (entities["orders"] + 
                                    profile["last_orders"])[:5]

        # Update last replies
        if reply:
            profile["last_replies"] = ([reply] + 
                                     profile["last_replies"])[:3]

        self._save_profiles()
        return profile

    def get_profile(self, email: str) -> Optional[Dict]:
        """Retrieve user profile."""
        return self.profiles.get(email)