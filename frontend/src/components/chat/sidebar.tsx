"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { MessageSquare, FileText, Upload, X, Sparkles } from "lucide-react";
import { motion } from "framer-motion";
import { useChatStore } from "@/store/chat";
import { cn } from "@/lib/utils";

interface SidebarProps {
  onClose: () => void;
}

const navItems = [
  { href: "/chat", label: "Chat", icon: MessageSquare },
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/upload", label: "Upload", icon: Upload },
];

export function Sidebar({ onClose }: SidebarProps) {
  const pathname = usePathname();
  const { clearHistory, messages } = useChatStore();

  return (
    <aside className="h-full bg-gray-900 border-r border-gray-800 flex flex-col">
      {/* Brand */}
      <div className="flex items-center justify-between px-4 py-4 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <span className="text-sm font-bold text-white">RAG Assistant</span>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(({ href, label, icon: Icon }) => (
          <Link
            key={href}
            href={href}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all",
              pathname === href
                ? "bg-violet-600/20 text-violet-300 border border-violet-500/30"
                : "text-gray-400 hover:bg-white/5 hover:text-white"
            )}
          >
            <Icon className="w-4 h-4" />
            {label}
          </Link>
        ))}
      </nav>

      {/* Clear chat */}
      {messages.length > 0 && (
        <div className="p-3 border-t border-gray-800">
          <button
            onClick={clearHistory}
            className="w-full px-3 py-2 text-xs text-gray-500 hover:text-red-400 hover:bg-red-400/10 rounded-xl transition-all"
          >
            Clear conversation
          </button>
        </div>
      )}
    </aside>
  );
}
