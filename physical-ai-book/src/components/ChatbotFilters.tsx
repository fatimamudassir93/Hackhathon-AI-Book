import React, { useState, useEffect } from 'react';
import styles from './ChatbotFilters.module.css';

interface ChatbotFiltersProps {
  apiUrl: string;
  selectedChapter: string | null;
  onChapterChange: (chapter: string | null) => void;
}

const ChatbotFilters: React.FC<ChatbotFiltersProps> = ({
  apiUrl,
  selectedChapter,
  onChapterChange
}) => {
  const [chapters, setChapters] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    fetchChapters();
  }, [apiUrl]);

  const fetchChapters = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/api/chapters`);

      if (!response.ok) {
        throw new Error(`Failed to fetch chapters: ${response.statusText}`);
      }

      const data = await response.json();
      setChapters(data.chapters || []);
    } catch (err) {
      console.error('Error fetching chapters:', err);
      setError(err instanceof Error ? err.message : 'Failed to load chapters');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChapterSelect = (chapter: string | null) => {
    onChapterChange(chapter);
    setIsExpanded(false);
  };

  const handleClearFilter = () => {
    onChapterChange(null);
  };

  return (
    <div className={styles.filtersContainer}>
      {/* Filter Toggle Button */}
      <button
        className={styles.filterToggle}
        onClick={() => setIsExpanded(!isExpanded)}
        aria-label="Toggle filters"
        title="Filter by chapter"
      >
        🔍 Filter {selectedChapter && <span className={styles.activeIndicator}>●</span>}
      </button>

      {/* Expanded Filter Panel */}
      {isExpanded && (
        <div className={styles.filterPanel}>
          <div className={styles.filterHeader}>
            <h4>Filter by Chapter</h4>
            <button
              className={styles.closeFilter}
              onClick={() => setIsExpanded(false)}
              aria-label="Close filters"
            >
              ✕
            </button>
          </div>

          <div className={styles.filterContent}>
            {isLoading && (
              <div className={styles.loadingState}>Loading chapters...</div>
            )}

            {error && (
              <div className={styles.errorState}>
                <p>⚠️ {error}</p>
                <button onClick={fetchChapters} className={styles.retryButton}>
                  Retry
                </button>
              </div>
            )}

            {!isLoading && !error && (
              <>
                {/* All Chapters Option */}
                <button
                  className={`${styles.chapterOption} ${!selectedChapter ? styles.selected : ''}`}
                  onClick={() => handleChapterSelect(null)}
                >
                  <span className={styles.chapterIcon}>📚</span>
                  All Chapters
                  {!selectedChapter && <span className={styles.checkmark}>✓</span>}
                </button>

                {/* Individual Chapter Options */}
                <div className={styles.chapterList}>
                  {chapters.map((chapter) => (
                    <button
                      key={chapter}
                      className={`${styles.chapterOption} ${selectedChapter === chapter ? styles.selected : ''}`}
                      onClick={() => handleChapterSelect(chapter)}
                    >
                      <span className={styles.chapterIcon}>📖</span>
                      {chapter}
                      {selectedChapter === chapter && <span className={styles.checkmark}>✓</span>}
                    </button>
                  ))}
                </div>

                {chapters.length === 0 && (
                  <div className={styles.emptyState}>
                    <p>No chapters available</p>
                    <small>Make sure the backend has indexed content</small>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Active Filter Badge */}
      {selectedChapter && !isExpanded && (
        <div className={styles.activeFilterBadge}>
          <span>📖 {selectedChapter}</span>
          <button
            onClick={handleClearFilter}
            className={styles.clearFilterButton}
            aria-label="Clear filter"
          >
            ✕
          </button>
        </div>
      )}
    </div>
  );
};

export default ChatbotFilters;
