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
    <main className="flex h-dvh w-full items-center justify-center px-3 py-4 sm:px-6">
      <div className="flex h-full w-full max-w-5xl flex-col overflow-hidden rounded-2xl border border-zinc-200 bg-white/90 shadow-xl backdrop-blur-sm">
        <ChatHeader onClear={clearMessages} canClear={canClear} />
        <MessageList messages={messages} isThinking={isThinking} endRef={endRef} />
        <ChatInput
          input={input}
          canSend={canSend}
          isThinking={isThinking}
          onInputChange={setInput}
          onSubmit={sendMessage}
        />
      </div>
    </main>
  );
}
