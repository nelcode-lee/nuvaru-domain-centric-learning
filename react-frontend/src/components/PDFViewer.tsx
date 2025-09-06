import React, { useState, useEffect } from 'react';
import styles from './PDFViewer.module.css';

interface PDFViewerProps {
  documentId: string;
  filename: string;
  onClose: () => void;
}

const PDFViewer: React.FC<PDFViewerProps> = ({ documentId, filename, onClose }) => {
  const [pdfUrl, setPdfUrl] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPDF = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Create a blob URL for the PDF
        const response = await fetch(`http://localhost:8000/api/v1/documents/${documentId}/download`);
        
        if (response.ok) {
          const blob = await response.blob();
          const url = URL.createObjectURL(blob);
          setPdfUrl(url);
        } else {
          setError('Failed to load PDF');
        }
      } catch (err) {
        setError('Error loading PDF');
        console.error('Error loading PDF:', err);
      } finally {
        setLoading(false);
      }
    };

    loadPDF();

    // Cleanup blob URL on unmount
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [documentId, pdfUrl]);

  return (
    <div className={styles.overlay}>
      <div className={styles.viewer}>
        <div className={styles.header}>
          <div className={styles.titleSection}>
            <span className={styles.fileIcon}>📄</span>
            <div>
              <h2 className={styles.title}>{filename}</h2>
              <p className={styles.subtitle}>PDF Viewer</p>
            </div>
          </div>
          <button onClick={onClose} className={styles.closeButton}>
            ✕
          </button>
        </div>

        <div className={styles.content}>
          {loading ? (
            <div className={styles.loadingContent}>
              <div className={styles.loadingSpinner}>⏳</div>
              <p>Loading PDF...</p>
            </div>
          ) : error ? (
            <div className={styles.errorContent}>
              <div className={styles.errorIcon}>❌</div>
              <p>{error}</p>
            </div>
          ) : pdfUrl ? (
            <iframe
              src={pdfUrl}
              className={styles.pdfFrame}
              title={filename}
            />
          ) : null}
        </div>

        <div className={styles.actions}>
          <button 
            className={styles.actionButton}
            onClick={() => {
              if (pdfUrl) {
                const link = document.createElement('a');
                link.href = pdfUrl;
                link.download = filename;
                link.click();
              }
            }}
          >
            📥 Download
          </button>
          <button 
            className={styles.actionButton}
            onClick={() => {
              if (pdfUrl) {
                window.open(pdfUrl, '_blank');
              }
            }}
          >
            🔗 Open in New Tab
          </button>
        </div>
      </div>
    </div>
  );
};

export default PDFViewer;
