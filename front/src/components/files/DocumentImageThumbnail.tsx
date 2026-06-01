'use client'

import { Maximize2 } from 'lucide-react'

type Props = {
  previewUrl: string
  filename: string
  onExpand: () => void
}

export function DocumentImageThumbnail({
  previewUrl,
  filename,
  onExpand,
}: Props) {
  return (
    <div className="relative h-12 w-12 shrink-0 overflow-hidden rounded-lg border border-card-border bg-content-bg">
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img
        src={previewUrl}
        alt=""
        className="h-full w-full object-cover"
        loading="lazy"
      />
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation()
          onExpand()
        }}
        className="absolute bottom-0.5 right-0.5 flex h-6 w-6 items-center justify-center rounded-md bg-black/55 text-white hover:bg-black/70 transition-colors"
        aria-label={`Expand ${filename}`}
        title="Expand image"
      >
        <Maximize2 size={12} aria-hidden />
      </button>
    </div>
  )
}
