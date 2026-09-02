"""
Smart Complaint Classifier - AI/ML Module
Uses keyword-based classification + sentiment analysis
No heavy ML dependencies needed (works offline)
"""

import re
from textblob import TextBlob

# ------ Category Keywords------
CATEGORY_KEYWORDS = {
    "Academic": [
        "exam", "examination", "result", "marks", "grade", "grading", "teacher",
        "professor", "lecturer", "class", "course", "curriculum", "syllabus",
        "assignment", "project", "attendance", "lecture", "practical", "lab",
        "subject", "faculty", "teaching", "study", "notes", "library", "book",
        "scholarship", "internal", "external", "board", "tu", "tribhuvan",
        "college", "tuition", "fee", "admission", "degree", "certificate",
        "marksheet", "transcript", "hall ticket", "thesis", "viva", "internship"
    ],
    "Hostel": [
        "hostel", "room", "dormitory", "mess", "food", "meal", "warden",
        "cleanliness", "dirty", "water", "bathroom", "toilet", "electricity",
        "wifi", "internet", "bed", "mattress", "pillow", "blanket", "roommate",
        "noise", "curfew", "gate", "lock", "security", "theft", "ragging",
        "bully", "bullying", "kitchen", "cook", "drinking water", "tap",
        "heater", "geyser", "canteen"
    ],
    "Transport": [
        "bus", "transport", "vehicle", "driver", "route", "timing", "late",
        "delay", "pickup", "drop", "fare", "ticket", "van", "tempo", "ride",
        "traffic", "road", "parking", "bicycle", "commute", "schedule",
        "conductor", "overcrowded", "breakdown", "accident"
    ],
    "Infrastructure": [
        "building", "classroom", "room", "chair", "bench", "desk", "projector",
        "whiteboard", "blackboard", "maintenance", "repair", "construction",
        "toilet", "washroom", "water", "electricity", "power", "generator",
        "lift", "elevator", "ramp", "disabled", "wifi", "network", "internet",
        "computer", "lab", "equipment", "fan", "ac", "air conditioner",
        "light", "bulb", "leaking", "roof", "wall", "floor", "ground",
        "playground", "sports", "canteen", "cafeteria", "garden", "gate",
        "basin", "door"
    ],
    "Administration": [
        "admin", "administration", "office", "staff", "principal", "dean",
        "rector", "management", "document", "certificate", "migration",
        "noc", "character", "recommendation", "letter", "fee", "payment",
        "receipt", "duplicate", "lost", "id card", "identity", "form",
        "application", "approval", "permission", "policy", "rule", "regulation",
        "discrimination", "harassment", "complaint", "grievance", "notice",
        "announcement", "holiday", "schedule", "timetable", "holiday"
    ],
}

# ─── Priority Keywords ────────────────────────────────────────────────────────
PRIORITY_KEYWORDS = {
    "Critical": [
        "urgent", "emergency", "immediately", "dangerous", "accident", "fire",
        "flood", "earthquake", "injury", "blood", "hospital", "ambulance",
        "police", "violence", "assault", "harassment", "ragging", "threat",
        "abuse", "discrimination", "broken", "collapsed", "crisis"
    ],
    "High": [
        "serious", "important", "asap", "quickly", "failing", "failed",
        "not working", "broken", "damaged", "stopped", "long time", "months",
        "weeks", "repeated", "multiple times", "still", "unresolved",
        "many students", "everyone", "whole class", "all"
    ],
    "Medium": [
        "problem", "issue", "concern", "trouble", "difficulty", "bad",
        "poor", "not good", "disappointing", "unfair", "wrong", "incorrect",
        "missing", "lack", "need", "request", "improve", "fix"
    ],
}

# ─── Classifier Class ─────────────────────────────────────────────────────────
class ComplaintClassifier:

    def classify_category(self, text: str) -> tuple[str, float]:
        """Returns (category, confidence_score)"""
        text_lower = text.lower()
        scores = {}

        for category, keywords in CATEGORY_KEYWORDS.items():
            count = sum(1 for kw in keywords if kw in text_lower)
            scores[category] = count

        if max(scores.values()) == 0:
            return "Other", 0.5

        best = max(scores, key=scores.get)
        total = sum(scores.values())
        confidence = round(scores[best] / total, 2) if total > 0 else 0.5
        return best, min(confidence + 0.3, 0.99)  # boost base confidence

    def classify_priority(self, text: str) -> str:
        """Returns priority level"""
        text_lower = text.lower()

        for priority in ["Critical", "High", "Medium"]:
            keywords = PRIORITY_KEYWORDS[priority]
            if any(kw in text_lower for kw in keywords):
                return priority

        return "Low"

    def analyze_sentiment(self, text: str) -> tuple[str, float]:
        """Returns (sentiment_label, polarity_score)"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to +1

        if polarity >= 0.2:
            label = "Positive"
        elif polarity >= -0.1:
            label = "Neutral"
        elif polarity >= -0.5:
            label = "Negative"
        else:
            label = "Very Negative"

        return label, round(polarity, 3)

    def extract_tags(self, text: str, category: str) -> list[str]:
        """Extract relevant tags from complaint text"""
        text_lower = text.lower()
        tags = []

        # Add category-specific tags
        if category in CATEGORY_KEYWORDS:
            for kw in CATEGORY_KEYWORDS[category]:
                if kw in text_lower and len(kw) > 3:
                    tags.append(kw)

        # Deduplicate and limit
        seen = set()
        unique_tags = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)

        return unique_tags[:5]

    def classify(self, title: str, description: str) -> dict:
        """Full classification pipeline"""
        combined_text = f"{title} {description}"

        category, confidence = self.classify_category(combined_text)
        priority = self.classify_priority(combined_text)
        sentiment, score = self.analyze_sentiment(combined_text)
        tags = self.extract_tags(combined_text, category)

        # Boost priority based on sentiment
        if sentiment == "Very Negative" and priority == "Low":
            priority = "Medium"
        elif sentiment == "Very Negative" and priority == "Medium":
            priority = "High"

        return {
            "category": category,
            "confidence": confidence,
            "priority": priority,
            "sentiment": sentiment,
            "sentiment_score": score,
            "tags": tags
        }


# Singleton instance
classifier = ComplaintClassifier()
