'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { ArrowRight, Loader2 } from 'lucide-react'

import {
  appendChatMessage,
  createChat,
  formatNewChatTitle,
  getChat,
  type ChatDetailResponse,
  type MessageResponse,
} from '@/lib/api'

const suggestions = [
  'Summarize our refund policy',
  'What does the onboarding guide say?',
  'Draft a customer support response',
  'Find contradictions across our docs',
]

type Props = {
  initialChatId?: string
}

function TypingBubble() {
  return (
    <div className="flex justify-start">
      <div
        className="max-w-[min(85%,28rem)] rounded-2xl rounded-bl-md border border-card-border bg-white px-4 py-3 shadow-sm"
        aria-label="Knowforge is typing"
      >
        <p className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-primary">
          Knowforge
        </p>
        <div className="flex items-center gap-1 py-0.5">
          <span className="h-2 w-2 rounded-full bg-text-secondary/45 animate-bounce [animation-delay:0ms]" />
          <span className="h-2 w-2 rounded-full bg-text-secondary/45 animate-bounce [animation-delay:150ms]" />
          <span className="h-2 w-2 rounded-full bg-text-secondary/45 animate-bounce [animation-delay:300ms]" />
        </div>
      </div>
    </div>
  )
}

function MessageBubble({ msg }: { msg: MessageResponse }) {
  const isUser = msg.role === 'user'

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-[min(85%,28rem)] ${
          isUser
            ? 'rounded-2xl rounded-br-md bg-primary px-4 py-3 text-sm leading-relaxed text-white shadow-sm'
            : 'rounded-2xl rounded-bl-md border border-card-border bg-white px-4 py-3 text-sm leading-relaxed text-text-primary shadow-sm'
        }`}
      >
        {!isUser ? (
          <p className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-primary">
            Knowforge
          </p>
        ) : null}
        <p className="whitespace-pre-wrap break-words">{msg.content}</p>
      </div>
    </div>
  )
}

export function ChatView({ initialChatId }: Props) {
  const [chatId, setChatId] = useState<string | null>(initialChatId ?? null)
  const [title, setTitle] = useState('New chat')
  const [messages, setMessages] = useState<MessageResponse[]>([])
  const [message, setMessage] = useState('')
  const [isSending, setIsSending] = useState(false)
  const [isAwaitingReply, setIsAwaitingReply] = useState(false)
  const [isLoading, setIsLoading] = useState(Boolean(initialChatId))
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const hasConversation = messages.length > 0 || isAwaitingReply

  const applyChat = useCallback((chat: ChatDetailResponse) => {
    setChatId(chat.id)
    setTitle(chat.title)
    setMessages(chat.messages)
  }, [])

  useEffect(() => {
    if (!initialChatId) return
    let cancelled = false
    setIsLoading(true)
    setError(null)
    void getChat(initialChatId)
      .then((chat) => {
        if (cancelled) return
        if (!chat) {
          setError('Chat not found.')
          return
        }
        applyChat(chat)
      })
      .catch(() => {
        if (!cancelled) {
          setError('Could not load this chat. Check that the API is running.')
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [initialChatId, applyChat])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isAwaitingReply])

  const handleSend = useCallback(async () => {
    const content = message.trim()
    if (!content || isSending) return

    const optimisticId = `pending-${crypto.randomUUID()}`
    const optimisticUser: MessageResponse = {
      id: optimisticId,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
      sources: [],
    }

    setMessages((prev) => [...prev, optimisticUser])
    setMessage('')
    setIsSending(true)
    setIsAwaitingReply(true)
    setError(null)

    try {
      let activeChatId = chatId
      if (!activeChatId) {
        const created = await createChat(formatNewChatTitle())
        activeChatId = created.id
        setChatId(created.id)
        setTitle(created.title)
        window.history.replaceState(null, '', `/chat/${created.id}`)
      }
      const updated = await appendChatMessage(activeChatId, content)
      applyChat(updated)
    } catch {
      setMessages((prev) => prev.filter((m) => m.id !== optimisticId))
      setMessage(content)
      setError('Could not send your message. Check that the API is running and try again.')
    } finally {
      setIsSending(false)
      setIsAwaitingReply(false)
    }
  }, [message, isSending, chatId, applyChat])

  const composer = (
    <div className="flex items-center gap-3 px-5 py-3 bg-content-bg border border-card-border rounded-full">
      <input
        type="text"
        value={message}
        disabled={isSending || isLoading}
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
        disabled={isSending || isLoading || !message.trim()}
        onClick={() => void handleSend()}
        className="w-9 h-9 flex items-center justify-center bg-primary hover:bg-primary-hover text-white rounded-full transition-colors shrink-0 disabled:opacity-50"
        aria-label="Send message"
      >
        <ArrowRight size={16} />
      </button>
    </div>
  )

  return (
    <div className="h-full flex flex-col">
      <header className="px-8 py-5 border-b border-card-border bg-white shrink-0">
        <h1 className="text-2xl font-bold text-text-primary truncate">{title}</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Ask questions grounded in your company documents
        </p>
      </header>

      {error ? (
        <p className="px-8 py-3 text-sm text-error bg-error/5 border-b border-error/20">
          {error}
        </p>
      ) : null}

      {isLoading ? (
        <div className="flex-1 flex items-center justify-center text-text-secondary">
          <Loader2 className="h-8 w-8 animate-spin text-primary" aria-hidden />
        </div>
      ) : !hasConversation ? (
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

            {composer}
          </div>
        </div>
      ) : (
        <div className="flex-1 flex flex-col min-h-0 p-8">
          <div className="flex-1 overflow-y-auto mb-6">
            <div className="max-w-3xl mx-auto space-y-4 px-1">
              {messages.map((msg) => (
                <MessageBubble key={msg.id} msg={msg} />
              ))}
              {isAwaitingReply ? <TypingBubble /> : null}
              <div ref={messagesEndRef} />
            </div>
          </div>
          <div className="max-w-3xl mx-auto w-full shrink-0">{composer}</div>
        </div>
      )}
    </div>
  )
}
