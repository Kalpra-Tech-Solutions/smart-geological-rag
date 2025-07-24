import streamlit as st
from typing import List, Dict, Any, Optional
from groq import Groq
from app.utils.config import Config
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import os
import pickle
from datetime import datetime


class AdvancedEmbeddingStore:
    """Advanced embedding store with hybrid search capabilities"""
    
    def __init__(self, embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        try:
            # Use the best sentence transformer model
            self.embedding_model = SentenceTransformer('all-mpnet-base-v2')  # Better than all-MiniLM-L6-v2
        except:
            # Fallback
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.documents = []
        self.embeddings = []
        self.metadata = []
        self.document_texts = []
        self.embedding_dim = None
        
    def add_documents(self, processed_files: List[Dict[str, Any]]) -> int:
        """Add documents with advanced embeddings"""
        added_count = 0
        
        for file_data in processed_files:
            if 'text' in file_data and not file_data['metadata'].get('error', False):
                text_content = file_data['text'].strip()
                if text_content and len(text_content) > 50:
                    
                    # Create multiple embeddings for different aspects
                    embeddings = self._create_multi_aspect_embeddings(text_content)
                    
                    doc_entry = {
                        'content': text_content,
                        'metadata': file_data['metadata'],
                        'embeddings': embeddings,
                        'doc_id': len(self.documents),
                        'added_at': datetime.now().isoformat()
                    }
                    
                    self.documents.append(doc_entry)
                    self.document_texts.append(text_content)
                    self.metadata.append(file_data['metadata'])
                    added_count += 1
        
        st.success(f"✅ Added {added_count} documents with advanced embeddings")
        return added_count
    
    def _create_multi_aspect_embeddings(self, text: str) -> Dict[str, np.ndarray]:
        """Create embeddings for different aspects of the text"""
        embeddings = {}
        
        # Full text embedding
        embeddings['full_text'] = self.embedding_model.encode(text[:1000])  # Limit for efficiency
        
        # Extract and embed key sections
        sections = self._extract_key_sections(text)
        for section_name, section_text in sections.items():
            if section_text:
                embeddings[section_name] = self.embedding_model.encode(section_text[:500])
        
        return embeddings
    
    def _extract_key_sections(self, text: str) -> Dict[str, str]:
        """Extract key sections from text for specialized embeddings"""
        sections = {
            'well_info': '',
            'technical_data': '',
            'geological_data': '',
            'numerical_data': ''
        }
        
        # Simple keyword-based section identification
        lines = text.split('\n')
        current_section = 'well_info'
        
        for line in lines:
            line_lower = line.lower()
            
            # Identify section based on content
            if any(word in line_lower for word in ['formation', 'lithology', 'geology', 'strat']):
                current_section = 'geological_data'
            elif any(word in line_lower for word in ['depth', 'pressure', 'rate', 'volume', 'porosity']):
                current_section = 'technical_data'
            elif any(char.isdigit() for char in line) and len([c for c in line if c.isdigit()]) > 3:
                current_section = 'numerical_data'
            
            sections[current_section] += line + '\n'
        
        return sections
    
    def advanced_search(self, query: str, limit: int = 5, search_type: str = "hybrid") -> List[Dict[str, Any]]:
        """Advanced search with multiple strategies"""
        if not self.documents:
            return []
        
        # Create query embedding
        query_embedding = self.embedding_model.encode(query)
        
        results = []
        
        for doc in self.documents:
            scores = {}
            
            # Vector similarity scores for different aspects
            for aspect, embedding in doc['embeddings'].items():
                similarity = np.dot(query_embedding, embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
                )
                scores[f'vector_{aspect}'] = similarity
            
            # Keyword matching score
            keyword_score = self._calculate_keyword_score(query, doc['content'])
            scores['keyword'] = keyword_score
            
            # Semantic coherence score
            semantic_score = self._calculate_semantic_score(query, doc['content'])
            scores['semantic'] = semantic_score
            
            # Combined hybrid score
            if search_type == "hybrid":
                final_score = (
                    scores['vector_full_text'] * 0.4 +
                    scores.get('vector_well_info', 0) * 0.2 +
                    scores.get('vector_technical_data', 0) * 0.2 +
                    scores['keyword'] * 0.1 +
                    scores['semantic'] * 0.1
                )
            elif search_type == "vector":
                final_score = scores['vector_full_text']
            elif search_type == "keyword":
                final_score = scores['keyword']
            else:
                final_score = scores['vector_full_text']
            
            results.append({
                'content': doc['content'],
                'metadata': doc['metadata'],
                'score': final_score,
                'detailed_scores': scores,
                'doc_id': doc['doc_id']
            })
        
        # Sort by score and return top results
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def _calculate_keyword_score(self, query: str, text: str) -> float:
        """Calculate keyword matching score"""
        query_words = set(query.lower().split())
        text_words = set(text.lower().split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(text_words)
        return len(intersection) / len(query_words)
    
    def _calculate_semantic_score(self, query: str, text: str) -> float:
        """Calculate semantic coherence score"""
        # Simple implementation - could be enhanced with more sophisticated NLP
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Look for semantic relationships (basic implementation)
        semantic_keywords = {
            'well': ['drill', 'bore', 'hole', 'shaft'],
            'formation': ['layer', 'unit', 'zone', 'horizon'],
            'depth': ['footage', 'interval', 'level'],
            'oil': ['petroleum', 'hydrocarbon', 'crude'],
            'gas': ['natural gas', 'methane', 'hydrocarbon']
        }
        
        score = 0.0
        for query_word in query_lower.split():
            if query_word in text_lower:
                score += 1.0
            else:
                # Check for semantic matches
                for key, synonyms in semantic_keywords.items():
                    if query_word == key and any(syn in text_lower for syn in synonyms):
                        score += 0.5
                        break
        
        return score / max(len(query_lower.split()), 1)
    
    def get_all_text(self) -> str:
        """Get all document text combined"""
        return "\n\n=== DOCUMENT SEPARATOR ===\n\n".join(self.document_texts)
    
    def save_embeddings(self, filepath: str):
        """Save embeddings to disk"""
        data = {
            'documents': self.documents,
            'document_texts': self.document_texts,
            'metadata': self.metadata
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
    
    def load_embeddings(self, filepath: str):
        """Load embeddings from disk"""
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.document_texts = data['document_texts']
                self.metadata = data['metadata']

class AdvancedGeologicalAgent:
    """Advanced geological analysis agent with pure LLM approach"""
    
    def __init__(self, groq_api_key: str, name: str, role: str, specialization: str):
        self.client = Groq(api_key=groq_api_key)
        self.name = name
        self.role = role
        self.specialization = specialization
        self.model = Config.TEXT_MODEL
    
    def analyze_with_context(self, query: str, context_documents: List[Dict], search_results: List[Dict]) -> str:
        """Advanced analysis with comprehensive context"""
        try:
            # Prepare context from search results
            context_text = ""
            for i, result in enumerate(search_results):
                context_text += f"\n--- RELEVANT DOCUMENT {i+1} (Score: {result['score']:.3f}) ---\n"
                context_text += f"Source: {result['metadata']['filename']}\n"
                context_text += f"Content: {result['content'][:2000]}\n"  # Limit each document
            
            system_prompt = f"""
            You are {self.name}, an expert {self.role} specializing in {self.specialization}.
            
            EXPERTISE AREAS:
            - Advanced geological interpretation and analysis
            - Well log analysis and petrophysical evaluation
            - Formation evaluation and reservoir characterization
            - Petroleum geology and hydrocarbon assessment
            - Drilling and completion engineering
            - Geospatial analysis and structural geology
            
            ANALYSIS APPROACH:
            - Use ONLY the information provided in the context documents
            - Provide specific, precise answers with exact values and details
            - Cross-reference information between multiple sources when available
            - Identify and resolve conflicts between different data sources
            - Maintain geological and engineering accuracy in all interpretations
            
            RESPONSE REQUIREMENTS:
            - Extract specific data points (names, numbers, dates, locations)
            - Provide comprehensive analysis with supporting evidence
            - Structure responses clearly with headers and bullet points
            - Include confidence levels and uncertainty assessments
            - Cite specific sources when referencing data
            
            CONTEXT DOCUMENTS:
            {context_text}
            """
            
            user_prompt = f"""
            Based on the geological documents provided in the context, please analyze and respond to this query:
            
            {query}
            
            Requirements:
            - Provide specific, detailed answers using the document content
            - Extract exact values, names, and technical data
            - Explain the geological significance of findings
            - Structure your response professionally with clear sections
            - If information is not available in the documents, state this clearly
            
            Focus on precision, accuracy, and comprehensive analysis.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error in {self.name} analysis: {str(e)}"

class AdvancedGeologicalRAGSystem:
    """Advanced RAG system with pure LLM approach and best-in-class search"""
    
    def __init__(self, groq_api_key: str, hf_api_key: str):
        self.groq_api_key = groq_api_key
        self.hf_api_key = hf_api_key
        
        # Advanced embedding store
        self.embedding_store = AdvancedEmbeddingStore()
        
        # Create specialized agents
        self.agents = {
            'document': AdvancedGeologicalAgent(
                groq_api_key, 
                "GeologicalDocumentSpecialist", 
                "expert geological document analyst",
                "comprehensive document interpretation and data extraction"
            ),
            'data': AdvancedGeologicalAgent(
                groq_api_key, 
                "PetrophysicalAnalyst", 
                "expert petrophysical and reservoir engineer",
                "well log analysis, formation evaluation, and reservoir characterization"
            ),
            'synthesis': AdvancedGeologicalAgent(
                groq_api_key, 
                "GeologicalSynthesisExpert", 
                "senior geological consultant",
                "integrated geological analysis and comprehensive interpretation"
            ),
            'vision': AdvancedGeologicalAgent(
                groq_api_key,
                "VisionGeologicalAnalyst",
                "expert in visual geological data interpretation",
                "chart analysis, log curve interpretation, and visual geological data"
            )
        }
        
    def add_documents_to_knowledge_base(self, processed_files: List[Dict[str, Any]]) -> int:
        """Add documents to advanced knowledge base"""
        try:
            docs_added = self.embedding_store.add_documents(processed_files)
            
            # Save embeddings for persistence
            os.makedirs('data', exist_ok=True)
            self.embedding_store.save_embeddings('data/advanced_embeddings.pkl')
            
            return docs_added
        except Exception as e:
            st.error(f"❌ Error adding documents to knowledge base: {str(e)}")
            return 0
    
    def query_agents(self, query: str, agent_type: str = 'synthesis', search_type: str = "hybrid") -> str:
        """Query agents with advanced search and context"""
        try:
            # Advanced multi-strategy search
            search_results = self.embedding_store.advanced_search(
                query, 
                limit=5, 
                search_type=search_type
            )
            
            if not search_results:
                return "❌ No relevant documents found. Please ensure you have uploaded and processed geological documents."
            
            # Get agent
            agent = self.agents.get(agent_type, self.agents['synthesis'])
            
            # Advanced analysis with context
            response = agent.analyze_with_context(query, self.embedding_store.documents, search_results)
            
            # Add search metadata
            search_info = f"\n\n---\n**Search Information:**\n"
            search_info += f"- Found {len(search_results)} relevant documents\n"
            search_info += f"- Search type: {search_type}\n"
            search_info += f"- Top document: {search_results[0]['metadata']['filename']} (score: {search_results[0]['score']:.3f})\n"
            
            return response + search_info
            
        except Exception as e:
            return f"❌ Error processing query: {str(e)}"
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            'agents_count': len(self.agents),
            'documents_loaded': len(self.embedding_store.documents),
            'knowledge_base_loaded': len(self.embedding_store.documents) > 0,
            'vector_db_type': 'Advanced Embedding Store with Hybrid Search',
            'text_model': Config.TEXT_MODEL,
            'vision_model': Config.VISION_MODEL,
            'embedding_model': 'all-mpnet-base-v2 (Advanced)',
            'search_capabilities': ['Vector Similarity', 'Keyword Matching', 'Semantic Analysis', 'Hybrid Fusion'],
            'processing_approach': 'Pure LLM with Heavy Vision Analysis'
        }
    
    def test_search_capabilities(self, query: str) -> Dict[str, Any]:
        """Test search capabilities with detailed results"""
        results = {}
        
        for search_type in ['vector', 'keyword', 'hybrid']:
            search_results = self.embedding_store.advanced_search(query, limit=3, search_type=search_type)
            results[search_type] = {
                'count': len(search_results),
                'top_score': search_results[0]['score'] if search_results else 0,
                'top_document': search_results[0]['metadata']['filename'] if search_results else 'None'
            }
        
        return results
class PureLLMRAGSystem:
    def __init__(self, groq_api_key: str, model_name: str):
        # ... existing initialization code ...
        self.response_formatter = ResponseFormatter()
    
    def process_query(self, query: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Process user query with enhanced response formatting"""
        try:
            # Reset confidence counter for new response
            self.response_formatter.reset_confidence_counter()
            
            # ... existing query processing code ...
            
            # Get raw response from your LLM
            raw_response = self.generate_response(enhanced_context, query, conversation_history)
            
            # Format the response with conclusion and filtering
            formatted_response = self.response_formatter.format_response(
                raw_response, 
                filename="", 
                include_conclusion=True
            )
            
            return {
                'response': formatted_response,
                'sources': sources,
                'confidence': confidence_score,
                'processing_time': time.time() - start_time
            }
            
        except Exception as e:
            return {
                'response': f"Error processing query: {str(e)}",
                'sources': [],
                'confidence': 0.0,
                'processing_time': 0.0
            }

    def generate_response(self, context: str, query: str, conversation_history: List[Dict] = None) -> str:
        """Generate response with improved prompting for better formatting"""
        
        system_prompt = """
You are an expert geological analyst. Provide comprehensive, well-structured responses.

RESPONSE FORMATTING REQUIREMENTS:
- Use clear headings and subheadings
- Present key information in bullet points
- Include only ONE confidence statement per response
- Focus on factual analysis without excessive reasoning explanations
- Structure responses logically with clear sections

AVOID:
- Showing your thinking process or reasoning steps
- Multiple confidence statements
- Verbose explanations of your analysis approach
- Unnecessary hedging or uncertainty markers
"""

        # ... rest of your response generation logic ...
        
        return response_content