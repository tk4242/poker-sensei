// ポーカー先生: クイズを1問ずつ表示し、各問の回答時間を記録する（JSなしでも全問表示で解ける）
(function () {
  document.documentElement.classList.add("js");

  const form = document.querySelector("form.quiz");
  if (form) {
    const qs = Array.from(form.querySelectorAll(".q"));
    const fill = document.querySelector(".progress .fill");
    const count = document.querySelector(".progress .count");
    const timer = document.querySelector(".progress .timer");
    const submit = form.querySelector(".submit");
    const limit = parseInt(form.dataset.limit || "0", 10);
    let cur = 0;
    let started = performance.now();
    let pending = null;

    function refresh() {
      const completed = qs.filter((q, i) => answered(i)).length;
      if (count) count.textContent = (cur + 1) + " / " + qs.length + "問（回答済み " + completed + "問）";
      if (fill) fill.style.width = Math.round((completed / qs.length) * 100) + "%";
      const next = qs[cur].querySelector(".next");
      if (next) next.disabled = !answered(cur);
      submit.classList.toggle("hide", cur !== qs.length - 1 || !answered(cur));
    }
    function show(i, focus = true) {
      clearTimeout(pending);
      pending = null;
      qs.forEach((q, j) => q.classList.toggle("hide", j !== i));
      cur = i;
      started = performance.now();
      refresh();
      if (focus) qs[i].querySelector(".text").focus({ preventScroll: true });
      window.scrollTo({ top: 0 });
    }
    function answered(i) { return !!qs[i].querySelector("input[type=radio]:checked"); }

    qs.forEach((q, i) => {
      const back = q.querySelector(".back");
      if (back) {
        back.hidden = false;
        back.addEventListener("click", () => show(i - 1));
      }
      const next = q.querySelector(".next");
      if (next) {
        next.hidden = false;
        next.addEventListener("click", () => { if (answered(i)) show(i + 1); });
      }
      q.querySelectorAll("input[type=radio]").forEach((r) => {
        r.addEventListener("change", () => {
          const t = q.querySelector("input.t");
          if (t && !t.value) t.value = Math.round(performance.now() - started);
          refresh();
          clearTimeout(pending);
          if (i < qs.length - 1) pending = setTimeout(() => show(i + 1), 220);
        });
      });
    });
    form.addEventListener("submit", (e) => {
      const missing = qs.findIndex((q, i) => !answered(i));
      if (missing >= 0) { e.preventDefault(); show(missing); }
    });
    if (timer) {
      setInterval(() => {
        const s = (performance.now() - started) / 1000;
        timer.textContent = s.toFixed(1) + "秒";
        timer.classList.toggle("bad", limit > 0 && s > limit);
      }, 100);
    }
    show(0, false);
  }

  // トレーニング: 問題を表示してから答えるまでの時間を送る（5秒以内の正解は「かいしん」）
  const train = document.querySelector("form.train");
  if (train) {
    const t0 = performance.now();
    let sent = false;
    train.addEventListener("submit", (e) => {
      if (sent) { e.preventDefault(); return; }
      sent = true;
      train.querySelector("input[name=t]").value = Math.round(performance.now() - t0);
    });
  }
  const next = document.querySelector(".cmd a[autofocus]");
  if (next) next.focus({ preventScroll: true });

  document.querySelectorAll("button.copy").forEach((b) => {
    b.addEventListener("click", async () => {
      const target = document.getElementById(b.dataset.target);
      try { await navigator.clipboard.writeText(target.textContent); b.textContent = "コピーしました"; }
      catch (_) { b.textContent = "長押しで選択してコピー"; }
    });
  });

  document.querySelectorAll("form[data-confirm]").forEach((f) => {
    f.addEventListener("submit", (e) => { if (!confirm(f.dataset.confirm)) e.preventDefault(); });
  });

  document.querySelectorAll("form.busy").forEach((f) => {
    f.addEventListener("submit", () => {
      const b = f.querySelector("button[type=submit]");
      if (b) { b.disabled = true; b.textContent = "考え中…（調べて出典を集めています。最大2〜3分）"; }
    });
  });
})();
