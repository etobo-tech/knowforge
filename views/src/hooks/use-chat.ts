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
      { id: crypto.randomUUID(), role: "user", text: userText },
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
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: "assistant",
          text: "I could not generate an answer right now. Please try again.",
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

  return {
    messages,
    input,
    isThinking,
    canSend,
    canClear,
    setInput,
    sendMessage,
    clearMessages,
  };
}
