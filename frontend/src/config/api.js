/**
 * API Configuration
 * Centralized API URL management for different environments
 */

// Determine the API URL based on the current environment
const getApiUrl = () => {
  // Production (GitHub Pages)
  if (window.location.hostname === 'nitheshkg.github.io') {
    return 'https://gj-pos-backend-544714625292.us-central1.run.app'
  }

  // Local development
  return 'http://localhost:5000'
}

export const API_URL = getApiUrl()

/**
 * Debug logging
 */
if (typeof window !== 'undefined') {
  console.log(`API Configuration: Using API URL = ${API_URL}`)
}
