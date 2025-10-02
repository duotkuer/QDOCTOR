import re
from typing import Tuple, List, Dict

# Basic PHI patterns - extend as needed
PHI_PATTERNS = [
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",  # emails
    r"\b(\+?\d{7,15})\b",                               # phone-like
    r"\b\d{6,12}\b"                                     # id-like
]

PROMPT_INJECTION_SIGNATURES = [
    "ignore previous", "ignore all prior instructions", "do not follow", 
    "bypass", "sudo", "rm -rf", "<script>", "jailbreak", "break out"
]

class InputGuardrail:
    """Validates and sanitizes user input."""
    def __init__(self):
        self.phi_patterns = [re.compile(p, re.IGNORECASE) for p in PHI_PATTERNS]
        self.injection_signs = [s.lower() for s in PROMPT_INJECTION_SIGNATURES]

    def validate(self, text: str) -> Tuple[bool, str]:
        """
        Returns (True, sanitized_text) on success.
        Returns (False, reason) on failure (e.g., prompt injection).
        """
        lowered = text.lower()
        for sig in self.injection_signs:
            if sig in lowered:
                return False, f"Rejected input: contains potential injection signature '{sig}'."

        sanitized = text
        # Redact PHI patterns
        for pat in self.phi_patterns:
            sanitized = pat.sub("[REDACTED]", sanitized)
        return True, sanitized

class OutputGuardrail:
    """Validates the LLM's generated response."""
    def validate(self, response: str, context_chunks: List[Dict]) -> Tuple[bool, str]:
        """
        Performs basic checks on the generated output.
        - Ensures response is not empty.
        - Checks for dangerous keywords if context is missing.
        - Avoids definitive medical advice, preferring referrals.
        """
        if not response or not response.strip():
            return False, "Empty or null response from model."

        lower = response.lower()
        
        # Check for refusal phrases
        refusal_phrases = ["i cannot answer", "i am not qualified", "i am an ai"]
        if any(phrase in lower for phrase in refusal_phrases):
            return False, "Model refused to answer the question."

        # If the response includes actionable instructions, ensure we have context to back it up.
        dangerous_keywords = ["prescribe", "dosage", "dosages", "administer", "injection", "surgery"]
        if any(k in lower for k in dangerous_keywords):
            if not context_chunks:
                return False, "Potentially actionable medical instruction was generated without supporting context."
        
        return True, response

class GuardrailService:
    """A wrapper service for both input and output guardrails."""
    def __init__(self):
        self.input_guard = InputGuardrail()
        self.output_guard = OutputGuardrail()