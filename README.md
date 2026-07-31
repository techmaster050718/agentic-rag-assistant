<div align="center">
  <h1>Agentic RAG Document Assistant</h1>
  <p>
    <strong>A production-ready, premium Retrieval-Augmented Generation (RAG) system powered by LangGraph, featuring multi-step AI reasoning, real-time streaming, and a luxury SaaS UI.</strong>
  </p>
  <p>
    <a href="#features"><img src="https://img.shields.io/badge/Features-Agentic%20RAG-9B111E?style=for-the-badge&logo=openai&logoColor=white" alt="Features"></a>
    <a href="#tech-stack"><img src="https://img.shields.io/badge/Stack-FastAPI%20%7C%20Next.js%20%7C%20LangGraph-050505?style=for-the-badge&logo=fastapi&logoColor=white" alt="Tech Stack"></a>
    <a href="#deployment"><img src="https://img.shields.io/badge/Deploy-GCP%20Cloud%20Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white" alt="Deployment"></a>
  </p>
</div>

<br />

## 🌟 Overview

Unlike traditional RAG systems that simply retrieve and generate, this **Agentic RAG Assistant** uses a **LangGraph state machine** to evaluate context, prevent hallucinations, and ask clarifying questions when the retrieved data is insufficient. 

Built with a focus on **enterprise-grade architecture**, **observability**, and **premium UI/UX**, this project is designed to serve as a flagship portfolio piece for senior engineering roles.

## ✨ Key Features

### 🧠 Agentic Reasoning
- **Multi-step LangGraph Workflow**: Memory ➔ Retrieve ➔ Compare ➔ Clarify/Summarize.
- **Hallucination Prevention**: The agent evaluates context sufficiency before generating an answer.
- **Grounded Answers**: Strict adherence to retrieved documents with inline citations `[1]`.

### 💎 Premium UI/UX
- **Luxury Dark Theme**: Pure black background with Deep Cherry Red accents.
- **Glassmorphism & Animations**: Smooth Framer Motion transitions, staggered lists, and glass cards.
- **Real-time Streaming**: ChatGPT-like token-by-token streaming via Server-Sent Events (SSE).
- **Agent Activity Timeline**: Visual indicators showing the agent's internal reasoning steps.

### 🏗️ Enterprise Architecture
- **Asynchronous FastAPI**: High-performance, non-blocking API with background task processing.
- **Robust Data Layer**: PostgreSQL for relational data, ChromaDB/pgvector for semantic search.
- **Observability Ready**: Structured logging and LangSmith integration for tracing agent steps.
- **Fully Containerized**: Multi-stage Docker builds and Docker Compose for local orchestration.

### 🚀 DevOps & CI/CD
- **Infrastructure as Code**: Terraform modules for GCP Cloud Run, Cloud SQL, and GCS.
- **Automated Pipelines**: GitHub Actions for continuous testing, building, and zero-downtime deployment.

## 🛠️ Tech Stack

| Category | Technologies |
| :--- | :--- |
| **Backend** | Python 3.11, FastAPI, SQLAlchemy, Alembic, Uvicorn |
| **AI / RAG** | LangGraph, LangChain, OpenAI (GPT-4o-mini, text-embedding-3-small) |
| **Frontend** | Next.js 14 (App Router), React, TypeScript, TailwindCSS, Framer Motion |
| **Database** | PostgreSQL (pgvector), ChromaDB |
| **Infrastructure** | Docker, Terraform, GCP Cloud Run, GCS, GitHub Actions |
| **Observability** | Structlog, LangSmith, Prometheus-ready architecture |

## 📂 Project Structure

```text
agentic-rag-assistant/
├── backend/            # FastAPI application, LangGraph agent, DB models
├── frontend/           # Next.js premium UI, components, state management
├── infra/
│   ├── docker/         # Docker Compose configurations
│   └── terraform/      # GCP Infrastructure as Code
├── docs/               # Architecture, API, and Deployment documentation
├── .github/workflows/  # CI/CD pipelines (GitHub Actions)
└── README.md