"use client";

import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, Circle, Loader2, X, Zap } from "lucide-react";
import type { AgentStep } from "@/types";

interface AgentTimelineProps {
  steps: AgentStep[];
  onClose: () => void;
}

const NODE_LABELS: Record<string, string> = {
  memory: "Loading Memory",
  retrieve: "Retrieving Documents",
  compare: "Evaluating Context",
  summarize: "Generating Answer",
  clarify: "Generating Clarification",
};

const NODE_COLORS: Record<string, string> = {
  memory: "text-blue-400",
  retrieve: "text-cyan-400",
  compare: "text-amber-400",
  summarize: "text-emerald-400",
  clarify: "text-rose-400",
};

export function AgentTimeline({ steps, onClose }: AgentTimelineProps) {
  return (
    <div className="h-full bg-gray-900/50 backdrop-blur-sm flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-violet-400" />
          <span className="text-sm font-semibold text-white">Agent Thinking</span>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded-lg hover:bg-white/10 text-gray-400 hover:text-white transition-colors"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Timeline */}
      <div className="flex-1 p-4 overflow-y-auto space-y-3">
        <AnimatePresence initial={false}>
          {steps.map((step, i) => (
            <motion.div
              key={`${step.node}-${i}`}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-3"
            >
              {/* Icon */}
              <div className="flex-shrink-0">
                {step.status === "running" ? (
                  <Loader2 className="w-5 h-5 text-violet-400 animate-spin" />
                ) : step.status === "done" ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                ) : (
                  <Circle className="w-5 h-5 text-gray-600" />
                )}
              </div>

              {/* Label */}
              <div className="flex-1 min-w-0">
                <p
                  className={`text-sm font-medium ${
                    step.status === "done"
                      ? "text-gray-300"
                      : step.status === "running"
                      ? NODE_COLORS[step.node] || "text-violet-400"
                      : "text-gray-600"
                  }`}
                >
                  {NODE_LABELS[step.node] || step.node}
                </p>
                <p className="text-xs text-gray-500 capitalize">{step.status}</p>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
