import type { Message } from "@/types/chat";
import type { RefObject } from "react";
import { MessageBubble } from "@/components/chat/message-bubble";

type MessageListProps = {
  messages: Message[];
  isThinking: boolean;
  endRef: RefObject<HTMLDivElement | null>;
};

export function MessageList({ messages, isThinking, endRef }: MessageListProps) {
  return (
    <section className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isThinking && (
          <article className="mr-auto rounded-2xl bg-zinc-100 px-4 py-3 text-sm text-zinc-600 sm:text-base">
            Thinking...
          </article>
        )}
        <div ref={endRef} />
      </div>
    </section>
  );
}
