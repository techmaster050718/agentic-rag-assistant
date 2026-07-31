export interface Message {
  role: "user" | "assistant";
  content: string;
  citations: Citation[];
}

export interface Citation {
  id: number;
  source: string;
  page?: number | null;
  text: string;
  score: number;
}

export interface AgentStep {
  node: string;
  status: "running" | "done" | "error";
  timestamp: number;
}

export interface Document {
  id: string;
  filename: string;
  status: "pending" | "ingested" | "failed";
  chunk_count: number;
  created_at: string;
}

export interface UploadItem {
  id: string;
  file: File;
  progress: number;
  status: "pending" | "uploading" | "done" | "error";
  error?: string;
  documentId?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  createdAt: Date;
  messageCount: number;
}
