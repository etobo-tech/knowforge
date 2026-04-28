import type { Message } from "@/types/chat";

type MessageBubbleProps = {
  message: Message;
};

export function MessageBubble({ message }: MessageBubbleProps) {
  return (
    <article
      className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm sm:text-base ${
        message.role === "user"
          ? "ml-auto bg-zinc-900 text-white"
          : "mr-auto bg-zinc-100 text-zinc-900"
      }`}
    >
      {message.text}
    </article>
  );
}
