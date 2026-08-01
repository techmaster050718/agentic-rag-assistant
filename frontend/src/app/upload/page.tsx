"use client";

import { AnimatePresence } from "framer-motion";
import { useCallback } from "react";
import { UploadZone } from "@/components/documents/upload-zone";
import { FileUploadItem } from "@/components/documents/file-upload-item";
import { useFileUpload } from "@/hooks/use-file-upload";
import { FadeIn } from "@/components/motion/fade-in";
import { Upload, CheckCircle2, MessageSquare } from "lucide-react";
import Link from "next/link";
import { Sidebar } from "@/components/chat/sidebar";

export default function UploadPage() {
  const { items, addFiles, uploadAll, removeItem } = useFileUpload();

  const handleFilesSelected = useCallback(
    async (files: File[]) => {
      const newItems = addFiles(files);
      await uploadAll(newItems);
    },
    [addFiles, uploadAll]
  );

  const allDone = items.length > 0 && items.every((i) => i.status === "done");

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
      {/* Persistent Sidebar */}
      <div className="w-64 flex-shrink-0">
        <Sidebar />
      </div>

      {/* Main content */}
      <main className="flex-1 overflow-y-auto px-6 py-12">
        <div className="max-w-2xl mx-auto">
          <FadeIn>
            <div className="flex items-center gap-3 mb-8">
              <div className="w-10 h-10 rounded-xl bg-violet-600/20 flex items-center justify-center">
                <Upload className="w-5 h-5 text-violet-400" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Upload Documents</h1>
                <p className="text-sm text-gray-400">PDF, TXT, MD, DOCX, CSV — up to 50MB each</p>
              </div>
            </div>
          </FadeIn>

          <FadeIn delay={0.1}>
            <UploadZone onFilesSelected={handleFilesSelected} />
          </FadeIn>

          {items.length > 0 && (
            <FadeIn delay={0.2} className="mt-6 space-y-3">
              <AnimatePresence>
                {items.map((item) => (
                  <FileUploadItem key={item.id} item={item} onRemove={removeItem} />
                ))}
              </AnimatePresence>

              {allDone && (
                <FadeIn>
                  <div className="p-5 bg-gray-900/50 rounded-xl mt-6 border border-gray-800 flex items-center justify-between">
                    <div className="flex items-center gap-3 text-emerald-400 text-sm font-medium">
                      <CheckCircle2 className="w-5 h-5" />
                      All documents ingested successfully!
                    </div>
                    <Link
                      href="/chat"
                      className="flex items-center gap-2 text-sm bg-violet-600 hover:bg-violet-700 text-white px-5 py-2.5 rounded-lg font-medium transition-colors"
                    >
                      <MessageSquare className="w-4 h-4" />
                      Go to Chat
                    </Link>
                  </div>
                </FadeIn>
              )}
            </FadeIn>
          )}
        </div>
      </main>
    </div>
  );
}
