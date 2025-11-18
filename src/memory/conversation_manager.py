from typing import List, Dict, Optional
import json
import os
from datetime import datetime
from pathlib import Path

class ConversationManager:
    """Manages conversation history and context"""
    
    def __init__(self, storage_path: str = "data/conversations"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.current_session = []
        
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add message to current session"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.current_session.append(message)
    
    def get_context(self, max_messages: int = 10) -> List[Dict]:
        """Get recent conversation context"""
        return self.current_session[-max_messages:]
    
    def save_session(self, session_id: str):
        """Save conversation session"""
        filepath = self.storage_path / f"{session_id}.json"
        with open(filepath, 'w') as f:
            json.dump({
                "session_id": session_id,
                "messages": self.current_session,
                "created_at": datetime.now().isoformat()
            }, f, indent=2)
    
    def load_session(self, session_id: str) -> List[Dict]:
        """Load conversation session"""
        filepath = self.storage_path / f"{session_id}.json"
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
                return data.get("messages", [])
        return []
    
    def clear_session(self):
        """Clear current session"""
        self.current_session = []

class UserProfileManager:
    """Manages user profiles and preferences"""
    
    def __init__(self, profile_path: str = "src/memory/user_profiles.json"):
        self.profile_path = profile_path
        self.profiles = self._load_profiles()
    
    def _load_profiles(self) -> Dict:
        """Load user profiles"""
        if os.path.exists(self.profile_path):
            with open(self.profile_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_profiles(self):
        """Save user profiles"""
        os.makedirs(os.path.dirname(self.profile_path), exist_ok=True)
        with open(self.profile_path, 'w') as f:
            json.dump(self.profiles, f, indent=2)
    
    def get_profile(self, user_id: str = "default") -> Dict:
        """Get user profile"""
        return self.profiles.get(user_id, self._create_default_profile())
    
    def _create_default_profile(self) -> Dict:
        """Create default profile"""
        return {
            "user_id": "default",
            "preferences": {
                "tone": "professional",
                "content_length": "medium",
                "include_sources": True,
                "seo_optimization": True
            },
            "brand_voice": {
                "style": "professional and informative",
                "vocabulary": "industry-standard",
                "avoid": []
            },
            "content_history": [],
            "learned_preferences": {}
        }
    
    def update_profile(self, user_id: str, updates: Dict):
        """Update user profile"""
        if user_id not in self.profiles:
            self.profiles[user_id] = self._create_default_profile()
        
        profile = self.profiles[user_id]
        for key, value in updates.items():
            if key in profile:
                if isinstance(profile[key], dict) and isinstance(value, dict):
                    profile[key].update(value)
                else:
                    profile[key] = value
        
        self._save_profiles()
    
    def learn_from_edits(self, user_id: str, original: str, edited: str):
        """Learn from user edits"""
        profile = self.get_profile(user_id)
        
        # Analyze differences
        changes = self._analyze_changes(original, edited)
        
        # Update learned preferences
        if "learned_preferences" not in profile:
            profile["learned_preferences"] = {}
        
        for change_type, change_data in changes.items():
            if change_type not in profile["learned_preferences"]:
                profile["learned_preferences"][change_type] = []
            profile["learned_preferences"][change_type].append(change_data)
        
        self.profiles[user_id] = profile
        self._save_profiles()
    
    def _analyze_changes(self, original: str, edited: str) -> Dict:
        """Analyze what changed between original and edited"""
        changes = {}
        
        # Simple analysis: word count, tone indicators
        orig_words = len(original.split())
        edit_words = len(edited.split())
        
        if abs(orig_words - edit_words) > 50:
            changes["length_preference"] = {
                "original_words": orig_words,
                "edited_words": edit_words,
                "change": "shorter" if edit_words < orig_words else "longer"
            }
        
        # Check for tone changes (simple heuristic)
        formal_words = ["furthermore", "however", "therefore", "consequently"]
        casual_words = ["anyway", "basically", "pretty much", "kind of"]
        
        orig_formal = sum(1 for word in formal_words if word in original.lower())
        edit_formal = sum(1 for word in formal_words if word in edited.lower())
        
        if edit_formal < orig_formal:
            changes["tone_preference"] = "more casual"
        elif edit_formal > orig_formal:
            changes["tone_preference"] = "more formal"
        
        return changes
