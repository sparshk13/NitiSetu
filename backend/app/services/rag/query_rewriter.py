import re
import logging
from typing import Dict, Optional, Tuple, Any

logger = logging.getLogger("nitisetu.rag.rewriter")

# In-memory session context cache keyed by conversation_id
# Format: {conversation_id: {"last_scheme_slug": str, "last_scheme_name": str, "turn_count": int}}
_CONVERSATION_MEMORY: Dict[str, Dict[str, Any]] = {}


class QueryRewriter:
    """
    Conversation-aware query rewriter that resolves pronouns, follow-ups,
    and ambiguous terminology without rewriting straightforward questions unnecessarily.
    """

    PRONOUNS_PATTERN = re.compile(r'\b(it|its|this scheme|the scheme|same scheme|this scholarship|the scholarship|is it|can i get it)\b', re.IGNORECASE)

    SCHEME_CANONICAL_NAMES: Dict[str, str] = {
        "kcc": "Kisan Credit Card (KCC)",
        "pmmy": "Pradhan Mantri MUDRA Yojana",
        "ssy": "Sukanya Samriddhi Yojana",
        "apy": "Atal Pension Yojana",
        "pm-kisan": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "ayushman-bharat-pmjay": "Ayushman Bharat PM-JAY",
        "national-scholarship-post-matric": "National Scholarship Portal (NSP) Post-Matric Scholarship",
        "pm-surya-ghar-muft-bijli": "PM Surya Ghar Muft Bijli Yojana",
        "pm-svanidhi": "PM SVANidhi",
        "pm-vishwakarma": "PM Vishwakarma Scheme",
        "pm-awas-yojana": "Pradhan Mantri Awas Yojana (PMAY)"
    }

    def record_turn(self, conversation_id: Optional[str], scheme_slug: Optional[str], scheme_name: Optional[str]):
        """Record active scheme context for a conversation session."""
        if not conversation_id or not scheme_slug:
            return
        entry = _CONVERSATION_MEMORY.get(conversation_id, {"turn_count": 0})
        entry["last_scheme_slug"] = scheme_slug
        entry["last_scheme_name"] = scheme_name or self.SCHEME_CANONICAL_NAMES.get(scheme_slug, scheme_slug)
        entry["turn_count"] = entry.get("turn_count", 0) + 1
        _CONVERSATION_MEMORY[conversation_id] = entry

    def get_session_scheme(self, conversation_id: Optional[str]) -> Optional[Tuple[str, str]]:
        """Retrieve previously discussed scheme slug and name."""
        if not conversation_id or conversation_id not in _CONVERSATION_MEMORY:
            return None
        mem = _CONVERSATION_MEMORY[conversation_id]
        return mem.get("last_scheme_slug"), mem.get("last_scheme_name")

    def rewrite_if_needed(
        self,
        question: str,
        explicit_scheme_slug: Optional[str] = None,
        conversation_id: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Rewrites conversational follow-up queries if they contain pronouns or context-dependent phrases.
        Returns: (rewritten_question, resolved_scheme_slug)
        """
        q_clean = question.strip()
        q_lower = q_clean.lower()

        # 1. If user explicitly provided a scheme slug, bind to it
        if explicit_scheme_slug and explicit_scheme_slug not in ("all", "undefined", ""):
            resolved_name = self.SCHEME_CANONICAL_NAMES.get(explicit_scheme_slug, explicit_scheme_slug)
            if self.PRONOUNS_PATTERN.search(q_lower):
                rewritten = self.PRONOUNS_PATTERN.sub(resolved_name, q_clean)
                return rewritten, explicit_scheme_slug
            return q_clean, explicit_scheme_slug

        # 2. Check if query contains pronouns referencing previous turn in conversation
        session_context = self.get_session_scheme(conversation_id)
        if session_context:
            last_slug, last_name = session_context
            # Follow-up short questions like: "What is its income limit?", "What documents are required?", "How to apply?"
            is_followup = bool(self.PRONOUNS_PATTERN.search(q_lower))
            is_context_dependent = len(q_clean.split()) <= 4 and any(
                w in q_lower for w in ["income limit", "documents required", "eligibility", "how to apply", "deadline", "benefits", "last date"]
            )

            if is_followup:
                rewritten = self.PRONOUNS_PATTERN.sub(last_name, q_clean)
                return rewritten, last_slug
            elif is_context_dependent and not any(k in q_lower for k in ["kisan", "mudra", "sukanya", "atal", "scholarship", "ayushman", "surya", "svanidhi", "vishwakarma"]):
                rewritten = f"{q_clean} for {last_name}"
                return rewritten, last_slug

        return q_clean, None


query_rewriter = QueryRewriter()
