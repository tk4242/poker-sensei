// Run the actual browser script with a small DOM/event fixture (no npm dependencies).
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { test } = require('node:test');
const script = fs.readFileSync(process.env.QUIZ_SCRIPT || 'app/sensei/static/app.js', 'utf8');

function element() {
  const classes = new Set();
  const events = {};
  return {
    hidden: true, disabled: false, value: '', style: {},
    classList: {
      add(c) { classes.add(c); },
      remove(c) { classes.delete(c); },
      toggle(c, on) { if (on) classes.add(c); else classes.delete(c); },
      contains(c) { return classes.has(c); },
    },
    addEventListener(type, fn) { events[type] = fn; },
    fire(type, event = {}) { if (!this.disabled) events[type]?.(event); },
    focus() { this.focused = true; },
  };
}
function fixture() {
  const pending = new Map();
  let id = 0;
  const questions = Array.from({length: 5}, (_, i) => {
    const q = element();
    q.radios = Array.from({length: 5}, element);
    q.time = element(); q.text = element();
    q.back = i ? element() : null;
    q.next = i < 4 ? element() : null;
    if (q.next) q.next.disabled = true;
    q.querySelectorAll = () => q.radios;
    q.querySelector = (s) => ({'.back': q.back, '.next': q.next, '.text': q.text, 'input.t': q.time})[s]
      || (s === 'input[type=radio]:checked' ? q.radios.find(r => r.checked) : null);
    return q;
  });
  const submit = element(), count = element(), fill = element(), form = element();
  form.dataset = {limit: '0'};
  form.querySelectorAll = () => questions;
  form.querySelector = (s) => s === '.submit' ? submit : questions[1].back;
  const document = {
    documentElement: element(), querySelectorAll: () => [],
    querySelector: s => ({'form.quiz': form, '.progress .count': count, '.progress .fill': fill})[s],
  };
  vm.runInNewContext(script, {document, window: {scrollTo() {}}, performance: {now: () => 1000},
    setTimeout(fn) { pending.set(++id, fn); return id; }, clearTimeout(id) { pending.delete(id); }, setInterval() {},
  });
  return {questions, submit, fill, count, form,
    current: () => questions.findIndex(q => !q.classList.contains('hide')),
    choose(i, answer = 0) {
      questions[i].radios.forEach((r, n) => r.checked = n === answer);
      questions[i].radios[answer].fire('change');
    },
    flush() { const jobs = [...pending.values()]; pending.clear(); jobs.forEach(fn => fn()); },
  };
}

test('all five questions can be revisited and advanced without changing answers', () => {
  const f = fixture();
  for (let i = 0; i < 5; i++) { assert.equal(f.current(), i); f.choose(i); f.flush(); }
  for (let i = 4; i > 0; i--) { f.questions[i].back.fire('click'); assert.equal(f.current(), i - 1); }
  for (let i = 0; i < 4; i++) { f.questions[i].next.fire('click'); assert.equal(f.current(), i + 1); }
  assert.equal(f.submit.classList.contains('hide'), false);
  assert.equal(f.fill.style.width, '100%');
  assert.equal(f.questions[4].text.focused, true);
});

test('back cancels a scheduled automatic advance after changing an answer', () => {
  const f = fixture();
  f.choose(0); f.flush(); f.choose(1); f.flush();
  f.choose(2); f.questions[2].back.fire('click'); f.flush();
  assert.equal(f.current(), 1);
});

test('unanswered questions cannot be skipped with next', () => {
  const f = fixture();
  assert.equal(f.questions[0].next.disabled, true);
  f.questions[0].next.fire('click');
  assert.equal(f.current(), 0);
  f.choose(0, 4); // Explicit “don't know” is an answer.
  assert.equal(f.questions[0].next.disabled, false);
  f.questions[0].next.fire('click'); f.flush();
  assert.equal(f.current(), 1);
  assert.equal(f.fill.style.width, '20%');
});

test('submit returns to first unanswered question and blocks grading', () => {
  const f = fixture();
  f.choose(0); f.flush();
  let blocked = false;
  f.form.fire('submit', {preventDefault() { blocked = true; }});
  assert.equal(blocked, true);
  assert.equal(f.current(), 1);
  assert.equal(f.questions[1].text.focused, true);
});
