import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { Message, Citation } from "@/types";

interface ChatState {
  messages: Message[];
  sessionId: string | null;
  isStreaming: boolean;
  addMessage: (message: Message) => void;
  updateLastMessage: (updates: Partial<Message>) => void;
  setSessionId: (id: string) => void;
  setIsStreaming: (streaming: boolean) => void;
  clearHistory: () => void;
}

export const useChatStore = create<ChatState>()(
  persist(
    (set) => ({
      messages: [],
      sessionId: null,
      isStreaming: false,

      addMessage: (message) =>
        set((state) => ({ messages: [...state.messages, message] })),

      updateLastMessage: (updates) =>
        set((state) => {
          const messages = [...state.messages];
          if (messages.length === 0) return state;
          messages[messages.length - 1] = {
            ...messages[messages.length - 1],
            ...updates,
          };
          return { messages };
        }),

      setSessionId: (id) => set({ sessionId: id }),
      setIsStreaming: (isStreaming) => set({ isStreaming }),
      clearHistory: () => set({ messages: [], sessionId: null }),
    }),
    {
      name: "rag-chat-store",
      partialize: (state) => ({
        messages: state.messages.slice(-50), // Persist last 50 messages
        sessionId: state.sessionId,
      }),
    }
  )
);
