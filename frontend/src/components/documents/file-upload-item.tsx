"use client";

import { motion } from "framer-motion";
import { FileText, CheckCircle2, XCircle, Loader2, X } from "lucide-react";
import { formatFileSize } from "@/lib/utils";
import type { UploadItem } from "@/types";

interface FileUploadItemProps {
  item: UploadItem;
  onRemove: (id: string) => void;
}

export function FileUploadItem({ item, onRemove }: FileUploadItemProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="flex items-center gap-3 p-3 rounded-xl bg-gray-800/60 border border-gray-700/50"
    >
      <FileText className="w-8 h-8 text-violet-400 flex-shrink-0" />

      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-white truncate">{item.file.name}</p>
        <p className="text-xs text-gray-400">{formatFileSize(item.file.size)}</p>

        {item.status === "uploading" && (
          <div className="mt-1.5 h-1 bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${item.progress}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
        )}

        {item.error && <p className="text-xs text-red-400 mt-0.5">{item.error}</p>}
      </div>

      <div className="flex-shrink-0">
        {item.status === "uploading" && (
          <Loader2 className="w-5 h-5 text-violet-400 animate-spin" />
        )}
        {item.status === "done" && (
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
        )}
        {item.status === "error" && (
          <XCircle className="w-5 h-5 text-red-400" />
        )}
        {item.status === "pending" && (
          <button
            onClick={() => onRemove(item.id)}
            className="p-1 rounded-lg hover:bg-white/10 text-gray-500 hover:text-white transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    </motion.div>
  );
}
