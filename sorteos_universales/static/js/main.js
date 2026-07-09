/* ══════════════════════════════════════════════
   SORTEOS UNIVERSALES — main.js
   · Stars canvas animation
   · Countdown timers
   · Ticket selection & purchase modal
   · Auto-dismiss flashes
══════════════════════════════════════════════ */

/* ── STARS ── */
(function initStars() {
  const canvas = document.getElementById('star-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let stars = [];
  function resize() { canvas.width = window.innerWidth; canvas.height = window.innerHeight; }
  function create() {
    stars = [];
    const n = Math.floor((canvas.width * canvas.height) / 4500);
    for (let i = 0; i < n; i++)
      stars.push({ x: Math.random()*canvas.width, y: Math.random()*canvas.height,
                   r: Math.random()*1.4+.3, speed: Math.random()*.004+.001, phase: Math.random()*Math.PI*2 });
  }
  function draw(t) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (const s of stars) {
      const a = .35 + .65*Math.abs(Math.sin(s.phase + t*s.speed));
      ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
      ctx.fillStyle = `rgba(255,255,255,${a})`; ctx.fill();
    }
    requestAnimationFrame(draw);
  }
  resize(); create(); requestAnimationFrame(draw);
  window.addEventListener('resize', () => { resize(); create(); });
})();

/* ── AUTO-DISMISS FLASH (5 s) ── */
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => el.remove());
}, 5000);

/* ══════════════════════════════════════════════
   COUNTDOWN
══════════════════════════════════════════════ */
function updateCountdowns() {
  document.querySelectorAll('[data-end]').forEach(el => {
    const end  = new Date(el.dataset.end);
    const diff = end - new Date();
    if (diff <= 0) {
      el.innerHTML = '<span style="color:#ef4444;font-size:.85rem;">Tiempo agotado</span>';
      return;
    }
    const d = Math.floor(diff / 86400000);
    const h = Math.floor((diff % 86400000) / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    const s = Math.floor((diff % 60000) / 1000);
    el.innerHTML = `
      <div class="cd-block"><span class="cd-digit">${String(d).padStart(2,'0')}</span><span class="cd-label">días</span></div>
      <div class="cd-block"><span class="cd-digit">${String(h).padStart(2,'0')}</span><span class="cd-label">hrs</span></div>
      <div class="cd-block"><span class="cd-digit">${String(m).padStart(2,'0')}</span><span class="cd-label">min</span></div>
      <div class="cd-block"><span class="cd-digit">${String(s).padStart(2,'0')}</span><span class="cd-label">seg</span></div>`;
  });
}
updateCountdowns();
setInterval(updateCountdowns, 1000);

/* ══════════════════════════════════════════════
   TICKET SELECTION
══════════════════════════════════════════════ */
const selectedTickets = new Set();

function getTicketStyleClass() {
  const grid = document.getElementById('ticket-grid');
  return grid ? grid.dataset.style || 'galactico' : 'galactico';
}

window.toggleTicket = function(el) {
  const num = parseInt(el.dataset.num);
  if (el.classList.contains('sold')) return;
  const style = getTicketStyleClass();
  const cls   = `t-${style}`;
  if (selectedTickets.has(num)) {
    selectedTickets.delete(num);
    el.classList.remove('selected'); el.classList.add('available');
  } else {
    selectedTickets.add(num);
    el.classList.remove('available'); el.classList.add('selected');
  }
  updateSummary();
};

function updateSummary() {
  const price = parseFloat(document.getElementById('ticket-price-val')?.dataset.price || 0);
  const countEl = document.getElementById('selected-count');
  const totalEl = document.getElementById('selected-total');
  const btnEl   = document.getElementById('btn-comprar');
  if (countEl) countEl.textContent = selectedTickets.size;
  if (totalEl) totalEl.textContent = `$${(selectedTickets.size * price).toFixed(2)}`;
  if (btnEl)   btnEl.disabled = selectedTickets.size === 0;
}

/* ── PURCHASE MODAL ── */
window.openPayModal = function() {
  if (selectedTickets.size === 0) return;
  const price   = parseFloat(document.getElementById('ticket-price-val')?.dataset.price || 0);
  const total   = (selectedTickets.size * price).toFixed(2);
  const tickStr = [...selectedTickets].sort((a,b)=>a-b).map(n=>`#${String(n).padStart(3,'0')}`).join(', ');
  const qrSrc   = document.getElementById('qr-data')?.dataset.src || '';
  const userName  = document.getElementById('user-info')?.dataset.name || '';
  const userEmail = document.getElementById('user-info')?.dataset.email || '';

  const qrHtml = qrSrc
    ? `<img src="${qrSrc}" alt="QR de pago" style="width:180px;height:180px;object-fit:contain;border-radius:12px;border:1px solid rgba(109,40,217,.4);margin:0 auto;display:block;"/>`
    : `<div style="width:180px;height:180px;background:#111c3a;border:2px dashed rgba(109,40,217,.4);border-radius:12px;margin:0 auto;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.5rem;color:#94a3b8;font-size:.8rem;text-align:center;">📱<br/>QR no configurado</div>`;

  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.id = 'pay-modal';
  modal.innerHTML = `
  <div class="modal-box" onclick="event.stopPropagation()">
    <h2 style="font-family:'Orbitron',sans-serif;font-weight:700;font-size:1.1rem;color:#c4b5fd;margin-bottom:.25rem;">💳 Completar Compra</h2>
    <p style="color:var(--mist);font-size:.82rem;margin-bottom:1.25rem;">Realiza el pago y registra tus datos para confirmar la compra.</p>

    <div style="background:rgba(34,211,238,.05);border:1px solid rgba(34,211,238,.2);border-radius:12px;padding:1rem;margin-bottom:1.25rem;font-size:.85rem;">
      <p style="color:var(--mist);">Boletos: <strong style="color:#e2e8f0;">${tickStr}</strong></p>
      <p style="color:var(--mist);">Cantidad: <strong style="color:var(--cyan);">${selectedTickets.size}</strong></p>
      <p style="color:var(--mist);">Total: <strong style="color:var(--gold);font-size:1.05rem;">$${total} USD</strong></p>
    </div>

    <p style="font-size:.78rem;color:var(--mist);text-transform:uppercase;letter-spacing:.08em;margin-bottom:.75rem;">Escanea el QR para pagar:</p>
    ${qrHtml}

    <div class="divider" style="margin:1.25rem 0;"></div>
    <p style="font-size:.78rem;color:var(--mist);text-transform:uppercase;letter-spacing:.08em;margin-bottom:.75rem;">Datos del comprador</p>

    <form id="pay-form" method="POST" action="${document.getElementById('pay-form-action')?.dataset.url}" style="display:flex;flex-direction:column;gap:.85rem;">
      <input type="hidden" name="csrf_token" value="${document.querySelector('meta[name=csrf-token]')?.content || ''}"/>
      ${[...selectedTickets].map(n=>`<input type="hidden" name="tickets" value="${n}"/>`).join('')}

      <div class="form-group">
        <label class="form-label">Nombre Completo</label>
        <input class="form-control" name="buyer_name" type="text" value="${userName}" placeholder="Tu nombre completo" required/>
      </div>
      <div class="form-group">
        <label class="form-label">Correo Electrónico</label>
        <input class="form-control" name="buyer_email" type="email" value="${userEmail}" placeholder="correo@ejemplo.com" required/>
      </div>
      <div class="form-group">
        <label class="form-label">Teléfono</label>
        <input class="form-control" name="buyer_phone" type="tel" placeholder="+591 70000000"/>
      </div>
      <div class="form-group">
        <label class="form-label">Referencia de Pago</label>
        <input class="form-control" name="pay_ref" type="text" placeholder="Ej: TRANSF-20240615-001"/>
      </div>
      <div style="display:flex;gap:.75rem;margin-top:.25rem;">
        <button type="button" class="btn btn-secondary flex-1" onclick="document.getElementById('pay-modal').remove()">Cancelar</button>
        <button type="submit" class="btn btn-primary flex-1">✓ Confirmar Compra</button>
      </div>
    </form>
  </div>`;
  modal.addEventListener('click', e => { if (e.target === modal) modal.remove(); });
  document.body.appendChild(modal);
};

/* ── CONFIRM DELETION ── */
window.confirmDelete = function(msg, formId) {
  if (confirm(msg)) {
    document.getElementById(formId).submit();
  }
};

/* ── SELECT ALL / DESELECT ── */
window.selectRandom = function(qty) {
  const available = [...document.querySelectorAll('.ticket.available')];
  const shuffled  = available.sort(() => Math.random() - .5).slice(0, qty);
  shuffled.forEach(el => { if (!selectedTickets.has(parseInt(el.dataset.num))) toggleTicket(el); });
};
