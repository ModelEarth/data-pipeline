/**
 * Flask Server Availability Check Utility
 * 
 * Checks if the Flask server is running on port 5000
 */

const FLASK_SERVER_URL = 'http://localhost:5001';
const FLASK_HEALTH_ENDPOINT = `${FLASK_SERVER_URL}/health`;

let flaskAvailable = null;
let checkPromise = null;

/**
 * Check if Flask server is available
 * @returns {Promise<boolean>} True if Flask server is available
 */
export async function checkFlaskAvailability() {
  // Return cached result if available
  if (flaskAvailable !== null) {
    return flaskAvailable;
  }

  // Return existing promise if check is in progress
  if (checkPromise) {
    return checkPromise;
  }

  // Perform check
  checkPromise = fetch(FLASK_HEALTH_ENDPOINT, {
    method: 'GET',
    mode: 'cors',
    cache: 'no-cache',
    signal: AbortSignal.timeout(2000) // 2 second timeout
  })
    .then(response => {
      if (response.ok) {
        flaskAvailable = true;
        return true;
      } else {
        flaskAvailable = false;
        return false;
      }
    })
    .catch(error => {
      // Network error or timeout - Flask not available
      flaskAvailable = false;
      return false;
    })
    .finally(() => {
      // Clear promise after completion
      checkPromise = null;
    });

  return checkPromise;
}

/**
 * Reset the cached availability status
 * Useful for re-checking after starting Flask server
 */
export function resetFlaskAvailability() {
  flaskAvailable = null;
  checkPromise = null;
}

/**
 * Get Flask server URL
 */
export function getFlaskServerUrl() {
  return FLASK_SERVER_URL;
}

/**
 * Get Flask API endpoint for running nodes
 */
export function getFlaskRunEndpoint() {
  return `${FLASK_SERVER_URL}/api/nodes/run`;
}

