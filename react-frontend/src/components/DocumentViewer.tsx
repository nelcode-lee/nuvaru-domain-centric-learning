import React, { useState, useEffect } from 'react';
import styles from './DocumentViewer.module.css';

interface DocumentViewerProps {
  document: {
    id: string;
    filename: string;
    content_type: string;
    size: number;
    status: string;
    chunks_count: number;
    created_at: string;
    content?: string;
  };
  onClose: () => void;
}

const DocumentViewer: React.FC<DocumentViewerProps> = ({ document, onClose }) => {
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(`http://localhost:8000/api/v1/documents/${document.id}/content`);
        
        if (response.ok) {
          const data = await response.json();
          setContent(data.content || '');
        } else {
          setError('Failed to load document content');
        }
      } catch (err) {
        setError('Error loading document content');
        console.error('Error fetching document content:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, [document.id]);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const getFileIcon = (contentType: string) => {
    if (contentType.includes('pdf')) return '📄';
    if (contentType.includes('text')) return '📝';
    if (contentType.includes('json')) return '📋';
    if (contentType.includes('markdown')) return '📖';
    return '📄';
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.viewer}>
        <div className={styles.header}>
          <div className={styles.titleSection}>
            <span className={styles.fileIcon}>{getFileIcon(document.content_type)}</span>
            <div>
              <h2 className={styles.title}>{document.filename}</h2>
              <p className={styles.subtitle}>Document Viewer</p>
            </div>
          </div>
          <button onClick={onClose} className={styles.closeButton}>
            ✕
          </button>
        </div>

        <div className={styles.metadata}>
          <div className={styles.metadataGrid}>
            <div className={styles.metadataItem}>
              <span className={styles.label}>File Type:</span>
              <span className={styles.value}>{document.content_type}</span>
            </div>
            <div className={styles.metadataItem}>
              <span className={styles.label}>File Size:</span>
              <span className={styles.value}>{formatFileSize(document.size)}</span>
            </div>
            <div className={styles.metadataItem}>
              <span className={styles.label}>Status:</span>
              <span className={`${styles.value} ${styles.status} ${styles[document.status]}`}>
                {document.status}
              </span>
            </div>
            <div className={styles.metadataItem}>
              <span className={styles.label}>Chunks:</span>
              <span className={styles.value}>{document.chunks_count}</span>
            </div>
            <div className={styles.metadataItem}>
              <span className={styles.label}>Uploaded:</span>
              <span className={styles.value}>{formatDate(document.created_at)}</span>
            </div>
            <div className={styles.metadataItem}>
              <span className={styles.label}>Document ID:</span>
              <span className={styles.value}>{document.id}</span>
            </div>
          </div>
        </div>

        <div className={styles.content}>
          <h3 className={styles.contentTitle}>Document Content</h3>
          <div className={styles.contentArea}>
            {loading ? (
              <div className={styles.loadingContent}>
                <div className={styles.loadingSpinner}>⏳</div>
                <p>Loading document content...</p>
              </div>
            ) : error ? (
              <div className={styles.errorContent}>
                <div className={styles.errorIcon}>❌</div>
                <p>{error}</p>
              </div>
            ) : content ? (
              <pre className={styles.textContent}>{content}</pre>
            ) : (
              <div className={styles.noContent}>
                <div className={styles.noContentIcon}>📄</div>
                <p>Content preview not available</p>
                <p className={styles.noContentSubtitle}>
                  This document has been processed and stored in the knowledge base.
                </p>
              </div>
            )}
          </div>
        </div>

        <div className={styles.actions}>
          <button 
            className={styles.actionButton}
            onClick={() => {
              const downloadUrl = `http://localhost:8000/api/v1/documents/${document.id}/download`;
              window.open(downloadUrl, '_blank');
            }}
          >
            📥 Download
          </button>
          <button 
            className={styles.actionButton}
            onClick={() => {
              // Refresh content
              window.location.reload();
            }}
          >
            🔄 Refresh
          </button>
          <button 
            className={styles.actionButton}
            onClick={() => {
              // Open in new tab for PDF viewing
              if (document.content_type.includes('pdf')) {
                const viewUrl = `http://localhost:8000/api/v1/documents/${document.id}/download`;
                window.open(viewUrl, '_blank');
              }
            }}
          >
            👁️ View Original
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentViewer;
