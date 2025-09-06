import React, { useState, useEffect, useCallback } from 'react';
import { Document } from './types/document';
import { TabType } from './components/Navigation';
import Header from './components/Header';
import Navigation from './components/Navigation';
import ChatInterface from './components/ChatInterface';
import UploadInterface from './components/UploadInterface';
import KnowledgeBase from './components/KnowledgeBase';
import AuthModal from './components/AuthModal';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { authApi } from './utils/authApi';
import styles from './App.module.css';

const AppContent: React.FC = () => {
  const { user, token, isAuthenticated, login, logout } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('chat');
  const [documents, setDocuments] = useState<Document[]>([]);
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [isLoading, setIsLoading] = useState(true);
  const [deletingDocument, setDeletingDocument] = useState<string | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Set token in API client when it changes
  useEffect(() => {
    authApi.setToken(token);
  }, [token]);

  const loadDocuments = useCallback(async () => {
    if (!isAuthenticated) {
      setDocuments([]);
      setIsLoading(false);
      return;
    }

    try {
      console.log('Loading documents...');
      const response = await authApi.getDocuments(100, 0);
      if (response.data && response.data.documents) {
        console.log('Documents loaded:', response.data.documents.length, 'documents');
        console.log('Document details:', response.data.documents.map((d: any) => ({ filename: d.filename, size: d.size })));
        setDocuments(response.data.documents || []);
      } else {
        console.error('Failed to load documents:', response.error);
        setDocuments([]);
      }
    } catch (error) {
      console.error('Failed to load documents:', error);
      setDocuments([]);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  const handleFileUpload = useCallback(async (files: FileList, forceUpload: boolean = false) => {
    if (!isAuthenticated) {
      alert('Please log in to upload documents');
      setShowAuthModal(true);
      return;
    }

    console.log('handleFileUpload called with files:', files);
    console.log('Number of files:', files.length);
    console.log('Force upload:', forceUpload);
    
    if (files.length === 0) {
      console.log('No files to upload');
      return;
    }
    
    try {
      // Upload files one by one since the backend expects a single file
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        console.log(`Uploading file ${i + 1}/${files.length}:`, file.name, file.type, file.size);
        
        const formData = new FormData();
        formData.append('file', file); // Note: 'file' not 'files' for single file upload
        if (forceUpload) {
          formData.append('force_upload', 'true');
        }
        
        console.log('Sending request to backend...');
        const response = await authApi.uploadDocument(file, forceUpload);

        console.log('Response received:', response.status, response.data ? 'success' : 'error');
        
        if (response.data) {
          console.log('Upload successful:', response.data);
          alert(`File "${file.name}" uploaded successfully!`);
        } else if (response.status === 409) {
          // Duplicate detected
          console.log('Duplicate detected:', response.error);
          
          const duplicateInfo = JSON.parse(response.error || '{}').duplicate_info;
          const message = duplicateInfo?.type === 'exact_duplicate' 
            ? `File "${file.name}" has already been uploaded.`
            : `File content already exists as "${duplicateInfo?.existing_filename || 'another file'}".`;
          
          const shouldForceUpload = window.confirm(
            `${message}\n\nDo you want to upload it anyway?`
          );
          
          if (shouldForceUpload) {
            // Retry with force upload
            await handleFileUpload(files, true);
            return;
          } else {
            alert(`Upload cancelled for "${file.name}" - duplicate detected.`);
          }
        } else {
          console.error('Upload failed:', response.status, response.error);
          alert(`Upload failed for "${file.name}": ${response.error || 'Unknown error'}`);
        }
      }
      
      // Reload documents after all uploads
      console.log('Reloading documents...');
      await loadDocuments();
      // Switch to documents tab to show the uploaded files
      setActiveTab('documents');
      
      // Force a small delay and reload again to ensure we get the latest data
      setTimeout(async () => {
        console.log('Force refreshing documents after upload...');
        await loadDocuments();
      }, 1000);
      
    } catch (error) {
      console.error('Upload error:', error);
      alert(`Upload error: ${error}`);
    }
  }, [isAuthenticated, loadDocuments]);

  const handleTabChange = useCallback((tab: TabType) => {
    setActiveTab(tab);
  }, []);

  const handleAuthSuccess = useCallback((token: string, user: any) => {
    login(token, user);
    setShowAuthModal(false);
  }, [login]);

  const handleLogout = useCallback(() => {
    logout();
    setActiveTab('chat');
  }, [logout]);

  const handleDeleteDocument = useCallback(async (documentId: string) => {
    try {
      setDeletingDocument(documentId);
      console.log('Deleting document:', documentId);
      const response = await fetch(`http://localhost:8000/api/v1/documents/${documentId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        console.log('Document deleted successfully');
        alert('Document deleted successfully!');
        // Reload documents after deletion
        await loadDocuments();
      } else if (response.status === 404) {
        console.log('Document not found - may have been already deleted');
        alert('Document not found - it may have been already deleted.');
        // Reload documents to refresh the list
        await loadDocuments();
      } else {
        const errorText = await response.text();
        console.error('Delete failed:', response.status, errorText);
        alert(`Delete failed: ${errorText}`);
      }
    } catch (error) {
      console.error('Delete error:', error);
      alert(`Delete error: ${error}`);
    } finally {
      setDeletingDocument(null);
    }
  }, [loadDocuments]);

  const handleUploadClick = useCallback(() => {
    setActiveTab('upload');
  }, []);

  useEffect(() => {
    loadDocuments();
  }, [loadDocuments]);

  const renderContent = () => {
    switch (activeTab) {
      case 'chat':
        return <ChatInterface />;
      case 'upload':
        return <UploadInterface onUpload={handleFileUpload} />;
      case 'documents':
        return (
          <KnowledgeBase 
            documents={documents} 
            onUploadClick={handleUploadClick}
            onRefresh={loadDocuments}
            onDeleteDocument={handleDeleteDocument}
            deletingDocument={deletingDocument}
          />
        );
      default:
        return <ChatInterface />;
    }
  };

  return (
    <div className={styles.app}>
      <Header 
        user={user} 
        onLoginClick={() => setShowAuthModal(true)}
        onLogoutClick={handleLogout}
      />
      
      <div className={styles.container}>
        <Navigation 
          activeTab={activeTab} 
          onTabChange={handleTabChange} 
        />
        
        <main className={styles.mainContent}>
          {isAuthenticated ? (
            renderContent()
          ) : (
            <div className={styles.authPrompt}>
              <h2>Welcome to Nuvaru RAG System</h2>
              <p>Please sign in to access the knowledge base and AI chat features.</p>
              <button 
                className={styles.loginButton}
                onClick={() => setShowAuthModal(true)}
              >
                Sign In
              </button>
            </div>
          )}
        </main>
      </div>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onAuthSuccess={handleAuthSuccess}
      />
    </div>
  );
};

const App: React.FC = () => {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
};

export default App;