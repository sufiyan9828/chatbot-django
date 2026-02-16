import re
import logging

logger = logging.getLogger(__name__)


class PIIMasker:
    """
    Utility to detect and mask Personally Identifiable Information (PII)
    before sending data to external AI services.
    """

    # Common Patterns
    PATTERNS = {
        # Credit Card (Basic 16-digit, supports common separators)
        "credit_card": r"\b(?:\d{4}[ -]?){3}\d{4}\b",
        # SSN (Social Security Number - USA)
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        # Email Address
        "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        # Phone Number (Basic International/US)
        "phone": r"\b(?:\+?\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b",
        # Aadhaar (India - 12 digits)
        "aadhaar": r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b",
    }

    @staticmethod
    def mask(text: str) -> str:
        """
        Mask all detected PII in the given text.
        """
        if not text:
            return text

        masked_text = text

        for pii_type, pattern in PIIMasker.PATTERNS.items():
            try:
                # Replace with [MASKED_TYPE]
                masked_text = re.sub(
                    pattern, f"[MASKED_{pii_type.upper()}]", masked_text
                )
            except Exception as e:
                logger.error(f"Error masking {pii_type}: {e}")

        return masked_text


# Singleton instance
pii_masker = PIIMasker()
