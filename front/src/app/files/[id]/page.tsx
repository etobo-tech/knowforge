import Link from 'next/link'
import { ArrowLeft } from 'lucide-react'

const mockFile = {
  name: 'refund_policy.pdf',
  status: 'indexed' as const,
  type: 'PDF',
  size: '1.4 MB',
  uploaded: 'May 14, 2026',
  chunks: 42,
  lastIndexed: 'May 14, 2026 · 2:45 PM',
  extractedText:
    'Customers may request a refund within 30 days of purchase. The product must be unused, include the original receipt, and be returned in its original packaging. International orders may require additional verification before approval.',
  detectedSections: [
    'Refund eligibility',
    'International orders',
    'Required receipt',
    'Packaging rules',
  ],
}

export default async function FileDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  await params

  return (
    <div className="h-full flex flex-col">
      <header className="px-8 py-5 border-b border-card-border bg-white">
        <Link
          href="/files"
          className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-primary mb-2 transition-colors"
        >
          <ArrowLeft size={14} />
          Back to files
        </Link>
        <h1 className="text-2xl font-bold text-text-primary">{mockFile.name}</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Review processing status, metadata and extracted text
        </p>
      </header>

      <div className="flex-1 p-8 overflow-y-auto">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-card-bg border border-card-border rounded-2xl p-8">
            <h2 className="text-xl font-bold text-text-primary mb-6">File metadata</h2>

            <dl className="space-y-4">
              <div className="flex items-center justify-between">
                <dt className="text-sm text-text-secondary">Status</dt>
                <dd>
                  <span className="inline-block w-14 h-5 rounded-full bg-success" />
                </dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-sm text-text-secondary">Type</dt>
                <dd className="text-sm font-medium text-text-primary">{mockFile.type}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-sm text-text-secondary">Size</dt>
                <dd className="text-sm font-medium text-text-primary">{mockFile.size}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-sm text-text-secondary">Uploaded</dt>
                <dd className="text-sm font-medium text-text-primary">{mockFile.uploaded}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-sm text-text-secondary">Chunks</dt>
                <dd className="text-sm font-medium text-text-primary">{mockFile.chunks}</dd>
              </div>
              <div className="flex items-center justify-between">
                <dt className="text-sm text-text-secondary">Last indexed</dt>
                <dd className="text-sm font-medium text-text-primary">{mockFile.lastIndexed}</dd>
              </div>
            </dl>

            <div className="flex gap-3 mt-8">
              <button className="px-6 py-2.5 bg-primary hover:bg-primary-hover text-white rounded-lg text-sm font-medium transition-colors">
                Reprocess
              </button>
              <button className="px-6 py-2.5 bg-transparent border border-error/30 text-error hover:bg-error/5 rounded-lg text-sm font-medium transition-colors">
                Delete file
              </button>
            </div>
          </div>

          <div className="bg-card-bg border border-card-border rounded-2xl p-8">
            <h2 className="text-xl font-bold text-text-primary mb-6">Extracted text preview</h2>
            <p className="text-sm text-text-secondary leading-relaxed mb-8">
              {mockFile.extractedText}
            </p>

            <h3 className="text-base font-semibold text-text-primary mb-4">Detected sections</h3>
            <div className="space-y-2.5">
              {mockFile.detectedSections.map((section) => (
                <div
                  key={section}
                  className="px-4 py-3 bg-content-bg border border-card-border rounded-xl text-sm text-text-primary"
                >
                  {section}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
