import lancedb
from agno import TextKnowledgeBase, Agent
from app.utils.config import GROQ_API_KEY, HUGGINGFACE_API_KEY, LANCEDB_PATH, EMBEDDING_MODEL, VISION_MODEL, TEXT_MODEL
from duckduckgo_search import DDGS
from sentence_transformers import SentenceTransformer
from groq import Groq

class SmartGeologicalRAGSystem:
    def __init__(self, groq_api_key, hf_api_key):
        self.groq_client = Groq(api_key=groq_api_key)
        self.hf_api_key = hf_api_key
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.ddgs = DDGS()

        # Initialize LanceDB
        self.db = lancedb.connect(LANCEDB_PATH)
        self.table_name = "geological_knowledge"
        try:
            self.table = self.db.create_table(
                self.table_name,
                schema=self.embedding_model.get_sentence_embedding_dimension(),
                mode="create"
            )
        except lancedb.errors.TableAlreadyExists:
            self.table = self.db.open_table(self.table_name)

        self.knowledge_base = TextKnowledgeBase(
            embedding_function=self.embedding_model.encode,
            vector_store=self.table,
            search_function=self.hybrid_search,
        )

        self.create_agents()

    def hybrid_search(self, query, vector, k=5, alpha=0.5):
        """
        Hybrid search using vector and full-text search.
        """
        vector_results = self.table.search(vector).limit(k).to_df()
        text_results = self.table.search(query).limit(k).to_df()

        # Combine results (simple concatenation for demonstration)
        combined_results = pd.concat([vector_results, text_results]).drop_duplicates()
        return combined_results

    def create_agents(self):
        """
        Create specialized geological agents.
        """
        self.vision_geologist = self.create_vision_geologist()
        self.document_analyst = self.create_document_analyst()
        self.research_specialist = self.create_research_specialist()
        self.data_analyst = self.create_data_analyst()
        self.synthesis_expert = self.create_synthesis_expert()

    def create_vision_geologist(self):
        """
        Creates the VisionGeologist agent.
        """
        return Agent(
            name="VisionGeologist",
            llm=self.groq_client,
            system_prompt="You are a Vision Geologist, expert in analyzing images, charts, and well log curves. Focus on formation analysis, log curves, graphs, and text extraction.",
            tools=[],  # No tools needed for vision analysis
        )

    def create_document_analyst(self):
        """
        Creates the DocumentAnalyst agent.
        """
        return Agent(
            name="DocumentAnalyst",
            llm=self.groq_client,
            system_prompt="You are a Document Analyst, expert in processing text and structured geological data.",
            tools=[],  # Add tools for document analysis if needed
        )

    def create_research_specialist(self):
        """
        Creates the ResearchSpecialist agent.
        """
        return Agent(
            name="ResearchSpecialist",
            llm=self.groq_client,
            system_prompt="You are a Research Specialist, providing geological context and citations. Use DuckDuckGo to find relevant information.",
            tools=[self.ddgs.text],  # Add DuckDuckGo search tool
        )

    def create_data_analyst(self):
        """
        Creates the DataAnalyst agent.
        """
        return Agent(
            name="DataAnalyst",
            llm=self.groq_client,
            system_prompt="You are a Data Analyst, expert in interpreting numerical data and petrophysical parameters.",
            tools=[],  # Add tools for data analysis if needed
        )

    def create_synthesis_expert(self):
        """
        Creates the SynthesisExpert agent.
        """
        return Agent(
            name="SynthesisExpert",
            llm=self.groq_client,
            system_prompt="You are a Synthesis Expert, combining insights from all agents to provide a comprehensive geological analysis.",
            tools=[],  # No tools needed for synthesis
        )

    def add_documents_to_knowledge_base(self, processed_files):
        """
        Add processed files to the LanceDB knowledge base.
        """
        for file_data in processed_files:
            if "text_content" in file_data:
                self.knowledge_base.add_documents([file_data["text_content"]])
