'use client'

import { useState, useRef, type DragEvent } from 'react'
import { Upload, CloudUpload } from 'lucide-react'

type FileStatus = 'processing' | 'indexed' | 'error'

interface UploadedFile {
  name: string
  size: string
  type: string
  status: FileStatus
}

const mockUploads: UploadedFile[] = [
  { name: 'refund_policy.pdf', size: '1.4 MB', type: 'PDF', status: 'processing' },
  { name: 'employee_handbook.docx', size: '2.8 MB', type: 'DOCX', status: 'indexed' },
  { name: 'contract_scan.pdf', size: '8.2 MB', type: 'PDF', status: 'error' },
]

const statusColors: Record<FileStatus, string> = {
  processing: 'bg-warning',
  indexed: 'bg-success',
  error: 'bg-error',
}

export default function UploadPage() {
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleDragOver = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e: DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }

  return (
    <div className="h-full flex flex-col">
      <header className="px-8 py-5 border-b border-card-border bg-white">
        <h1 className="text-2xl font-bold text-text-primary">Upload files</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Add documents to your company knowledge base
        </p>
      </header>

      <div className="flex-1 p-8 overflow-y-auto">
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-2xl p-12 text-center cursor-pointer transition-colors ${
            isDragging
              ? 'border-primary bg-primary/5'
              : 'border-card-border bg-card-bg hover:border-primary/40'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.txt,.md"
            className="hidden"
          />
          <CloudUpload size={40} className="mx-auto mb-4 text-text-secondary/50" />
          <p className="text-lg font-semibold text-text-primary mb-1">
            Drop files here or click to upload
          </p>
          <p className="text-sm text-text-secondary mb-5">
            PDF, DOCX, TXT, MD &middot; Max 25 MB per file
          </p>
          <button
            onClick={(e) => {
              e.stopPropagation()
              fileInputRef.current?.click()
            }}
            className="inline-flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary-hover text-white rounded-lg text-sm font-medium transition-colors"
          >
            <Upload size={14} />
            Browse files
          </button>
        </div>

        <div className="mt-10">
          <h2 className="text-lg font-bold text-text-primary mb-4">Recent uploads</h2>
          <div className="space-y-3">
            {mockUploads.map((file) => (
              <div
                key={file.name}
                className="flex items-center justify-between px-6 py-4 bg-card-bg border border-card-border rounded-xl"
              >
                <div>
                  <p className="text-sm font-semibold text-text-primary">{file.name}</p>
                  <p className="text-xs text-text-secondary mt-0.5">
                    {file.size} &middot; {file.type}
                  </p>
                </div>
                <span className={`w-14 h-6 rounded-full ${statusColors[file.status]}`} />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
