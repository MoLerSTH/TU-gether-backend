// app/static/js/admin_event.js
(function () {
  const $  = (s, r = document) => r.querySelector(s);

  // ---- DOM ----
  const addBtn     = $('#add-btn');
  const overlay    = $('#overlay');
  const modal      = $('#modal');
  const closeBtn   = $('#close-btn');
  const form       = $('#event-form');
  const saveBtn    = $('#save-btn');

  const tbBody     = $('#table-body');
  const reloadBtn  = $('#reload-btn');
  const filterText = $('#filter-text');

  // Inputs
  const $title     = $('#event-title');
  const $major     = $('#event-major');
  const $faculty   = $('#event-faculty');
  const $category  = $('#event-category');
  const $eventDate = $('#event-date');
  const $deadline  = $('#deadline-date');
  const $openAt    = $('#register-open-at');    
  const $status    = $('#event-status');
  const $picture   = $('#event-picture');
  const $tags      = $('#event-tags');
  const $detail    = $('#event-detail');
  const $min       = $('#event-min');
  const $max       = $('#event-max');
  const $audience = $('#audience-type');
  const $year     = $('#student-year');

  $status && ($status.disabled = true);
  $status && ($status.title = "สถานะจะถูกตั้งอัตโนมัติตามวันเวลาที่กำหนด");
  

  // Map enum value to label
function statusLabel(val) {
  const k = String(val || '').split('.').pop().toUpperCase(); // "StatusEnum.OPEN" -> "OPEN"
  const map = { OPEN:'Open', CLOSE:'Close', FULL:'Full', UPCOMING:'Upcoming' }; // หรือจะแปลเป็นไทยก็ได้
  return map[k] || k;
}
// Audience type change
function toggleStudentFields() {
  const mode = $audience?.value || 'student';   // student | public | all
  const disabled = (mode === 'public');

  // ปิด/เปิด
  [$faculty, $major, $year].forEach(el => {
    if (!el) return;
    el.disabled = disabled;
  });

  if (disabled) {
    // บุคคลทั่วไป -> เคลียร์ค่า (หรือจะตั้งเป็น "ทั้งหมด" ก็ได้)
    if ($faculty) $faculty.value = '';
    if ($major)   {
      $major.innerHTML = `<option value="">-- เลือกสาขา --</option>`;
      $major.value = '';
    }
    if ($year)    $year.value = 'all';
  }
}

  



// ---- Dynamic Faculty & Major Selection ----
function getMajorsData() {
  try { if (typeof majorsData !== 'undefined' && majorsData) return majorsData; } catch {}
  if (typeof window !== 'undefined' && window.majorsData) return window.majorsData;
  return null;
}

const thaiSort = (a,b)=> a.localeCompare(b,'th',{ sensitivity:'base', numeric:true });

function populateMajors(faculty){
  const majorSelect = document.getElementById('event-major');
  if (!majorSelect) return;

  // เคลียร์ก่อนเสมอ + ใส่ placeholder
  majorSelect.innerHTML = `<option value="">-- เลือกสาขา --</option>`;

  // ถ้าเลือกคณะ = "ทั้งหมด" ให้สาขามี "ทั้งหมด" และเลือกให้เลย
  if (faculty === 'ทั้งหมด') {
    const opt = document.createElement('option');
    opt.value = 'ทั้งหมด';
    opt.textContent = 'ทั้งหมด';
    opt.selected = true;
    majorSelect.appendChild(opt);
    return;
  }

  // กรณีคณะปกติ
  const MD = getMajorsData();
  if (!faculty || !MD || !MD[faculty]) return;

  MD[faculty]
    .filter(m => m && m !== 'ทั้งหมด')
    .slice()
    .sort(thaiSort)
    .forEach(m => {
      const opt = document.createElement('option');
      opt.value = m;
      opt.textContent = m;
      majorSelect.appendChild(opt);
    });
}

function populateFaculties(){
  const facultySelect = document.getElementById('event-faculty');
  if (!facultySelect) return;

  const MD = getMajorsData();
  if (!MD || typeof MD !== 'object') {
    console.error('majorsData ยังไม่ถูกโหลด/ไม่ถูกต้อง');
    return;
  }

  // หัวตัวเลือก + "ทั้งหมด" (เฉพาะหัว)
  facultySelect.innerHTML = `
    <option value="">-- เลือกคณะ --</option>
    <option value="ทั้งหมด">ทั้งหมด</option>
  `;

  [...new Set(Object.keys(MD))]
    .filter(f => f && f !== 'ทั้งหมด')
    .sort(thaiSort)
    .forEach(f => {
      const opt = document.createElement('option');
      opt.value = f;
      opt.textContent = f;
      facultySelect.appendChild(opt);
    });

  facultySelect.addEventListener('change', e => populateMajors(e.target.value));
}

// โหลดคณะเมื่อ DOM พร้อม
document.addEventListener('DOMContentLoaded', populateFaculties);
$audience?.addEventListener('change', toggleStudentFields);
addBtn?.addEventListener('click', (e)=>{
  e.preventDefault();
  form?.reset();
  if ($audience) $audience.value = 'student';
  if ($year)     $year.value = 'all';
  toggleStudentFields();
  showModal();
});

function fillFormFromItem(it){
  // ...
  if ($audience) $audience.value = it?.audience || it?.audience_type || 'student';
  toggleStudentFields();
  // ...
}



  // ---- State ----
  let allEvents = [];
  let editingId = null;

  const esc = (s='') => String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
  function toIsoZ(local){ if(!local) return null; const d=new Date(local); return isNaN(d)?null:d.toISOString(); }
  function isoToLocalInput(iso){
    if(!iso) return '';
    const d = new Date(iso);
    if (isNaN(d)) return '';
    const p = n => String(n).padStart(2,'0');
    return `${d.getFullYear()}-${p(d.getMonth()+1)}-${p(d.getDate())}T${p(d.getHours())}:${p(d.getMinutes())}`;
  }
  function toIntOrNull(v) {
    if (v === undefined || v === null) return null;
    const s = String(v).trim();
    if (s === "") return null;
    const n = Number(s);
    return Number.isFinite(n) ? Math.trunc(n) : null;
  }
  const pruneNullish = (obj) => Object.fromEntries(Object.entries(obj).filter(([,v]) => v !== null && v !== undefined));
  const toast = (m)=> alert(m);

  async function api(url, opts = {}) {
    const r = await fetch(url, { credentials: 'include', ...opts });
    if (!r.ok) {
      let msg = 'เกิดข้อผิดพลาด';
      try { const j = await r.json(); msg = j.detail || msg; } catch {}
      console.error("[Admin API error]", url, msg);
      throw new Error(msg);
    }
    try { return await r.json(); } catch { return null; }
  }

  // ---- Modal (ฟอร์ม) ----
  function reallyHide() {
    if (overlay) { overlay.classList.remove('open'); overlay.hidden = true; overlay.style.display = 'none'; }
    if (modal)   { modal.classList.remove('open');   modal.hidden = true;   modal.style.display   = 'none'; }
    document.body.style.overflow = '';
  }
  function showModal() {
    if (overlay) { overlay.hidden = false; overlay.classList.add('open'); overlay.style.display = 'block'; }
    if (modal)   { modal.hidden   = false; modal.classList.add('open');   modal.style.display   = 'grid'; }
    document.body.style.overflow = 'hidden';
    ($title || modal.querySelector('input,select,textarea'))?.focus();
  }
  function hideModal() {
    editingId = null;
    form?.reset();
    reallyHide();
  }
  reallyHide();

  // ---- Registrations Modal ----
  let regModal = null;
  function ensureRegModal(){
    if (regModal && document.body.contains(regModal)) return regModal;
    regModal = document.createElement('div');
    regModal.id = 'reglist-modal';
    regModal.className = 'modal';
    regModal.hidden = true;
    regModal.style.display = 'none';
    document.body.appendChild(regModal);
    return regModal;
  }

  function openRegModal(html){
    ensureRegModal();
    regModal.innerHTML = `
      <div class="modal-card" style="max-width:800px;">
        <h3 style="margin:12px 16px 8px 16px;">รายชื่อผู้ลงทะเบียน</h3>
        <div style="padding:0 16px 8px 16px; color:#6b7280; font-size:12px">เรียงตามเวลาลงทะเบียนล่าสุด</div>
        <div class="table-wrap" style="max-height:60vh; overflow:auto; padding:0 16px;">${html}</div>
        <div class="actions" style="display:flex;justify-content:flex-end;gap:8px;padding:12px 16px 16px;">
          <button class="btn" id="reglist-close-btn">ปิด</button>
        </div>
      </div>
    `;
    // show
    overlay.hidden = false; overlay.classList.add('open'); overlay.style.display = 'block';
    regModal.hidden = false; regModal.classList.add('open'); regModal.style.display = 'grid';
    document.body.style.overflow = 'hidden';

    // listeners (ครั้งเดียวต่อการเปิด)
    $('#reglist-close-btn', regModal)?.addEventListener('click', closeRegModal, { once: true });
    overlay.addEventListener('click', onOverlayCloseOnce, { once: true });
    document.addEventListener('keydown', onEscCloseOnce, { once: true });
  }

  function closeRegModal(){
    if (!regModal) return;
    overlay.classList.remove('open'); overlay.hidden = true; overlay.style.display = 'none';
    regModal.classList.remove('open'); regModal.hidden = true; regModal.style.display = 'none';
    regModal.innerHTML = '';
    document.body.style.overflow = '';
  }
  function onOverlayCloseOnce(e){ if (e.target === overlay) closeRegModal(); }
  function onEscCloseOnce(e){ if (e.key === 'Escape') closeRegModal(); }

  function fmtDate(val){
    if (!val) return '-';
    try {
      if (typeof val === 'string') return new Date(val).toLocaleString('th-TH');
      if (val.seconds) return new Date(val.seconds * 1000).toLocaleString('th-TH');
    } catch {}
    return String(val);
  }

  async function showRegistrations(eventId){
    try{
      const rows = await api(`/api/admin/events/${encodeURIComponent(eventId)}/registrations`);
      let html = '';
      if (!rows || !rows.length){
        html = `<div class="muted" style="padding:12px 0 16px;">— ยังไม่มีผู้ลงทะเบียน —</div>`;
      } else {
        html = `
          <table class="table" style="width:100%; border-collapse:collapse;">
            <thead>
              <tr>
                <th style="text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;">User ID</th>
                <th style="text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;">Fullname</th>
                <th style="text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;">Role</th>
                <th style="text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;">Reg At</th>
              </tr>
            </thead>
            <tbody>
              ${rows.map((r)=>`
                <tr>
                  <td style="padding:8px;border-bottom:1px solid #f3f4f6;">${esc(r.user_id || '')}</td>
                  <td style="padding:8px;border-bottom:1px solid #f3f4f6;">${esc(r.full_name || '')}</td>
                  <td style="padding:8px;border-bottom:1px solid #f3f4f6;">${esc(r.role || '')}</td>
                  <td style="padding:8px;border-bottom:1px solid #f3f4f6;">${esc(fmtDate(r.registered_at))}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `;
      }
      openRegModal(html);
    }catch(err){
      toast(err.message || 'โหลดรายชื่อไม่สำเร็จ');
    }
  }


  // ---- Fill/Collect ----
  function fillFormFromItem(it){
  $title.value     = it?.title || '';
  $detail.value    = it?.detail || '';
  $faculty.value   = it?.faculty || '';
  populateMajors($faculty.value);          // <-- เพิ่มบรรทัดนี้
  $major.value     = it?.major || it?.location || '';
  $category.value  = it?.category || '';
  if ($status) $status.value = statusLabel(it?.status || 'Upcoming');
  $picture.value   = it?.picture_url || '';
  $tags.value      = Array.isArray(it?.tags) ? it.tags.join(',') : (it?.tags || '');
  $eventDate.value = isoToLocalInput(it?.event_date);
  $deadline.value  = isoToLocalInput(it?.deadline_date);
  $openAt.value    = isoToLocalInput(it?.register_open_at);
  if ($min) $min.value = (it?.min_register ?? '').toString();
  if ($max) $max.value = (it?.max_register ?? '').toString();
  $audience && ($audience.value = it?.audience || 'student');
toggleStudentFields();  // ต้องเรียกก่อนเพื่อเปิด/ปิด field ให้ถูก

$faculty.value = it?.faculty || '';
populateMajors($faculty.value);

$year && ($year.value = it?.student_year || 'all');
$major.value = it?.major || it?.location || '';
}

  // (ฟังก์ชันนี้ถูกเรียกใช้โดย ImageKit wrapper ด้านล่างอีกที)
  let _originalFillForm = function (it) {
    $title.value = it?.title || '';
    $detail.value = it?.detail || '';
    $category.value = it?.category || '';
    if ($status) $status.value = statusLabel(it?.status || 'Upcoming');
    $picture.value = it?.picture_url || ''; // (hidden input)
    $tags.value = Array.isArray(it?.tags) ? it.tags.join(',') : (it?.tags || '');
    $eventDate.value = isoToLocalInput(it?.event_date);
    $deadline.value = isoToLocalInput(it?.deadline_date);
    $openAt.value = isoToLocalInput(it?.register_open_at);
    if ($min) $min.value = (it?.min_register ?? '').toString();
    if ($max) $max.value = (it?.max_register ?? '').toString();

    // --- ส่วนที่ต้องจัดการ Audience/Student ---
    $audience && ($audience.value = it?.audience || 'student');
    toggleStudentFields(); // เรียกก่อน เพื่อเปิด/ปิด field

    // ค่อยกำหนดค่า field ที่อาจถูกปิด
    $faculty.value = it?.faculty || '';
    populateMajors($faculty.value); // เรียกเพื่อเติมสาขาตามคณะ

    $year && ($year.value = it?.student_year || 'all');
    $major.value = it?.major || it?.location || ''; // location เป็น fallback? (คงไว้ตามเดิม)
  }

  // (ตัวแปร fillFormFromItem จะถูก override โดย ImageKit wrapper ด้านล่าง)
  // เราจะกำหนด _originalFillForm ให้เป็น fillFormFromItem ที่แท้จริงก่อน
  var fillFormFromItem = _originalFillForm;
  
 function collectPayload() {
  const audience = ($audience?.value || 'student'); // <-- มีจริงใน DOM

  const payload = {
  title:        $title.value.trim(),
  detail:       $detail.value.trim(),
  category:     $category.value.trim(),

  faculty:      $faculty?.value?.trim() || null,
  major:        $major?.value?.trim() || null,

  grade:        $year?.value || null,           
  audience:     audience,

  event_date:    toIsoZ($eventDate.value),
  deadline_date: toIsoZ($deadline.value),
  register_open_at: toIsoZ($openAt.value),

  picture_url:  $picture.value.trim() || null,
  tags:         ($tags.value || '').split(',').map(s=>s.trim()).filter(Boolean),
  min_register: $min ? toIntOrNull($min.value) : null,
  max_register: $max ? toIntOrNull($max.value) : null,
};

  // ถ้าไม่ใช่นักศึกษา -> เคลียร์ 3 ช่องออก
  if (audience !== 'student') {
    payload.faculty      = null;
    payload.major        = null;
    payload.student_year = null;
  }
  return pruneNullish(payload);
}


  function validatePayload(p){
  const norm = v => String(v||'').trim().toLowerCase();
  const mapAudience = (v) => {
    v = norm(v);
    if (v === 'student' || v === 'นักศึกษา') return 'student';
    if (v === 'public'  || v === 'บุคคลทั่วไป') return 'public';
    if (v === 'all'     || v === 'ทั้งหมด') return 'all';
    return 'student'; // fallback
  };

  const mode = mapAudience(p?.audience ?? $audience?.value ?? 'student'); // <-- ใช้ของ payload ก่อน
  const yearOk = (y) => ['1','2','3','4','all','ทั้งหมด'].includes(norm(y));

  const minVal = ('min_register' in p) ? p.min_register : null;
  const maxVal = ('max_register' in p) ? p.max_register : null;

  const mustBase = {
    'ชื่อกิจกรรม': p.title,
    'รายละเอียด': p.detail,
    'หมวดหมู่': p.category,
    'วันจัดกิจกรรม': p.event_date,
    'ปิดรับสมัคร': p.deadline_date,
  };

  // บังคับเฉพาะโหมดนักศึกษาเท่านั้น
  const must = (mode === 'student')
    ? { ...mustBase, 'คณะ': p.faculty, 'สาขาวิชา': p.major, 'ชั้นปี': (p.student_year ?? 'all') }
    : mustBase;

  for (const [label, val] of Object.entries(must)) {
    if (!val) { toast(`กรุณากรอกข้อมูลให้ครบ: ${label}`); return false; }
  }

  if (mode === 'student' && p.student_year && !yearOk(p.student_year)) {
    toast('ชั้นปีไม่ถูกต้อง (ต้องเป็น 1,2,3,4 หรือ all/ทั้งหมด)'); return false;
  }

  // เวลา + min/max (เหมือนเดิม)
  if (p.register_open_at && p.deadline_date &&
      (new Date(p.register_open_at) > new Date(p.deadline_date))) {
    toast("เวลา 'เปิดลงทะเบียน' ต้องไม่ช้ากว่า 'ปิดรับสมัคร'"); return false;
  }
  if (p.deadline_date && p.event_date &&
      (new Date(p.deadline_date) > new Date(p.event_date))) {
    toast("เวลา 'ปิดรับสมัคร' ต้องไม่ช้ากว่า 'วันจัดกิจกรรม'"); return false;
  }
  if (minVal != null && minVal < 0) { toast("ขั้นต่ำต้องเป็นเลขไม่ติดลบ"); return false; }
  if (maxVal != null && maxVal < 0) { toast("สูงสุดต้องเป็นเลขไม่ติดลบ"); return false; }
  if (minVal != null && maxVal != null && maxVal < minVal) {
    toast("ค่าขั้นสูงสุดต้องมากกว่าหรือเท่าขั้นต่ำ"); return false;
  }
  return true;
}
const mode = $audience ? $audience.value : 'student';
if (mode !== 'student') {
  payload.faculty = null;
  payload.major = null;
  payload.grade = null;
}

function toggleStudentFields() {
  const mode = $audience?.value || 'student';          // 'student' | 'public' | 'all'
  const disabled = (mode !== 'student');               // ปิดเมื่อ public หรือ all

  [$faculty, $major, $year].forEach(el => {
    if (!el) return;
    el.disabled = disabled;
  });

  if (disabled) {
    // เคลียร์ค่า (หรือจะตั้งเป็น "ทั้งหมด" ก็ได้ตามต้องการ)
    if ($faculty) $faculty.value = '';
    if ($major) {
      $major.innerHTML = `<option value="">-- เลือกสาขา --</option>`;
      $major.value = '';
    }
    if ($year) $year.value = 'all';
  }
}
tbBody?.addEventListener('click', async (e) => {
  const btn = e.target.closest('.export-btn');
  if (!btn) return;

  const id = btn.dataset.id;
  const oldHtml = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = "<i class='bx bx-time-five'></i> กำลังเตรียม...";

  try {
    const res = await fetch(`/api/events/${encodeURIComponent(id)}/export`, {
      credentials: 'include'
    });
    if (!res.ok) {
      let msg = 'Export ล้มเหลว';
      try { const j = await res.json(); msg = j.detail || msg; } catch {}
      throw new Error(msg);
    }

    // ----- ดึงชื่อไฟล์จาก Content-Disposition -----
    const dispo = res.headers.get('Content-Disposition') || '';
    let filename = 'export.xlsx';

    // ลองอ่านแบบ filename*=UTF-8''...
    let m = dispo.match(/filename\*=(?:UTF-8'')?([^;]+)/i);
    if (m && m[1]) {
      filename = decodeURIComponent(m[1].replace(/"/g, ''));
    } else {
      // ถ้าไม่มี ลองอ่าน filename="..."
      m = dispo.match(/filename="?([^\";]+)"?/i);
      if (m && m[1]) filename = m[1];
    }
    // ---------------------------------------------

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    a.download = filename; // << ใช้ชื่อจาก header
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (err) {
    alert(err.message || 'เกิดข้อผิดพลาดระหว่าง export');
  } finally {
    btn.disabled = false;
    btn.innerHTML = oldHtml;
  }
});

  // ---- Table ----
  async function loadEvents(){
    if (!tbBody) return;
    tbBody.innerHTML = `<tr><td colspan="7" class="muted">กำลังโหลด...</td></tr>`;
    try{
      const items = await api('/api/admin/events');
      allEvents = Array.isArray(items) ? items : [];
      renderTable();
    }catch(e){
      tbBody.innerHTML = `<tr><td colspan="7" style="color:#b91c1c">${esc(e.message)}</td></tr>`;
    }
  }

  function renderTable(){
    const q = (filterText?.value || '').trim().toLowerCase();
    const rows = allEvents.filter(it => !q || [it.title, it.category, it.faculty, it.event_id]
      .some(v => (v || '').toString().toLowerCase().includes(q)));

    if (!rows.length){
      tbBody.innerHTML = `<tr><td colspan="7" class="muted">ไม่พบข้อมูล</td></tr>`;
      return;
    }

    tbBody.innerHTML = '';
    rows.forEach(it=>{
      const tr = document.createElement('tr');
      const d  = (it?.event_date || '').toString().slice(0,10);
      const eid = esc(it.event_id || '');
      const statusKey = (it.status || '').toLowerCase();
      tr.innerHTML = `
        <td>${eid}</td>
        <td>${esc(it.title || '')}</td>
        <td>${esc(it.faculty || '')}</td>
        <td>${esc(it.category || '')}</td>
        <td>${esc(d)}</td>
        <td>
          <span class="status-${statusKey}">
            ${esc(statusLabel(it.status))}
          </span>
        </td>
        <td>
          <a class="btn sm" href="/events/${eid}" target="_blank" rel="noopener">ดูหน้า</a>
          <button class="btn sm" data-action="regs"  data-id="${eid}">รายชื่อ</button>
          <button class="btn sm" data-action="edit"  data-id="${eid}">แก้ไข</button>
          <button class="btn sm" data-action="delete" data-id="${eid}">ลบ</button>
          <button type="button" class="btn sm export-btn" data-id="${eid}" title="Export ผู้ลงทะเบียน">
            <i class='bx bx-download'></i> Export
          </button>
        </td>
      `;

      tr.querySelector('[data-action="regs"]')?.addEventListener('click', (e)=>{
        e.preventDefault();
        showRegistrations(String(it.event_id));
      });

      tr.querySelector('[data-action="edit"]')?.addEventListener('click', (e)=>{
        e.preventDefault();
        const item = allEvents.find(x => String(x.event_id) === String(it.event_id)) || it;
        editingId = String(item.event_id);
        const titleEl = document.getElementById('modal-title');
        if (titleEl) titleEl.textContent = `แก้ไขกิจกรรม (#${editingId})`;
        fillFormFromItem(item);
        showModal();
      });

      tr.querySelector('[data-action="delete"]')?.addEventListener('click', async (e)=>{
        e.preventDefault();
        const id = String(it.event_id);
        if (!confirm(`ยืนยันลบกิจกรรม #${id} ?`)) return;
        try{
          await api(`/api/admin/events/${encodeURIComponent(id)}`, { method: 'DELETE' });
          allEvents = allEvents.filter(x => String(x.event_id) !== id);
          renderTable();
        }catch(err){
          toast(err.message || 'ลบไม่สำเร็จ');
        }
      });

      tbBody.appendChild(tr);
    });
  }

  // ---- เปิดฟอร์มเพิ่มกิจกรรม ----
  addBtn?.addEventListener('click', (e)=>{
  e.preventDefault();
  editingId = null;
  const titleEl = document.getElementById('modal-title');
  if (titleEl) titleEl.textContent = 'เพิ่มกิจกรรม';
  form?.reset();

  // ค่าเริ่มต้น
  if ($status)   $status.value = 'Open';
  if ($audience) $audience.value = 'student';
  if ($year)     $year.value = 'all';
  toggleStudentFields();

  showModal();
});

  // ---- ปิดฟอร์ม ----
  closeBtn?.addEventListener('click', (e)=>{ e.preventDefault(); hideModal(); });
  overlay?.addEventListener('click', (e)=>{ if (e.target === overlay) hideModal(); });
  document.addEventListener('keydown', (e)=>{ if (e.key === 'Escape') hideModal(); });

  // ---- Submit ----
  form?.addEventListener('submit', async (e)=>{
    e.preventDefault();
    const payload = collectPayload();
    if (!validatePayload(payload)) return;

    saveBtn.disabled = true;
    try{
      if (!editingId) {
        await api('/api/admin/events', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      } else {
        await api(`/api/admin/events/${encodeURIComponent(editingId)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });
      }
      hideModal();
      await loadEvents();
    }catch(err){
      toast(err.message || 'บันทึกไม่สำเร็จ');
    }finally{
      saveBtn.disabled = false;
    }
  });

  // ---- Filters & init ----
  filterText?.addEventListener('input', renderTable);
  reloadBtn?.addEventListener('click', ()=> loadEvents());

  loadEvents();
  
    // ==== ImageKit Upload Block (drop-in) ======================================
  const $file = document.getElementById('event-picture-file'); // <input type="file">
  const $hidden = document.getElementById('event-picture'); // <input type="hidden"> (เก็บ URL)
  const $prevImg = document.getElementById('event-picture-preview');
  const $nameEl = document.getElementById('event-picture-name');
  const $barWrap = document.getElementById('event-picture-progress');
  const $bar = document.getElementById('event-picture-bar');
  const $btnReUp = document.getElementById('btn-reupload');
  const $btnClear = document.getElementById('btn-clearimg');

  const UPLOAD_ENDPOINT = '/api/upload-image'; // FastAPI proxy ไป ImageKit

  function _setProgress(pct) { if ($barWrap && $bar) { $barWrap.hidden = false; $bar.style.width = (pct || 0) + '%'; } }
  function _stopProgress() { if ($barWrap && $bar) { setTimeout(() => { $barWrap.hidden = true; $bar.style.width = '0%'; }, 500); } }

  function resetImageUI() {
    if ($prevImg) { $prevImg.style.display = 'none'; $prevImg.src = ''; }
    if ($nameEl) $nameEl.textContent = '';
    if ($hidden) $hidden.value = '';
    if ($file) $file.value = '';
    if ($btnReUp) $btnReUp.hidden = true;
    if ($btnClear) $btnClear.hidden = true;
    _setProgress(0); _stopProgress();
  }

  function showPreviewFromUrl(url, name) {
    if (!url) return resetImageUI();
    if ($prevImg) {
      $prevImg.src = url + '?tr=w-400,h-280,fo-auto';
      $prevImg.style.display = 'block';
    }
    if ($nameEl) $nameEl.textContent = name || url.split('/').pop();
    if ($btnReUp) $btnReUp.hidden = false;
    if ($btnClear) $btnClear.hidden = false;
  }

  function validateFile(file) {
    const ok = ['image/jpeg', 'image/png', 'image/webp'];
    const max = 2 * 1024 * 1024; // 2MB
    if (!ok.includes(file.type)) { alert('รองรับเฉพาะ JPG/PNG/WEBP'); return false; }
    if (file.size > max) { alert('ไฟล์ใหญ่เกิน 2MB'); return false; }
    return true;
  }

  async function uploadToImageKit(file) {
    _setProgress(10);
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(UPLOAD_ENDPOINT, { method: 'POST', body: formData, credentials: 'include' });
    _setProgress(70);
    if (!res.ok) {
      let msg = 'อัปโหลดไม่สำเร็จ';
      try { const t = await res.text(); if (t) msg = t; } catch { }
      throw new Error(msg);
    }
    const data = await res.json();
    _setProgress(100);
    return data; // { url, thumbnail, name }
  }

  // เปลี่ยนไฟล์ -> อัปโหลด + ใส่ URL ลง hidden
  $file?.addEventListener('change', async () => {
    const f = $file.files?.[0]; if (!f) return;
    if (!validateFile(f)) { $file.value = ''; return; }
    try {
      _setProgress(5);
      const up = await uploadToImageKit(f);
      if ($hidden) $hidden.value = up.url || '';
      showPreviewFromUrl(up.url, up.name || f.name);
    } catch (err) {
      console.error(err);
      alert(err.message || 'อัปโหลดไม่สำเร็จ');
      resetImageUI();
    } finally {
      _stopProgress();
    }
  });

  // ปุ่มเปลี่ยนไฟล์ / ล้างรูป
  $btnReUp?.addEventListener('click', () => $file?.click());
  $btnClear?.addEventListener('click', () => resetImageUI());

  // เมื่อเปิด modal: ถ้าเป็น "เพิ่ม" ให้ล้างรูป, ถ้า "แก้ไข" และมี URL เดิมให้โชว์ preview
  const _origShowModal = showModal;
  showModal = function () {
    _origShowModal();
    // ถ้าเป็นโหมดเพิ่ม (editingId == null) -> เคลียร์
    if (!editingId) resetImageUI();
    else {
      // โหมดแก้ไข: ถ้ามี URL ใน hidden ให้โชว์
      const url = ($hidden?.value || '').trim();
      if (url) showPreviewFromUrl(url);
    }
  };

  // เมื่อปิด modal -> ล้าง state รูปภาพด้วย (กันค่าติด)
  const _origHideModal = hideModal;
  hideModal = function () {
    _origHideModal();
    resetImageUI();
  };

  // ตอน fillFormFromItem (มีอยู่แล้วในไฟล์เดิม) ให้เพิ่มบรรทัดนี้ท้ายฟังก์ชัน:
  // ✅ FIX: เราใช้ _originalFillForm (ตัวแปรที่เราระบุไว้ข้างบน) เป็นตัวจริง
  const _origFillFormFromItem = _originalFillForm;
  fillFormFromItem = function (it) {
    _origFillFormFromItem(it); // เรียกตัวจริงที่เราจัดระเบียบไว้
    const url = (it?.picture_url || it?.picture || '').trim();
    // if ($hidden) $hidden.value = url; // (ซ้ำซ้อน _originalFillForm ทำไปแล้ว)
    if (url) showPreviewFromUrl(url); else resetImageUI();
  };
  // ==== ImageKit Upload Block END ============================================

})();
