/**
 * BloodDrop — Runtime Configuration
 *
 * Single service deployment: Django serves both frontend + API.
 * API is on the same origin, so no absolute URL needed.
 *
 * Set to empty string = uses same-origin /api/ automatically.
 * Only change this if you split frontend/backend to separate services.
 */

window.__BLOODDROP_API__ = '';  // same-origin: /api/ will be used
