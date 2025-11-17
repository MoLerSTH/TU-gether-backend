// app/static/js/me_registrations.js

(function () {

  const $ = (s, r = document) => r.querySelector(s);

  const listEl = $('#list');

  const tpl = $('#card-tpl');

  const state = { rows: [], all: [] };



  // --- date helpers (รองรับ ISO และ Firestore Timestamp) ---

  function toDate(v) {

    if (!v) return null;

    if (typeof v === 'object' && typeof v.seconds === 'number') {

      return new Date(v.seconds * 1000);

    }

    const d = new Date(v);

    return isNaN(d) ? null : d;

  }

  function fmtDate(v) {

    const d = toDate(v);

    return d ? d.toLocaleString() : '-';

  }



  // --- Render ---

  function render() {

    listEl.innerHTML = '';

    for (const row of state.rows) {

      const node = tpl.content.cloneNode(true);

      const img = node.querySelector('[data-field="picture"]');

      const title = node.querySelector('[data-field="title"]');

      const meta = node.querySelector('[data-field="meta"]');

      const registered = node.querySelector('[data-field="registered"]'); // ต้องมี <div data-field="registered"></div> ใน template

      const badges = node.querySelector('[data-field="badges"]');

      const btnCancel = node.querySelector('[data-action="cancel"]');

      const aCert = node.querySelector('[data-action="cert"]');



      // --- รูป ---

      img.src = row.picture_url || '/static/placeholder.png';

      img.alt = row.event_title || 'event';



      // --- ข้อมูลกิจกรรม ---

      title.textContent = row.event_title || '(no title)';

      meta.textContent = `${fmtDate(row.event_date)} • ${row.faculty || ''} • ${row.category || ''}`;



      // --- เวลาที่ลงทะเบียน ---

      if (registered) {

        registered.textContent = `Registered: ${fmtDate(row.registered_at)}`;

        registered.title = String(row.registered_at ?? '');

      }



      // --- แสดงสถานะ ---

      badges.innerHTML = `

        <span class="px-2 py-0.5 border rounded mr-1">Event: ${row.event_status}</span>

        <span class="px-2 py-0.5 border rounded">Me: ${row.user_status}</span>

      `;



      // --- Logic สำหรับปุ่ม Cancel ---

      const isEventOpen = String(row.event_status || '').toLowerCase() === 'open';

      const canCancel = isEventOpen && row.user_status === 'confirmed';



      // ✅ ปุ่มแสดงตลอด แต่จะถูก disable ถ้ายกเลิกไม่ได้

      btnCancel.disabled = !canCancel;

      btnCancel.title = canCancel

        ? 'Click to cancel registration'

        : 'Cancel is available only while the event is Open';

      btnCancel.classList.toggle('opacity-50', !canCancel);



      btnCancel.onclick = async () => {

        if (!canCancel) {

          alert('You can only cancel when the event is still Open.');

          return;

        }

        if (!confirm('Cancel this registration?')) return;

        const r = await fetch(`/api/me/registrations/${row.event_id}`, { method: 'DELETE' });

        if (!r.ok) {

          const j = await r.json().catch(() => ({}));

          alert(j.detail || 'Cancel failed');

          return;

        }

        await reload();

      };



      // --- Certificate ---

      if (row.certificate_url) {

        aCert.classList.remove('hidden');

        aCert.href = row.certificate_url;

        aCert.textContent = 'Certificate';

      }



      listEl.appendChild(node);

    }

  }



  // --- Filter ---

  function applyFilter() {

    const q = ($('#search-text').value || '').toLowerCase();

    const st = $('#status-filter').value || '';

    state.rows = state.all.filter(x => {

      const okQ = !q || (x.event_title || '').toLowerCase().includes(q);

      const okS = !st || x.user_status === st;

      return okQ && okS;

    });

    render();

  }



  // --- Reload ---

  async function reload() {

    const st = $('#status-filter').value;

    const url = st

      ? `/api/me/registrations?status=${encodeURIComponent(st)}`

      : '/api/me/registrations';

    const res = await fetch(url);

    if (!res.ok) {

      const j = await res.json().catch(() => ({}));

      console.error('Load registrations failed:', res.status, j);

      alert(j.detail || `Failed to load registrations (${res.status})`);

      state.all = [];

      applyFilter();

      return;

    }

    state.all = await res.json();

    applyFilter();

  }



  // --- Event bindings ---

  $('#reload-btn').onclick = reload;

  $('#status-filter').onchange = applyFilter;

  $('#search-text').oninput = applyFilter;



  reload();

})();