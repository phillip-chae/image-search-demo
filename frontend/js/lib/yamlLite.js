function isObject(value) {
  return Boolean(value) && typeof value === 'object' && !Array.isArray(value);
}

function stripBom(text) {
  return text.charCodeAt(0) === 0xfeff ? text.slice(1) : text;
}

function parseScalar(raw) {
  const value = raw.trim();
  if (value === '') return '';

  if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
    const unquoted = value.slice(1, -1);
    // Minimal unescape for double-quoted values.
    if (value.startsWith('"')) {
      return unquoted
        .replaceAll('\\"', '"')
        .replaceAll('\\n', '\n')
        .replaceAll('\\t', '\t')
        .replaceAll('\\\\', '\\');
    }
    return unquoted;
  }

  const lower = value.toLowerCase();
  if (lower === 'true') return true;
  if (lower === 'false') return false;
  if (lower === 'null' || lower === '~') return null;

  // number (int or float)
  if (/^-?\d+(\.\d+)?$/.test(value)) {
    const n = Number(value);
    if (Number.isFinite(n)) return n;
  }

  return value;
}

/**
 * A small YAML parser for the repo's config-like YAML.
 *
 * Supported:
 * - nested objects via indentation
 * - key: value
 * - key: (object)
 * - strings (quoted/unquoted), numbers, booleans, null
 * - full-line comments starting with '#'
 *
 * Not supported:
 * - arrays/lists
 * - anchors, multi-doc, complex scalars
 */
export function parseYamlLite(yamlText) {
  const text = stripBom(String(yamlText ?? ''));
  const root = {};
  const stack = [{ indent: -1, obj: root }];

  const lines = text.split(/\r?\n/);
  for (const originalLine of lines) {
    if (!originalLine.trim()) continue;
    const trimmed = originalLine.trimStart();
    if (trimmed.startsWith('#')) continue;

    // Indentation (spaces only)
    const indent = originalLine.length - trimmed.length;

    // Basic 'key: value' split (first colon)
    const colonIndex = trimmed.indexOf(':');
    if (colonIndex <= 0) {
      throw new Error(`Invalid YAML (expected 'key:'): ${originalLine}`);
    }

    const key = trimmed.slice(0, colonIndex).trim();
    const afterColon = trimmed.slice(colonIndex + 1);

    while (stack.length > 1 && indent <= stack.at(-1).indent) {
      stack.pop();
    }

    const parent = stack.at(-1).obj;
    if (!isObject(parent)) {
      throw new Error('Invalid YAML nesting (parent is not an object).');
    }

    if (afterColon.trim() === '') {
      const child = {};
      parent[key] = child;
      stack.push({ indent, obj: child });
      continue;
    }

    parent[key] = parseScalar(afterColon);
  }

  return root;
}
