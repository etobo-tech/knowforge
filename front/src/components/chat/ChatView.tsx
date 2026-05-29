'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { ArrowRight, Check, Loader2, Pencil, Trash2, X } from 'lucide-react'

import {
  appendChatMessage,
  createChat,
  deleteChatMessage,
  formatNewChatTitle,
  getCachedChat,
  getChat,
  notifyChatsUpdated,
  truncateMessagesForEdit,
  updateChatMessage,
  type ChatDetailResponse,
  type MessageResponse,
} from '@/lib/api'
import { setCachedChat } from '@/lib/chatCache'

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

function MessageBubble({
  msg,
  isEditing,
  editDraft,
  actionsDisabled,
  onEditStart,
  onEditDraftChange,
  onEditSave,
  onEditCancel,
  onDelete,
  isDeleting,
  isSavingEdit,
}: {
  msg: MessageResponse
  isEditing?: boolean
  editDraft?: string
  actionsDisabled?: boolean
  onEditStart?: (messageId: string, content: string) => void
  onEditDraftChange?: (value: string) => void
  onEditSave?: () => void
  onEditCancel?: () => void
  onDelete?: (messageId: string) => void
  isDeleting?: boolean
  isSavingEdit?: boolean
}) {
  const isUser = msg.role === 'user'
  const canAct =
    isUser && !msg.id.startsWith('pending-') && !actionsDisabled && onDelete && onEditStart

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`group flex max-w-[min(85%,28rem)] flex-col ${
          isUser ? 'items-end' : 'items-start'
        }`}
      >
        <div
          className={
            isUser
              ? 'w-full rounded-2xl rounded-br-md bg-primary px-4 py-3 text-sm leading-relaxed text-white shadow-sm'
              : 'rounded-2xl rounded-bl-md border border-card-border bg-white px-4 py-3 text-sm leading-relaxed text-text-primary shadow-sm'
          }
        >
          {!isUser ? (
            <p className="mb-1 text-[10px] font-semibold uppercase tracking-wider text-primary">
              Knowforge
            </p>
          ) : null}
          {isEditing ? (
            <textarea
              value={editDraft}
              onChange={(e) => onEditDraftChange?.(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Escape') {
                  e.preventDefault()
                  onEditCancel?.()
                }
              }}
              disabled={isSavingEdit}
              autoFocus
              rows={Math.min(8, Math.max(2, (editDraft ?? '').split('\n').length))}
              className="w-full min-h-[2.5rem] resize-y bg-white/10 text-white placeholder:text-white/60 outline-none disabled:opacity-50"
              aria-label="Edit message"
            />
          ) : (
            <p className="whitespace-pre-wrap break-words">{msg.content}</p>
          )}
        </div>
        {canAct || isEditing ? (
          <div
            className={`mt-1 flex items-center gap-1 ${
              isEditing ? 'opacity-100' : 'opacity-0 transition-opacity group-hover:opacity-100'
            }`}
          >
            {isEditing ? (
              <>
                <button
                  type="button"
                  onClick={() => onEditSave?.()}
                  disabled={isSavingEdit || !editDraft?.trim()}
                  className="flex items-center justify-center p-1 text-text-secondary hover:text-primary disabled:opacity-50"
                  aria-label="Save message"
                >
                  {isSavingEdit ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Check size={14} />
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => onEditCancel?.()}
                  disabled={isSavingEdit}
                  className="flex items-center justify-center p-1 text-text-secondary hover:text-primary disabled:opacity-50"
                  aria-label="Cancel edit"
                >
                  <X size={14} />
                </button>
              </>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => onEditStart?.(msg.id, msg.content)}
                  disabled={isDeleting}
                  className="flex items-center justify-center p-1 text-text-secondary hover:text-primary disabled:opacity-50"
                  aria-label="Edit message"
                >
                  <Pencil size={14} />
                </button>
                <button
                  type="button"
                  onClick={() => onDelete?.(msg.id)}
                  disabled={isDeleting}
                  className="flex items-center justify-center p-1 text-text-secondary hover:text-primary disabled:opacity-50"
                  aria-label="Delete message"
                >
                  {isDeleting ? (
                    <Loader2 size={14} className="animate-spin" />
                  ) : (
                    <Trash2 size={14} />
                  )}
                </button>
              </>
            )}
          </div>
        ) : null}
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
  const [deletingMessageId, setDeletingMessageId] = useState<string | null>(null)
  const [editingMessageId, setEditingMessageId] = useState<string | null>(null)
  const [editDraft, setEditDraft] = useState('')
  const [isSavingEdit, setIsSavingEdit] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const hasConversation = messages.length > 0 || isAwaitingReply
  const messageActionsBusy =
    isSending || isAwaitingReply || isSavingEdit || Boolean(deletingMessageId)

  const applyChat = useCallback((chat: ChatDetailResponse) => {
    setChatId(chat.id)
    setTitle(chat.title)
    setMessages(chat.messages)
  }, [])

  useEffect(() => {
    if (!initialChatId) return

    const cached = getCachedChat(initialChatId)
    if (cached) {
      applyChat(cached)
      setIsLoading(false)
      setError(null)
      return
    }

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
    if (!content || isSending || editingMessageId) return

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
      notifyChatsUpdated()
    } catch {
      setMessages((prev) => prev.filter((m) => m.id !== optimisticId))
      setMessage(content)
      setError('Could not send your message. Check that the API is running and try again.')
    } finally {
      setIsSending(false)
      setIsAwaitingReply(false)
    }
  }, [message, isSending, chatId, editingMessageId, applyChat])

  const handleDeleteMessage = useCallback(
    async (messageId: string) => {
      if (!chatId || deletingMessageId || messageActionsBusy || editingMessageId) return

      setDeletingMessageId(messageId)
      setError(null)

      try {
        await deleteChatMessage(chatId, messageId)
        const updated = await getChat(chatId, { force: true })
        if (updated) {
          applyChat(updated)
        }
        notifyChatsUpdated()
      } catch {
        setError('Could not delete the message. Try again.')
      } finally {
        setDeletingMessageId(null)
      }
    },
    [chatId, deletingMessageId, messageActionsBusy, editingMessageId, applyChat],
  )

  const handleStartEdit = useCallback(
    (messageId: string, content: string) => {
      if (messageActionsBusy || editingMessageId) return
      setEditingMessageId(messageId)
      setEditDraft(content)
      setError(null)
    },
    [messageActionsBusy, editingMessageId],
  )

  const handleCancelEdit = useCallback(() => {
    if (isSavingEdit) return
    setEditingMessageId(null)
    setEditDraft('')
  }, [isSavingEdit])

  const handleSaveEdit = useCallback(async () => {
    const content = editDraft.trim()
    if (!chatId || !editingMessageId || !content || isSavingEdit) return

    const messageId = editingMessageId
    const previousMessages = messages

    setIsSavingEdit(true)
    setIsAwaitingReply(true)
    setError(null)
    setEditingMessageId(null)
    setEditDraft('')

    const truncated = truncateMessagesForEdit(previousMessages, messageId, content)
    setMessages(truncated)
    const cached = getCachedChat(chatId)
    if (cached) {
      setCachedChat({ ...cached, messages: truncated })
    }

    try {
      const updated = await updateChatMessage(chatId, messageId, content)
      applyChat(updated)
      notifyChatsUpdated()
    } catch {
      setMessages(previousMessages)
      if (cached) {
        setCachedChat({ ...cached, messages: previousMessages })
      }
      setEditingMessageId(messageId)
      setEditDraft(content)
      setError('Could not save the message. Try again.')
    } finally {
      setIsSavingEdit(false)
      setIsAwaitingReply(false)
    }
  }, [chatId, editingMessageId, editDraft, isSavingEdit, messages, applyChat])

  const composer = (
    <div className="flex items-center gap-3 px-5 py-3 bg-content-bg border border-card-border rounded-full">
      <input
        type="text"
        value={message}
        disabled={isSending || isLoading || isSavingEdit || Boolean(editingMessageId)}
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
        disabled={
          isSending || isLoading || isSavingEdit || Boolean(editingMessageId) || !message.trim()
        }
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
                <MessageBubble
                  key={msg.id}
                  msg={msg}
                  isEditing={editingMessageId === msg.id}
                  editDraft={editingMessageId === msg.id ? editDraft : undefined}
                  actionsDisabled={messageActionsBusy || Boolean(editingMessageId)}
                  onEditStart={handleStartEdit}
                  onEditDraftChange={setEditDraft}
                  onEditSave={() => void handleSaveEdit()}
                  onEditCancel={handleCancelEdit}
                  onDelete={handleDeleteMessage}
                  isDeleting={deletingMessageId === msg.id}
                  isSavingEdit={isSavingEdit && editingMessageId === msg.id}
                />
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
