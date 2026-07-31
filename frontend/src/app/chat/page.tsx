"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useChatStore } from "@/store/chat";
import { MessageBubble } from "@/components/chat/message-bubble";
import { ChatInput } from "@/components/chat/chat-input";
import { Sidebar } from "@/components/chat/sidebar";
import { CitationPanel } from "@/components/chat/citation-panel";
import { AgentTimeline } from "@/components/chat/agent-timeline";
import { TopBar } from "@/components/layout/top-bar";
import { FadeIn } from "@/components/motion/fade-in";
import { TypingIndicator } from "@/components/motion/typing-indicator";
import { api } from "@/lib/api";
import type { Citation, AgentStep } from "@/types";

export default function ChatPage() {
  const {
    messages,
    sessionId,
    addMessage,
    updateLastMessage,
    setSessionId,
    isStreaming,
    setIsStreaming,
  } = useChatStore();

  const [agentSteps, setAgentSteps] = useState<AgentStep[]>([]);
  const [selectedCitations, setSelectedCitations] = useState<Citation[]>([]);
  const [showCitationPanel, setShowCitationPanel] = useState(false);
  const [showAgentTimeline, setShowAgentTimeline] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const handleSend = useCallback(
    async (query: string) => {
      if (!query.trim() || isStreaming) return;

      // Add user message
      addMessage({ role: "user", content: query, citations: [] });
      setIsStreaming(true);
      setAgentSteps([]);
      setShowAgentTimeline(true);

      // Placeholder assistant message
      addMessage({ role: "assistant", content: "", citations: [] });

      try {
        const stream = await api.streamChat({
          query,
          session_id: sessionId || undefined,
        });

        let fullContent = "";
        const reader = stream.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const text = decoder.decode(value, { stream: true });
          const lines = text.split("\n");

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            const raw = line.slice(6).trim();
            if (raw === "[DONE]") break;

            try {
              const event = JSON.parse(raw);

              if (event.type === "token") {
                fullContent += event.content;
                updateLastMessage({ content: fullContent });
              } else if (event.type === "step_start") {
                setAgentSteps((prev) => [
                  ...prev,
                  { node: event.node, status: "running", timestamp: Date.now() },
                ]);
              } else if (event.type === "step_end") {
                setAgentSteps((prev) =>
                  prev.map((s) =>
                    s.node === event.node ? { ...s, status: "done" } : s
                  )
                );
              } else if (event.type === "final") {
                if (event.session_id) setSessionId(event.session_id);
                updateLastMessage({
                  content: event.answer || fullContent,
                  citations: event.citations || [],
                });
                if (event.citations?.length > 0) {
                  setSelectedCitations(event.citations);
                  setShowCitationPanel(true);
                }
              }
            } catch {
              // Non-JSON line, skip
            }
          }
        }
      } catch (err) {
        updateLastMessage({ content: "An error occurred. Please try again." });
      } finally {
        setIsStreaming(false);
      }
    },
    [isStreaming, sessionId, addMessage, updateLastMessage, setIsStreaming, setSessionId]
  );

  const handleCitationClick = useCallback((citations: Citation[]) => {
    setSelectedCitations(citations);
    setShowCitationPanel(true);
  }, []);

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
      {/* Sidebar */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ x: -280, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -280, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="w-72 flex-shrink-0"
          >
            <Sidebar onClose={() => setSidebarOpen(false)} />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main chat area */}
      <div className="flex flex-col flex-1 min-w-0">
        <TopBar
          onToggleSidebar={() => setSidebarOpen((o) => !o)}
          onToggleTimeline={() => setShowAgentTimeline((o) => !o)}
          showTimelineButton={agentSteps.length > 0}
        />

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 scrollbar-thin scrollbar-track-gray-900 scrollbar-thumb-gray-700">
          <AnimatePresence initial={false}>
            {messages.map((msg, i) => (
              <FadeIn key={i}>
                <MessageBubble
                  message={msg}
                  onCitationClick={handleCitationClick}
                />
              </FadeIn>
            ))}
          </AnimatePresence>

          {isStreaming && messages[messages.length - 1]?.content === "" && (
            <FadeIn>
              <TypingIndicator />
            </FadeIn>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-800 p-4">
          <ChatInput onSend={handleSend} disabled={isStreaming} />
        </div>
      </div>

      {/* Agent Timeline — critical fix #7a: integrated */}
      <AnimatePresence>
        {showAgentTimeline && agentSteps.length > 0 && (
          <motion.div
            initial={{ x: 320, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 320, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="w-80 flex-shrink-0 border-l border-gray-800"
          >
            <AgentTimeline
              steps={agentSteps}
              onClose={() => setShowAgentTimeline(false)}
            />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Citation Panel — critical fix #7b: integrated */}
      <AnimatePresence>
        {showCitationPanel && selectedCitations.length > 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="fixed bottom-24 right-6 z-50 w-96"
          >
            <CitationPanel
              citations={selectedCitations}
              onClose={() => setShowCitationPanel(false)}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
