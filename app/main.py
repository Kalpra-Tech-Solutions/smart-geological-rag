import streamlit as st
import pandas as pd
import os
from typing import List, Dict, Any
from app.processors.file_processor import PureLLMFileProcessor
from app.agents.rag_system import AdvancedGeologicalRAGSystem
from app.utils.config import Config

# Page configuration
st.set_page_config(
    page_title="Pure LLM Geological RAG System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #2E8B57, #4169E1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-card {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .advanced-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .vision-badge {
        background-color: #ff6b6b;
        color: white;
        padding: 0.2rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'file_processor' not in st.session_state:
        st.session_state.file_processor = None
    if 'processed_files' not in st.session_state:
        st.session_state.processed_files = []
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False

def main():
    init_session_state()
    
    # Main header
    st.markdown('<h1 class="main-header">🧠 Pure LLM Geological RAG System</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="advanced-card">
        <h4>🚀 Advanced Features</h4>
        <p>✨ Pure LLM extraction (No regex, no hardcoding)</p>
        <p>👁️ Heavy vision analysis by default</p>
        <p>🔍 Advanced hybrid search with embeddings</p>
        <p>🧠 Best-in-class prompting and analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ System Configuration")
        
        # Validate API keys
        is_valid, message = Config.validate_required_keys()
        
        if is_valid:
            st.markdown("""
            <div class="success-card">
                <h4>✅ Pure LLM System Ready</h4>
                <p>Advanced AI extraction enabled</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Initialize systems
            if not st.session_state.system_initialized:
                try:
                    with st.spinner("🚀 Initializing Pure LLM System..."):
                        Config.cleanup_temp_directory()
                        
                        st.session_state.rag_system = AdvancedGeologicalRAGSystem(
                            Config.GROQ_API_KEY, Config.HUGGINGFACE_API_KEY
                        )
                        st.session_state.file_processor = PureLLMFileProcessor(
                            Config.GROQ_API_KEY
                        )
                        st.session_state.system_initialized = True
                        
                    st.success("✅ Pure LLM system initialized!")
                    
                    # Display advanced stats
                    stats = st.session_state.rag_system.get_system_stats()
                    st.markdown(f"""
                    <div class="advanced-card">
                        <h4>📊 Advanced System Status</h4>
                        <p>🤖 Agents: {stats['agents_count']}</p>
                        <p>📄 Documents: {stats['documents_loaded']}</p>
                        <p>🔍 Search: {stats['vector_db_type'][:30]}...</p>
                        <p>🧠 Processing: {stats['processing_approach']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ System initialization failed: {str(e)}")
        else:
            st.error(f"❌ {message}")
        
        # File upload section
        st.header("📁 Advanced Document Upload")
        st.markdown("**Supports:** PDF, CSV, Excel, Images, TXT, DOCX, LAS")
        
        uploaded_files = st.file_uploader(
            "Upload geological documents",
            accept_multiple_files=True,
            type=['pdf', 'csv', 'xlsx', 'xls', 'txt', 'docx', 'png', 'jpg', 'jpeg', 'las', 'tiff', 'tif'],
            help="Upload files for pure LLM analysis with heavy vision processing"
        )
        
        # Processing options (Force vision is always enabled)
        if uploaded_files and st.session_state.system_initialized:
            st.subheader("🧠 Pure LLM Processing")
            
            st.markdown("""
            <div class="vision-badge">HEAVY VISION ENABLED</div>
            """, unsafe_allow_html=True)
            
            st.info("🔥 Force vision is enabled by default for maximum extraction quality")
            
            # Process files button
            if st.button("🚀 Process with Pure LLM Analysis", type="primary"):
                process_files_pure_llm(uploaded_files)
        
        # Display processed files
        if st.session_state.processed_files:
            display_processed_files_advanced()
    
    # Main chat interface
    st.header("💬 Advanced Geological Chat")
    
    if st.session_state.system_initialized and st.session_state.rag_system:
        # Search type selection
        search_type = st.selectbox(
            "🔍 Search Strategy",
            ['hybrid', 'vector', 'keyword'],
            format_func=lambda x: {
                'hybrid': '🎯 Hybrid Search (Vector + Keyword + Semantic)',
                'vector': '🔢 Vector Similarity Search',
                'keyword': '🔤 Keyword Matching Search'
            }[x],
            index=0  # Default to hybrid
        )
        
        # Agent selection
        agent_type = st.selectbox(
            "🤖 Select Expert Agent",
            ['synthesis', 'document', 'data', 'vision'],
            format_func=lambda x: {
                'synthesis': '🧠 Geological Synthesis Expert (Recommended)',
                'document': '📄 Document Analysis Specialist',
                'data': '📊 Petrophysical Data Analyst',
                'vision': '👁️ Vision Analysis Expert'
            }[x]
        )
        
        # Knowledge base status
        stats = st.session_state.rag_system.get_system_stats()
        if stats['knowledge_base_loaded']:
            st.success(f"✅ Advanced Knowledge Base: {stats['documents_loaded']} documents with embeddings")
            
            # Test search capabilities
            if st.button("🧪 Test Search Capabilities"):
                test_results = st.session_state.rag_system.test_search_capabilities("well name API number depth")
                st.write("**Search Test Results:**")
                for search_method, results in test_results.items():
                    st.write(f"- {search_method.title()}: {results['count']} results, top score: {results['top_score']:.3f}")
        else:
            st.warning("⚠️ Upload and process documents to enable advanced search")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask about your geological documents with advanced AI analysis..."):
            handle_chat_input_advanced(prompt, agent_type, search_type)
        
        # Example queries
        if len(st.session_state.messages) == 0:
            st.markdown("""
            ### 💡 Try These Advanced Queries:
            - "Extract all well identification data from the uploaded documents"
            - "Analyze the formation tops and provide detailed geological interpretation"
            - "What are the petrophysical properties and reservoir characteristics?"
            - "Provide a comprehensive summary of all technical data"
            - "Compare the geological data across different wells"
            - "What production and testing information is available?"
            """)
    else:
        st.info("🔧 Initialize the system and upload documents to start advanced analysis")

def process_files_pure_llm(uploaded_files):
    """Process files with pure LLM approach"""
    st.session_state.processed_files = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, uploaded_file in enumerate(uploaded_files):
        status_text.text(f"🧠 Pure LLM processing: {uploaded_file.name}... ({i+1}/{len(uploaded_files)})")
        
        try:
            with st.spinner(f"Advanced analysis of {uploaded_file.name}..."):
                # Force vision is always True
                processed_data = st.session_state.file_processor.process_file(uploaded_file, force_vision=True)
                st.session_state.processed_files.append(processed_data)
                
        except Exception as e:
            error_data = {
                'text': f"Error processing {uploaded_file.name}: {str(e)}",
                'metadata': {'filename': uploaded_file.name, 'type': 'error', 'error': True}
            }
            st.session_state.processed_files.append(error_data)
            st.error(f"Error processing {uploaded_file.name}: {str(e)}")
        
        progress_bar.progress((i + 1) / len(uploaded_files))
    
    # Add to knowledge base
    try:
        docs_added = st.session_state.rag_system.add_documents_to_knowledge_base(st.session_state.processed_files)
        
        status_text.empty()
        
        successful_files = len([f for f in st.session_state.processed_files if not f['metadata'].get('error', False)])
        st.success(f"✅ Pure LLM processing complete: {successful_files}/{len(uploaded_files)} files, {docs_added} in advanced knowledge base")
        
        # Clean up
        Config.cleanup_temp_directory()
            
    except Exception as e:
        st.error(f"❌ Error adding to knowledge base: {str(e)}")

def display_processed_files_advanced():
    """Display processed files with advanced information"""
    st.header("📋 Pure LLM Processing Results")
    
    total_docs = len(st.session_state.processed_files)
    successful_docs = len([f for f in st.session_state.processed_files if not f['metadata'].get('error', False)])
    vision_docs = len([f for f in st.session_state.processed_files if f['metadata'].get('has_vision_analysis', False)])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Files", total_docs)
    with col2:
        st.metric("Successfully Processed", successful_docs)
    with col3:
        st.metric("With Vision Analysis", vision_docs)
    
    for file_data in st.session_state.processed_files:
        metadata = file_data['metadata']
        
        # Status indicator
        if metadata.get('error', False):
            status = "❌ Error"
            color = "red"
        elif metadata.get('has_vision_analysis', False):
            status = "🧠 Pure LLM + Vision"
            color = "green"
        else:
            status = "📄 Text Only"
            color = "blue"
        
        with st.expander(f"{status} {metadata['filename']}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**File Information:**")
                st.json(metadata)
            
            with col2:
                if 'processing_stats' in file_data:
                    st.markdown("**Processing Statistics:**")
                    stats = file_data['processing_stats']
                    for key, value in stats.items():
                        st.text(f"{key}: {value}")
                
                # Show extraction preview
                if 'text' in file_data and len(file_data['text']) > 100:
                    st.markdown("**Extraction Preview:**")
                    st.text(file_data['text'][:500] + "..." if len(file_data['text']) > 500 else file_data['text'])

def handle_chat_input_advanced(prompt, agent_type, search_type):
    """Handle chat input with advanced processing"""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        try:
            with st.spinner(f"🧠 Advanced analysis with {search_type} search..."):
                response_text = st.session_state.rag_system.query_agents(prompt, agent_type, search_type)
                
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            error_response = f"❌ Error in advanced analysis: {str(e)}"
            st.error(error_response)
            st.session_state.messages.append({"role": "assistant", "content": error_response})

if __name__ == "__main__":
    main()
