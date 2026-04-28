type ChatHeaderProps = {
  onClear: () => void;
  canClear: boolean;
};

export function ChatHeader({ onClear, canClear }: ChatHeaderProps) {
  return (
    <header className="border-b border-zinc-200 bg-white px-4 py-3 sm:px-6">
      <div className="mx-auto flex w-full max-w-3xl items-center justify-between">
        <h1 className="text-sm font-semibold text-zinc-900 sm:text-base">Knowforge Chat</h1>
        <button
          type="button"
          onClick={onClear}
          disabled={!canClear}
          className="rounded-lg border border-zinc-300 px-3 py-1.5 text-xs font-medium text-zinc-700 disabled:cursor-not-allowed disabled:opacity-40 sm:text-sm"
        >
          Clear chat
        </button>
      </div>
    </header>
  );
}
