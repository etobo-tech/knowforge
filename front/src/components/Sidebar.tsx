'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useCallback, useEffect, useState } from 'react'
import { Plus, Settings, MessageSquare, FolderOpen, Upload } from 'lucide-react'

import { ThemeToggle } from '@/components/ThemeToggle'
import {
  CHATS_UPDATED_EVENT,
  getCachedChatList,
  listChats,
  type ChatSummaryResponse,
} from '@/lib/api'

const knowledgeBase = [
  { name: 'Files', href: '/files', icon: FolderOpen },
  { name: 'Upload files', href: '/upload', icon: Upload },
]

function chatHref(id: string) {
  return `/chat/${id}`
}

function isChatActive(pathname: string, chatId: string) {
  return pathname === chatHref(chatId)
}

export default function Sidebar() {
  const pathname = usePathname()
  const [chats, setChats] = useState<ChatSummaryResponse[]>([])
  const [isLoadingChats, setIsLoadingChats] = useState(true)
  const [chatsError, setChatsError] = useState(false)

  const loadChats = useCallback(async (force = false) => {
    setChatsError(false)

    if (!force) {
      const cached = getCachedChatList()
      if (cached) {
        setChats(cached)
        setIsLoadingChats(false)
        return
      }
    }

    setIsLoadingChats(true)
    try {
      const items = await listChats({ force: true })
      setChats(items)
    } catch {
      setChatsError(true)
    } finally {
      setIsLoadingChats(false)
    }
  }, [])

  useEffect(() => {
    void loadChats()
    const onChatsUpdated = () => {
      void loadChats(true)
    }
    window.addEventListener(CHATS_UPDATED_EVENT, onChatsUpdated)
    return () => window.removeEventListener(CHATS_UPDATED_EVENT, onChatsUpdated)
  }, [loadChats])

  return (
    <aside className="w-56 bg-sidebar-bg text-sidebar-text flex flex-col h-screen shrink-0">
      <div className="p-5 pb-4">
        <h1 className="text-xl font-bold text-white tracking-tight">Knowforge</h1>
      </div>

      <div className="px-4 mb-6">
        <Link
          href="/chat/new"
          className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-primary hover:bg-primary-hover text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Plus size={16} />
          New Chat
        </Link>
      </div>

      <nav className="flex-1 overflow-y-auto px-2">
        <div className="mb-6">
          <p className="px-3 mb-1.5 text-xs font-semibold uppercase tracking-wider text-sidebar-text/60">
            Chats
          </p>
          {isLoadingChats ? (
            <p className="px-3 py-2 text-xs text-sidebar-text/50">Loading…</p>
          ) : chatsError ? (
            <p className="px-3 py-2 text-xs text-sidebar-text/50">Could not load chats</p>
          ) : chats.length === 0 ? (
            <p className="px-3 py-2 text-xs text-sidebar-text/50">No chats yet</p>
          ) : (
            chats.map((chat) => {
              const href = chatHref(chat.id)
              const active = isChatActive(pathname, chat.id)
              return (
                <Link
                  key={chat.id}
                  href={href}
                  title={chat.title}
                  className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors min-w-0 ${
                    active
                      ? 'bg-sidebar-active text-white'
                      : 'hover:bg-sidebar-active/50 text-sidebar-text'
                  }`}
                >
                  <MessageSquare size={14} className="opacity-60 shrink-0" />
                  <span className="truncate">{chat.title}</span>
                </Link>
              )
            })
          )}
        </div>

        <div>
          <p className="px-3 mb-1.5 text-xs font-semibold uppercase tracking-wider text-sidebar-text/60">
            Knowledge Base
          </p>
          {knowledgeBase.map((item) => {
            const Icon = item.icon
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                  pathname === item.href
                    ? 'bg-sidebar-active text-white'
                    : 'hover:bg-sidebar-active/50 text-sidebar-text'
                }`}
              >
                <Icon size={14} className="opacity-60" />
                {item.name}
              </Link>
            )
          })}
        </div>
      </nav>

      <div className="space-y-1 border-t border-white/10 p-4">
        <ThemeToggle />
        <Link
          href="/settings"
          className="flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm text-sidebar-text transition-colors hover:bg-sidebar-active/50"
        >
          <Settings size={14} className="opacity-60" />
          Settings
        </Link>
      </div>
    </aside>
  )
}
