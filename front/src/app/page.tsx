import Link from 'next/link'
import { Upload } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="h-full flex flex-col">
      <header className="px-8 py-5 border-b border-card-border bg-card-bg">
        <h1 className="text-2xl font-bold text-text-primary">Welcome to Knowforge</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Build a searchable knowledge base from company documents
        </p>
      </header>

      <div className="flex-1 flex items-center justify-center p-8">
        <div className="bg-card-bg rounded-2xl border border-card-border p-12 max-w-xl w-full text-center">
          <h2 className="text-3xl font-bold text-text-primary mb-4">
            Build your first knowledge base
          </h2>
          <p className="text-text-secondary mb-8 leading-relaxed">
            Upload company documents and turn them into an AI knowledge
            base you can search, query, and reuse across chats.
          </p>

          <Link
            href="/upload"
            className="inline-flex items-center gap-2 px-8 py-3.5 bg-primary hover:bg-primary-hover text-white rounded-full text-base font-medium transition-colors"
          >
            <Upload size={18} />
            Upload your first files
          </Link>

          <div className="mt-6">
            <span className="inline-block px-6 py-2.5 bg-primary/5 text-primary/70 rounded-full text-sm">
              Recommended: PDF, DOCX, TXT, MD files
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
