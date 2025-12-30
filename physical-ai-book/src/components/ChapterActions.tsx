import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useApiUrl } from '../utils/apiConfig';
import styles from './ChapterActions.module.css';

interface ChapterActionsProps {
  chapterId: string;
  chapterContent: string;
  onContentUpdate?: (content: string, language: string) => void;
}

const ChapterActions: React.FC<ChapterActionsProps> = ({
  chapterId,
  chapterContent,
  onContentUpdate
}) => {
  const { user, token } = useAuth();
  const API_URL = useApiUrl();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handlePersonalize = async () => {
    if (!token) return;

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${API_URL}/api/personalize/${chapterId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          chapter_id: chapterId,
          chapter_content: chapterContent
        })
      });

      if (!response.ok) {
        throw new Error('Personalization failed');
      }

      const data = await response.json();
      setSuccess('Chapter personalized successfully!');

      if (onContentUpdate) {
        onContentUpdate(data.content, data.language);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to personalize content');
    } finally {
      setIsLoading(false);
    }
  };

  const handleTranslate = async () => {
    if (!token) return;

    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await fetch(`${API_URL}/api/translate/${chapterId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          chapter_id: chapterId,
          chapter_content: chapterContent,
          target_language: 'ur'
        })
      });

      if (!response.ok) {
        throw new Error('Translation failed');
      }

      const data = await response.json();
      setSuccess('Chapter translated to Urdu successfully!');

      if (onContentUpdate) {
        onContentUpdate(data.content, data.language);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to translate content');
    } finally {
      setIsLoading(false);
    }
  };

  if (!user) {
    return (
      <div className={styles.loginPrompt}>
        🔒 Sign in to personalize or translate this chapter
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {error && <div className={styles.error}>❌ {error}</div>}
      {success && <div className={styles.success}>✅ {success}</div>}

      <div className={styles.userInfo}>
        <span className={styles.badge}>
          Level: {user.profile?.technical_level || 'Not set'}
        </span>
      </div>

      <div className={styles.buttons}>
        <button
          className={styles.actionButton}
          onClick={handlePersonalize}
          disabled={isLoading}
          title="Adapt this chapter to your technical level and learning goals"
        >
          🎯 Personalize for Me
        </button>

        <button
          className={`${styles.actionButton} ${styles.translateButton}`}
          onClick={handleTranslate}
          disabled={isLoading}
          title="Translate this chapter to Urdu"
        >
          🌐 Translate to Urdu
        </button>
      </div>

      {isLoading && (
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <span>Processing... This may take a moment</span>
        </div>
      )}
    </div>
  );
};

export default ChapterActions;
