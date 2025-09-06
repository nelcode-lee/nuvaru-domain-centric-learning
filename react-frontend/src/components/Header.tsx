import React from 'react';
import styles from './Header.module.css';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  last_login: string | null;
  bio: string | null;
  avatar_url: string | null;
  preferred_language: string;
  timezone: string;
}

interface HeaderProps {
  user?: User | null;
  onLoginClick?: () => void;
  onLogoutClick?: () => void;
}

const Header: React.FC<HeaderProps> = ({ user, onLoginClick, onLogoutClick }) => {
  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <div className={styles.brandSection}>
          <div className={styles.logoContainer}>
            <img 
              src="/v3 nuvaru logo.png?v=2" 
              alt="Nuvaru Logo" 
              className={styles.logo}
              onError={(e) => {
                // Fallback to gradient logo if image fails to load
                e.currentTarget.style.display = 'none';
                e.currentTarget.parentElement!.innerHTML = `
                  <div class="${styles.fallbackLogo}">N</div>
                `;
              }}
            />
          </div>
        </div>
        
        <div className={styles.statusSection}>
          <div className={styles.statusBadge}>
            <div className={styles.statusDot}></div>
            <span className={styles.statusText}>System Online</span>
          </div>
        </div>

        <div className={styles.userSection}>
          {user ? (
            <div className={styles.userInfo}>
              <div className={styles.userDetails}>
                <span className={styles.userName}>
                  {user.full_name || user.username}
                </span>
                <span className={styles.userEmail}>{user.email}</span>
              </div>
              <button 
                className={styles.logoutButton}
                onClick={onLogoutClick}
                title="Sign Out"
              >
                Sign Out
              </button>
            </div>
          ) : (
            <button 
              className={styles.loginButton}
              onClick={onLoginClick}
            >
              Sign In
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
