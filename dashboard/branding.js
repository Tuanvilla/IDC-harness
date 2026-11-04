/* branding.js - đổi logo/avatar + cấu hình tên miền riêng (HTTPS).
   Tách riêng khỏi app.js (file đó có encoding hỗn hợp, sửa dễ hỏng). Vanilla DOM, không cần Alpine. */
(function () {
  "use strict";

  function $(id) { return document.getElementById(id); }

  // Cả thẻ tên miền (wizard 3 bước + badge DNS/SSL) lẫn dòng trạng thái ảnh đại diện đều
  // được VẼ MỘT LẦN bằng JS, nên đổi ngôn ngữ giao diện là chúng đứng nguyên tiếng cũ.
  // Nhớ lại dữ liệu đã vẽ để lượt "javis:i18n" dựng lại y hệt bằng từ điển mới, khỏi phải
  // gọi lại máy chủ.
  var _logoCustom = null;    // true/false = đang dùng ảnh riêng / ảnh mặc định; null = chưa biết

  function setStatus(id, msg, isErr) {
    var el = $(id);
    if (!el) return;
    el.textContent = msg || "";
    el.style.color = isErr ? "var(--red)" : "";
  }

  function esc(s) { return (s || "").toString().replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;"); }

  function _injectDomCss() {
    if (document.getElementById("domCss")) return;
    var s = document.createElement("style"); s.id = "domCss";
    s.textContent =
      // Ô nhập: flex-basis auto + grow, KHÔNG dùng flex:1 (basis 0). Với basis 0 thì cỡ
      // mong muốn của ô nhập bằng 0, nên hàng thiếu chỗ là nó teo hết còn nút giữ nguyên.
      // Nút vẫn khai width:auto: .gcard-btn tự nó đã auto, nhưng khai ở đây thì hàng này
      // miễn nhiễm với bất kỳ luật full-width nào của trang chủ quản sau này.
      // KHÔNG đặt align-items:center: ở màn hẹp hàng này xoay thành cột, mà center thì con
      // co về bề ngang nội dung thay vì giãn hết hàng - ô nhập lại bé. Để mặc định stretch.
      // margin-top:0 on the buttons: .gcard-btn carries a 14px top margin for stacked cards, which here
      // dropped the Save button 14px below the field it belongs to.
      ".dom-field{display:flex;gap:6px}" +
      ".dom-field input{flex:1 1 auto;min-width:0;width:auto;background:var(--field-bg);" +
      "border:1px solid var(--border);color:var(--text);border-radius:7px;padding:8px 10px;font-size:14px}" +
      ".dom-field input:focus{outline:none;border-color:var(--accent)}" +
      ".dom-field .gcard-btn{flex:0 0 auto;width:auto;white-space:nowrap;margin-top:0}" +
      ".dom-status{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px}" +
      ".dom-badge{font-size:12.5px;padding:3px 10px;border-radius:20px;border:1px solid var(--hairline);background:var(--surface-2);color:var(--text2);white-space:nowrap}" +
      ".dom-badge.ok{background:var(--ok-wash);border-color:var(--green);color:var(--green)}" +
      ".dom-badge.warn{background:var(--warn-wash);border-color:var(--warn-line);color:var(--warn-ink)}" +
      ".dom-badge.bad{background:var(--danger-wash);border-color:var(--danger-line);color:var(--red)}" +
      // Hai nút chia đôi hàng: phải khai flex CHO CẢ HAI (trước đây bỏ sót nút ghost nên nó
      // nuốt hàng còn nút kia teo). Một selector là đủ vì cả hai nay cùng họ .gcard-btn.
      ".dom-ssl{display:flex;gap:6px;margin-top:9px}" +
      ".dom-ssl .gcard-btn{flex:1 1 0;width:auto;white-space:nowrap;margin-top:0}" +
      ".dom-guide{margin-top:10px;font-size:13px;line-height:1.55;color:var(--text);display:flex;flex-direction:column;gap:8px}" +
      ".dom-step{display:grid;grid-template-columns:25px minmax(0,1fr);gap:8px;padding:9px 10px;background:var(--surface-1);border:1px solid var(--hairline);border-radius:9px}" +
      ".dom-step.done{border-color:var(--ok-line);background:var(--ok-wash)}" +
      ".dom-step.warn{border-color:var(--warn-line);background:var(--warn-wash)}" +
      ".dom-step-num{width:24px;height:24px;display:inline-flex;align-items:center;justify-content:center;border-radius:50%;background:var(--hairline);font-weight:700}" +
      ".dom-step.done .dom-step-num{background:var(--ok-wash);color:var(--green)}" +
      ".dom-step p{margin:3px 0 0;color:var(--text3)}.dom-step code{display:inline-block;margin-top:5px;background:var(--info-wash);padding:3px 7px;border-radius:5px;font-size:12px;overflow-wrap:anywhere}" +
      ".dom-copy{margin:7px 0 0;padding:5px 9px;border:1px solid var(--hairline);border-radius:7px;background:var(--surface-2);color:var(--text);cursor:pointer}" +
      ".dom-copy:hover{border-color:var(--info-line);color:var(--info-ink)}" +
      ".dom-open{display:inline-block;margin-top:6px;color:var(--green);text-decoration:none}.dom-open:hover{text-decoration:underline}" +
      ".dom-docs{display:flex;gap:12px;flex-wrap:wrap;margin-top:10px;padding-top:9px;border-top:1px solid var(--surface-3)}" +
      ".dom-docs a{font-size:12.5px;color:var(--link-ink);text-decoration:none}.dom-docs a:hover{text-decoration:underline}" +
      "@media(max-width:600px){.dom-field,.dom-ssl{flex-direction:column}.dom-field .gcard-btn,.dom-ssl .gcard-btn{width:100%}}";
    document.head.appendChild(s);
  }

  // Đổi src mọi ảnh logo (header, thanh bên, màn đăng nhập, preview) để thấy ảnh mới ngay.
  // `rieng` = từ giờ đang dùng logo NGƯỜI DÙNG tải lên hay logo mặc định. Linh vật chỉ được
  // thay chỗ logo trên thanh bên khi người dùng CHƯA tải logo riêng, nên phải báo cho nó.
  function bustLogos(rieng) {
    var v = "/brand-logo?v=" + Date.now();
    document.querySelectorAll('img[src^="/brand-logo"]').forEach(function (img) { img.src = v; });
    doiFavicon(v);
    try { if (window.JavisPet) window.JavisPet.setLogoRieng(rieng); } catch (e) {}
  }

  // ICON TRÊN TAB cũng phải đổi theo logo. Ảnh nằm trong trang thì đổi `src` là xong, nhưng
  // favicon nằm ở thẻ <link rel="icon"> trong <head>, và nó có hai chỗ kẹt:
  //
  //   1. index.html trỏ sẵn `/brand-logo?v=<phiên bản app>`. Chuỗi `v` đó chỉ đổi khi app lên
  //      bản mới, nên tải logo khác lên thì URL vẫn y nguyên và trình duyệt không có lý do gì
  //      đi lấy lại. Chú thích cũ trong index.html ghi favicon "tự đổi theo ảnh user tải lên",
  //      nhưng thực tế phải đợi tới lần app lên bản sau (chủ dự án báo 18/09).
  //   2. Trình duyệt cache favicon lì hơn hẳn ảnh thường, và chỉ đổi mỗi `href` của thẻ cũ thì
  //      nhiều bản Safari/Firefox làm ngơ. Cách ăn chắc là GỠ thẻ cũ ra rồi gắn thẻ mới vào.
  //
  // Gắn lại cả `apple-touch-icon` vì index.html khai cả hai, và đó là icon dùng khi người ta
  // thêm IDC Harness vào màn hình chính iPhone.
  function doiFavicon(v) {
    try {
      var head = document.head;
      if (!head) return;
      var cu = head.querySelectorAll('link[rel="icon"], link[rel="shortcut icon"], link[rel="apple-touch-icon"]');
      Array.prototype.forEach.call(cu, function (l) { if (l.parentNode) l.parentNode.removeChild(l); });
      ["icon", "apple-touch-icon"].forEach(function (rel) {
        var l = document.createElement("link");
        l.setAttribute("rel", rel);
        l.setAttribute("href", v);
        head.appendChild(l);
      });
    } catch (e) { /* favicon là phần trang trí: hỏng thì thôi, đừng làm gãy luồng tải logo */ }
  }

  // ---------- Logo / avatar ----------
  async function uploadLogo(file) {
    if (!file) return;
    setStatus("brandLogoStatus", window.t("brand.uploading"), false);
    try {
      var fd = new FormData();
      fd.append("file", file);
      var r = await fetch("/branding/logo", { method: "POST", body: fd });
      var j = await r.json().catch(function () { return {}; });
      if (!r.ok || !j.ok) { setStatus("brandLogoStatus", j.error || window.t("brand.upload_failed"), true); return; }
      bustLogos(true);
      _logoCustom = true;
      setStatus("brandLogoStatus", window.t("brand.image_updated"), false);
    } catch (e) {
      setStatus("brandLogoStatus", window.t("brand.net_err_upload"), true);
    }
  }

  async function resetLogo() {
    setStatus("brandLogoStatus", window.t("brand.restoring"), false);
    try {
      var r = await fetch("/branding/logo/reset", { method: "POST" });
      var j = await r.json().catch(function () { return {}; });
      if (!r.ok || !j.ok) { setStatus("brandLogoStatus", (j && j.error) || window.t("brand.restore_failed"), true); return; }
      bustLogos(false);
      _logoCustom = false;
      setStatus("brandLogoStatus", window.t("brand.image_reset"), false);
    } catch (e) {
      setStatus("brandLogoStatus", window.t("app.err_net"), true);
    }
  }

  // ---------- Tên miền & SSL ----------
  function _badge(id, text, cls) {
    var e = $(id); if (!e) return;
    e.textContent = text; e.className = "dom-badge " + (cls || "");
  }

  // Nạp giá trị hiện tại khi mở Cài đặt.
  async function loadExtras() {
    try {
      var r = await fetch("/settings");
      var j = await r.json();
      var b = j.branding || {};
      _logoCustom = !!b.logo_ext;
      setStatus("brandLogoStatus", _logoCustom ? window.t("brand.using_custom_image") : window.t("brand.using_default_image"), false);
    } catch (e) { /* im lặng */ }
  }

  function bind() {
    _injectDomCss();
    var sBtn = $("settingsBtn");
    if (sBtn) sBtn.addEventListener("click", function () { setTimeout(loadExtras, 50); });

    var li = $("brandLogoInput");
    if (li) li.addEventListener("change", function (e) {
      var f = e.target.files && e.target.files[0];
      if (f) uploadLogo(f);
      e.target.value = "";   // cho phép chọn lại cùng file
    });
    var lr = $("brandLogoReset");
    if (lr) lr.addEventListener("click", resetLogo);


    // Controls giờ nằm trong sidebar (luôn hiển thị) → nạp giá trị hiện tại ngay khi tải trang.
    loadExtras();
  }

  // Đổi ngôn ngữ giao diện (hoặc từ điển vừa nạp xong): dựng lại phần chữ do JS vẽ.
  // Chỉ dựng lại thứ đã từng vẽ, để không tự dưng in "Chưa đặt tên miền" lên một trang
  // chưa hề mở phần tên miền.
  window.addEventListener("javis:i18n", function () {
    if (_logoCustom !== null) {
      setStatus("brandLogoStatus", _logoCustom ? window.t("brand.using_custom_image") : window.t("brand.using_default_image"), false);
    }
  });

  // Cho trang Cài đặt (console.js) gọi nạp lại giá trị avatar khi mở trang.
  window.__javisRefreshExtras = loadExtras;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();
