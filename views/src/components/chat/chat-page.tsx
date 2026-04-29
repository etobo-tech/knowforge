"use client";

import { useEffect, useState, useRef } from "react";
import { ChatHeader } from "@/components/chat/chat-header";
import { ChatInput } from "@/components/chat/chat-input";
import { MessageList } from "@/components/chat/message-list";
import { useChat } from "@/hooks/use-chat";
import { waitForKnowledgeFileStatus } from "@/services/files/file-status-service";
import { uploadKnowledgeFile } from "@/services/files/file-upload-service";

const workspaceId = process.env.NEXT_PUBLIC_WORKSPACE_ID ?? "default-workspace";

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
    addAssistantMessage,
  } = useChat();
  const endRef = useRef<HTMLDivElement | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isThinking]);

  const handleUpload = async (file: File) => {
    setIsUploading(true);
    try {
      const result = await uploadKnowledgeFile({
        file,
        workspaceId,
      });
      addAssistantMessage({
        text: `File uploaded: ${file.name} (id: ${result.fileId}, status: ${result.status})`,
      });
      const statusResult = await waitForKnowledgeFileStatus({
        fileId: result.fileId,
      });
      addAssistantMessage({
        text: `File status update: ${statusResult.status} (id: ${statusResult.fileId})`,
        kind: statusResult.status === "failed" || statusResult.status === "not_found" ? "error" : "normal",
      });
    } catch (error) {
      const detail =
        error instanceof Error && error.message === "unsupported_file_type"
          ? "Only .txt and .md files are supported right now."
          : "File upload failed. Please try again.";
      addAssistantMessage({
        text: detail,
        kind: "error",
      });
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className="flex h-dvh w-full items-center justify-center px-3 py-4 sm:px-6">
      <div className="flex h-full w-full max-w-5xl flex-col overflow-hidden rounded-2xl border border-zinc-200 bg-white/90 shadow-xl backdrop-blur-sm">
        <ChatHeader
          onClear={clearMessages}
          onUpload={handleUpload}
          isUploading={isUploading}
          canClear={canClear}
        />
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
