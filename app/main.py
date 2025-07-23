import streamlit as st
from app.utils.config import validate_api_keys, GROQ_API_KEY, HUGGINGFACE_API_KEY
from app.processors.file_processor import SmartMultimodalFileProcessor
from app.agents.rag_system import SmartGeologicalRAGSystem
import os
import io

# Custom CSS for styling
st.markdown(
    """
    <style>
    .reportview-container {
        background: #f0f8ff; /* Background color */
    }
    .main {
        color: #2E8B57; /* Primary geological theme color */
    }
    .sidebar .sidebar-content {
        background-color: #e6f2ff; /* Sidebar background color */
    }
    h1, h2, h3 {
        color: #2E8B57; /* Header color */
    }
    .stButton>button {
        color: #ffffff;
        background-color: #2E8B57;
        border: none;
        padding: 10px 20px;
        border-radius: 5px;
    }
    .stTextInput>label {
        color: #2E8B57;
    }
    .stSelectbox>label {
        color: #2E8B57;
    }
    .stNumberInput>label {
        color: #2E8B57;
    }
    .stFileUploader>label {
        color: #2E8B57;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def main():
    st.title("Smart Geological RAG System")

    # Sidebar for API keys and settings
    with st.sidebar:
        st.header("API Keys")
        groq_api_key = st.text_input("Groq API Key", type="password", value=GROQ_API_KEY if GROQ_API_KEY else "")
        hf_api_key = st.text_input("HuggingFace API Key", type="password", value=HUGGINGFACE_API_KEY if HUGGINGFACE_API_KEY else "")

        if st.button("Validate API Keys"):
            os.environ["GROQ_API_KEY"] = groq_api_key
            os.environ["HUGGINGFACE_API_KEY"] = hf_api_key
            try:
                validate_api_keys()
                st.success("API Keys Validated!")
            except ValueError as e:
                st.error(f"API Key Error: {e}")

        st.header("Settings")
        force_vision = st.checkbox("Force Vision Analysis", False)

    # File upload section
    st.header("Upload Geological Data")
    uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True, type=["pdf", "csv", "xlsx", "jpg", "jpeg", "png", "doc", "docx", "txt"])

    # Initialize processors and RAG system
    if groq_api_key and hf_api_key:
        file_processor = SmartMultimodalFileProcessor(groq_api_key)
        rag_system = SmartGeologicalRAGSystem(groq_api_key, hf_api_key)

        processed_files = []
        if uploaded_files:
            with st.spinner("Processing files..."):
                for uploaded_file in uploaded_files:
                    file_bytes = uploaded_file.read()
                    file_data = file_processor.process_file(file_bytes, uploaded_file.name, force_vision)
                    processed_files.append(file_data)

                rag_system.add_documents_to_knowledge_base(processed_files)

            st.success("Files processed and added to knowledge base!")

        # Agent selection and chat interface
        st.header("Chat with Geological Agents")
        agent_names = ["VisionGeologist", "DocumentAnalyst", "ResearchSpecialist", "DataAnalyst", "SynthesisExpert"]
        agent_selection = st.selectbox("Select an Agent", agent_names)

        if agent_selection:
            agent = getattr(rag_system, f"create_{agent_selection.lower()}")()  # Access agent dynamically
            query = st.text_input("Enter your geological query:")
            if query:
                with st.spinner("Generating response..."):
                    prompt = f"{agent.system_prompt}\nUser Query: {query}"
                    response = rag_system.groq_client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": prompt}]
                    ).choices[0].message.content
                    st.write(response)

        # Statistics Dashboard (Example)
        st.header("Processing Statistics")
        if processed_files:
            total_vision_calls_made = sum([file_data.get("stats", {}).get("vision_calls_made", 0) for file_data in processed_files if "stats" in file_data])
            total_vision_calls_saved = sum([file_data.get("stats", {}).get("vision_calls_saved", 0) for file_data in processed_files if "stats" in file_data])
            total_pages = sum([file_data.get("stats", {}).get("total_pages", 0) for file_data in processed_files if "stats" in file_data])

            st.write(f"Total Vision Calls Made: {total_vision_calls_made}")
            st.write(f"Total Vision Calls Saved: {total_vision_calls_saved}")
            st.write(f"Total Pages Processed: {total_pages}")

            if total_pages > 0:
                efficiency_percentage = (total_vision_calls_saved / total_pages) * 100
                st.write(f"Efficiency (Vision Calls Saved): {efficiency_percentage:.2f}%")

if __name__ == "__main__":
    main()
