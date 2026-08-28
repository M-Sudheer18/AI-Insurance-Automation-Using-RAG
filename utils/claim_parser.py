import logging
from utils.pdf_reader import PDFReader

logger = logging.getLogger(__name__)

# Prepare document text for the RAG chain
class ClaimParser:
    @staticmethod
    def prepare_claim_payload(
        query: str,
        patient_doc_path: str,
        bill_doc_path: str,
        medical_report_path: str,
        max_amount: str = "Amount not explicitly specified"
    ) -> dict:
        logger.info(
            "Parsing claim documents for RAG payload..."
        )
        try:
            # Extract patient information
            patient_info_text = PDFReader.extract_text(
                patient_doc_path
            )
            # Extract medical bill
            medical_bill_text = PDFReader.extract_text(
                bill_doc_path
            )
            # Extract medical report
            medical_report_text = PDFReader.extract_text(
                medical_report_path
            )
            payload = {
                "query": query,
                # Used specifically for exclusion retrieval
                "exclusion_query": (
                    f"general insurance exclusions related to "
                    f"{query}"
                ),
                "patient_info": patient_info_text,
                "medical_bill_info": medical_bill_text,
                "medical_report": medical_report_text,
                "max_amount": max_amount
            }
            logger.info(
                "Claim payload successfully structured."
            )
            return payload
        except Exception as e:
            logger.exception(
                "Failed to parse claim document."
            )
            raise RuntimeError(
                "Claim document parser failed."
            ) from e