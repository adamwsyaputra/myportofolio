let toastTimer;

function hideToastManual() {
  const toastComponent = document.getElementById('toast-component');
  if (!toastComponent) return;

  if (toastTimer) {
    clearTimeout(toastTimer);
  }

  toastComponent.classList.remove('toast-show');
  toastComponent.classList.add('toast-hidden');

  toastTimer = setTimeout(() => {
    try {
      if (toastComponent.matches(':popover-open')) {
        toastComponent.hidePopover();
      }
    } catch (e) {
      // Safe fallback
    }
  }, 300);
}

function showToast(title, message, type = 'normal', duration = 3000) {
  const toastComponent = document.getElementById('toast-component');
  const toastTitle = document.getElementById('toast-title');
  const toastMessage = document.getElementById('toast-message');
  const toastTag = document.getElementById('toast-tag');
  const toastIconSymbol = document.getElementById('toast-icon-symbol');

  if (!toastComponent || !toastTitle || !toastMessage) {
    return;
  }

  // Cancel existing timers with clearTimeout(toastTimer)
  if (toastTimer) {
    clearTimeout(toastTimer);
  }

  // Reset previously applied color classes before adding the active one
  toastComponent.classList.remove('toast-normal', 'toast-success', 'toast-error');
  toastComponent.classList.add(`toast-${type}`);

  // Set content via textContent (avoids accidental HTML/XSS injection)
  toastTitle.textContent = title;
  toastMessage.textContent = message;

  // Update comic tag and icon symbol if elements exist
  if (toastTag) {
    if (type === 'success') {
      toastTag.textContent = 'SUCCESS // VERIFIED';
    } else if (type === 'error') {
      toastTag.textContent = 'ALERT // ATTENTION';
    } else {
      toastTag.textContent = 'DISPATCH // SYSTEM';
    }
  }

  if (toastIconSymbol) {
    if (type === 'success') {
      toastIconSymbol.textContent = '✓';
    } else if (type === 'error') {
      toastIconSymbol.textContent = '!';
    } else {
      toastIconSymbol.textContent = '★';
    }
  }

  // Call toastComponent.showPopover()
  try {
    if (!toastComponent.matches(':popover-open')) {
      toastComponent.showPopover();
    }
  } catch (e) {
    toastComponent.showPopover();
  }

  // Trigger void toastComponent.offsetHeight; (forces DOM reflow so CSS transitions execute smoothly)
  void toastComponent.offsetHeight;

  // Swap .toast-hidden for .toast-show
  toastComponent.classList.remove('toast-hidden');
  toastComponent.classList.add('toast-show');

  // Use chained setTimeout calls to slide down, wait for animation (300ms), and finally execute hidePopover()
  toastTimer = setTimeout(() => {
    toastComponent.classList.remove('toast-show');
    toastComponent.classList.add('toast-hidden');

    toastTimer = setTimeout(() => {
      try {
        if (toastComponent.matches(':popover-open')) {
          toastComponent.hidePopover();
        }
      } catch (e) {
        // Safe fallback
      }
    }, 300);
  }, duration);
}

// Make showToast accessible globally
window.showToast = showToast;
window.hideToastManual = hideToastManual;
