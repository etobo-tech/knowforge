'use client'

import { useState } from 'react'
import { ArrowRight } from 'lucide-react'

const mockConversation = {
  title: 'Refund policy questions',
  messages: [
    {
      role: 'user' as const,
      content: 'What is our refund policy for international orders?',
    },
    {
      role: 'assistant' as const,
      content:
        'Based on your documents, international customers can request a refund within 30 days if the product is unused and includes the original receipt.',
      suggestedReply:
        'Hi, thanks for reaching out. According to our refund policy, you can request a refund within 30 days of purchase as long as the product is unused and you have the original receipt.',
      sources: [
        { name: 'refund_policy.pdf', detail: 'page 2' },
        { name: 'support_faq.docx', detail: 'Returns' },
      ],
    },
  ],
  contextSources: [
    { name: 'refund_policy.pdf', type: 'PDF', chunks: 42 },
    { name: 'support_faq.docx', type: 'DOCX', chunks: 18 },
  ],
  confidence: 78,
  groundedSections: 2,
}

export default function ChatPage() {
  const [message, setMessage] = useState('')

  return (
    <div className="h-full flex flex-col">
      <header className="px-8 py-5 border-b border-card-border bg-white">
        <h1 className="text-2xl font-bold text-text-primary">
          Chat: {mockConversation.title}
        </h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Ask questions grounded in your company documents
        </p>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col p-8 overflow-y-auto">
          <div className="bg-card-bg rounded-2xl border border-card-border p-8 mb-auto">
            {mockConversation.messages.map((msg, i) => (
              <div key={i} className="mb-8 last:mb-0">
                <p className={`text-xs font-semibold uppercase tracking-wider mb-2 ${
                  msg.role === 'user' ? 'text-text-primary' : 'text-primary'
                }`}>
                  {msg.role === 'user' ? 'User' : 'Knowforge'}
                </p>
                <div className="bg-content-bg rounded-xl px-5 py-4 text-sm leading-relaxed text-text-primary">
                  {msg.content}
                </div>
                {msg.role === 'assistant' && msg.suggestedReply && (
                  <div className="mt-4">
                    <p className="text-sm font-semibold text-text-primary mb-2">Suggested reply</p>
                    <div className="bg-content-bg rounded-xl px-5 py-4 text-sm leading-relaxed text-text-secondary">
                      {msg.suggestedReply}
                    </div>
                  </div>
                )}
              </div>
            ))}

            <div className="mt-8 pt-6 border-t border-card-border">
              <p className="text-sm font-semibold text-text-primary mb-3">Sources</p>
              <div className="flex flex-wrap gap-3">
                {mockConversation.messages
                  .filter((m) => m.role === 'assistant')
                  .flatMap((m) => m.sources || [])
                  .map((source, i) => (
                    <span
                      key={i}
                      className="px-4 py-2 bg-content-bg border border-card-border rounded-lg text-sm text-text-secondary"
                    >
                      {source.name} &middot; {source.detail}
                    </span>
                  ))}
              </div>
            </div>
          </div>

          <div className="mt-6 flex items-center gap-3 px-5 py-3 bg-card-bg border border-card-border rounded-full">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask anything about your documents..."
              className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-secondary/60 outline-none"
            />
            <button className="w-9 h-9 flex items-center justify-center bg-primary hover:bg-primary-hover text-white rounded-full transition-colors shrink-0">
              <ArrowRight size={16} />
            </button>
          </div>
        </div>

        <aside className="w-72 border-l border-card-border bg-white p-6 overflow-y-auto shrink-0">
          <h3 className="text-lg font-bold text-text-primary mb-1">Sources / Context</h3>
          <p className="text-xs text-text-secondary mb-5">Used sources</p>

          <div className="space-y-3 mb-8">
            {mockConversation.contextSources.map((source) => (
              <div
                key={source.name}
                className="px-4 py-3 bg-content-bg border border-card-border rounded-xl"
              >
                <p className="text-sm font-semibold text-text-primary">{source.name}</p>
                <p className="text-xs text-text-secondary mt-0.5">
                  {source.type} &middot; Indexed &middot; {source.chunks} chunks
                </p>
              </div>
            ))}
          </div>

          <div>
            <h4 className="text-sm font-semibold text-text-primary mb-3">Answer confidence</h4>
            <div className="w-full h-2.5 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-success rounded-full transition-all"
                style={{ width: `${mockConversation.confidence}%` }}
              />
            </div>
            <p className="text-xs text-text-secondary mt-2">
              Grounded in {mockConversation.groundedSections} document sections
            </p>
          </div>
        </aside>
      </div>
    </div>
  )
}
