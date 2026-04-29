"use client";

import { useMemo, useState } from "react";
import type { ChatService } from "@/services/chat/chat-service";
import { getChatService } from "@/services/chat/get-chat-service";
import type { Message } from "@/types/chat";

const initialMessages: Message[] = [
  {
    id: "welcome",
    role: "assistant",
    text: "Welcome to Knowforge. Ask me anything about your documentation.",
    createdAt: Date.now(),
    kind: "normal",
  },
];

const defaultChatService = getChatService();

export function useChat(chatService: ChatService = defaultChatService) {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isThinking, setIsThinking] = useState(false);

  const canSend = useMemo(
    () => input.trim().length > 0 && !isThinking,
    [input, isThinking],
  );

  const sendMessage = async () => {
    if (!canSend) return;

    const userText = input.trim();
    setInput("");
    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: "user",
        text: userText,
        createdAt: Date.now(),
        kind: "normal",
      },
    ]);
    setIsThinking(true);

    try {
      const reply = await chatService.ask(userText);

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text: reply.text,
          createdAt: Date.now(),
          kind: "normal",
          citations: reply.citations,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text: "I could not generate an answer right now. Please try again.",
          createdAt: Date.now(),
          kind: "error",
        },
      ]);
    } finally {
      setIsThinking(false);
    }
  };

  const clearMessages = () => {
    if (isThinking) return;
    setMessages(initialMessages);
  };

  const canClear = messages.length > 1 && !isThinking;

  const addAssistantMessage = ({
    text,
    kind = "normal",
  }: {
    text: string;
    kind?: "normal" | "error";
  }) => {
    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: "assistant",
        text,
        createdAt: Date.now(),
        kind,
      },
    ]);
  };

  return {
    messages,
    input,
    isThinking,
    canSend,
    canClear,
    setInput,
    sendMessage,
    clearMessages,
    addAssistantMessage,
  };
}
