import { useEffect, useRef } from "react";
import type { ChangeEvent, FormEvent, KeyboardEvent } from "react";

type ChatInputProps = {
  input: string;
  canSend: boolean;
  isThinking: boolean;
  onInputChange: (value: string) => void;
  onSubmit: () => Promise<void>;
};

export function ChatInput({
  input,
  canSend,
  isThinking,
  onInputChange,
  onSubmit,
}: ChatInputProps) {
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;
    textarea.style.height = "0px";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 160)}px`;
  }, [input]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onSubmit();
  };

  const handleChange = (event: ChangeEvent<HTMLTextAreaElement>) => {
    onInputChange(event.target.value);
  };

  const handleKeyDown = async (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key !== "Enter" || event.shiftKey) return;
    event.preventDefault();
    await onSubmit();
  };

  return (
    <section className="border-t border-zinc-200 bg-white/95 px-4 py-4 sm:px-6">
      <form
        className="mx-auto flex w-full max-w-3xl items-end gap-3"
        onSubmit={handleSubmit}
      >
        <textarea
          ref={textareaRef}
          rows={1}
          className="max-h-40 min-h-11 flex-1 resize-none rounded-xl border border-zinc-300 bg-white px-4 py-3 text-sm text-zinc-800 placeholder:text-zinc-500 outline-none focus:border-zinc-500 focus:ring-2 focus:ring-zinc-200 disabled:cursor-not-allowed disabled:bg-zinc-100 disabled:text-zinc-500 sm:text-base"
          value={input}
          placeholder="Write your question here..."
          disabled={isThinking}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
        />
        <button
          type="submit"
          disabled={!canSend}
          className="h-11 rounded-xl bg-zinc-900 px-5 text-sm font-medium text-white shadow-sm transition hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-50 sm:text-base"
        >
          Send
        </button>
      </form>
    </section>
  );
}
