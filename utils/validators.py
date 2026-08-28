import logging
from pathlib import Path
from config import ALLOWED_EXTENSIONS, MAX_CONTENT_LENGTH

logger = logging.getLogger(__name__)

# Performs rule-based validation for uploaded claim documents.
class ClaimValidator:
    REQUIRED_DOCUMENTS = [
        "patient_info",
        "medical_bill",
        "medical_report",
    ]

    # Validate uploaded file based on existence, extension, and size.
    @staticmethod
    def validate_file(file_path: str) -> bool:
        path = Path(file_path)
        if not path.exists():
            logger.error("Uploaded file not found: %s", path)
            return False

        if path.suffix.lower().replace(".", "") not in ALLOWED_EXTENSIONS:
            logger.warning("Invalid file type: %s", path.suffix)
            return False

        file_size = path.stat().st_size

        if file_size > MAX_CONTENT_LENGTH:
            logger.warning(
                "File exceeds maximum allowed size (%d bytes).",
                MAX_CONTENT_LENGTH,
            )
            return False

        logger.info("File validation successful: %s", path.name)
        return True

    @staticmethod
    def validate_required_documents(claim_data: dict) -> tuple[bool, list[str]]:
        """
        Check whether all required claim documents are present in the payload.
        """
        missing_documents = []

        for document in ClaimValidator.REQUIRED_DOCUMENTS:
            value = claim_data.get(document)
            
            if value is None:
                missing_documents.append(document)
                continue

            if isinstance(value, str) and not value.strip():
                missing_documents.append(document)

        if missing_documents:
            logger.warning(
                "Missing required documents: %s",
                ", ".join(missing_documents),
            )
            return False, missing_documents

        logger.info("All required claim documents are available.")
        return True, []

    @staticmethod
    def validate_claim_amount(
        claimed_amount: float,
        max_amount: float,
    ) -> bool:
        """
        Validate claim amount against the policy limit.
        """
        if claimed_amount <= 0:
            logger.warning("Invalid claim amount: %.2f", claimed_amount)
            return False

        if claimed_amount > max_amount:
            logger.warning(
                "Claim amount %.2f exceeds policy limit %.2f",
                claimed_amount,
                max_amount,
            )
            return False

        logger.info("Claim amount validation successful.")
        return True