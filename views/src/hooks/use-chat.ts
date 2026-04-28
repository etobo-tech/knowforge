"use client";

import { useMemo, useState } from "react";
import type { Message } from "@/types/chat";

const initialMessages: Message[] = [
  {
    id: "welcome",
    role: "assistant",
    text: "Welcome to Knowforge. Ask me anything about your documentation.",
  },
];

export function useChat() {
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

    await new Promise((resolve) => setTimeout(resolve, 700));

    setMessages((prev) => [
      ...prev,
      {
        id: crypto.randomUUID(),
        role: "assistant",
        text: `Mock answer: I received "${userText}". Backend integration comes next.`,
      },
    ]);
    setIsThinking(false);
  };

  return { messages, input, isThinking, canSend, setInput, sendMessage };
}
