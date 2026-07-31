"use client";

import { AnimatePresence, motion } from "framer-motion";
import { DocumentCard } from "./document-card";
import { Skeleton } from "@/components/motion/skeleton";
import type { Document } from "@/types";

interface DocumentListProps {
  documents: Document[];
  loading: boolean;
  onDelete: (id: string) => void;
}

export function DocumentList({ documents, loading, onDelete }: DocumentListProps) {
  if (loading) {
    return (
      <div className="space-y-3">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="p-4 rounded-2xl bg-gray-800/60 border border-gray-700/50">
            <Skeleton lines={2} />
          </div>
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="text-center py-16 text-gray-500">
        <p className="text-lg font-medium">No documents yet</p>
        <p className="text-sm mt-1">Upload documents to get started</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <AnimatePresence mode="popLayout">
        {documents.map((doc) => (
          <DocumentCard key={doc.id} document={doc} onDelete={onDelete} />
        ))}
      </AnimatePresence>
    </div>
  );
}
