import { clearChildren } from './dom.js';

export function renderResults({ resultsEl, imageIds, imagesBasePath, maxResultsRender }) {
  clearChildren(resultsEl);

  const limit = Math.max(0, Math.min(Number(maxResultsRender ?? 200) || 200, imageIds.length));
  const frag = document.createDocumentFragment();

  for (let i = 0; i < limit; i += 1) {
    const imageId = imageIds[i];

    const card = document.createElement('div');
    card.className = 'card';

    const img = document.createElement('img');
    img.className = 'thumb';
    img.loading = 'lazy';
    img.alt = imageId;
    img.src = `${String(imagesBasePath || '/images').replace(/\/$/, '')}/${encodeURIComponent(imageId)}`;

    const meta = document.createElement('div');
    meta.className = 'meta';
    meta.textContent = imageId;

    card.appendChild(img);
    card.appendChild(meta);
    frag.appendChild(card);
  }

  resultsEl.appendChild(frag);

  return { rendered: limit, total: imageIds.length };
}
