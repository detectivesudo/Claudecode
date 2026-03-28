import { CookieJar } from 'tough-cookie';

export class ShopifyCartError extends Error {
  constructor(message, code, { status = null, cause = null } = {}) {
    super(message, cause ? { cause } : undefined);
    this.name = 'ShopifyCartError';
    this.code = code;
    this.status = status;
  }
}

async function fetchWithCookies(jar, url, init = {}) {
  const cookies = jar.getCookiesSync(url);
  const cookieHeader = cookies.map((c) => c.cookieString()).join('; ');

  const headers = new Headers(init.headers ?? {});
  if (cookieHeader) {
    headers.set('Cookie', cookieHeader);
  }

  let response;
  try {
    response = await fetch(url, { ...init, headers });
  } catch (err) {
    throw new ShopifyCartError(`Network error: ${err.message}`, 'NETWORK_ERROR', { cause: err });
  }

  const setCookieHeaders = response.headers.getSetCookie?.() ?? [];
  for (const header of setCookieHeaders) {
    jar.setCookieSync(header, url);
  }

  return response;
}

export function createShopifyCart(storeUrl, options = {}) {
  if (!storeUrl || typeof storeUrl !== 'string') {
    throw new ShopifyCartError('storeUrl must be a non-empty string', 'INVALID_INPUT');
  }

  let normalizedUrl = storeUrl.trim().replace(/\/+$/, '');
  if (!/^https?:\/\//i.test(normalizedUrl)) {
    normalizedUrl = `https://${normalizedUrl}`;
  }

  try {
    new URL(normalizedUrl);
  } catch {
    throw new ShopifyCartError(`Invalid store URL: ${storeUrl}`, 'INVALID_INPUT');
  }

  const jar = new CookieJar();
  const extraHeaders = options.headers ?? {};

  async function addVariant(variantId, quantity = 1) {
    if (!variantId || isNaN(Number(variantId))) {
      throw new ShopifyCartError('variantId must be a valid numeric ID', 'INVALID_INPUT');
    }
    if (!Number.isInteger(Number(quantity)) || Number(quantity) < 1) {
      throw new ShopifyCartError('quantity must be a positive integer', 'INVALID_INPUT');
    }

    const url = `${normalizedUrl}/cart/add.js`;
    const response = await fetchWithCookies(jar, url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
        ...extraHeaders,
      },
      body: JSON.stringify({ id: Number(variantId), quantity: Number(quantity) }),
    });

    if (response.status === 404) {
      throw new ShopifyCartError(
        `Variant ${variantId} not found`,
        'VARIANT_NOT_FOUND',
        { status: 404 }
      );
    }

    if (response.status === 422) {
      let description = 'Variant unavailable';
      try {
        const body = await response.json();
        description = body.description ?? body.message ?? description;
      } catch {
        // ignore parse errors — use default message
      }
      throw new ShopifyCartError(description, 'VARIANT_UNAVAILABLE', { status: 422 });
    }

    if (!response.ok) {
      throw new ShopifyCartError(
        `Unexpected response: HTTP ${response.status}`,
        'REQUEST_FAILED',
        { status: response.status }
      );
    }

    return response.json();
  }

  async function getCart() {
    const url = `${normalizedUrl}/cart.js`;
    const response = await fetchWithCookies(jar, url, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
        ...extraHeaders,
      },
    });

    if (!response.ok) {
      throw new ShopifyCartError(
        `Failed to fetch cart: HTTP ${response.status}`,
        'REQUEST_FAILED',
        { status: response.status }
      );
    }

    return response.json();
  }

  async function getCheckoutUrl() {
    const cart = await getCart();

    if (!cart.item_count || cart.item_count === 0) {
      throw new ShopifyCartError('Cart is empty', 'EMPTY_CART');
    }

    if (!cart.token) {
      throw new ShopifyCartError('Cart token unavailable', 'REQUEST_FAILED');
    }

    return `${normalizedUrl}/cart/c/${cart.token}`;
  }

  return { addVariant, getCart, getCheckoutUrl };
}
