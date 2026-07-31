"use client";

import { motion, AnimatePresence } from "framer-motion";
import type { Citation } from "@/types";
import { X, FileText, Star } from "lucide-react";
import { truncate } from "@/lib/utils";

interface CitationPanelProps {
  citations: Citation[];
  onClose: () => void;
}

export function CitationPanel({ citations, onClose }: CitationPanelProps) {
  return (
    <div className="bg-gray-900/95 backdrop-blur-xl border border-gray-700/50 rounded-2xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700/50 bg-gradient-to-r from-violet-900/30 to-indigo-900/30">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-violet-400" />
          <span className="text-sm font-semibold text-white">
            Sources · {citations.length}
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Citations */}
      <div className="max-h-80 overflow-y-auto divide-y divide-gray-800/50">
        {citations.map((citation, i) => (
          <motion.div
            key={citation.id}
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.05 }}
            className="p-4 hover:bg-white/5 transition-colors cursor-pointer"
          >
            <div className="flex items-start gap-3">
              <span className="flex-shrink-0 w-6 h-6 rounded-full bg-violet-600/20 text-violet-400 text-xs font-bold flex items-center justify-center">
                {citation.id}
              </span>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <p className="text-xs font-medium text-violet-300 truncate">
                    {citation.source}
                  </p>
                  {citation.page && (
                    <span className="text-xs text-gray-500">p.{citation.page}</span>
                  )}
                  <div className="ml-auto flex items-center gap-0.5">
                    <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                    <span className="text-xs text-gray-400">
                      {(citation.score * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
                <p className="text-xs text-gray-400 leading-relaxed">
                  {truncate(citation.text, 150)}
                </p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
