'use client'

import { useRouter } from 'next/navigation'
import { useCallback, useState } from 'react'
import { ArrowRight, Loader2 } from 'lucide-react'

import {
  appendChatMessage,
  createChat,
  formatNewChatTitle,
} from '@/lib/api'

const suggestions = [
  'Summarize our refund policy',
  'What does the onboarding guide say?',
  'Draft a customer support response',
  'Find contradictions across our docs',
]

export default function NewChatPage() {
  const router = useRouter()
  const [message, setMessage] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSend = useCallback(async () => {
    const content = message.trim()
    if (!content || isSending) return

    setIsSending(true)
    setError(null)
    try {
      const chat = await createChat(formatNewChatTitle())
      await appendChatMessage(chat.id, content)
      router.push(`/chat/${chat.id}`)
    } catch {
      setError('Could not start the chat. Check that the API is running and try again.')
    } finally {
      setIsSending(false)
    }
  }, [message, isSending, router])

  return (
    <div className="h-full flex flex-col">
      <header className="px-8 py-5 border-b border-card-border bg-white">
        <h1 className="text-2xl font-bold text-text-primary">New chat</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Start a conversation with your company knowledge base
        </p>
      </header>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="bg-card-bg rounded-2xl border border-card-border p-12 max-w-2xl w-full">
          <h2 className="text-3xl font-bold text-text-primary text-center mb-3">
            Ask your knowledge base anything
          </h2>
          <p className="text-text-secondary text-center mb-10">
            Use your uploaded documents as the source of truth.
          </p>

          <div className="space-y-3 mb-10">
            {suggestions.map((suggestion) => (
              <button
                key={suggestion}
                type="button"
                disabled={isSending}
                onClick={() => setMessage(suggestion)}
                className="w-full text-left px-5 py-3.5 bg-content-bg border border-card-border rounded-xl text-sm text-text-primary hover:border-primary/40 hover:bg-primary/5 transition-colors disabled:opacity-50"
              >
                {suggestion}
              </button>
            ))}
          </div>

          {error ? (
            <p className="mb-4 text-center text-sm text-error">{error}</p>
          ) : null}

          <div className="flex items-center gap-3 px-5 py-3 bg-content-bg border border-card-border rounded-full">
            <input
              type="text"
              value={message}
              disabled={isSending}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  void handleSend()
                }
              }}
              placeholder="Ask anything about your documents..."
              className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-secondary/60 outline-none disabled:opacity-50"
            />
            <button
              type="button"
              disabled={isSending || !message.trim()}
              onClick={() => void handleSend()}
              className="w-9 h-9 flex items-center justify-center bg-primary hover:bg-primary-hover text-white rounded-full transition-colors shrink-0 disabled:opacity-50"
            >
              {isSending ? (
                <Loader2 size={16} className="animate-spin" aria-hidden />
              ) : (
                <ArrowRight size={16} />
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
