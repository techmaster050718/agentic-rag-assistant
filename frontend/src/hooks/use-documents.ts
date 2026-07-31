"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Document } from "@/types";

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listDocuments();
      setDocuments(data.documents as Document[]);
    } catch (err: any) {
      setError(err.message || "Failed to load documents");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const deleteDocument = useCallback(
    async (id: string) => {
      try {
        await api.deleteDocument(id);
        setDocuments((prev) => prev.filter((d) => d.id !== id));
      } catch (err: any) {
        setError(err.message || "Failed to delete document");
      }
    },
    []
  );

  return { documents, loading, error, refetch: fetchDocuments, deleteDocument };
}
