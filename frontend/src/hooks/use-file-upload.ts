"use client";

import { useCallback, useState } from "react";
import { api } from "@/lib/api";
import type { UploadItem } from "@/types";

export function useFileUpload() {
  const [items, setItems] = useState<UploadItem[]>([]);

  const addFiles = useCallback((files: File[]) => {
    const newItems: UploadItem[] = files.map((file) => ({
      id: crypto.randomUUID(),
      file,
      progress: 0,
      status: "pending",
    }));
    setItems((prev) => [...prev, ...newItems]);
    return newItems;
  }, []);

  const uploadAll = useCallback(
    async (fileItems: UploadItem[]) => {
      const pending = fileItems.filter((i) => i.status === "pending");

      await Promise.allSettled(
        pending.map(async (item) => {
          setItems((prev) =>
            prev.map((i) => (i.id === item.id ? { ...i, status: "uploading", progress: 10 } : i))
          );

          try {
            // Simulate progress increments
            const progressInterval = setInterval(() => {
              setItems((prev) =>
                prev.map((i) =>
                  i.id === item.id && i.progress < 80
                    ? { ...i, progress: i.progress + 15 }
                    : i
                )
              );
            }, 300);

            const result = await api.uploadDocument(item.file);
            clearInterval(progressInterval);

            setItems((prev) =>
              prev.map((i) =>
                i.id === item.id
                  ? { ...i, status: "done", progress: 100, documentId: result.document_id }
                  : i
              )
            );
          } catch (err: any) {
            setItems((prev) =>
              prev.map((i) =>
                i.id === item.id
                  ? { ...i, status: "error", error: err.message || "Upload failed" }
                  : i
              )
            );
          }
        })
      );
    },
    []
  );

  const removeItem = useCallback((id: string) => {
    setItems((prev) => prev.filter((i) => i.id !== id));
  }, []);

  const clearAll = useCallback(() => setItems([]), []);

  return { items, addFiles, uploadAll, removeItem, clearAll };
}
