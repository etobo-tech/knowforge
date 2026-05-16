'use client'

import Link from 'next/link'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { Loader2, Search, Upload } from 'lucide-react'

import { deleteDocument, documentDownloadHref, listDocuments, type DocumentResponse } from '@/lib/api'
import {
  documentStatusLabel,
  formatFileSize,
  formatShortDate,
  mapDocumentStatus,
  mimeToLabel,
  statusBadgeClasses,
  type FileStatus,
} from '@/lib/documents'

function rowUiStatus(status: string): FileStatus {
  return mapDocumentStatus(status)
}

export default function FilesPage() {
  const [documents, setDocuments] = useState<DocumentResponse[] | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [deletingId, setDeletingId] = useState<string | null>(null)

  const load = useCallback(() => {
    setLoadError(null)
    setDocuments(null)
    void listDocuments()
      .then(setDocuments)
      .catch(() =>
        setLoadError(
          'Could not load documents. Check that the API is running and try again.',
        ),
      )
  }, [])

  useEffect(() => {
    load()
  }, [load])

  const filtered = useMemo(() => {
    if (!documents) return []
    const q = query.trim().toLowerCase()
    if (!q) return documents
    return documents.filter((d) => d.filename.toLowerCase().includes(q))
  }, [documents, query])

  const handleDelete = useCallback(
    async (id: string, name: string) => {
      if (!window.confirm(`Delete “${name}”? This cannot be undone.`)) return
      setDeletingId(id)
      try {
        await deleteDocument(id)
        setDocuments((prev) =>
          prev ? prev.filter((d) => d.id !== id) : prev,
        )
      } catch {
        window.alert('Could not delete the file. Try again.')
      } finally {
        setDeletingId(null)
      }
    },
    [],
  )

  const loading = documents === null && !loadError

  return (
    <div className="h-full flex flex-col">
      <header className="px-8 py-5 border-b border-card-border bg-white">
        <h1 className="text-2xl font-bold text-text-primary">Knowledge Base</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Manage the documents used by the RAG system
        </p>
      </header>

      <div className="flex-1 p-8 overflow-y-auto">
        <div className="flex items-center gap-4 mb-6">
          <div className="flex-1 flex items-center gap-3 px-4 py-2.5 bg-card-bg border border-card-border rounded-xl">
            <Search size={16} className="text-text-secondary/50 shrink-0" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search files..."
              className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-secondary/50 outline-none"
            />
          </div>
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary hover:bg-primary-hover text-white rounded-xl text-sm font-medium transition-colors shrink-0"
          >
            <Upload size={14} />
            Upload files
          </Link>
        </div>

        {loadError ? (
          <div className="rounded-2xl border border-card-border bg-card-bg px-6 py-8 text-center">
            <p className="text-sm text-text-secondary mb-4">{loadError}</p>
            <button
              type="button"
              onClick={() => load()}
              className="rounded-lg bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary-hover"
            >
              Retry
            </button>
          </div>
        ) : null}

        {loading ? (
          <div className="flex flex-col items-center justify-center gap-3 py-24 text-text-secondary">
            <Loader2 className="h-8 w-8 animate-spin text-primary" aria-hidden />
            <p className="text-sm">Loading documents…</p>
          </div>
        ) : null}

        {!loading && !loadError && documents?.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-card-border bg-card-bg px-6 py-16 text-center">
            <p className="text-sm text-text-secondary mb-4">
              No documents yet. Upload files to populate the knowledge base.
            </p>
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
            >
              <Upload size={14} />
              Upload files
            </Link>
          </div>
        ) : null}

        {!loading && !loadError && documents && documents.length > 0 ? (
          <div className="bg-card-bg border border-card-border rounded-2xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-card-border">
                  <th className="text-left px-6 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                    Name
                  </th>
                  <th className="text-left px-4 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                    Type
                  </th>
                  <th className="text-left px-4 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                    Size
                  </th>
                  <th className="text-left px-4 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                    Status
                  </th>
                  <th className="text-left px-4 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                    Uploaded
                  </th>
                  <th className="text-center px-4 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                    Chunks
                  </th>
                  <th className="text-right px-6 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody>
                {filtered.length === 0 ? (
                  <tr>
                    <td
                      colSpan={7}
                      className="px-6 py-10 text-center text-sm text-text-secondary"
                    >
                      No files match your search.
                    </td>
                  </tr>
                ) : (
                  filtered.map((file) => {
                    const ui = rowUiStatus(file.status)
                    const busy = deletingId === file.id
                    return (
                      <tr
                        key={file.id}
                        className="border-b border-card-border last:border-b-0 hover:bg-content-bg/50 transition-colors"
                      >
                        <td className="px-6 py-4">
                          <span className="text-sm font-semibold text-text-primary">
                            {file.filename}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-sm text-text-secondary">
                          {mimeToLabel(file.mime_type)}
                        </td>
                        <td className="px-4 py-4 text-sm text-text-secondary">
                          {formatFileSize(file.size_bytes)}
                        </td>
                        <td className="px-4 py-4">
                          <span
                            className={`inline-flex h-5 w-[5.25rem] shrink-0 items-center justify-center truncate rounded-full px-1.5 text-[10px] font-semibold leading-none tracking-tight ${statusBadgeClasses[ui]}`}
                          >
                            {documentStatusLabel(file.status)}
                          </span>
                        </td>
                        <td className="px-4 py-4 text-sm text-text-secondary">
                          {formatShortDate(file.created_at)}
                        </td>
                        <td className="px-4 py-4 text-sm text-text-secondary text-center">
                          {file.chunks_count}
                        </td>
                        <td className="px-6 py-4 text-right">
                          {ui === 'error' ? (
                            <span className="text-sm text-text-secondary">
                              <a
                                href={documentDownloadHref(file.id)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-primary hover:underline"
                              >
                                Download
                              </a>
                              {' '}&middot;{' '}
                              <button
                                type="button"
                                disabled
                                className="text-text-secondary/50 cursor-not-allowed"
                                title="Reprocess is not available yet"
                              >
                                Reprocess
                              </button>
                              {' '}&middot;{' '}
                              <button
                                type="button"
                                disabled={busy}
                                onClick={() =>
                                  void handleDelete(file.id, file.filename)
                                }
                                className="text-error hover:underline disabled:opacity-50"
                              >
                                {busy ? 'Deleting…' : 'Delete'}
                              </button>
                            </span>
                          ) : (
                            <span className="text-sm text-text-secondary">
                              <a
                                href={documentDownloadHref(file.id)}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-primary hover:underline"
                              >
                                Download
                              </a>
                              {' '}&middot;{' '}
                              <button
                                type="button"
                                disabled={busy}
                                onClick={() => void handleDelete(file.id, file.filename)}
                                className="text-error hover:underline disabled:opacity-50"
                              >
                                {busy ? 'Deleting…' : 'Delete'}
                              </button>
                            </span>
                          )}
                        </td>
                      </tr>
                    )
                  })
                )}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>
    </div>
  )
}
