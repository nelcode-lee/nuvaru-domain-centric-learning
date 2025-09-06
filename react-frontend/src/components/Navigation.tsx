import React from 'react';
import styles from './Navigation.module.css';

export type TabType = 'chat' | 'upload' | 'documents';

interface NavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

const Navigation: React.FC<NavigationProps> = ({ activeTab, onTabChange }) => {
  const tabs = [
    { id: 'chat' as TabType, name: 'AI Chat', icon: '💬' },
    { id: 'upload' as TabType, name: 'Upload', icon: '📄' },
    { id: 'documents' as TabType, name: 'Knowledge Base', icon: '📚' }
  ];

  return (
    <nav className={styles.navigation}>
      <div className={styles.tabContainer}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`${styles.tab} ${activeTab === tab.id ? styles.activeTab : ''}`}
          >
            <span className={styles.tabIcon}>{tab.icon}</span>
            {tab.name}
          </button>
        ))}
      </div>
    </nav>
  );
};

export default Navigation;

