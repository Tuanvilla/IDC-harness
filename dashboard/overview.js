/* Trang Tổng quan IDC (nhánh ui/tong-quan-idc).
 *
 * console.js dựng khung rồi gọi window.IDCOverview.render(el), y như trang Gói
 * (packs.js). Để riêng file vì console.js đã ~9k dòng.
 *
 * NGUYÊN TẮC DỮ LIỆU — đọc kỹ trước khi sửa:
 * - Mọi số vận hành (tải điện, PUE, nhiệt độ, UPS, ca trực, sự kiện) trong file
 *   này là SỐ MINH HỌA lấy từ bản xem trước thiết kế, KHÔNG phải số đo thật.
 *   Giao diện ghi rõ điều đó ở banner đầu trang và chân trang. Đừng bao giờ
 *   trình bày chúng như số liệu live.
 * - Chỉ khối "Hệ thống" cuối trang là SỐ THẬT: lấy từ API sẵn có của server
 *   (/health, /version, /brains). Hỏng mạng thì hiện "—", không bịa.
 * - Realtime BMS/DCIM là Giai đoạn 2 của dự án (xem báo cáo trình duyệt);
 *   trang này chưa nối gì tới đó.
 */
(function () {
  "use strict";

  function ic(ten, opt) { return (window.ic ? window.ic(ten, opt) : ""); }

  const esc = (s) => (s || "").toString()
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#39;");

  function tw(khoa, mac) {
    if (typeof window !== "undefined" && window.t) {
      const s = window.t(khoa);
      return (s && s !== khoa) ? s : (mac || khoa);
    }
    return mac || khoa;
  }

  // ---- Số minh họa (bản xem trước thiết kế) — KHÔNG phải số đo thật ----
  const DEMO = {
    all: {
      nhan: "Toàn trung tâm",
      kpi: [
        { k: "Tổng tải điện", v: "842 kW", sub: "▲3,1% so với hôm qua · 61% công suất thiết kế" },
        { k: "PUE", v: "1,48", sub: "▼0,03 trong 7 ngày · Mục tiêu ≤ 1,50" },
        { k: "Nhiệt độ / Độ ẩm", v: "22,4 °C · 47%", sub: "Trong ngưỡng 20–24 °C" },
        { k: "UPS online", v: "20/20", sub: "0 UPS lỗi · 1 UPS sắp đến hạn ắc quy" },
      ],
    },
    a: {
      nhan: "Phòng máy A",
      kpi: [
        { k: "Tổng tải điện", v: "471 kW", sub: "▲2,4% so với hôm qua · 59% công suất thiết kế" },
        { k: "PUE", v: "1,44", sub: "▼0,02 trong 7 ngày · Mục tiêu ≤ 1,50" },
        { k: "Nhiệt độ / Độ ẩm", v: "21,9 °C · 45%", sub: "Trong ngưỡng 20–24 °C" },
        { k: "UPS online", v: "12/12", sub: "0 UPS lỗi" },
      ],
    },
    b: {
      nhan: "Phòng máy B",
      kpi: [
        { k: "Tổng tải điện", v: "371 kW", sub: "▲4,0% so với hôm qua · 64% công suất thiết kế" },
        { k: "PUE", v: "1,53", sub: "▲0,01 trong 7 ngày · Mục tiêu ≤ 1,50" },
        { k: "Nhiệt độ / Độ ẩm", v: "23,1 °C · 49%", sub: "Trong ngưỡng 20–24 °C" },
        { k: "UPS online", v: "8/8", sub: "0 UPS lỗi · 1 UPS sắp đến hạn ắc quy" },
      ],
    },
  };

  // Biểu đồ minh họa: tải điện + PUE ngày hôm qua. Chuỗi demo vẽ tay, neo đúng
  // một mốc có trong bản xem trước — 18:00 · 856 kW — các giờ khác không có
  // giá trị thật nên không được đọc như số đo.
  const DEMO_CHART = {
    gio: ["00", "03", "06", "09", "12", "15", "18", "21", "24"],
    taiKw: [640, 610, 660, 740, 810, 830, 856, 790, 700],
    pue: [1.44, 1.42, 1.45, 1.48, 1.50, 1.51, 1.52, 1.49, 1.46],
  };

  const UPS_ROWS = [
    { ten: "4 UPS Liebert NX300 · 300 kVA", chi: "A1–A4", tai: 58, pin: "42 phút", canh: false },
    { ten: "Dãy B · 8 UPS", chi: "B1–B8", tai: 63, pin: "38 phút", canh: false },
    { ten: "UPS B7 · ắc quy yếu", chi: "Sức khỏe pin 71% · pin 19 phút", tai: 71, pin: "19 phút", canh: true },
  ];

  const HE_THONG = [
    { ten: "Điện lưới & máy phát", dong: ["2 lộ lưới đang cấp · ATS sẵn sàng", "Điện áp 400 V · Máy phát 3/3 · Dầu 86%"] },
    { ten: "Làm lạnh", dong: ["CRAC N+1 · 1 máy nghỉ luân phiên", "Gió cấp 18,5 °C · Gió hồi 27,1 °C · Chiller 2/3"] },
    { ten: "PCCC & an ninh", dong: ["Đầu báo khói online · Cửa từ đóng kín", "Đầu báo 128/128 · Camera 46/46 · Ra vào ca này: 14"] },
  ];

  // Ca trực: snapshot demo ngày 15/11/2026 (bản xem trước không ghi tên người trực).
  const CA_TRUC = [
    { ca: "Sáng · 06:00–14:00", tt: "Đã bàn giao 14:02 · Không tồn đọng", xong: true },
    { ca: "Chiều · 14:00–22:00", tt: "Đang trực · Kiểm tra UPS B7 lúc 18:30", xong: false },
    { ca: "Đêm · 22:00–06:00", tt: "Bàn giao 22:00 · Mang biên bản kiểm tra B7", xong: false },
  ];
  const VIEC_CA = [
    { ten: "Tuần tra vòng 1 — ghi nhiệt độ 6 điểm", xong: true },
    { ten: "Đối chiếu tải UPS", xong: true },
    { ten: "Kiểm tra ắc quy B7, chụp ảnh màn hình gửi nhóm", xong: false },
    { ten: "Tuần tra vòng 2 lúc 20:00 + ký sổ bàn giao ca đêm", xong: false },
  ];

  const SU_KIEN = [
    { gio: "16:42", nd: "UPS B7 xuống 71% sức khỏe pin" },
    { gio: "09:15", nd: "Chạy thử máy phát số 2 đạt" },
    { gio: "Hôm qua", nd: "Bảo trì CRAC A3" },
    { gio: "Hôm qua", nd: "Bàn giao ca" },
  ];

  async function getJson(url) {
    try {
      const r = await fetch(url);
      return await r.json();
    } catch (e) { return null; }
  }

  function veBieuDo(canvas) {
    if (!canvas || !canvas.getContext) return;
    const ctx = canvas.getContext("2d");
    const dpr = window.devicePixelRatio || 1;
    const W = canvas.clientWidth || 600;
    const H = 260;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    canvas.style.height = H + "px";
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, W, H);
    const padL = 44, padR = 44, padT = 12, padB = 26;
    const iw = W - padL - padR, ih = H - padT - padB;
    const taiMin = 300, taiMax = 900, pueMin = 1.30, pueMax = 1.70;
    const x = (i) => padL + (iw * i) / (DEMO_CHART.gio.length - 1);
    const yTai = (v) => padT + ih * (1 - (v - taiMin) / (taiMax - taiMin));
    const yPue = (v) => padT + ih * (1 - (v - pueMin) / (pueMax - pueMin));
    const cs = getComputedStyle(document.documentElement);
    const grid = (cs.getPropertyValue("--border") || "#36364c").trim();
    const text3 = (cs.getPropertyValue("--text3") || "#9a9ab6").trim();
    const accent = (cs.getPropertyValue("--accent") || "#ff7a3c").trim();
    const accent2 = (cs.getPropertyValue("--accent2") || "#8b5cf6").trim();
    ctx.font = "11px sans-serif";
    ctx.textAlign = "right";
    ctx.fillStyle = text3;
    [300, 600, 900].forEach((v) => {
      ctx.fillText(v + "", padL - 6, yTai(v) + 4);
      ctx.strokeStyle = grid; ctx.globalAlpha = 0.5;
      ctx.beginPath(); ctx.moveTo(padL, yTai(v)); ctx.lineTo(W - padR, yTai(v)); ctx.stroke();
      ctx.globalAlpha = 1;
    });
    ctx.textAlign = "left";
    [1.30, 1.50, 1.70].forEach((v) => ctx.fillText(v.toFixed(2), W - padR + 6, yPue(v) + 4));
    ctx.textAlign = "center";
    DEMO_CHART.gio.forEach((g, i) => ctx.fillText(g + "h", x(i), H - 8));
    const veDuong = (ys, mau, rong) => {
      ctx.strokeStyle = mau; ctx.lineWidth = rong; ctx.beginPath();
      ys.forEach((v, i) => { const px = x(i), py = ys === DEMO_CHART.taiKw ? yTai(v) : yPue(v); i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); });
      ctx.stroke();
    };
    veDuong(DEMO_CHART.taiKw, accent, 2);
    veDuong(DEMO_CHART.pue, accent2, 2);
    // Điểm neo duy nhất có giá trị thật trong bản xem trước: 18:00 · 856 kW.
    const i18 = DEMO_CHART.gio.indexOf("18");
    ctx.fillStyle = accent;
    ctx.beginPath(); ctx.arc(x(i18), yTai(856), 4, 0, Math.PI * 2); ctx.fill();
    ctx.textAlign = "center";
    ctx.fillText("18:00 · 856 kW", x(i18), yTai(856) - 10);
  }

  function htmlKpi(scope) {
    return DEMO[scope].kpi.map((k) =>
      '<div class="ov-card ov-kpi"><div class="ov-k">' + esc(k.k) + '</div>' +
      '<div class="ov-v">' + esc(k.v) + '</div>' +
      '<div class="ov-sub">' + esc(k.sub) + '</div></div>').join("");
  }

  function render(el) {
    const tieuDe = tw("page.tongquan.title", "Tổng quan IDC");
    const phuDe = tw("page.tongquan.sub", "Vận hành trung tâm IDC · điện, lạnh, UPS, ca trực");
    el.innerHTML =
      '<div class="ov-wrap">' +
      '<div class="ov-head"><div><h2 class="ov-title">' + esc(tieuDe) + '</h2>' +
      '<div class="ov-sub">' + esc(phuDe) + '</div></div>' +
      '<span class="ov-pill ov-pill-ok">Ổn định · 1 lưu ý: ắc quy UPS B7</span></div>' +
      '<div class="ov-banner">Số liệu vận hành dưới đây là <b>minh họa</b> theo bản thiết kế — chưa nối BMS/DCIM realtime (Giai đoạn 2). Chỉ khối “Hệ thống” cuối trang là số thật từ máy chủ.</div>' +
      '<div class="ov-scope" role="group" aria-label="Phạm vi">' +
      '<button class="ov-scope-btn ov-on" data-scope="all">Toàn trung tâm</button>' +
      '<button class="ov-scope-btn" data-scope="a">Phòng máy A</button>' +
      '<button class="ov-scope-btn" data-scope="b">Phòng máy B</button></div>' +
      '<div class="ov-kpis" id="ovKpis">' + htmlKpi("all") + '</div>' +
      '<div class="ov-grid-2">' +
      '<section class="ov-card"><h3 class="ov-sec">Tải điện &amp; PUE — ngày hôm qua <span class="ov-tag">Minh họa</span></h3>' +
      '<div class="ov-legend"><span><i class="ov-dot" style="background:var(--accent)"></i>Tải điện (kW, trục trái)</span>' +
      '<span><i class="ov-dot" style="background:var(--accent2)"></i>PUE (trục phải)</span></div>' +
      '<canvas id="ovChart" class="ov-chart" aria-label="Biểu đồ tải điện và PUE ngày hôm qua (minh họa)"></canvas></section>' +
      '<section class="ov-card"><h3 class="ov-sec">UPS — 20 UPS độc lập <span class="ov-tag">Minh họa</span></h3>' +
      UPS_ROWS.map((u) =>
        '<div class="ov-ups' + (u.canh ? ' ov-ups-warn' : '') + '">' +
        '<div class="ov-ups-top"><b>' + esc(u.ten) + '</b><span>' + esc(u.pin) + '</span></div>' +
        '<div class="ov-ups-sub">' + esc(u.chi) + '</div>' +
        '<div class="ov-bar"><i style="width:' + u.tai + '%"></i></div>' +
        '<div class="ov-ups-sub">Tải ' + u.tai + '%</div></div>').join("") +
      '<div class="ov-ups-foot">Tải trung bình toàn hệ 61% · Riêng B7: 71% — nên lên lịch thay ắc quy.</div></section>' +
      '</div>' +
      '<div class="ov-grid-3">' +
      HE_THONG.map((h) =>
        '<section class="ov-card"><h3 class="ov-sec">' + esc(h.ten) + '</h3>' +
        '<span class="ov-pill ov-pill-ok">Bình thường</span>' +
        h.dong.map((d) => '<div class="ov-line">' + esc(d) + '</div>').join("") + '</section>').join("") +
      '</div>' +
      '<div class="ov-grid-2">' +
      '<section class="ov-card"><h3 class="ov-sec">Ca trực — 15/11/2026 <span class="ov-tag">Minh họa</span></h3>' +
      CA_TRUC.map((c) =>
        '<div class="ov-ca"><b>' + esc(c.ca) + '</b><div class="ov-line">' + esc(c.tt) + '</div></div>').join("") +
      '<h4 class="ov-sec2">Việc ca này</h4>' +
      VIEC_CA.map((v) =>
        '<label class="ov-viec"><input type="checkbox" disabled' + (v.xong ? ' checked' : '') + '> <span' +
        (v.xong ? ' class="ov-xong"' : '') + '>' + esc(v.ten) + '</span></label>').join("") +
      '</section>' +
      '<section class="ov-card"><h3 class="ov-sec">Sự kiện gần đây <span class="ov-tag">Minh họa</span></h3>' +
      SU_KIEN.map((s) =>
        '<div class="ov-sk"><span class="ov-sk-gio">' + esc(s.gio) + '</span><span>' + esc(s.nd) + '</span></div>').join("") +
      '</section></div>' +
      '<section class="ov-card"><h3 class="ov-sec">Hệ thống — số thật từ máy chủ</h3>' +
      '<div id="ovLive" class="ov-live">Đang lấy…</div></section>' +
      '<div class="ov-foot">Số vận hành trên trang này là minh họa theo bản thiết kế. Realtime BMS/DCIM là Giai đoạn 2 — chưa nối.</div>' +
      '</div>';

    veBieuDo(el.querySelector("#ovChart"));

    el.querySelectorAll(".ov-scope-btn").forEach((b) => {
      b.addEventListener("click", () => {
        el.querySelectorAll(".ov-scope-btn").forEach((x) => x.classList.remove("ov-on"));
        b.classList.add("ov-on");
        const k = el.querySelector("#ovKpis");
        if (k) k.innerHTML = htmlKpi(b.dataset.scope || "all");
      });
    });

    // Khối live: chỉ API thật, hỏng thì hiện "—", không bịa số.
    (async () => {
      const host = el.querySelector("#ovLive");
      if (!host) return;
      const [h, v, br] = await Promise.all([getJson("/health"), getJson("/version"), getJson("/brains")]);
      if (!el.isConnected) return;
      const brains = (br && br.brains) || [];
      const idc = brains.find((x) => x && (x.name === "IDC" || (x.label || "").toUpperCase().includes("IDC")));
      host.innerHTML =
        '<div class="ov-live-row"><span>Trạng thái máy chủ</span><b>' + esc((h && h.status) || "—") + '</b></div>' +
        '<div class="ov-live-row"><span>Phiên bản đang chạy</span><b>' + esc((v && v.current) || "—") +
        ((v && v.latest && v.latest !== v.current) ? ' · Mới nhất: ' + esc(v.latest) : "") + '</b></div>' +
        '<div class="ov-live-row"><span>Brain</span><b>' + esc(String(brains.length || "—")) + ' brain' +
        (idc ? ' · IDC: ' + esc(String(idc.notes || 0)) + ' note' : "") + '</b></div>';
    })();
  }

  window.IDCOverview = { render: render };
})();
