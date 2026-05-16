import { useCallback, useEffect, useRef, useState } from 'react'

import { uploadDocument } from '@/lib/api'
import {
  documentToUploadedFile,
  pendingRowFromLocalFile,
  type UploadedFile,
} from '@/lib/documents'
import { sha256HexFromFile } from '@/lib/fileHash'
import { toPublicUploadErrorMessage } from '@/lib/uploadErrors'
import {
  uploadSessionRowsFromStaged,
  type StagedFile,
  type UploadSessionRow,
} from '@/lib/uploadQueue'

const NOTICE_MS = 6000

/** Max parallel document uploads per batch */
const UPLOAD_CONCURRENCY = 5

const MSG_DUPLICATE_STAGED =
  'This file is already in the upload queue. It was not added again.'

const MSG_ALREADY_IN_KB =
  'This file is already in your knowledge base (same content). It was not added to the queue.'

type UploadOneFileResult =
  | { kind: 'uploaded'; created: boolean }
  | { kind: 'skipped_duplicate_in_list' }
  | { kind: 'error'; message: string }

function dedupeRowsById(rows: UploadedFile[]): UploadedFile[] {
  const seen = new Set<string>()
  return rows.filter((row) => {
    if (seen.has(row.id)) return false
    seen.add(row.id)
    return true
  })
}

function dedupeRowsByContentHash(rows: UploadedFile[]): UploadedFile[] {
  const seen = new Set<string>()
  return rows.filter((row) => {
    const h = row.content_hash
    if (!h) return true
    if (seen.has(h)) return false
    seen.add(h)
    return true
  })
}

export function useDocumentUpload() {
  const [stagedFiles, setStagedFiles] = useState<StagedFile[]>([])
  const [uploadSessionRows, setUploadSessionRows] = useState<UploadSessionRow[]>(
    [],
  )
  const [uploads, setUploads] = useState<UploadedFile[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadNotice, setUploadNotice] = useState<string | null>(null)

  const uploadsRef = useRef(uploads)
  uploadsRef.current = uploads

  useEffect(() => {
    if (!uploadNotice) return
    const t = window.setTimeout(() => setUploadNotice(null), NOTICE_MS)
    return () => window.clearTimeout(t)
  }, [uploadNotice])

  const prevStagedLenRef = useRef(0)

  useEffect(() => {
    const len = stagedFiles.length
    if (len > 0 && prevStagedLenRef.current === 0) {
      setUploadSessionRows([])
    }
    prevStagedLenRef.current = len
  }, [stagedFiles])

  const dismissUploadSession = useCallback(() => {
    setUploadSessionRows([])
  }, [])

  const addStagedFiles = useCallback(async (files: File[]) => {
    for (const file of files) {
      const contentHash = await sha256HexFromFile(file)
      setStagedFiles((prev) => {
        if (uploadsRef.current.some((r) => r.content_hash === contentHash)) {
          setUploadNotice(MSG_ALREADY_IN_KB)
          return prev
        }
        if (prev.some((s) => s.contentHash === contentHash)) {
          setUploadNotice(MSG_DUPLICATE_STAGED)
          return prev
        }
        return [...prev, { id: crypto.randomUUID(), file, contentHash }]
      })
    }
  }, [])

  const removeStaged = useCallback((id: string) => {
    setStagedFiles((prev) => prev.filter((s) => s.id !== id))
  }, [])

  const clearStaged = useCallback(() => {
    setStagedFiles([])
  }, [])

  const uploadOneFile = useCallback(
    async (file: File): Promise<UploadOneFileResult> => {
      const contentHash = await sha256HexFromFile(file)
      const pendingId = crypto.randomUUID()

      const skipRef = { current: false }
      setUploads((prev) => {
        if (prev.some((r) => r.content_hash === contentHash)) {
          skipRef.current = true
          return prev
        }
        skipRef.current = false
        return [pendingRowFromLocalFile(file, pendingId, contentHash), ...prev]
      })

      if (skipRef.current) {
        return { kind: 'skipped_duplicate_in_list' }
      }

      try {
        const { document, created } = await uploadDocument(file)
        const done = documentToUploadedFile(document)
        setUploads((prev) => {
          const replaced = prev.map((row) =>
            row.id === pendingId ? done : row,
          )
          return dedupeRowsByContentHash(dedupeRowsById(replaced))
        })
        return { kind: 'uploaded', created }
      } catch (err) {
        const message = toPublicUploadErrorMessage(err)
        setUploads((prev) =>
          prev.map((row) =>
            row.id === pendingId
              ? { ...row, status: 'error', error: message }
              : row,
          ),
        )
        return { kind: 'error', message }
      }
    },
    [],
  )

  const commitStaged = useCallback(async () => {
    const snapshot = [...stagedFiles]
    if (snapshot.length === 0) return

    const initialRows = uploadSessionRowsFromStaged(snapshot)
    setStagedFiles([])
    setUploadSessionRows(initialRows)
    setIsUploading(true)

    const applyResult = (
      rowId: string,
      result: UploadOneFileResult,
    ): void => {
      setUploadSessionRows((prev) =>
        prev.map((r) => {
          if (r.id !== rowId) return r
          if (result.kind === 'uploaded') {
            return {
              ...r,
              phase: 'done',
              alreadyInDb: !result.created,
              duplicateInList: undefined,
            }
          }
          if (result.kind === 'skipped_duplicate_in_list') {
            return {
              ...r,
              phase: 'done',
              duplicateInList: true,
              alreadyInDb: undefined,
            }
          }
          return {
            ...r,
            phase: 'error',
            errorMessage: result.message,
          }
        }),
      )
    }

    try {
      let nextIndex = 0
      const workerCount = Math.min(UPLOAD_CONCURRENCY, snapshot.length)
      const workers = Array.from({ length: workerCount }, async () => {
        while (true) {
          const i = nextIndex++
          if (i >= snapshot.length) return
          const s = snapshot[i]!
          setUploadSessionRows((prev) =>
            prev.map((r) =>
              r.id === s.id ? { ...r, phase: 'uploading' } : r,
            ),
          )
          const result = await uploadOneFile(s.file)
          applyResult(s.id, result)
        }
      })
      await Promise.all(workers)
    } finally {
      setIsUploading(false)
    }
  }, [stagedFiles, uploadOneFile])

  return {
    stagedFiles,
    uploadSessionRows,
    isUploading,
    uploadNotice,
    addStagedFiles,
    removeStaged,
    clearStaged,
    commitStaged,
    dismissUploadSession,
  }
}
