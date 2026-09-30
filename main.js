/* ─ main.js – CyberSafe client-side logic ─ */

// ── Mobile navigation toggle ──
(function () {
  const toggle = document.querySelector('.nav-toggle');
  const links  = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => {
      links.classList.toggle('open');
      toggle.textContent = links.classList.contains('open') ? '✕' : '☰';
    });
  }
})();

// ── Flash message dismiss ──
document.querySelectorAll('.flash-close').forEach(btn => {
  btn.addEventListener('click', () => {
    btn.closest('.flash')?.remove();
  });
});

// Auto-dismiss flash messages after 6 seconds
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => {
    el.style.transition = 'opacity 0.5s';
    el.style.opacity    = '0';
    setTimeout(() => el.remove(), 500);
  });
}, 6000);

// ── Password strength meter ──
function calcStrength(pwd) {
  let score = 0;
  if (pwd.length >= 8)  score++;
  if (pwd.length >= 12) score++;
  if (/[A-Z]/.test(pwd)) score++;
  if (/[a-z]/.test(pwd)) score++;
  if (/\d/.test(pwd))    score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;
  return score; // 0-6
}

const pwdInput = document.getElementById('password');
const pwdFill  = document.querySelector('.pwd-strength-fill');
const pwdText  = document.querySelector('.pwd-strength-text');

if (pwdInput && pwdFill) {
  const colors = ['#ff4d6d','#ff4d6d','#ffd60a','#ffd60a','#00d4ff','#00ff88','#00ff88'];
  const labels = ['','Very Weak','Weak','Fair','Good','Strong','Very Strong'];
  pwdInput.addEventListener('input', () => {
    const s   = calcStrength(pwdInput.value);
    const pct = Math.round((s / 6) * 100);
    pwdFill.style.width      = pct + '%';
    pwdFill.style.background = colors[s];
    if (pwdText) { pwdText.textContent = labels[s]; pwdText.style.color = colors[s]; }
  });
}

// ── Confirm password match indicator ──
const confirmInput = document.getElementById('confirm_password');
if (pwdInput && confirmInput) {
  function checkMatch() {
    const ok = pwdInput.value && pwdInput.value === confirmInput.value;
    confirmInput.style.borderColor = ok ? 'var(--green)' : (confirmInput.value ? 'var(--red)' : '');
  }
  confirmInput.addEventListener('input', checkMatch);
  pwdInput.addEventListener('input', checkMatch);
}

// ── Copy Complaint ID to clipboard ──
const copyBtn = document.getElementById('copy-cid');
if (copyBtn) {
  copyBtn.addEventListener('click', () => {
    const cid = copyBtn.dataset.cid;
    navigator.clipboard.writeText(cid).then(() => {
      const orig = copyBtn.textContent;
      copyBtn.textContent = '✓ Copied!';
      setTimeout(() => { copyBtn.textContent = orig; }, 2000);
    });
  });
}

// ── Character counter for description textarea ──
const descTextarea   = document.getElementById('description');
const descCounter    = document.getElementById('desc-counter');
if (descTextarea && descCounter) {
  descTextarea.addEventListener('input', () => {
    const len = descTextarea.value.length;
    descCounter.textContent = `${len} characters${len < 30 ? ' (minimum 30)' : ''}`;
    descCounter.style.color = len < 30 ? 'var(--red)' : 'var(--green)';
  });
}

// ── File upload preview / validation ──
const fileInput   = document.getElementById('evidence');
const filePreview = document.getElementById('file-preview');
if (fileInput && filePreview) {
  fileInput.addEventListener('change', () => {
    const file = fileInput.files[0];
    if (!file) { filePreview.textContent = ''; return; }
    const allowed = ['png','jpg','jpeg','gif','pdf','txt'];
    const ext = file.name.split('.').pop().toLowerCase();
    if (!allowed.includes(ext)) {
      filePreview.textContent = '⚠ File type not allowed.';
      filePreview.style.color = 'var(--red)';
      fileInput.value = '';
    } else {
      const kb = (file.size / 1024).toFixed(1);
      filePreview.textContent = `✓ ${file.name} (${kb} KB)`;
      filePreview.style.color = 'var(--green)';
    }
  });
}

// ── Complaint tracking input – uppercase on type ──
const trackInput = document.getElementById('track-input');
if (trackInput) {
  trackInput.addEventListener('input', () => {
    const cur = trackInput.selectionStart;
    trackInput.value = trackInput.value.toUpperCase();
    trackInput.setSelectionRange(cur, cur);
  });
}

// ── Admin: confirm before destructive actions ──
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', (e) => {
    if (!confirm(el.dataset.confirm)) e.preventDefault();
  });
});

// ── Animated counter for stat numbers ──
function animateCounter(el) {
  const target = parseInt(el.dataset.target || el.textContent, 10);
  if (isNaN(target)) return;
  let current = 0;
  const step  = Math.max(1, Math.ceil(target / 40));
  const timer = setInterval(() => {
    current = Math.min(current + step, target);
    el.textContent = current;
    if (current >= target) clearInterval(timer);
  }, 30);
}

const counters = document.querySelectorAll('.stat-num[data-target]');
if ('IntersectionObserver' in window) {
  const obs = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { animateCounter(e.target); obs.unobserve(e.target); }});
  }, { threshold: 0.6 });
  counters.forEach(c => obs.observe(c));
} else {
  counters.forEach(animateCounter);
}

// ── Incident date: block future dates ──
const incidentDate = document.getElementById('incident_date');
if (incidentDate) {
  incidentDate.setAttribute('max', new Date().toISOString().split('T')[0]);
}
