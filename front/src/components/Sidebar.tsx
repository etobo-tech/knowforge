'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { Plus, Settings, MessageSquare, FolderOpen, Upload } from 'lucide-react'

const chats = [
  { name: 'Support questions', href: '/chat/support-questions' },
  { name: 'Sales FAQ', href: '/chat/sales-faq' },
  { name: 'Product docs', href: '/chat/product-docs' },
  { name: 'Onboarding', href: '/chat/onboarding' },
]

const knowledgeBase = [
  { name: 'Files', href: '/files', icon: FolderOpen },
  { name: 'Upload files', href: '/upload', icon: Upload },
]

export default function Sidebar() {
  const pathname = usePathname()

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
          {chats.map((chat) => (
            <Link
              key={chat.href}
              href={chat.href}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                pathname === chat.href
                  ? 'bg-sidebar-active text-white'
                  : 'hover:bg-sidebar-active/50 text-sidebar-text'
              }`}
            >
              <MessageSquare size={14} className="opacity-60" />
              {chat.name}
            </Link>
          ))}
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

      <div className="p-4 border-t border-white/10">
        <Link
          href="/settings"
          className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm text-sidebar-text hover:bg-sidebar-active/50 transition-colors"
        >
          <Settings size={14} className="opacity-60" />
          Settings
        </Link>
      </div>
    </aside>
  )
}
