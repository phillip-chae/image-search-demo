import { defaultConfig } from './defaultConfig.js';
import { parseYamlLite } from '../lib/yamlLite.js';

function isObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function deepMerge(base, override) {
  if (!isObject(base)) return override;
  if (!isObject(override)) return base;

  const out = { ...base };
  for (const [key, value] of Object.entries(override)) {
    const existing = out[key];
    if (isObject(existing) && isObject(value)) {
      out[key] = deepMerge(existing, value);
    } else {
      out[key] = value;
    }
  }
  return out;
}

export async function loadRuntimeConfig({ url = '/config.yaml' } = {}) {
  const res = await fetch(url, {
    method: 'GET',
    cache: 'no-store',
    headers: {
      'Accept': 'text/yaml, text/plain, */*',
    },
  });

  if (!res.ok) {
    // Non-fatal: fallback to defaults.
    return { config: defaultConfig, source: 'defaults', warning: `Config fetch failed (${res.status}). Using defaults.` };
  }

  const text = await res.text();
  try {
    const parsed = parseYamlLite(text);
    const merged = deepMerge(defaultConfig, parsed);
    return { config: merged, source: url };
  } catch (e) {
    return { config: defaultConfig, source: 'defaults', warning: `Config parse failed. Using defaults.` };
  }
}
