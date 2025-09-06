import { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import { 
  DocumentTextIcon, 
  MagnifyingGlassIcon,
  TrashIcon,
  EyeIcon,
  CalendarIcon
} from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'
import { apiService } from '../services/api'

interface Document {
  id: string
  filename: string
  content_type: string
  size: number
  status: string
  metadata: any
  user_id: number
  chunks_count: number
}

interface DocumentListProps {
  onDocumentsChange?: (documents: Document[]) => void
}

export function DocumentList({ onDocumentsChange }: DocumentListProps) {
  const [searchQuery, setSearchQuery] = useState('')
  const [filteredDocuments, setFilteredDocuments] = useState<Document[]>([])

  const { data: documents = [], isLoading, refetch } = useQuery(
    'documents',
    () => apiService.getDocuments(),
    {
      onSuccess: (data) => {
        onDocumentsChange?.(data)
        setFilteredDocuments(data)
      },
      onError: (error: any) => {
        toast.error('Failed to load documents')
      }
    }
  )

  useEffect(() => {
    if (searchQuery.trim()) {
      const filtered = documents.filter(doc =>
        doc.filename.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.content_type.toLowerCase().includes(searchQuery.toLowerCase())
      )
      setFilteredDocuments(filtered)
    } else {
      setFilteredDocuments(documents)
    }
  }, [searchQuery, documents])

  const handleDelete = async (documentId: string) => {
    if (!confirm('Are you sure you want to delete this document?')) return

    try {
      await apiService.deleteDocument(documentId)
      toast.success('Document deleted successfully')
      refetch()
    } catch (error) {
      toast.error('Failed to delete document')
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const getFileIcon = (contentType: string) => {
    switch (contentType) {
      case 'text/markdown':
        return <DocumentTextIcon className="h-8 w-8 text-blue-500" />
      case 'application/json':
        return <DocumentTextIcon className="h-8 w-8 text-green-500" />
      default:
        return <DocumentTextIcon className="h-8 w-8 text-gray-500" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'processed':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Processed</span>
      case 'processing':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">Processing</span>
      case 'error':
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">Error</span>
      default:
        return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">{status}</span>
    }
  }

  if (isLoading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Loading documents...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Search and Stats */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            Documents ({filteredDocuments.length})
          </h3>
          <button
            onClick={() => refetch()}
            className="text-sm text-blue-600 hover:text-blue-800"
          >
            Refresh
          </button>
        </div>
        
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search documents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Documents List */}
      {filteredDocuments.length === 0 ? (
        <div className="card text-center py-12">
          <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-300 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {searchQuery ? 'No documents found' : 'No documents uploaded'}
          </h3>
          <p className="text-gray-600">
            {searchQuery 
              ? 'Try adjusting your search terms'
              : 'Upload some documents to get started with your knowledge base'
            }
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredDocuments.map((doc) => (
            <div key={doc.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-4">
                  {getFileIcon(doc.content_type)}
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h4 className="text-lg font-medium text-gray-900">
                        {doc.filename}
                      </h4>
                      {getStatusBadge(doc.status)}
                    </div>
                    
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <CalendarIcon className="h-4 w-4" />
                        <span>{formatFileSize(doc.size)}</span>
                      </div>
                      <div>
                        <span className="font-medium">Type:</span> {doc.content_type}
                      </div>
                      <div>
                        <span className="font-medium">Chunks:</span> {doc.chunks_count}
                      </div>
                      <div>
                        <span className="font-medium">ID:</span> {doc.id.slice(0, 8)}...
                      </div>
                    </div>
                    
                    {doc.metadata && Object.keys(doc.metadata).length > 0 && (
                      <div className="mt-3">
                        <details className="text-sm">
                          <summary className="cursor-pointer text-blue-600 hover:text-blue-800">
                            View Metadata
                          </summary>
                          <pre className="mt-2 p-2 bg-gray-50 rounded text-xs overflow-x-auto">
                            {JSON.stringify(doc.metadata, null, 2)}
                          </pre>
                        </details>
                      </div>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => window.open(`/api/v1/documents/${doc.id}`, '_blank')}
                    className="p-2 text-gray-400 hover:text-gray-600"
                    title="View Document"
                  >
                    <EyeIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(doc.id)}
                    className="p-2 text-gray-400 hover:text-red-600"
                    title="Delete Document"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}


