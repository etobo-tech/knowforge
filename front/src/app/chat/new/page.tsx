'use client'

import { useState } from 'react'
import { ArrowRight } from 'lucide-react'

const suggestions = [
  'Summarize our refund policy',
  'What does the onboarding guide say?',
  'Draft a customer support response',
  'Find contradictions across our docs',
]

export default function NewChatPage() {
  const [message, setMessage] = useState('')

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
                onClick={() => setMessage(suggestion)}
                className="w-full text-left px-5 py-3.5 bg-content-bg border border-card-border rounded-xl text-sm text-text-primary hover:border-primary/40 hover:bg-primary/5 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-3 px-5 py-3 bg-content-bg border border-card-border rounded-full">
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
      </div>
    </div>
  )
}
