'use client'

import { useRef, useState, type DragEvent } from 'react'
import { CloudUpload, Upload } from 'lucide-react'

const ACCEPT = '.pdf,.docx,.txt,.md'

type Props = {
  isUploading: boolean
  onFilesSelected: (files: File[]) => void
}

export function UploadDropzone({ isUploading, onFilesSelected }: Props) {
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const dragOver = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const dragLeave = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const drop = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files.length > 0) {
      onFilesSelected(Array.from(e.dataTransfer.files))
    }
  }

  const onInputChange = (files: FileList | null) => {
    if (files?.length) {
      onFilesSelected(Array.from(files))
    }
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div
      onDragOver={dragOver}
      onDragLeave={dragLeave}
      onDrop={drop}
      onClick={() => !isUploading && inputRef.current?.click()}
      className={`border-2 border-dashed rounded-2xl p-12 text-center transition-colors ${
        isUploading ? 'cursor-wait opacity-60' : 'cursor-pointer'
      } ${
        isDragging
          ? 'border-primary bg-primary/5'
          : 'border-card-border bg-card-bg hover:border-primary/40'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        multiple
        accept={ACCEPT}
        className="hidden"
        disabled={isUploading}
        onChange={(e) => onInputChange(e.target.files)}
      />
      <CloudUpload size={40} className="mx-auto mb-4 text-text-secondary/50" />
      <p className="text-lg font-semibold text-text-primary mb-1">
        {isUploading ? 'Uploading…' : 'Drop files here or click to upload'}
      </p>
      <p className="text-sm text-text-secondary mb-5">
        PDF, DOCX, TXT, MD &middot; Max 25 MB per file
      </p>
      <button
        type="button"
        disabled={isUploading}
        onClick={(e) => {
          e.stopPropagation()
          inputRef.current?.click()
        }}
        className="inline-flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary-hover disabled:opacity-50 text-white rounded-lg text-sm font-medium transition-colors"
      >
        <Upload size={14} />
        Browse files
      </button>
    </div>
  )
}
