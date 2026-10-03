/**
 * Features: Stacking upwards, independent in/out animations, auto-dismiss, and hover-to-pause
 * Integrated with Top Layer (popover="manual") to render cleanly above modals and backdrops.
 */

function getOrCreateToastContainer() {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    container.setAttribute('popover', 'manual');
    container.setAttribute('aria-live', 'polite');
    container.setAttribute('aria-atomic', 'true');
    document.body.appendChild(container);
  } else if (!container.hasAttribute('popover')) {
    container.setAttribute('popover', 'manual');
  }
  return container;
}

function dismissToastItem(toastEl) {
  if (!toastEl || toastEl._isDismissing) return;
  toastEl._isDismissing = true;

  if (toastEl._dismissTimer) {
    clearTimeout(toastEl._dismissTimer);
  }

  // Trigger individual out-animation
  toastEl.classList.remove('toast-enter-active');
  toastEl.classList.add('toast-exit-active');

  // Remove from DOM once out-animation completes
  setTimeout(() => {
    const container = toastEl.parentElement || document.getElementById('toast-container');
    try {
      if (toastEl.parentNode) {
        toastEl.parentNode.removeChild(toastEl);
      }
    } catch (e) {
      // Safe fallback
    }

    if (container) {
      const activeToasts = container.querySelectorAll('.toast-item:not(.toast-exit-active)');
      if (activeToasts.length === 0) {
        try {
          if (typeof container.hidePopover === 'function' && container.matches(':popover-open')) {
            container.hidePopover();
          }
        } catch (e) {
          // Safe fallback
        }
      }
    }
  }, 350);
}

function showToast(title, message, type = 'normal', duration = 3000) {
  const container = getOrCreateToastContainer();

  // Promote container into the Top Layer so it floats above modals and backdrops
  try {
    if (typeof container.showPopover === 'function') {
      if (!container.matches(':popover-open')) {
        container.showPopover();
      } else {
        // Re-promote to top of the top-layer stack above any newly opened modal/dialog
        container.hidePopover();
        container.showPopover();
      }
    }
  } catch (e) {
    // Graceful fallback for non-popover environments
  }

  // Limit stack to maximum 3 visible toasts to prevent overflowing viewport
  const activeToasts = container.querySelectorAll('.toast-item:not(.toast-exit-active)');
  if (activeToasts.length >= 3) {
    dismissToastItem(activeToasts[0]);
  }

  let tagText = 'DISPATCH // SYSTEM';
  let iconSymbol = '★';
  if (type === 'success') {
    tagText = 'SUCCESS // VERIFIED';
    iconSymbol = '✓';
  } else if (type === 'error') {
    tagText = 'ALERT // ATTENTION';
    iconSymbol = '!';
  }

  const toastEl = document.createElement('div');
  toastEl.className = `toast-item toast-${type}`;
  toastEl.setAttribute('role', 'status');

  toastEl.innerHTML = `
    <div class="toast-header-bar">
      <div class="toast-dots">
        <span class="comic-dot red"></span>
        <span class="comic-dot yellow"></span>
        <span class="comic-dot green"></span>
      </div>
      <span class="toast-badge-tag">${tagText}</span>
      <button type="button" class="toast-close-btn" aria-label="Dismiss notification">&times;</button>
    </div>
    <div class="toast-body">
      <div class="toast-icon-box">
        <span class="toast-icon-symbol">${iconSymbol}</span>
      </div>
      <div class="toast-content">
        <h3 class="toast-title"></h3>
        <p class="toast-message"></p>
      </div>
    </div>
  `;

  // Safely assign title and message via textContent (prevent XSS injection)
  toastEl.querySelector('.toast-title').textContent = title;
  toastEl.querySelector('.toast-message').textContent = message;

  // Dismiss button handler
  const closeBtn = toastEl.querySelector('.toast-close-btn');
  if (closeBtn) {
    closeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      dismissToastItem(toastEl);
    });
  }

  // Auto-dismiss timer
  toastEl._dismissTimer = setTimeout(() => {
    dismissToastItem(toastEl);
  }, duration);

  // Pause timer on hover, resume when mouse leaves
  toastEl.addEventListener('mouseenter', () => {
    if (toastEl._dismissTimer) {
      clearTimeout(toastEl._dismissTimer);
    }
  });

  toastEl.addEventListener('mouseleave', () => {
    if (!toastEl._isDismissing) {
      toastEl._dismissTimer = setTimeout(() => {
        dismissToastItem(toastEl);
      }, duration / 2);
    }
  });

  // Append new toast (stacks upwards due to flex-direction: column-reverse on container)
  container.appendChild(toastEl);

  // Force DOM reflow to trigger smooth in-animation
  void toastEl.offsetHeight;
  requestAnimationFrame(() => {
    toastEl.classList.add('toast-enter-active');
  });

  return toastEl;
}

// Backward compatibility helper
function hideToastManual() {
  const container = document.getElementById('toast-container');
  if (container) {
    const activeToasts = container.querySelectorAll('.toast-item:not(.toast-exit-active)');
    if (activeToasts.length > 0) {
      dismissToastItem(activeToasts[activeToasts.length - 1]);
    }
  }
}

// Global exposure
window.showToast = showToast;
window.dismissToastItem = dismissToastItem;
window.hideToastManual = hideToastManual;
