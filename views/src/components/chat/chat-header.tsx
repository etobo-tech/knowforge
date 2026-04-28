type ChatHeaderProps = {
  onClear: () => void;
  onRetry?: () => Promise<void>;
  canClear: boolean;
  canRetry?: boolean;
};

export function ChatHeader({ onClear, onRetry, canClear, canRetry }: ChatHeaderProps) {
  return (
    <header className="border-b border-zinc-200 bg-white/95 px-4 py-3 sm:px-6">
      <div className="mx-auto flex w-full max-w-3xl items-center justify-between gap-2">
        <div>
          <h1 className="text-sm font-semibold text-zinc-900 sm:text-base">Knowforge Chat</h1>
          <p className="text-xs text-zinc-500">Ask questions about your knowledge base</p>
        </div>
        <div className="flex items-center gap-2">
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              disabled={!canRetry}
              className="rounded-lg border border-zinc-300 px-3 py-1.5 text-xs font-medium text-zinc-700 disabled:cursor-not-allowed disabled:opacity-40 sm:text-sm"
            >
              Retry
            </button>
          )}
          <button
            type="button"
            onClick={onClear}
            disabled={!canClear}
            className="rounded-lg border border-zinc-300 px-3 py-1.5 text-xs font-medium text-zinc-700 disabled:cursor-not-allowed disabled:opacity-40 sm:text-sm"
          >
            Clear chat
          </button>
        </div>
      </div>
    </header>
  );
}
