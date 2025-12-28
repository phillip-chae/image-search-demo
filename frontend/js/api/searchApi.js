import { httpJson } from '../lib/http.js';

export function createSearchApi({ searchBasePath, timeoutMs }) {
  const base = String(searchBasePath || '/api').replace(/\/$/, '');

  return {
    async searchByText(text) {
      const q = encodeURIComponent(String(text ?? '').trim());
      const url = `${base}/v1/image/search?text=${q}`;
      const data = await httpJson(url, { timeoutMs });

      if (!Array.isArray(data) || !data.every((x) => typeof x === 'string')) {
        throw new Error('Unexpected search response (expected JSON array of image IDs).');
      }
      return data;
    },
  };
}
