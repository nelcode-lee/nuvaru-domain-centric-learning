import React, { useCallback, useState } from 'react';
import styles from './UploadInterface.module.css';

interface UploadInterfaceProps {
  onUpload?: (files: FileList) => void;
}

const UploadInterface: React.FC<UploadInterfaceProps> = ({ onUpload }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{ current: number; total: number }>({ current: 0, total: 0 });

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
    const files = e.dataTransfer.files;
    if (files.length > 0 && onUpload) {
      onUpload(files);
    }
  }, [onUpload]);

  const handleFileSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    console.log('File select triggered, files:', files);
    
    if (files && files.length > 0) {
      console.log('Files selected:', files.length, 'files');
      for (let i = 0; i < files.length; i++) {
        console.log(`File ${i + 1}:`, files[i].name, files[i].type, files[i].size);
      }
      
      if (onUpload) {
        setIsUploading(true);
        setUploadProgress({ current: 0, total: files.length });
        
        try {
          // Upload files one by one with progress tracking
          for (let i = 0; i < files.length; i++) {
            console.log(`Starting upload ${i + 1}/${files.length}:`, files[i].name);
            setUploadProgress({ current: i + 1, total: files.length });
            
            // Create a new FileList with just this file
            const singleFileList = new DataTransfer();
            singleFileList.items.add(files[i]);
            
            console.log('Calling onUpload with file:', files[i].name);
            await onUpload(singleFileList.files);
            console.log('Upload completed for:', files[i].name);
          }
        } catch (error) {
          console.error('Upload error in handleFileSelect:', error);
        } finally {
          setIsUploading(false);
          setUploadProgress({ current: 0, total: 0 });
        }
      } else {
        console.error('onUpload function not provided');
      }
      
      // Reset the input so the same file can be selected again
      e.target.value = '';
    } else {
      console.log('No files selected');
    }
  }, [onUpload]);

  const handleAreaClick = useCallback(() => {
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    if (fileInput) {
      fileInput.click();
    }
  }, []);

  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h2 className={styles.title}>Document Upload</h2>
        <p className={styles.subtitle}>
          Upload your documents to build your knowledge base
        </p>
      </div>
      
      <div 
        className={`${styles.uploadArea} ${isDragOver ? styles.dragOver : ''} ${isUploading ? styles.uploading : ''}`}
        onDragOver={!isUploading ? handleDragOver : undefined}
        onDragLeave={!isUploading ? handleDragLeave : undefined}
        onDrop={!isUploading ? handleDrop : undefined}
        onClick={!isUploading ? handleAreaClick : undefined}
      >
        <input
          id="file-input"
          type="file"
          multiple
          accept=".pdf,.txt,.md,.json"
          onChange={handleFileSelect}
          onClick={(e) => {
            console.log('File input clicked');
            e.stopPropagation();
          }}
          className={styles.fileInput}
        />
        <div className={styles.uploadIcon}>
          {isUploading ? '⏳' : '📄'}
        </div>
        <h3 className={styles.uploadTitle}>
          {isUploading ? `Uploading files... (${uploadProgress.current}/${uploadProgress.total})` : 'Drag and drop files here'}
        </h3>
        <p className={styles.uploadSubtitle}>
          {isUploading ? 'Please wait while we process your files' : 'or click to select files from your computer'}
        </p>
        <div className={styles.fileInfo}>
          <p>Supported formats: PDF, TXT, MD, JSON</p>
          <p>Maximum file size: 10MB per file</p>
          <button 
            onClick={() => {
              console.log('Test upload button clicked');
              // Create a test file
              const testContent = "This is a test document for upload testing.";
              const blob = new Blob([testContent], { type: 'text/plain' });
              const file = new File([blob], 'test.txt', { type: 'text/plain' });
              const dataTransfer = new DataTransfer();
              dataTransfer.items.add(file);
              console.log('Created test file:', file.name, file.type, file.size);
              handleFileSelect({ target: { files: dataTransfer.files } } as any);
            }}
            className={styles.testButton}
          >
            Test Upload
          </button>
          <button 
            onClick={() => {
              console.log('Debug: onUpload function exists:', !!onUpload);
              console.log('Debug: handleFileSelect function exists:', !!handleFileSelect);
            }}
            className={styles.testButton}
            style={{ marginLeft: '8px', backgroundColor: '#10b981' }}
          >
            Debug Info
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadInterface;
