import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from config import LLM_MODEL, TEMPERATURE, MAX_OUTPUT_TOKENS, GOOGLE_API_KEY
from rag.retriever import RetrieverManager
from rag.insurance_prompt import PROMPT

logger = logging.getLogger(__name__)

class RAGChainManager:
    def __init__(self, retriever_manager: RetrieverManager):
        if retriever_manager is None:
            logger.error("Cannot initialize RAGChainManager without a valid RetrieverManager.")
            raise ValueError("RetrieverManager Instance are Required.")
        self.retriever = retriever_manager.get_retriever()

        logger.info(
            "Initializing Gemini model: %s",
            LLM_MODEL
        )
        self.llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            temperature=TEMPERATURE,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            google_api_key=GOOGLE_API_KEY
        )

        # The system prompt for insurance claims
        self.prompt = ChatPromptTemplate.from_template(PROMPT)

    # Helper function to format retrieved documents into a single string.
    @staticmethod
    def _format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Constructs the RAG pipeline using LangChain Expression Language (LCEL).
    def build_chain(self):
        logger.info("Building the LCEL RAG Chain")

        try:
            # LCEL Pipeline Definition
            chain = (
                {
                    # Retrieve policy / claim approval context
                    "claim_approval_context": (
                        lambda x: x["query"]
                    ) 
                    | self.retriever 
                    | self._format_docs,

                    # Retrieve general exclusion context
                    "general_exclusion_context": (
                        lambda x: x["exclusion_query"]
                    )
                    | self.retriever
                    | self._format_docs,
                    
                    # Patient information
                    "patient_info": lambda x: x["patient_info"],
                    # Medical bill
                    "medical_bill_info": lambda x: x["medical_bill_info"],
                    # Medical report
                    "medical_report": lambda x: x["medical_report"],
                    # Maximum claim amount
                    "max_amount": lambda x: x["max_amount"],
                }
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
            logger.info("Rag Chain Successfully Constructed")
            return chain
        except Exception as e:
            logger.exception("Failed to Build the Rag Chain")
            raise RuntimeError("Rag Chain Construction Failed") from e