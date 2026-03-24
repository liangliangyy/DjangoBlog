/**
 * Legacy comment reply helpers (old non-Alpine comment templates).
 * Exposes do_reply / cancel_reply globally and sets up delegated click handlers
 * for data-action="do-reply" / data-action="cancel-reply" attributes.
 */

function do_reply(parentid) {
  document.getElementById('id_parent_comment_id').value = parentid;
  const form = document.getElementById('commentform');
  const target = document.getElementById('div-comment-' + parentid);
  if (target && form) target.appendChild(form);
  const cancelBtn = document.getElementById('cancel_comment');
  if (cancelBtn) {
    cancelBtn.classList.remove('hidden');
    cancelBtn.classList.add('inline-flex');
  }
}

function cancel_reply() {
  document.getElementById('id_parent_comment_id').value = '';
  const form = document.getElementById('commentform');
  const respond = document.getElementById('respond');
  if (form && respond) respond.appendChild(form);
  const cancelBtn = document.getElementById('cancel_comment');
  if (cancelBtn) {
    cancelBtn.classList.add('hidden');
    cancelBtn.classList.remove('inline-flex');
  }
}

export function initLegacyCommentsFeature() {
  // Expose as globals so any remaining inline references still work
  window.do_reply = do_reply;
  window.cancel_reply = cancel_reply;

  // Delegated handler for data-action attributes
  document.addEventListener('click', function (e) {
    const doReplyBtn = e.target.closest('[data-action="do-reply"]');
    if (doReplyBtn) {
      e.preventDefault();
      do_reply(doReplyBtn.dataset.pk);
      return;
    }
    const cancelBtn = e.target.closest('[data-action="cancel-reply"]');
    if (cancelBtn) {
      e.preventDefault();
      cancel_reply();
    }
  });
}
