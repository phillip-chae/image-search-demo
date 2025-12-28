export function $(selector, root = document) {
  const el = root.querySelector(selector);
  if (!el) throw new Error(`Missing element: ${selector}`);
  return el;
}

export function setText(el, text) {
  el.textContent = String(text ?? '');
}

export function clearChildren(el) {
  while (el.firstChild) el.removeChild(el.firstChild);
}
