/**
 * State Management Utilities
 * Handles URL hash and localStorage persistence for the admin interface
 */

const STORAGE_KEY = 'data-pipeline-admin-state';

/**
 * Get hash parameters as an object
 * @returns {Object} Hash parameters
 */
export function getHash() {
  const hash = window.location.hash.slice(1);
  if (!hash) return {};

  const params = {};
  hash.split('&').forEach(part => {
    const [key, value] = part.split('=');
    if (key) {
      params[decodeURIComponent(key)] = value ? decodeURIComponent(value) : '';
    }
  });
  return params;
}

/**
 * Update hash and trigger hashChangeEvent
 * @param {Object} params - Parameters to set in hash
 */
export function goHash(params) {
  const currentHash = getHash();
  const newHash = { ...currentHash, ...params };

  // Remove empty values
  Object.keys(newHash).forEach(key => {
    if (newHash[key] === '' || newHash[key] === null || newHash[key] === undefined) {
      delete newHash[key];
    }
  });

  const hashString = Object.entries(newHash)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');

  window.location.hash = hashString;

  // Dispatch custom event for listeners
  document.dispatchEvent(new CustomEvent('hashChangeEvent', { detail: newHash }));
}

/**
 * Update hash without triggering hashChangeEvent
 * @param {Object} params - Parameters to set in hash
 */
export function updateHash(params) {
  const currentHash = getHash();
  const newHash = { ...currentHash, ...params };

  // Remove empty values
  Object.keys(newHash).forEach(key => {
    if (newHash[key] === '' || newHash[key] === null || newHash[key] === undefined) {
      delete newHash[key];
    }
  });

  const hashString = Object.entries(newHash)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join('&');

  // Use replaceState to avoid triggering hashchange event
  const newUrl = window.location.pathname + (hashString ? '#' + hashString : '');
  window.history.replaceState(null, '', newUrl);
}

/**
 * Save state to localStorage
 * @param {Object} state - State to save (view, selectedNodeId)
 */
export function saveState(state) {
  try {
    const existingState = loadState();
    const newState = { ...existingState, ...state };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(newState));
  } catch (e) {
    console.warn('Failed to save state to localStorage:', e);
  }
}

/**
 * Load state from localStorage
 * @returns {Object} Saved state or defaults
 */
export function loadState() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (e) {
    console.warn('Failed to load state from localStorage:', e);
  }
  return {
    view: 'column',
    selectedNodeId: null
  };
}

/**
 * Initialize state from hash (priority) or localStorage (fallback)
 * @returns {Object} Initial state
 */
export function initializeState() {
  const hash = getHash();
  const saved = loadState();

  return {
    view: hash.view || saved.view || 'column',
    selectedNodeId: hash.node || saved.selectedNodeId || null
  };
}

/**
 * Setup hash change listener
 * @param {Function} callback - Called when hash changes
 * @returns {Function} Cleanup function
 */
export function onHashChange(callback) {
  const handler = () => {
    const hash = getHash();
    callback(hash);
  };

  // Listen for browser back/forward and manual URL edits
  window.addEventListener('hashchange', handler);

  // Listen for programmatic changes via goHash
  document.addEventListener('hashChangeEvent', (e) => {
    callback(e.detail || getHash());
  });

  return () => {
    window.removeEventListener('hashchange', handler);
  };
}
