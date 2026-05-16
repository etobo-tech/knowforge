/** User-facing upload errors (no stack traces or ORM internals). */

const MSG_GENERIC =
  "We couldn't upload this file. Try again, or use a different export if the problem continues."

const MSG_INVALID_CONTENT =
  'This document could not be processed because it contains invalid or unsupported content. Try saving a new copy or exporting to PDF.'

const MSG_TOO_LARGE =
  'This file is larger than the maximum size allowed.'

const MSG_UNSUPPORTED =
  "This file type isn't supported."

const MSG_NETWORK =
  "We couldn't reach the server. Check your connection and try again."

function looksLikeInternalOrStackTrace(text: string): boolean {
  const lower = text.toLowerCase()
  if (text.length > 240) return true
  return (
    /sqlalchemy|psycopg|traceback|session\.rollback|rolled back|original exception|internal server|mod_wsgi|uvicorn\.error|file "[/\\]|line \d+|https?:\/\//i.test(
      text,
    ) ||
    (lower.includes('exception') && lower.includes('flush')) ||
    (lower.includes('session') && lower.includes('transaction'))
  )
}

/**
 * Maps API/network/ORM errors to short, safe copy for the UI.
 * Never forwards raw server tracebacks.
 */
export function toPublicUploadErrorMessage(raw: unknown): string {
  const text =
    typeof raw === 'string'
      ? raw.trim()
      : raw instanceof Error
        ? raw.message.trim()
        : ''

  if (!text) return MSG_GENERIC

  const lower = text.toLowerCase()

  if (
    text.includes('\0') ||
    /nul|0x00|cannot contain nul/i.test(text)
  ) {
    return MSG_INVALID_CONTENT
  }

  if (
    /(^|\s)413(\s|$)|payload too large|request entity too large|content too large|upload failed \(413\)/i.test(
      lower,
    )
  ) {
    return MSG_TOO_LARGE
  }

  if (/(^|\s)415(\s|$)|unsupported media|mime type not allowed|upload failed \(415\)/i.test(lower)) {
    return MSG_UNSUPPORTED
  }

  if (
    /failed to fetch|networkerror|load failed|connection refused|network request failed|upload failed \(0\)/i.test(
      lower,
    )
  ) {
    return MSG_NETWORK
  }

  if (looksLikeInternalOrStackTrace(text)) {
    return MSG_GENERIC
  }

  return MSG_GENERIC
}
