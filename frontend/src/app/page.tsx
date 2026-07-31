"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { MessageSquare, Upload, FileText, Sparkles, ArrowRight, Zap, Shield, Brain } from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "Multi-Step Agent",
    description: "LangGraph orchestrates memory, retrieval, evaluation, and generation for grounded answers.",
  },
  {
    icon: Zap,
    title: "Real-Time Streaming",
    description: "Tokens stream via SSE for an instant, ChatGPT-like experience with live agent steps.",
  },
  {
    icon: Shield,
    title: "Grounded Citations",
    description: "Every answer includes inline citations with source passages and relevance scores.",
  },
];

const navCards = [
  { href: "/chat", label: "Open Chat", icon: MessageSquare, gradient: "from-violet-600 to-indigo-600" },
  { href: "/upload", label: "Upload Docs", icon: Upload, gradient: "from-cyan-600 to-blue-600" },
  { href: "/documents", label: "My Documents", icon: FileText, gradient: "from-emerald-600 to-teal-600" },
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gray-950 text-white">
      {/* Hero */}
      <section className="relative overflow-hidden px-6 py-24 text-center">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-900/20 via-transparent to-indigo-900/20 pointer-events-none" />
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-violet-500/30 bg-violet-500/10 text-violet-300 text-sm mb-6">
            <Sparkles className="w-4 h-4" />
            Powered by LangGraph + GPT-4o-mini
          </div>
          <h1 className="text-5xl sm:text-7xl font-bold tracking-tight mb-6 bg-gradient-to-br from-white via-gray-100 to-gray-400 bg-clip-text text-transparent">
            Agentic RAG<br />Document Assistant
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto mb-10">
            Upload your documents and get grounded, cited answers from an intelligent multi-step agent.
            No hallucinations — every answer is traceable to a source.
          </p>
          <Link
            href="/chat"
            className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white font-semibold shadow-xl shadow-violet-500/30 transition-all hover:scale-105"
          >
            Start Chatting <ArrowRight className="w-5 h-5" />
          </Link>
        </motion.div>
      </section>

      {/* Nav Cards */}
      <section className="px-6 pb-16 max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-4">
        {navCards.map(({ href, label, icon: Icon, gradient }, i) => (
          <motion.div
            key={href}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 * i }}
          >
            <Link
              href={href}
              className={`flex items-center gap-3 p-5 rounded-2xl bg-gradient-to-br ${gradient} hover:scale-105 transition-all shadow-lg font-semibold`}
            >
              <Icon className="w-6 h-6" />
              {label}
              <ArrowRight className="w-4 h-4 ml-auto" />
            </Link>
          </motion.div>
        ))}
      </section>

      {/* Features */}
      <section className="px-6 pb-24 max-w-4xl mx-auto grid grid-cols-1 sm:grid-cols-3 gap-6">
        {features.map(({ icon: Icon, title, description }, i) => (
          <motion.div
            key={title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + 0.1 * i }}
            className="p-6 rounded-2xl bg-gray-900/60 border border-gray-800 hover:border-gray-700 transition-all"
          >
            <Icon className="w-8 h-8 text-violet-400 mb-4" />
            <h3 className="font-semibold text-white mb-2">{title}</h3>
            <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
          </motion.div>
        ))}
      </section>
    </main>
  );
}
