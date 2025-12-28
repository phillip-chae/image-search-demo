import { loadRuntimeConfig } from './config/loadConfig.js';
import { createSearchApi } from './api/searchApi.js';
import { $, setText, clearChildren } from './ui/dom.js';
import { renderResults } from './ui/renderResults.js';

function setBusy(isBusy) {
  const submit = $('#submit');
  submit.disabled = Boolean(isBusy);
  submit.setAttribute('aria-busy', String(Boolean(isBusy)));
}

function setStatus(message) {
  const statusEl = $('#status');
  setText(statusEl, message);
}

function normalizeErrorMessage(err) {
  if (!err) return 'Request failed.';
  if (typeof err === 'string') return err;
  if (err instanceof Error && err.message) return err.message;
  return 'Request failed.';
}

async function bootstrap() {
  setStatus('Loading config...');

  const { config, warning } = await loadRuntimeConfig({ url: '/config.yaml' });
  if (warning) {
    // Keep UX minimal: show once, still usable.
    setStatus(warning);
  } else {
    setStatus('');
  }

  document.title = config?.app?.title || 'Image Search';
  setText($('#pageTitle'), config?.app?.title || 'Image Search');

  const api = createSearchApi({
    searchBasePath: config?.api?.searchBasePath,
    timeoutMs: config?.api?.requestTimeoutMs,
  });

  const form = $('#searchForm');
  const queryInput = $('#query');
  const resultsEl = $('#results');

  const clearResults = () => clearChildren(resultsEl);

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const text = (queryInput.value || '').trim();
    if (!text) {
      setStatus('Enter a query.');
      clearResults();
      return;
    }

    setBusy(true);
    setStatus('Searching...');
    clearResults();

    try {
      const imageIds = await api.searchByText(text);
      const { rendered, total } = renderResults({
        resultsEl,
        imageIds,
        imagesBasePath: config?.api?.imagesBasePath,
        maxResultsRender: config?.ui?.maxResultsRender,
      });

      const extra = rendered < total ? ` (showing ${rendered} of ${total})` : '';
      setStatus(`Found ${total} result(s).${extra}`);
    } catch (err) {
      console.error(err);
      setStatus(normalizeErrorMessage(err));
    } finally {
      setBusy(false);
    }
  });

  // Autofocus in a safe way
  queryInput.focus();
}

bootstrap().catch((err) => {
  console.error(err);
  try {
    setStatus('Failed to initialize frontend.');
  } catch {
    // ignore
  }
});
