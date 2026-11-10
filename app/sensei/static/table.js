/* 通信・採点はサーバー。JSは卓の演出と、条件選択の補助のみ。 */
(() => {
  const setup = document.querySelector('#table-setup');
  if (setup) {
    const players = setup.querySelector('[name=players]');
    const position = setup.querySelector('[name=position]');
    const stack = setup.querySelector('[name=stack]');
    const groups = [...position.querySelectorAll('optgroup')].map(g => g.cloneNode(true));
    function update() {
      const mode = setup.querySelector('[name=mode]:checked').value;
      // 人数はユーザーの選択を保持。未収録のレンジを勝手にHUへ置き換えない。
      const unavailable = mode === 'range' && players.value !== '2';
      setup.querySelector('[type=submit]').disabled = unavailable;
      setup.querySelector('[data-hu-option]').hidden = !unavailable;
      const previous = position.value;
      position.querySelectorAll('optgroup').forEach(g => g.remove());
      const group = groups.find(g => g.dataset.players === players.value);
      position.append(group.cloneNode(true));
      if ([...position.options].some(o => o.value === previous)) position.value = previous;
      else position.value = 'random';
      position.disabled = mode === 'flop' || mode === 'decisions';
      stack.disabled = mode !== 'range';
      document.querySelector('#setup-note').textContent = mode === 'range'
        ? unavailable
          ? `${players.value}人のGTOレンジは未収録です。人数を保って「席と動く順番」「フロップの判断」を選ぶか、下のボタンでHUへ切り替えてください。`
          : '収録済み：HU（2人）、5・8・10bb。SBのpush/foldとBBのcall/foldを学びます。'
        : mode === 'decisions' ? '席とスタックは問題ごとに固定。出典で確認した場面のアクションを選び、理由を学びます。相手の手札が見えない問題もあります。'
        : mode === 'flop' ? 'あなたはBTN（2人卓ではBTN/SB）。相手の2枚を見ながら、オッズを判断する計算練習です。'
        : '席を確認して、次に動く人を選びましょう。フロップ前と後の両方を出題します。';
    }
    setup.addEventListener('change', e => { if (e.target.name === 'mode' || e.target === players) update(); });
    setup.querySelector('[data-switch-hu]').addEventListener('click', () => {
      players.value = '2';
      update();
    });
    update();
  }
  const motion = document.querySelector('[data-motion]');
  let savedMotion = false;
  try { savedMotion = localStorage.getItem('sensei.reduceMotion') === '1'; } catch (_) { /* 保存不可でも学習可能 */ }
  document.documentElement.classList.toggle('no-table-motion', savedMotion);
  if (motion) {
    motion.checked = savedMotion;
    motion.addEventListener('change', () => {
      document.documentElement.classList.toggle('no-table-motion', motion.checked);
      if (motion.checked) document.querySelector('.poker-table')?.getAnimations({subtree:true}).forEach(a => a.cancel());
      try { localStorage.setItem('sensei.reduceMotion', motion.checked ? '1' : '0'); } catch (_) { /* 任意設定 */ }
    });
  }
  function animateChips() {
    if (document.documentElement.classList.contains('no-table-motion') || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    document.querySelectorAll('[data-chip]').forEach((chip, i) => {
      const dx = 210 - Number(chip.getAttribute('cx'));
      const dy = 183 - Number(chip.getAttribute('cy'));
      chip.animate([{opacity:0, transform:'translate(0,0)'}, {opacity:1,offset:.15},
        {opacity:1,offset:.8,transform:`translate(${dx}px,${dy}px)`},
        {opacity:0,transform:`translate(${dx}px,${dy}px)`}], {duration:850,delay:350+i*200});
    });
  }
  animateChips();
  document.querySelector('[data-replay]')?.addEventListener('click', () => {
    const table = document.querySelector('.poker-table');
    const clone = table.cloneNode(true);
    table.replaceWith(clone);
    animateChips();
  });
  document.querySelector('[data-range-zoom]')?.addEventListener('change', e => {
    document.querySelector('.range-scroll').classList.toggle('zoomed', e.target.checked);
  });
  document.querySelectorAll('.range-cell').forEach(cell => cell.addEventListener('click', e => {
    // 修飾キーは通常のリンク操作を維持。
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    const f = Number(cell.dataset.frequency);
    document.querySelectorAll('.range-cell.chosen').forEach(el => el.classList.remove('chosen'));
    cell.classList.add('chosen');
    document.querySelector('#range-hand').textContent = cell.dataset.hand;
    const detail = document.querySelector('#range-detail');
    detail.textContent = `${detail.dataset.action} ${(f*100).toFixed(2)}% / フォールド ${((1-f)*100).toFixed(2)}%`;
    history.replaceState(null, '', cell.href);
    document.querySelector('#hand-detail').focus({preventScroll:true});
    document.querySelector('#hand-detail').scrollIntoView({block:'nearest'});
  }));
})();
