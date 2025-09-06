import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { CloudArrowUpIcon, DocumentTextIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { useMutation } from 'react-query'
import toast from 'react-hot-toast'
import { apiService } from '../services/api'

interface DocumentUploadProps {
  onUploadSuccess?: () => void
}

export function DocumentUpload({ onUploadSuccess }: DocumentUploadProps) {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [isUploading, setIsUploading] = useState(false)

  const uploadMutation = useMutation(
    async (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('knowledge_base_id', 'default')
      
      const response = await apiService.uploadDocument(formData)
      return response
    },
    {
      onSuccess: (data) => {
        toast.success(`Document "${data.filename}" uploaded successfully!`)
        setUploadedFiles(prev => prev.filter(f => f.name !== data.filename))
        onUploadSuccess?.()
      },
      onError: (error: any) => {
        toast.error('Failed to upload document. Please try again.')
      }
    }
  )

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const validFiles = acceptedFiles.filter(file => {
      const validTypes = ['text/plain', 'text/markdown', 'application/json']
      return validTypes.includes(file.type) || 
             file.name.endsWith('.txt') || 
             file.name.endsWith('.md') || 
             file.name.endsWith('.json')
    })

    if (validFiles.length !== acceptedFiles.length) {
      toast.error('Some files were skipped. Only TXT, MD, and JSON files are supported.')
    }

    setUploadedFiles(prev => [...prev, ...validFiles])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/json': ['.json']
    },
    multiple: true
  })

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const uploadFiles = async () => {
    if (uploadedFiles.length === 0) return

    setIsUploading(true)
    try {
      for (const file of uploadedFiles) {
        await uploadMutation.mutateAsync(file)
      }
    } finally {
      setIsUploading(false)
    }
  }

  const getFileIcon = (file: File) => {
    if (file.type === 'text/markdown' || file.name.endsWith('.md')) {
      return <DocumentTextIcon className="h-8 w-8 text-blue-500" />
    }
    if (file.type === 'application/json' || file.name.endsWith('.json')) {
      return <DocumentTextIcon className="h-8 w-8 text-green-500" />
    }
    return <DocumentTextIcon className="h-8 w-8 text-gray-500" />
  }

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200 ${
          isDragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          {isDragActive ? 'Drop files here' : 'Upload Documents'}
        </h3>
        <p className="text-gray-600 mb-4">
          Drag and drop files here, or click to select files
        </p>
        <p className="text-sm text-gray-500">
          Supported formats: TXT, MD, JSON (Max 10MB per file)
        </p>
      </div>

      {/* File List */}
      {uploadedFiles.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-medium text-gray-900 mb-4">
            Files to Upload ({uploadedFiles.length})
          </h3>
          <div className="space-y-3">
            {uploadedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  {getFileIcon(file)}
                  <div>
                    <div className="font-medium text-gray-900">{file.name}</div>
                    <div className="text-sm text-gray-500">
                      {(file.size / 1024).toFixed(1)} KB
                    </div>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
          
          <div className="mt-6 flex justify-end space-x-3">
            <button
              onClick={() => setUploadedFiles([])}
              className="btn-secondary"
              disabled={isUploading}
            >
              Clear All
            </button>
            <button
              onClick={uploadFiles}
              className="btn-primary"
              disabled={isUploading}
            >
              {isUploading ? 'Uploading...' : `Upload ${uploadedFiles.length} Files`}
            </button>
          </div>
        </div>
      )}

      {/* Upload Guidelines */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Upload Guidelines
        </h3>
        <div className="space-y-3 text-sm text-gray-600">
          <div className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <strong>Text Files (.txt):</strong> Plain text documents, reports, notes
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <strong>Markdown (.md):</strong> Structured documents with formatting
            </div>
          </div>
          <div className="flex items-start space-x-2">
            <div className="w-2 h-2 bg-purple-500 rounded-full mt-2 flex-shrink-0"></div>
            <div>
              <strong>JSON (.json):</strong> Structured data, configurations, metadata
            </div>
          </div>
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-blue-800">
              <strong>Tip:</strong> Documents will be automatically processed and added to your knowledge base. 
              You can then ask questions about their content using the AI Chat.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}


