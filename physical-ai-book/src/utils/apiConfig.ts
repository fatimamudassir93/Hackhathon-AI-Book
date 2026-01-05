import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

/**
 * Hook to get the API URL from Docusaurus configuration
 * Falls back to localhost:8000 for local development
 */
export function useApiUrl(): string {
  const { siteConfig } = useDocusaurusContext();
  return (siteConfig.customFields?.apiUrl as string) || 'http://localhost:8000';
}

/**
 * Get API URL for non-hook contexts (server-side or initial render)
 * Uses browser environment variable if available
 */
export function getApiUrl(): string {
  if (typeof window !== 'undefined' && window.docusaurus) {
    return (window.docusaurus.siteConfig?.customFields?.apiUrl as string) || 'http://localhost:8000';
  }
  return process.env.REACT_APP_API_URL || 'http://localhost:8000';
}

// Type augmentation for window.docusaurus
declare global {
  interface Window {
    docusaurus?: {
      siteConfig?: {
        customFields?: {
          apiUrl?: string;
        };
      };
    };
  }
}
