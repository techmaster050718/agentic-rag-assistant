"use client";

import { motion } from "framer-motion";
import { FileText, Trash2, CheckCircle2, Clock, AlertCircle } from "lucide-react";
import type { Document } from "@/types";
import { formatRelativeTime } from "@/lib/utils";

interface DocumentCardProps {
  document: Document;
  onDelete: (id: string) => void;
}

const statusConfig = {
  ingested: { icon: CheckCircle2, color: "text-emerald-400", label: "Ingested" },
  pending: { icon: Clock, color: "text-amber-400", label: "Processing" },
  failed: { icon: AlertCircle, color: "text-red-400", label: "Failed" },
};

export function DocumentCard({ document: doc, onDelete }: DocumentCardProps) {
  const status = statusConfig[doc.status] || statusConfig.pending;
  const StatusIcon = status.icon;

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.96 }}
      className="flex items-start gap-4 p-4 rounded-2xl bg-gray-800/60 border border-gray-700/50 hover:border-gray-600/70 transition-all group"
    >
      <div className="w-10 h-10 rounded-xl bg-violet-600/20 flex items-center justify-center flex-shrink-0">
        <FileText className="w-5 h-5 text-violet-400" />
      </div>

      <div className="flex-1 min-w-0">
        <p className="font-medium text-white truncate text-sm">{doc.filename}</p>
        <div className="flex items-center gap-3 mt-1">
          <div className={`flex items-center gap-1 ${status.color}`}>
            <StatusIcon className="w-3 h-3" />
            <span className="text-xs">{status.label}</span>
          </div>
          {doc.chunk_count > 0 && (
            <span className="text-xs text-gray-500">{doc.chunk_count} chunks</span>
          )}
          <span className="text-xs text-gray-500">{formatRelativeTime(doc.created_at)}</span>
        </div>
      </div>

      <button
        onClick={() => onDelete(doc.id)}
        className="flex-shrink-0 p-2 rounded-xl text-gray-600 hover:text-red-400 hover:bg-red-400/10 opacity-0 group-hover:opacity-100 transition-all"
      >
        <Trash2 className="w-4 h-4" />
      </button>
    </motion.div>
  );
}
