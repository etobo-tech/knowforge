type Props = {
  message: string | null
}

export function UploadNoticeBanner({ message }: Props) {
  if (!message) return null

  return (
    <div
      role="status"
      className="mb-6 rounded-xl border border-primary/30 bg-primary/5 px-4 py-3 text-sm text-text-primary"
    >
      {message}
    </div>
  )
}
