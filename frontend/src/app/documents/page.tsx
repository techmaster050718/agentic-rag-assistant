"use client";

import { AnimatePresence } from "framer-motion";
import { useDocuments } from "@/hooks/use-documents";
import { DocumentList } from "@/components/documents/document-list";
import { FadeIn } from "@/components/motion/fade-in";
import { FileText, RefreshCw } from "lucide-react";

export default function DocumentsPage() {
  const { documents, loading, error, refetch, deleteDocument } = useDocuments();

  return (
    <main className="min-h-screen bg-gray-950 text-white px-6 py-12">
      <div className="max-w-3xl mx-auto">
        <FadeIn>
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-violet-600/20 flex items-center justify-center">
                <FileText className="w-5 h-5 text-violet-400" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Documents</h1>
                <p className="text-sm text-gray-400">
                  {documents.length} document{documents.length !== 1 ? "s" : ""} ingested
                </p>
              </div>
            </div>

            <button
              onClick={refetch}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-700 hover:border-gray-600 text-sm text-gray-400 hover:text-white transition-all disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
              Refresh
            </button>
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-xl bg-red-900/20 border border-red-700/50 text-red-300 text-sm">
              {error}
            </div>
          )}
        </FadeIn>

        <DocumentList documents={documents} loading={loading} onDelete={deleteDocument} />
      </div>
    </main>
  );
}
