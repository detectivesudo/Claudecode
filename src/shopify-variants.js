const HANDLE_RE = /^[a-z0-9_-]+$/i;

export class ShopifyVariantError extends Error {
  constructor(message, code, { status = null, cause = null } = {}) {
    super(message, cause ? { cause } : undefined);
    this.name = 'ShopifyVariantError';
    this.code = code;
    this.status = status;
  }
}

function normalizeUrl(storeUrl) {
  if (!storeUrl || typeof storeUrl !== 'string') {
    throw new ShopifyVariantError('storeUrl must be a non-empty string', 'INVALID_INPUT');
  }
  let url = storeUrl.trim().replace(/\/+$/, '');
  if (!/^https?:\/\//i.test(url)) {
    url = `https://${url}`;
  }
  try {
    new URL(url);
  } catch {
    throw new ShopifyVariantError(`Invalid store URL: ${storeUrl}`, 'INVALID_INPUT');
  }
  return url;
}

async function fetchProduct(normalizedUrl, handle, extraHeaders) {
  if (!handle || typeof handle !== 'string' || !HANDLE_RE.test(handle.trim())) {
    throw new ShopifyVariantError(
      `Invalid product handle: "${handle}". Must contain only letters, numbers, hyphens, and underscores.`,
      'INVALID_INPUT'
    );
  }

  const url = `${normalizedUrl}/products/${handle.trim()}.js`;

  let response;
  try {
    response = await fetch(url, {
      headers: { Accept: 'application/json', ...extraHeaders },
    });
  } catch (err) {
    throw new ShopifyVariantError(`Network error: ${err.message}`, 'NETWORK_ERROR', { cause: err });
  }

  if (response.status === 404) {
    throw new ShopifyVariantError(`Product not found: "${handle}"`, 'PRODUCT_NOT_FOUND', { status: 404 });
  }

  if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After');
    throw new ShopifyVariantError(
      `Rate limited. Retry after: ${retryAfter ?? 'unknown'}`,
      'RATE_LIMITED',
      { status: 429 }
    );
  }

  if (!response.ok) {
    throw new ShopifyVariantError(
      `Unexpected response: HTTP ${response.status}`,
      'REQUEST_FAILED',
      { status: response.status }
    );
  }

  return response.json();
}

export function createVariantScraper(storeUrl, options = {}) {
  const normalizedUrl = normalizeUrl(storeUrl);
  const extraHeaders = options.headers ?? {};

  async function getProduct(handle) {
    return fetchProduct(normalizedUrl, handle, extraHeaders);
  }

  async function getVariants(handle) {
    const product = await fetchProduct(normalizedUrl, handle, extraHeaders);
    return Array.isArray(product.variants) ? product.variants : [];
  }

  async function getAvailableVariants(handle) {
    const variants = await getVariants(handle);
    return variants.filter((v) => v.available === true);
  }

  return { getProduct, getVariants, getAvailableVariants };
}

export function createStockMonitor(storeUrl, options = {}) {
  const normalizedUrl = normalizeUrl(storeUrl);
  const scraper = createVariantScraper(normalizedUrl, options);

  // Map<handle, { intervalId, previousState: Map<variantId, variantObj> }>
  const watchers = new Map();

  function buildDiff(previousState, currentState) {
    const changes = [];

    for (const [id, prev] of previousState) {
      if (!currentState.has(id)) {
        changes.push({ type: 'removed', variant: prev });
      }
    }

    for (const [id, curr] of currentState) {
      if (!previousState.has(id)) {
        changes.push({ type: 'added', variant: curr });
      } else {
        const prev = previousState.get(id);
        if (!prev.available && curr.available) {
          changes.push({ type: 'restock', variant: curr });
        } else if (prev.available && !curr.available) {
          changes.push({ type: 'sold_out', variant: curr });
        }
      }
    }

    return changes;
  }

  async function watch(handle, callback, watchOptions = {}) {
    if (!handle || typeof handle !== 'string') {
      throw new ShopifyVariantError('handle must be a non-empty string', 'INVALID_INPUT');
    }
    if (typeof callback !== 'function') {
      throw new ShopifyVariantError('callback must be a function', 'INVALID_INPUT');
    }

    // Re-watch: clear any existing watcher for this handle
    if (watchers.has(handle)) {
      unwatch(handle);
    }

    const interval = Math.max(1000, watchOptions.interval ?? 10_000);

    // Initial fetch — build baseline snapshot, no callback
    let previousState;
    try {
      const variants = await scraper.getVariants(handle);
      previousState = new Map(variants.map((v) => [v.id, v]));
    } catch (err) {
      callback(null, err);
      return;
    }

    let running = false;

    async function tick() {
      if (running) return;
      running = true;
      try {
        const variants = await scraper.getVariants(handle);
        const currentState = new Map(variants.map((v) => [v.id, v]));
        const changes = buildDiff(previousState, currentState);
        previousState = currentState;
        if (changes.length > 0) {
          callback(changes);
        }
      } catch (err) {
        callback(null, err);
      } finally {
        running = false;
      }
    }

    const intervalId = setInterval(() => { tick(); }, interval);
    watchers.set(handle, { intervalId, get previousState() { return previousState; } });
  }

  function unwatch(handle) {
    const watcher = watchers.get(handle);
    if (watcher) {
      clearInterval(watcher.intervalId);
      watchers.delete(handle);
    }
  }

  function stop() {
    for (const handle of Array.from(watchers.keys())) {
      unwatch(handle);
    }
  }

  return { watch, unwatch, stop };
}
