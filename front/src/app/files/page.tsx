import Link from 'next/link'
import { Search, Upload } from 'lucide-react'

type FileStatus = 'indexed' | 'error'

interface KBFile {
  id: string
  name: string
  type: string
  size: string
  status: FileStatus
  uploaded: string
  chunks: number
}

const mockFiles: KBFile[] = [
  { id: '1', name: 'refund_policy.pdf', type: 'PDF', size: '1.4 MB', status: 'indexed', uploaded: 'May 14', chunks: 42 },
  { id: '2', name: 'support_faq.docx', type: 'DOCX', size: '900 KB', status: 'indexed', uploaded: 'May 14', chunks: 18 },
  { id: '3', name: 'old_prices.xlsx', type: 'XLSX', size: '2.1 MB', status: 'error', uploaded: 'May 13', chunks: 0 },
  { id: '4', name: 'onboarding.md', type: 'MD', size: '320 KB', status: 'indexed', uploaded: 'May 12', chunks: 9 },
]

const statusBadge: Record<FileStatus, string> = {
  indexed: 'bg-success',
  error: 'bg-error',
}

export default function FilesPage() {
  return (
    <div className="h-full flex flex-col">
      <header className="px-8 py-5 border-b border-card-border bg-white">
        <h1 className="text-2xl font-bold text-text-primary">Knowledge Base</h1>
        <p className="text-sm text-text-secondary mt-0.5">
          Manage the documents used by the RAG system
        </p>
      </header>

      <div className="flex-1 p-8 overflow-y-auto">
        <div className="flex items-center gap-4 mb-6">
          <div className="flex-1 flex items-center gap-3 px-4 py-2.5 bg-card-bg border border-card-border rounded-xl">
            <Search size={16} className="text-text-secondary/50" />
            <input
              type="text"
              placeholder="Search files..."
              className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-secondary/50 outline-none"
            />
          </div>
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-primary hover:bg-primary-hover text-white rounded-xl text-sm font-medium transition-colors shrink-0"
          >
            <Upload size={14} />
            Upload files
          </Link>
        </div>

        <div className="bg-card-bg border border-card-border rounded-2xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-card-border">
                <th className="text-left px-6 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">Name</th>
                <th className="text-left px-4 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">Type</th>
                <th className="text-left px-4 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">Size</th>
                <th className="text-left px-4 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">Status</th>
                <th className="text-left px-4 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">Uploaded</th>
                <th className="text-center px-4 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">Chunks</th>
                <th className="text-right px-6 py-3.5 text-xs font-semibold text-text-secondary uppercase tracking-wider">Actions</th>
              </tr>
            </thead>
            <tbody>
              {mockFiles.map((file) => (
                <tr key={file.id} className="border-b border-card-border last:border-b-0 hover:bg-content-bg/50 transition-colors">
                  <td className="px-6 py-4">
                    <span className="text-sm font-semibold text-text-primary">{file.name}</span>
                  </td>
                  <td className="px-4 py-4 text-sm text-text-secondary">{file.type}</td>
                  <td className="px-4 py-4 text-sm text-text-secondary">{file.size}</td>
                  <td className="px-4 py-4">
                    <span className={`inline-block w-14 h-5 rounded-full ${statusBadge[file.status]}`} />
                  </td>
                  <td className="px-4 py-4 text-sm text-text-secondary">{file.uploaded}</td>
                  <td className="px-4 py-4 text-sm text-text-secondary text-center">{file.chunks}</td>
                  <td className="px-6 py-4 text-right">
                    {file.status === 'indexed' ? (
                      <span className="text-sm text-text-secondary">
                        <Link href={`/files/${file.id}`} className="text-primary hover:underline">View</Link>
                        {' '}&middot;{' '}
                        <button className="text-error hover:underline">Delete</button>
                      </span>
                    ) : (
                      <button className="text-sm text-primary hover:underline">Reprocess</button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
