const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_PREFIX = `${BASE_URL}/api/v1`;

interface StreamChatParams {
  query: string;
  session_id?: string;
  document_ids?: string[];
}

export const api = {
  /**
   * Start a streaming chat request and return a ReadableStream.
   */
  async streamChat(params: StreamChatParams): Promise<ReadableStream<Uint8Array>> {
    const response = await fetch(`${API_PREFIX}/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      throw new Error(`Chat stream failed: ${response.status} ${response.statusText}`);
    }

    return response.body!;
  },

  /**
   * Upload a document for ingestion.
   */
  async uploadDocument(file: File): Promise<{
    document_id: string;
    filename: string;
    chunk_count: number;
    status: string;
  }> {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_PREFIX}/ingest/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({ detail: "Upload failed" }));
      throw new Error(err.detail || "Upload failed");
    }

    const data = await response.json();
    // Backend returns `id`, map to `document_id` for the hook
    return { ...data, document_id: data.document_id ?? data.id };
  },

  /**
   * Fetch list of all documents.
   */
  async listDocuments(): Promise<{
    documents: Array<{
      id: string;
      filename: string;
      status: string;
      chunk_count: number;
      created_at: string;
    }>;
    total: number;
  }> {
    const response = await fetch(`${API_PREFIX}/documents`);
    if (!response.ok) throw new Error("Failed to load documents");
    return response.json();
  },

  /**
   * Delete a document by ID.
   */
  async deleteDocument(documentId: string): Promise<void> {
    const response = await fetch(`${API_PREFIX}/documents/${documentId}`, {
      method: "DELETE",
    });
    if (!response.ok && response.status !== 204) {
      throw new Error("Failed to delete document");
    }
  },

  /**
   * Health check.
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await fetch(`${API_PREFIX}/health`);
    return response.json();
  },
};
