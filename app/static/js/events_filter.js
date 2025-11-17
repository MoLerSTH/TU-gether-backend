// app/static/js/events_filter.js

(function () {
  // ถ้าไม่มี container ก็ไม่ต้องทำอะไร
  const grid = document.querySelector(".news-container");
  if (!grid) return;

  const cards = Array.from(grid.querySelectorAll(".news-card"));

  // อ่าน element filter
  const inputText   = document.getElementById("f-text");
  const selFaculty  = document.getElementById("f-faculty");
  const selCategory = document.getElementById("f-category");
  const btnClear    = document.getElementById("f-clear");

  // ✅ 1. ทำให้ dropdown ไม่ซ้ำค่า
  function dedupeSelect(sel) {
    if (!sel) return;
    const seen = new Set();
    const opts = Array.from(sel.querySelectorAll("option"));
    opts.forEach((op) => {
      const v = (op.value || "").trim();
      const t = (op.textContent || "").trim();
      // ข้าม "ทั้งหมด"
      if (v === "") return;
      const key = v.toLowerCase();
      if (seen.has(key)) {
        op.remove();
      } else {
        seen.add(key);
      }
    });
  }
  dedupeSelect(selFaculty);
  dedupeSelect(selCategory);

  // ✅ 2. เตรียม metadata จากการ์ด
  // ใน HTML เดิม card ไม่มี data- อะไรเลย เราเลยจะอ่านจาก text แล้วเก็บใส่ dataset เอง
  cards.forEach((card) => {
    const titleEl = card.querySelector("h2");
    const descEl  = card.querySelector(".desc");
    // พวกคณะ / หมวดหมู่ ตอนนี้ยังไม่ถูกแสดงบนการ์ด
    // แต่ในตัวจริงของคุณมันอยู่ใน data จาก backend → เราจะฝังลงไปตอน render ฝั่ง template จะชัวร์กว่า
    // ดังนั้นถ้าไม่เจอจาก dataset ก็จะ fallback ไปที่ text รวม
    card.__filter = {
      title: (titleEl?.textContent || "").toLowerCase(),
      desc:  (descEl?.textContent  || "").toLowerCase(),
      faculty: (card.getAttribute("data-faculty") || "").toLowerCase(),
      category: (card.getAttribute("data-category") || "").toLowerCase(),
    };
  });

  // ✅ 3. ฟังก์ชันกรอง
  function applyFilter() {
    const textVal   = (inputText?.value || "").trim().toLowerCase();
    const facVal    = (selFaculty?.value || "").trim().toLowerCase();
    const catVal    = (selCategory?.value || "").trim().toLowerCase();

    let anyVisible = false;

    cards.forEach((card) => {
      const meta = card.__filter || {};
      let ok = true;

      // กรองตาม text (ชื่อ + รายละเอียด)
      if (textVal) {
        const hay = (meta.title || "") + " " + (meta.desc || "");
        if (!hay.includes(textVal)) {
          ok = false;
        }
      }

      // กรองตามคณะ
      if (ok && facVal) {
        const cf = (meta.faculty || "");
        if (!cf || cf !== facVal) {
          ok = false;
        }
      }

      // กรองตามหมวดหมู่
      if (ok && catVal) {
        const cc = (meta.category || "");
        if (!cc || cc !== catVal) {
          ok = false;
        }
      }

      card.style.display = ok ? "" : "none";
      if (ok) anyVisible = true;
    });

    // ถ้าอยากทำข้อความ "ไม่พบกิจกรรม" ก็ทำตรงนี้ได้
    toggleEmptyState(!anyVisible);
  }

  // ✅ 4. ปุ่มล้าง
  if (btnClear) {
    btnClear.addEventListener("click", () => {
      if (inputText) inputText.value = "";
      if (selFaculty) selFaculty.value = "";
      if (selCategory) selCategory.value = "";
      applyFilter();
    });
  }

  // ✅ 5. ผูก event
  if (inputText)  inputText.addEventListener("input", applyFilter);
  if (selFaculty) selFaculty.addEventListener("change", applyFilter);
  if (selCategory) selCategory.addEventListener("change", applyFilter);

  // ✅ 6. empty state
  function toggleEmptyState(show) {
    let el = document.getElementById("events-empty-state");
    if (show) {
      if (!el) {
        el = document.createElement("p");
        el.id = "events-empty-state";
        el.textContent = "ไม่พบกิจกรรมที่ตรงกับตัวกรอง";
        el.style.opacity = ".6";
        el.style.padding = "1rem";
        grid.parentElement?.appendChild(el);
      }
    } else {
      if (el) el.remove();
    }
  }

})();