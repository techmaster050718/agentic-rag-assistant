"use client";

import { Menu, Zap } from "lucide-react";

interface TopBarProps {
  onToggleSidebar: () => void;
  onToggleTimeline?: () => void;
  showTimelineButton?: boolean;
}

export function TopBar({ onToggleSidebar, onToggleTimeline, showTimelineButton }: TopBarProps) {
  return (
    <header className="flex items-center justify-between px-4 py-3 border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm">
      <button
        onClick={onToggleSidebar}
        className="p-2 rounded-xl hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
      >
        <Menu className="w-5 h-5" />
      </button>

      <h1 className="text-sm font-semibold text-white">
        Agentic RAG Assistant
      </h1>

      <div className="w-9 flex justify-end">
        {showTimelineButton && onToggleTimeline && (
          <button
            onClick={onToggleTimeline}
            className="p-2 rounded-xl hover:bg-violet-600/20 text-gray-400 hover:text-violet-400 transition-colors"
            title="Toggle agent timeline"
          >
            <Zap className="w-4 h-4" />
          </button>
        )}
      </div>
    </header>
  );
}
