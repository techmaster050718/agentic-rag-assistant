"use client";

import { motion } from "framer-motion";

export function TypingIndicator() {
  return (
    <div className="flex items-center gap-3 max-w-4xl mr-auto">
      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-800 border border-gray-600 flex items-center justify-center flex-shrink-0">
        <span className="text-xs">🤖</span>
      </div>
      <div className="bg-gray-800/80 border border-gray-700/50 rounded-2xl rounded-tl-sm px-4 py-3">
        <div className="flex items-center gap-1.5">
          {[0, 0.2, 0.4].map((delay, i) => (
            <motion.span
              key={i}
              className="w-2 h-2 bg-violet-400 rounded-full"
              animate={{ opacity: [0.3, 1, 0.3], scale: [0.8, 1.2, 0.8] }}
              transition={{ duration: 1, repeat: Infinity, delay }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
