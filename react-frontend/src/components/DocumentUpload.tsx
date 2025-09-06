import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  DocumentArrowUpIcon, 
  CloudArrowUpIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { UploadProgress } from '../types/document';

interface DocumentUploadProps {
  onUpload: () => void;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onUpload }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const handleFiles = useCallback(async (files: File[]) => {
    if (files.length === 0) return;

    setIsUploading(true);
    const progressItems: UploadProgress[] = files.map(file => ({
      filename: file.name,
      progress: 0,
      status: 'uploading'
    }));
    setUploadProgress(progressItems);

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      await uploadFile(file, i);
    }

    setIsUploading(false);
    onUpload();
  }, [onUpload]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  }, [handleFiles]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      handleFiles(files);
    }
  };

  const uploadFile = async (file: File, index: number) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('content_type', file.type);

    try {
      setUploadProgress(prev => prev.map((item, i) => 
        i === index ? { ...item, status: 'processing' } : item
      ));

      const response = await fetch('http://localhost:8000/api/v1/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        setUploadProgress(prev => prev.map((item, i) => 
          i === index ? { ...item, progress: 100, status: 'completed' } : item
        ));
      } else {
        throw new Error('Upload failed');
      }
    } catch (error) {
      setUploadProgress(prev => prev.map((item, i) => 
        i === index ? { 
          ...item, 
          status: 'error', 
          error: 'Upload failed' 
        } : item
      ));
    }
  };

  const removeProgressItem = (index: number) => {
    setUploadProgress(prev => prev.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", duration: 0.5 }}
          className="w-20 h-20 bg-gradient-to-r from-emerald-500 to-teal-600 rounded-3xl flex items-center justify-center mx-auto mb-6"
        >
          <DocumentArrowUpIcon className="h-10 w-10 text-white" />
        </motion.div>
        <h2 className="text-3xl font-bold text-gray-800 mb-4">Upload Documents</h2>
        <p className="text-gray-600 text-lg max-w-2xl mx-auto">
          Upload your documents to build your knowledge base. Supported formats: PDF, TXT, MD, JSON
        </p>
      </div>

      {/* Upload Area */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="bg-white/60 backdrop-blur-md rounded-3xl shadow-2xl border border-white/20 p-8"
      >
        <div
          className={`relative border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300 ${
            isDragOver
              ? 'border-emerald-400 bg-emerald-50/50 scale-105'
              : 'border-gray-300 hover:border-emerald-400 hover:bg-emerald-50/30'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            type="file"
            multiple
            accept=".pdf,.txt,.md,.json"
            onChange={handleFileSelect}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            disabled={isUploading}
          />
          
          <motion.div
            animate={{ 
              scale: isDragOver ? 1.1 : 1,
              rotate: isDragOver ? 5 : 0 
            }}
            transition={{ duration: 0.2 }}
          >
            <CloudArrowUpIcon className="h-16 w-16 text-emerald-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-800 mb-2">
              {isDragOver ? 'Drop files here' : 'Drag and drop files here'}
            </h3>
            <p className="text-gray-600 mb-6">
              or click to select files from your computer
            </p>
            <div className="text-sm text-gray-500">
              <p>Supported formats: PDF, TXT, MD, JSON</p>
              <p>Maximum file size: 10MB per file</p>
            </div>
          </motion.div>
        </div>
      </motion.div>

      {/* Upload Progress */}
      <AnimatePresence>
        {uploadProgress.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-white/60 backdrop-blur-md rounded-3xl shadow-2xl border border-white/20 p-6"
          >
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Upload Progress</h3>
            <div className="space-y-3">
              {uploadProgress.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="flex items-center space-x-3 p-3 bg-white/50 rounded-2xl"
                >
                  <div className="flex-shrink-0">
                    {item.status === 'completed' && (
                      <CheckCircleIcon className="h-6 w-6 text-green-500" />
                    )}
                    {item.status === 'error' && (
                      <ExclamationTriangleIcon className="h-6 w-6 text-red-500" />
                    )}
                    {item.status === 'uploading' && (
                      <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
                    )}
                    {item.status === 'processing' && (
                      <div className="w-6 h-6 border-2 border-yellow-500 border-t-transparent rounded-full animate-spin" />
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">
                      {item.filename}
                    </p>
                    <div className="mt-1">
                      <div className="bg-gray-200 rounded-full h-2">
                        <motion.div
                          className="bg-gradient-to-r from-blue-500 to-indigo-600 h-2 rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${item.progress}%` }}
                          transition={{ duration: 0.5 }}
                        />
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      {item.status === 'uploading' && 'Uploading...'}
                      {item.status === 'processing' && 'Processing...'}
                      {item.status === 'completed' && 'Completed'}
                      {item.status === 'error' && item.error}
                    </p>
                  </div>
                  
                  <button
                    onClick={() => removeProgressItem(index)}
                    className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <XMarkIcon className="h-4 w-4" />
                  </button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DocumentUpload;