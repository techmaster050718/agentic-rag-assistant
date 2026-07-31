# Architecture Overview

The Agentic RAG Document Assistant is built on a modular, microservices-inspired architecture designed for scalability, observability, and maintainability.

## System Components

1. **Frontend (Next.js)**: A premium, server-side rendered React application providing a luxury SaaS user experience.
2. **Backend API (FastAPI)**: A high-performance, asynchronous Python API that orchestrates document ingestion.
3. **Agentic Core (LangGraph)**: The brain of the application. Instead of a simple retrieve-and-generate pipeline, it uses a multi-step state machine to evaluate context, prevent hallucinations, and generate grounded answers.
4. **Vector Store (ChromaDB / pgvector)**: Stores high-dimensional embeddings for semantic search.
