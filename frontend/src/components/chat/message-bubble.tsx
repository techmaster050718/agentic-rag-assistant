"use client";

import { motion } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { Bot, User, FileText } from "lucide-react";
import type { Message, Citation } from "@/types";
import { cn } from "@/lib/utils";

interface MessageBubbleProps {
  message: Message;
  onCitationClick?: (citations: Citation[]) => void;
}

export function MessageBubble({ message, onCitationClick }: MessageBubbleProps) {
  const isUser = message.role === "user";
  const hasCitations = message.citations && message.citations.length > 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn("flex gap-3 max-w-4xl", isUser ? "ml-auto flex-row-reverse" : "mr-auto")}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center",
          isUser
            ? "bg-gradient-to-br from-violet-600 to-indigo-600"
            : "bg-gradient-to-br from-gray-700 to-gray-800 border border-gray-600"
        )}
      >
        {isUser ? (
          <User className="w-4 h-4 text-white" />
        ) : (
          <Bot className="w-4 h-4 text-violet-400" />
        )}
      </div>

      {/* Bubble */}
      <div className="max-w-[80%]">
        <div
          className={cn(
            "px-4 py-3 rounded-2xl text-sm leading-relaxed",
            isUser
              ? "bg-gradient-to-br from-violet-600 to-indigo-700 text-white rounded-tr-sm"
              : "bg-gray-800/80 text-gray-100 border border-gray-700/50 rounded-tl-sm"
          )}
        >
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <div className="prose prose-invert prose-sm max-w-none">
              <ReactMarkdown>{message.content || "…"}</ReactMarkdown>
            </div>
          )}
        </div>

        {/* Citations badge */}
        {hasCitations && (
          <button
            onClick={() => onCitationClick?.(message.citations)}
            className="mt-2 flex items-center gap-1.5 text-xs text-violet-400 hover:text-violet-300 transition-colors group"
          >
            <FileText className="w-3 h-3" />
            <span className="group-hover:underline">
              {message.citations.length} source{message.citations.length !== 1 ? "s" : ""}
            </span>
          </button>
        )}
      </div>
    </motion.div>
  );
}
