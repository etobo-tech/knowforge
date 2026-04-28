import type { FormEvent } from "react";

type ChatInputProps = {
  input: string;
  canSend: boolean;
  onInputChange: (value: string) => void;
  onSubmit: () => Promise<void>;
};

export function ChatInput({
  input,
  canSend,
  onInputChange,
  onSubmit,
}: ChatInputProps) {
  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    await onSubmit();
  };

  return (
    <section className="border-t border-zinc-200 bg-white px-4 py-4 sm:px-6">
      <form className="mx-auto flex w-full max-w-3xl gap-3" onSubmit={handleSubmit}>
        <input
          className="h-11 flex-1 rounded-xl border border-zinc-300 px-4 text-sm outline-none focus:border-zinc-500 sm:text-base"
          value={input}
          placeholder="Type your question..."
          onChange={(event) => onInputChange(event.target.value)}
        />
        <button
          type="submit"
          disabled={!canSend}
          className="h-11 rounded-xl bg-zinc-900 px-5 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50 sm:text-base"
        >
          Send
        </button>
      </form>
    </section>
  );
}
