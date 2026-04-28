"use client";

import { useEffect, useRef } from "react";
import { ChatHeader } from "@/components/chat/chat-header";
import { ChatInput } from "@/components/chat/chat-input";
import { MessageList } from "@/components/chat/message-list";
import { useChat } from "@/hooks/use-chat";

export function ChatPage() {
  const {
    messages,
    input,
    isThinking,
    canSend,
    canClear,
    setInput,
    sendMessage,
    clearMessages,
  } = useChat();
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  return (
    <main className="mx-auto flex h-dvh w-full max-w-4xl flex-col bg-white">
      <ChatHeader onClear={clearMessages} canClear={canClear} />
      <MessageList messages={messages} isThinking={isThinking} endRef={endRef} />
      <ChatInput
        input={input}
        canSend={canSend}
        onInputChange={setInput}
        onSubmit={sendMessage}
      />
    </main>
  );
}
