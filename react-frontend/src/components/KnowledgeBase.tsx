import React, { useState } from 'react';
import { Document } from '../types/document';
import DocumentViewer from './DocumentViewer';
import PDFViewer from './PDFViewer';
import styles from './KnowledgeBase.module.css';

interface KnowledgeBaseProps {
  documents: Document[];
  onUploadClick: () => void;
  onRefresh?: () => void;
  onDeleteDocument?: (documentId: string) => void;
  deletingDocument?: string | null;
}

const KnowledgeBase: React.FC<KnowledgeBaseProps> = ({ documents, onUploadClick, onRefresh, onDeleteDocument, deletingDocument }) => {
  const [viewingDocument, setViewingDocument] = useState<Document | null>(null);
  const [viewingPDF, setViewingPDF] = useState<Document | null>(null);
  const totalChunks = documents.reduce((sum, doc) => sum + doc.chunks_count, 0);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileTypeLabel = (contentType: string) => {
    if (contentType.includes('pdf')) return 'PDF Document';
    if (contentType.includes('text/plain')) return 'Text File';
    if (contentType.includes('text/markdown')) return 'Markdown';
    if (contentType.includes('application/json')) return 'JSON File';
    return 'Document';
  };

  const getFileIcon = (contentType: string) => {
    if (contentType.includes('pdf')) return '📄';
    if (contentType.includes('text/plain')) return '📝';
    if (contentType.includes('text/markdown')) return '📖';
    if (contentType.includes('application/json')) return '📋';
    return '📄';
  };

  return (
    <div>
      <div className={styles.card}>
        <div className={styles.header}>
          <div className={styles.headerContent}>
            <div>
              <h2 className={styles.title}>Knowledge Base</h2>
              <p className={styles.subtitle}>
                Your uploaded documents are processed and ready for AI chat
              </p>
            </div>
            {onRefresh && (
              <button onClick={onRefresh} className={styles.refreshButton}>
                🔄 Refresh
              </button>
            )}
          </div>
        </div>

        <div className={styles.statsGrid}>
          <div className={styles.statCard}>
            <div className={styles.statIcon}>📄</div>
            <h3 className={styles.statValue}>{documents.length}</h3>
            <p className={styles.statLabel}>Documents</p>
          </div>
          
          <div className={styles.statCard}>
            <div className={styles.statIcon}>📊</div>
            <h3 className={styles.statValue}>{totalChunks}</h3>
            <p className={styles.statLabel}>Chunks Processed</p>
          </div>
          
          <div className={styles.statCard}>
            <div className={styles.statIcon}>✅</div>
            <h3 className={styles.statValue}>Ready</h3>
            <p className={styles.statLabel}>Status</p>
          </div>
        </div>
      </div>

      <div className={styles.card}>
        <h3 className={styles.documentsTitle}>Your Documents</h3>
        
        {documents.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>📄</div>
            <h3 className={styles.emptyTitle}>No documents yet</h3>
            <p className={styles.emptySubtitle}>
              Upload some documents to get started with your knowledge base
            </p>
            <button
              onClick={onUploadClick}
              className={styles.uploadButton}
            >
              Upload Documents
            </button>
          </div>
        ) : (
          <div className={styles.documentsList}>
            {documents.map((doc) => (
              <div key={doc.id} className={styles.documentItem}>
                <div className={styles.documentIcon}>{getFileIcon(doc.content_type)}</div>
                
                <div className={styles.documentInfo}>
                  <div className={styles.documentHeader}>
                    <h4 className={styles.documentName}>{doc.filename}</h4>
                    <span className={styles.fileTypeLabel}>{getFileTypeLabel(doc.content_type)}</span>
                  </div>
                  <div className={styles.documentMeta}>
                    <span className={styles.metaItem}>
                      <span className={styles.metaLabel}>Status:</span>
                      <span className={`${styles.metaValue} ${styles[doc.status]}`}>{doc.status}</span>
                    </span>
                    <span className={styles.metaItem}>
                      <span className={styles.metaLabel}>Size:</span>
                      <span className={styles.metaValue}>{formatFileSize(doc.size)}</span>
                    </span>
                    <span className={styles.metaItem}>
                      <span className={styles.metaLabel}>Chunks:</span>
                      <span className={styles.metaValue}>{doc.chunks_count}</span>
                    </span>
                    <span className={styles.metaItem}>
                      <span className={styles.metaLabel}>Uploaded:</span>
                      <span className={styles.metaValue}>{new Date(doc.created_at).toLocaleDateString()}</span>
                    </span>
                  </div>
                </div>
                
                <div className={styles.documentActions}>
                  <button 
                    className={styles.viewButton}
                    onClick={() => setViewingDocument(doc)}
                    title="View document details"
                  >
                    👁️
                  </button>
                  {doc.content_type.includes('pdf') && (
                    <button 
                      className={styles.pdfButton}
                      onClick={() => setViewingPDF(doc)}
                      title="View PDF"
                    >
                      📄
                    </button>
                  )}
                  <button 
                    className={styles.documentAction} 
                    onClick={() => {
                      const downloadUrl = `http://localhost:8000/api/v1/documents/${doc.id}/download`;
                      window.open(downloadUrl, '_blank');
                    }}
                    title="Download document"
                  >
                    📥
                  </button>
                  {onDeleteDocument && (
                    <button 
                      className={styles.deleteButton}
                      onClick={() => {
                        if (window.confirm(`Are you sure you want to delete "${doc.filename}"?`)) {
                          onDeleteDocument(doc.id);
                        }
                      }}
                      title="Delete document"
                      disabled={deletingDocument === doc.id}
                    >
                      {deletingDocument === doc.id ? '⏳' : '🗑️'}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {viewingDocument && (
        <DocumentViewer
          document={viewingDocument}
          onClose={() => setViewingDocument(null)}
        />
      )}

      {viewingPDF && (
        <PDFViewer
          documentId={viewingPDF.id}
          filename={viewingPDF.filename}
          onClose={() => setViewingPDF(null)}
        />
      )}
    </div>
  );
};

export default KnowledgeBase;