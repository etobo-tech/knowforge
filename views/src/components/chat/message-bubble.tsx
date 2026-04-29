import type { Message } from "@/types/chat";

type MessageBubbleProps = {
  message: Message;
};

export function MessageBubble({ message }: MessageBubbleProps) {
  const timestamp = new Date(message.createdAt).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
  const isError = message.kind === "error";

  return (
    <article
      className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm sm:text-base ${
        message.role === "user"
          ? "ml-auto bg-zinc-900 text-white"
          : isError
            ? "mr-auto border border-red-200 bg-red-50 text-red-800"
            : "mr-auto bg-zinc-100 text-zinc-900"
      }`}
    >
      <p>{message.text}</p>
      {message.role === "assistant" &&
        message.citations &&
        message.citations.length > 0 && (
          <p className="mt-2 text-xs text-zinc-500">
            Sources:{" "}
            {message.citations
              .map((item) => `${item.fileId}:${item.chunkId}`)
              .join(", ")}
          </p>
        )}
      <p
        className={`mt-1 text-[11px] ${
          message.role === "user"
            ? "text-zinc-300"
            : isError
              ? "text-red-500"
              : "text-zinc-500"
        }`}
      >
        {timestamp}
      </p>
    </article>
  );
}
