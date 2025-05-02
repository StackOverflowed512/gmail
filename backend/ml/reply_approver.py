import json
from datetime import datetime
from typing import Dict
import streamlit as st

class ReplyApprover:
    def __init__(self, log_path: str = "sent_log.json"):
        self.log_path = log_path
        self._load_log()

    def _load_log(self):
        """Load existing sent log or create new."""
        try:
            with open(self.log_path, 'r') as f:
                self.sent_log = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.sent_log = []

    def _save_log(self):
        """Save sent log to JSON file."""
        with open(self.log_path, 'w') as f:
            json.dump(self.sent_log, f, indent=2)

    def approve_reply(self, 
                     email_data: Dict,
                     generated_reply: str,
                     use_streamlit: bool = False) -> str:
        """
        Get approval for generated reply, optionally using Streamlit UI.
        Returns approved (possibly edited) reply text.
        """
        if use_streamlit:
            return self._streamlit_approval(email_data, generated_reply)
        else:
            return self._terminal_approval(email_data, generated_reply)

    def _terminal_approval(self, email_data: Dict, generated_reply: str) -> str:
        """Get reply approval via terminal interface."""
        print("\n=== Email Context ===")
        print(f"From: {email_data['from']}")
        print(f"Subject: {email_data['subject']}")
        print("\n=== Generated Reply ===")
        print(generated_reply)
        print("\n=== Options ===")
        print("1. Approve as-is")
        print("2. Edit reply")
        print("3. Reject and regenerate")
        
        choice = input("\nEnter choice (1-3): ")
        
        if choice == "1":
            approved_reply = generated_reply
        elif choice == "2":
            print("\nEnter edited reply (Ctrl+D or Ctrl+Z on Windows to finish):")
            lines = []
            while True:
                try:
                    line = input()
                    lines.append(line)
                except EOFError:
                    break
            approved_reply = "\n".join(lines)
        else:
            return None

        # Log approved reply
        self.sent_log.append({
            "timestamp": datetime.now().isoformat(),
            "to": email_data["from"],
            "subject": email_data["subject"],
            "reply": approved_reply
        })
        self._save_log()

        return approved_reply

    def _streamlit_approval(self, email_data: Dict, generated_reply: str) -> str:
        """Get reply approval via Streamlit UI."""
        st.header("Email Reply Approval")
        
        # Show email context
        st.subheader("Email Context")
        st.text(f"From: {email_data['from']}")
        st.text(f"Subject: {email_data['subject']}")
        
        # Show generated reply with editing option
        st.subheader("Generated Reply")
        edited_reply = st.text_area("Edit reply if needed:", 
                                  value=generated_reply,
                                  height=200)
        
        # Approval buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Approve"):
                # Log approved reply
                self.sent_log.append({
                    "timestamp": datetime.now().isoformat(),
                    "to": email_data["from"],
                    "subject": email_data["subject"],
                    "reply": edited_reply
                })
                self._save_log()
                return edited_reply
                
        with col2:
            if st.button("Reject"):
                return None

        return None  # Default return if no action taken