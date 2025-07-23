# Smart Geological RAG System

A multimodal AI system for analyzing geological documents, well logs, and formation data.

## Features

- **Smart Vision Processing**: Intelligently decides when to use vision models for cost savings.
- **Multi-Agent Architecture**: Specialized agents for different geological analysis tasks.
- **LanceDB Integration**: Hybrid search with no database server required.
- **Multi-Format Support**: Process PDFs, CSVs, Excel, images, DOCX, and TXT files.
- **Streamlit UI**: Professional, real-time interface for analysis.

## Quick Start

1.  **Clone the repository:**
    ```bash
    git clone https:
    cd smart-geological-rag
    ```

2.  **Set up API Keys:**
    -     - Add your Groq and HuggingFace API keys to the `.env` file.

3.  **Run with Docker:**
    ```bash
    docker-compose up --build
    ```
    Open your browser to `http://localhost:8501`.

4.  **Local Setup (without Docker):**
    ```bash
    bash setup.sh
    bash run.sh
    ```

## Usage

1.  Enter your API keys in the sidebar.
2.  Upload your geological files.
3.  Select an agent to chat with.
4.  View real-time processing statistics and cost savings.

## Troubleshooting

- **Docker build fails**: Ensure you have the latest version of Docker and Docker Compose installed.
- **API key errors**: Double-check that your API keys are correct and have the necessary permissions.
- **File upload issues**: Check the file size limits and supported formats.
