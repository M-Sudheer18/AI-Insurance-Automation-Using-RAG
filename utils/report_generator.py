import logging
from datetime import datetime
from pathlib import Path
from config import BASE_DIR

logger = logging.getLogger(__name__)

REPORT_FOLDER = BASE_DIR / "reports"
REPORT_FOLDER.mkdir(parents=True, exist_ok=True)

# Utility class to handle the formatting and saving of AI-generated claim reports.
class ReportGenerator:
    # Saves the generated LLM report to a timestamped Markdown file. 
    # Returns the saved file path.
    @staticmethod
    def save_report(claim_id: str, report_content: str) -> str:
        if not report_content:
            logger.error("No report content is provided to save.")
            raise ValueError("report content cannot be empty")
        logger.info("Generating report file for Claim ID: %s", claim_id)

        # Generate a unique filename based on the claim ID and current time
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"claim_report_{claim_id}_{timestamp}.md"
        file_path = REPORT_FOLDER / file_name

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                # Inject a professional header before the LLM's content
                file.write(f"# Insurance Claim Assessment Report\n")
                file.write(f"**Claim ID:** {claim_id}\n")
                file.write(f"**Date Generated:** {datetime.now().strftime(r'%Y-%m-%d %H:%M:%S')}\n")
                file.write("---\n\n")
                # Write the actual AI-generated report
                file.write(report_content)
            logger.info("Successfully Saved claim report to %s", file_path)
            return str(file_path)
        except Exception as e:
            logger.exception("Failed to save the report for claim %s", claim_id)
            raise RuntimeError(f"Report generation failed for claim {claim_id}") from e

    @staticmethod
    def parse_report_to_dict(report_content: str) -> dict:
        logger.info("Parsing report content into dictionary format...")
        parsed_data = {
            "information": "UNKNOWN",
            "exclusion": "UNKNOWN",
            "final_decision": "MANUAL REVIEW",
            "approved_amount": None,
        }
        lines = report_content.splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            # Remove Markdown formatting
            clean_line = line.replace("**", "").strip()
            if clean_line.upper().startswith("INFORMATION:"):
                parsed_data["information"] = (
                    clean_line.split(":", 1)[1].strip().upper()
                )
            elif clean_line.upper().startswith("EXCLUSION:"):
                parsed_data["exclusion"] = (
                    clean_line.split(":", 1)[1].strip().upper()
                )
            elif clean_line.upper().startswith("FINAL DECISION:"):
                parsed_data["final_decision"] = (
                    clean_line.split(":", 1)[1].strip().upper()
                )
            elif (
                "MAXIMUM AMOUNT APPROVED:" in clean_line.upper()
                or "APPROVED AMOUNT:" in clean_line.upper()
            ):
                amount_text = clean_line.split(":", 1)[1].strip()
                try:
                    amount_text = (
                        amount_text
                        .replace("₹", "")
                        .replace("$", "")
                        .replace(",", "")
                        .strip()
                    )
                    parsed_data["approved_amount"] = float(amount_text)
                except ValueError:
                    logger.warning(
                        "Could not parse approved amount: %s",
                        amount_text
                    )
        logger.info(
            "Parsed claim result | information=%s | exclusion=%s | decision=%s | approved_amount=%s",
            parsed_data["information"],
            parsed_data["exclusion"],
            parsed_data["final_decision"],
            parsed_data["approved_amount"],
        )
        return parsed_data