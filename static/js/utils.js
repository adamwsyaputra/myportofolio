/**
 * Shared JavaScript Utilities
 * Provides global helper functions for CSRF cookie parsing and XSS escaping.
 */

/**
 * Parses and returns the value of a cookie by name.
 * @param {string} name - Name of the cookie (e.g., 'csrftoken')
 * @returns {string|null} - Cookie value or null if not found
 */
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

/**
 * Escapes special HTML characters in dynamic data to prevent Stored & Reflected XSS.
 * @param {*} value - The string or value to sanitize
 * @returns {string} - HTML entity encoded string
 */
function escapeHtml(value) {
  return String(value ?? '')
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}

// Expose explicitly to global window object
window.getCookie = getCookie;
window.escapeHtml = escapeHtml;
