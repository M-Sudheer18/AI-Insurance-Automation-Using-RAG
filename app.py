import re
import os
import logging
import markdown
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import request, render_template, Flask, send_file

from config import UPLOADS_FOLDER, FLASK_DEBUG

from utils.validators import ClaimValidator
from utils.pdf_reader import PDFReader
from utils.report_generator import ReportGenerator
from utils.claim_parser import ClaimParser

from rag.loader import DocumentsLoader
from rag.splitter import TextSplitter
from rag.embeddings import EmbeddingsManager
from rag.vector_store import VectorStoreManager
from rag.retriever import RetrieverManager
from rag.chain import RAGChainManager

# Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask App
app = Flask(__name__)
app.config["UPLOADS_FOLDER"] = str(UPLOADS_FOLDER)
# Upload directory exists
os.makedirs(
    app.config["UPLOADS_FOLDER"], 
    exist_ok=True
    )

# Global RAG Chain
claim_chain = None

# Initialize RAG System
def initialize_rag_system():
    global claim_chain
    logger.warning("Starting Rag System Initialization..")

    try:
        # Load Policy Documents
        loader = DocumentsLoader()
        raw_docs = loader.load_documents()
        logger.info(
            "Loaded %d policy document pages.",
            len(raw_docs)
        )
        splitter = TextSplitter()
        chunks = splitter.split_documents(raw_docs)
        logger.info(
            "Created %d documents Chunks",
            len(chunks)
        )
        embeddings_mgr = EmbeddingsManager()
        embeddings = embeddings_mgr.get_embeddings()
        vector_mgr = VectorStoreManager(
            embeddings=embeddings
        )
        v_store = vector_mgr.load_vector_store()
        if v_store is None:
            if not chunks:
                raise RuntimeError(
                    "No document chunks available to create FAISS index."
                )
            logger.info("No Existing Vector index Create New Index..")
            v_store = vector_mgr.create_vector_store(
                chunks
            )
            vector_mgr.save_local()

        # Create Retriever
        retriever_mgr = RetrieverManager(
            vector_store=v_store
        )
        # Create RAG Chain
        rag_chain_mgr = RAGChainManager(
            retriever_manager=retriever_mgr
        )
        claim_chain = rag_chain_mgr.build_chain()
        logger.info("Rag Chain Initialized Successfully, Ready for the Requests")
    except Exception as e:
        logger.error("Critical failure during RAG initialization. App will not process claims. Error: %s", str(e))
        claim_chain = None

# Initialize RAG Before Application Starts
with app.app_context():
    initialize_rag_system()

# Home Route
@app.route('/', methods = ["GET"])
def index():
    return render_template("index.html")

# Health Check
@app.route("/api/v1/health", methods=["GET"])
def health_check():
    status = "healthy" if claim_chain is not None else "degraded"
    return {
        "status": status,
        "service": "Insurance Claim Verification Api"
    }, 200

@app.route("/download_report/<path:filename>")
def download_report(filename):
    report_folder = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "reports"
    )

    report_path = os.path.join(
        report_folder,
        filename
    )

    if not os.path.exists(report_path):
        return "Report not found.", 404

    return send_file(
        report_path,
        as_attachment=True
    )

# Process Insurance Claim
@app.route("/api/v1/process_claim", methods=["POST"])
def process_claim():
    if claim_chain is None:
        logger.error(
            "Claim processing requested while RAG system is unavailable."
        )
        return render_template(
            'result.html', 
            output="<h1>System Error</h1><p>The AI verification system is currently offline.</p>"
        ), 503
    uploaded_paths = {}
    try:
        # Get Form Data
        form_data = request.form
        name = form_data.get(
            "name",
            "N/A"
        )
        address = form_data.get(
            "address",
            "N/A"
        )
        claim_type = form_data.get(
            "claim_type",
            "N/A"
        )
        claim_reason = form_data.get(
            "claim_reason",
            "N/A"
        )
        medical_facility = form_data.get(
            "medical_facility",
            "N/A"
        )
        total_claim_amount = form_data.get(
            "total_claim_amount",
            "N/A"
        )
        description = form_data.get(
            "description",
            "N/A"
        )
        # Validate Required Form Fields
        required_fields = {
            "name": name,
            "address": address,
            "claim_type": claim_type,
            "claim_reason": claim_reason,
            "medical_facility": medical_facility,
            "total_claim_amount": total_claim_amount,
            # "description": description
        }

        missing_fields = [
            field
            for field, value in required_fields.items()
            if not value or value == "N/A"
        ]
        if missing_fields:
            logger.warning(
                "Missing Form Fields: %s",
                missing_fields
            )
            return (
                f"Missing Required Fields: {', '.join(missing_fields)}",
                400
            )
        # Process Uploaded Documents
        expected_files = [
            "patient_info",
            "medical_bill",
            "medical_report"
        ]
        for file_key in expected_files:
            uploaded_file = request.files.get(file_key)
            # All three documents are required
            if (
                uploaded_file is None
                or uploaded_file.filename == ""
            ):
                logger.warning(
                    "Missing Required File: %s",
                    file_key
                )
                return (
                    f"Missing Required file: {file_key}",
                    400
                )
            filename = secure_filename(
                uploaded_file.filename
            )
            if not filename:
                return (
                    f"Invalid filename for {file_key}.",
                    400
                )

            file_path = os.path.join(app.config["UPLOADS_FOLDER"], filename)
            uploaded_file.save(file_path)

            # Validate file
            if not ClaimValidator.validate_file(
                file_path
                ):
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return (
                        f"Validation failed for file: {filename}." 
                        f"Please upload a valid PDF within the allowed size.", 
                        400
                    )

            uploaded_paths[file_key] = file_path
        logger.info(
            "All claim documents uploaded successfully."
        )

        # Prepare RAG Input
        payload = ClaimParser.prepare_claim_payload(
            query=claim_reason,
            patient_doc_path=uploaded_paths["patient_info"],
            bill_doc_path=uploaded_paths["medical_bill"],
            medical_report_path=uploaded_paths["medical_report"],
            max_amount=total_claim_amount
        )
        # Invoke Gemini + RAG
        logger.info("Invoking Gemini RAG Chain...")
        llm_response = claim_chain.invoke(
            payload
        )
        # Ensure response is a string
        if not isinstance(
            llm_response,
            str
        ):
            llm_response = str(
                llm_response
            )
        logger.info(
            "Gemini claim analysis completed."
        )

        # Convert Markdown to HTML
        html_report = markdown.markdown(
            llm_response
        )

        # Extract FINAL DECISION from Gemini response
        decision_match = re.search(
            r"FINAL\s+DECISION\s*:\s*(APPROVED|REJECTED|MANUAL\s+REVIEW)",
            llm_response,
            re.IGNORECASE
        )
        if decision_match:
            claim_status = decision_match.group(1).upper()
            if claim_status == "MANUAL REVIEW":
                claim_status = "MANUAL REVIEW"
        else:
            logger.warning("Could not determine FINAL DECISION from Gemini response.")
            claim_status = "MANUAL REVIEW"

        # Save AI Report
        claim_id = (
            f"{name.replace(' ', '_')}_"
            f"{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        report_path = ReportGenerator.save_report(
            claim_id=claim_id,
            report_content=llm_response
        )
        report_filename = os.path.basename(report_path)

        # Extract INFORMATION result
        information_match = re.search(
            r"INFORMATION\s*:\s*(TRUE|FALSE)",
            llm_response,
            re.IGNORECASE
        )

        information = (
            information_match.group(1).upper()
            if information_match
            else "UNKNOWN"
        )

        # Extract EXCLUSION result
        exclusion_match = re.search(
            r"EXCLUSION\s*:\s*(TRUE|FALSE)",
            llm_response,
            re.IGNORECASE
        )

        exclusion = (
            exclusion_match.group(1).upper()
            if exclusion_match
            else "UNKNOWN"
        )

        # Render Result Page
        return render_template(
            "result.html",
            name=name,
            address=address,
            claim_type=claim_type,
            claim_reason=claim_reason,
            medical_facility=medical_facility,
            total_claim_amount=total_claim_amount,
            description=description,
            claim_status=claim_status,
            approved_amount="See AI Report",
            information=information,
            exclusion=exclusion,
            output=html_report,
            report_filename=report_filename
        )
    except Exception as e:
        logger.exception("Error during claim processing workflow.")
        error_message = f"<h2>Claim Processing Error</h2><p>An unexpected error occurred while processing the claim.: {str(e)}</p>"
        return render_template(
            "result.html", 
            output=error_message
        ), 500
    finally:
        # Cleanup Uploaded Files
        for path in uploaded_paths.values():
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info(
                        "Removed temporary file: %s",
                        path
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to remove temporary file: %s",
                        path
                    )

# Run Flask Application
if __name__ == '__main__':
    app.run(
        debug=FLASK_DEBUG,
        host="0.0.0.0",
        port=5000
    )