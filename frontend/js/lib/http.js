export class HttpError extends Error {
  constructor(message, { status, url, body } = {}) {
    super(message);
    this.name = 'HttpError';
    this.status = status;
    this.url = url;
    this.body = body;
  }
}

export async function httpJson(url, { method = 'GET', timeoutMs = 20000, headers = {}, signal } = {}) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(new Error('Request timeout')), timeoutMs);

  const chainedSignal = signal
    ? AbortSignal.any([signal, controller.signal])
    : controller.signal;

  try {
    const res = await fetch(url, {
      method,
      headers: {
        'Accept': 'application/json',
        ...headers,
      },
      signal: chainedSignal,
    });

    if (!res.ok) {
      const bodyText = await res.text().catch(() => '');
      throw new HttpError(`Request failed (${res.status})`, {
        status: res.status,
        url,
        body: bodyText,
      });
    }

    return await res.json();
  } finally {
    clearTimeout(timeoutId);
  }
}
