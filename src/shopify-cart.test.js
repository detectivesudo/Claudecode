import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import { MockAgent, setGlobalDispatcher } from 'undici';
import { createShopifyCart, ShopifyCartError } from './shopify-cart.js';

const STORE_ORIGIN = 'https://test.myshopify.com';
const STORE_URL = 'https://test.myshopify.com';

// ---------------------------------------------------------------------------
// ShopifyCartError
// ---------------------------------------------------------------------------

describe('ShopifyCartError', () => {
  it('extends Error', () => {
    const err = new ShopifyCartError('msg', 'CODE');
    assert.ok(err instanceof Error);
  });

  it('sets .name to ShopifyCartError', () => {
    const err = new ShopifyCartError('msg', 'CODE');
    assert.equal(err.name, 'ShopifyCartError');
  });

  it('sets .code', () => {
    const err = new ShopifyCartError('msg', 'INVALID_INPUT');
    assert.equal(err.code, 'INVALID_INPUT');
  });

  it('sets .status from options', () => {
    const err = new ShopifyCartError('msg', 'CODE', { status: 404 });
    assert.equal(err.status, 404);
  });

  it('status defaults to null when not provided', () => {
    const err = new ShopifyCartError('msg', 'CODE');
    assert.equal(err.status, null);
  });

  it('sets .cause from options', () => {
    const original = new Error('original');
    const err = new ShopifyCartError('msg', 'CODE', { cause: original });
    assert.equal(err.cause, original);
  });

  it('cause is undefined when not provided', () => {
    const err = new ShopifyCartError('msg', 'CODE');
    assert.equal(err.cause, undefined);
  });

  it('sets .message correctly', () => {
    const err = new ShopifyCartError('something went wrong', 'CODE');
    assert.equal(err.message, 'something went wrong');
  });
});

// ---------------------------------------------------------------------------
// createShopifyCart — input validation
// ---------------------------------------------------------------------------

describe('createShopifyCart — input validation', () => {
  it('throws INVALID_INPUT for null storeUrl', () => {
    assert.throws(
      () => createShopifyCart(null),
      (err) => {
        assert.ok(err instanceof ShopifyCartError);
        assert.equal(err.code, 'INVALID_INPUT');
        return true;
      }
    );
  });

  it('throws INVALID_INPUT for undefined storeUrl', () => {
    assert.throws(
      () => createShopifyCart(undefined),
      (err) => { assert.equal(err.code, 'INVALID_INPUT'); return true; }
    );
  });

  it('throws INVALID_INPUT for empty string storeUrl', () => {
    assert.throws(
      () => createShopifyCart(''),
      (err) => { assert.equal(err.code, 'INVALID_INPUT'); return true; }
    );
  });

  it('throws INVALID_INPUT for numeric storeUrl', () => {
    assert.throws(
      () => createShopifyCart(42),
      (err) => { assert.equal(err.code, 'INVALID_INPUT'); return true; }
    );
  });

  it('throws INVALID_INPUT for a syntactically invalid URL string', () => {
    assert.throws(
      () => createShopifyCart('not a valid url!!!'),
      (err) => { assert.equal(err.code, 'INVALID_INPUT'); return true; }
    );
  });

  it('returns addVariant, getCart, getCheckoutUrl functions on valid input', () => {
    const cart = createShopifyCart(STORE_URL);
    assert.equal(typeof cart.addVariant, 'function');
    assert.equal(typeof cart.getCart, 'function');
    assert.equal(typeof cart.getCheckoutUrl, 'function');
  });
});

// ---------------------------------------------------------------------------
// createShopifyCart — URL normalization
// ---------------------------------------------------------------------------

describe('createShopifyCart — URL normalization', () => {
  let agent, pool;

  beforeEach(() => {
    agent = new MockAgent();
    agent.disableNetConnect();
    setGlobalDispatcher(agent);
    pool = agent.get(STORE_ORIGIN);
  });

  afterEach(async () => { await agent.close(); });

  const cartBody = JSON.stringify({ item_count: 0, token: null });

  it('prepends https:// for a bare domain', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, cartBody, { headers: { 'content-type': 'application/json' } });
    const cart = createShopifyCart('test.myshopify.com');
    await cart.getCart();
  });

  it('strips a single trailing slash', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, cartBody, { headers: { 'content-type': 'application/json' } });
    const cart = createShopifyCart('https://test.myshopify.com/');
    await cart.getCart();
  });

  it('strips multiple trailing slashes', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, cartBody, { headers: { 'content-type': 'application/json' } });
    const cart = createShopifyCart('https://test.myshopify.com///');
    await cart.getCart();
  });

  it('trims leading/trailing whitespace', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, cartBody, { headers: { 'content-type': 'application/json' } });
    const cart = createShopifyCart('  https://test.myshopify.com  ');
    await cart.getCart();
  });

  it('preserves http:// scheme as-is', async () => {
    const httpAgent = new MockAgent();
    httpAgent.disableNetConnect();
    setGlobalDispatcher(httpAgent);
    const httpPool = httpAgent.get('http://test.myshopify.com');
    httpPool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, cartBody, { headers: { 'content-type': 'application/json' } });
    const cart = createShopifyCart('http://test.myshopify.com');
    await cart.getCart();
    await httpAgent.close();
  });
});

// ---------------------------------------------------------------------------
// addVariant — input validation
// ---------------------------------------------------------------------------

describe('addVariant — input validation', () => {
  let agent, pool, cart;

  beforeEach(() => {
    agent = new MockAgent();
    agent.disableNetConnect();
    setGlobalDispatcher(agent);
    pool = agent.get(STORE_ORIGIN);
    cart = createShopifyCart(STORE_URL);
  });

  afterEach(async () => { await agent.close(); });

  const rejectInput = async (fn) => {
    await assert.rejects(fn, (err) => {
      assert.ok(err instanceof ShopifyCartError);
      assert.equal(err.code, 'INVALID_INPUT');
      return true;
    });
  };

  it('throws INVALID_INPUT for null variantId', () => rejectInput(() => cart.addVariant(null)));
  it('throws INVALID_INPUT for undefined variantId', () => rejectInput(() => cart.addVariant(undefined)));
  it('throws INVALID_INPUT for non-numeric string variantId', () => rejectInput(() => cart.addVariant('abc')));
  it('throws INVALID_INPUT for zero variantId', () => rejectInput(() => cart.addVariant(0)));
  it('throws INVALID_INPUT for quantity 0', () => rejectInput(() => cart.addVariant(123, 0)));
  it('throws INVALID_INPUT for negative quantity', () => rejectInput(() => cart.addVariant(123, -1)));
  it('throws INVALID_INPUT for fractional quantity', () => rejectInput(() => cart.addVariant(123, 1.5)));

  it('accepts a string numeric variantId', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(200, JSON.stringify({ id: 456789 }), { headers: { 'content-type': 'application/json' } });
    await cart.addVariant('456789');
  });

  it('accepts a string integer quantity', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(200, JSON.stringify({ id: 123 }), { headers: { 'content-type': 'application/json' } });
    await cart.addVariant(123, '2');
  });

  it('defaults quantity to 1', async () => {
    let capturedBody;
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(200, (opts) => {
        capturedBody = JSON.parse(opts.body);
        return JSON.stringify({ id: 123 });
      }, { headers: { 'content-type': 'application/json' } });
    await cart.addVariant(123);
    assert.equal(capturedBody.quantity, 1);
  });
});

// ---------------------------------------------------------------------------
// addVariant — HTTP response handling
// ---------------------------------------------------------------------------

describe('addVariant — HTTP response handling', () => {
  let agent, pool, cart;

  beforeEach(() => {
    agent = new MockAgent();
    agent.disableNetConnect();
    setGlobalDispatcher(agent);
    pool = agent.get(STORE_ORIGIN);
    cart = createShopifyCart(STORE_URL);
  });

  afterEach(async () => { await agent.close(); });

  it('returns parsed JSON on 200', async () => {
    const body = { id: 1, title: 'Shirt' };
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(200, JSON.stringify(body), { headers: { 'content-type': 'application/json' } });
    const result = await cart.addVariant(1);
    assert.deepEqual(result, body);
  });

  it('throws VARIANT_NOT_FOUND on 404', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(404, '{}', { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.addVariant(99),
      (err) => {
        assert.ok(err instanceof ShopifyCartError);
        assert.equal(err.code, 'VARIANT_NOT_FOUND');
        assert.equal(err.status, 404);
        assert.ok(err.message.includes('99'));
        return true;
      }
    );
  });

  it('throws VARIANT_UNAVAILABLE on 422 using description field', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(422, JSON.stringify({ description: 'Sold out' }), { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.addVariant(1),
      (err) => {
        assert.equal(err.code, 'VARIANT_UNAVAILABLE');
        assert.equal(err.status, 422);
        assert.equal(err.message, 'Sold out');
        return true;
      }
    );
  });

  it('throws VARIANT_UNAVAILABLE on 422 using message field when no description', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(422, JSON.stringify({ message: 'Out of stock' }), { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.addVariant(1),
      (err) => {
        assert.equal(err.code, 'VARIANT_UNAVAILABLE');
        assert.equal(err.message, 'Out of stock');
        return true;
      }
    );
  });

  it('throws VARIANT_UNAVAILABLE on 422 with fallback when body is empty object', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(422, JSON.stringify({}), { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.addVariant(1),
      (err) => {
        assert.equal(err.code, 'VARIANT_UNAVAILABLE');
        assert.equal(err.message, 'Variant unavailable');
        return true;
      }
    );
  });

  it('throws VARIANT_UNAVAILABLE on 422 with fallback when body is non-JSON', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(422, 'plain error text', { headers: { 'content-type': 'text/plain' } });
    await assert.rejects(
      () => cart.addVariant(1),
      (err) => {
        assert.equal(err.code, 'VARIANT_UNAVAILABLE');
        assert.equal(err.message, 'Variant unavailable');
        return true;
      }
    );
  });

  it('throws REQUEST_FAILED on 500', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(500, '{}', { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.addVariant(1),
      (err) => {
        assert.equal(err.code, 'REQUEST_FAILED');
        assert.equal(err.status, 500);
        return true;
      }
    );
  });

  it('throws REQUEST_FAILED on 503', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(503, '{}', { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.addVariant(1),
      (err) => {
        assert.equal(err.code, 'REQUEST_FAILED');
        assert.equal(err.status, 503);
        return true;
      }
    );
  });

  it('throws NETWORK_ERROR on fetch rejection', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .replyWithError(new Error('ECONNREFUSED'));
    await assert.rejects(
      () => cart.addVariant(1),
      (err) => {
        assert.ok(err instanceof ShopifyCartError);
        assert.equal(err.code, 'NETWORK_ERROR');
        assert.ok(err.message.startsWith('Network error:'));
        assert.ok(err.cause instanceof Error);
        return true;
      }
    );
  });

  it('sends POST to /cart/add.js', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(200, JSON.stringify({ id: 1 }), { headers: { 'content-type': 'application/json' } });
    await cart.addVariant(1);
  });

  it('sends correct JSON body', async () => {
    let capturedBody;
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(200, (opts) => {
        capturedBody = JSON.parse(opts.body);
        return JSON.stringify({ id: 123 });
      }, { headers: { 'content-type': 'application/json' } });
    await cart.addVariant(123, 1);
    assert.deepEqual(capturedBody, { id: 123, quantity: 1 });
  });

  it('sends Content-Type and Accept headers', async () => {
    let capturedHeaders;
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(200, (opts) => {
        capturedHeaders = opts.headers;
        return JSON.stringify({ id: 1 });
      }, { headers: { 'content-type': 'application/json' } });
    await cart.addVariant(1);
    assert.equal(capturedHeaders['Content-Type'], 'application/json');
    assert.equal(capturedHeaders['Accept'], 'application/json');
  });
});

// ---------------------------------------------------------------------------
// getCart — HTTP response handling
// ---------------------------------------------------------------------------

describe('getCart — HTTP response handling', () => {
  let agent, pool, cart;

  beforeEach(() => {
    agent = new MockAgent();
    agent.disableNetConnect();
    setGlobalDispatcher(agent);
    pool = agent.get(STORE_ORIGIN);
    cart = createShopifyCart(STORE_URL);
  });

  afterEach(async () => { await agent.close(); });

  it('returns parsed cart JSON on 200', async () => {
    const body = { item_count: 2, token: 'abc' };
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, JSON.stringify(body), { headers: { 'content-type': 'application/json' } });
    const result = await cart.getCart();
    assert.deepEqual(result, body);
  });

  it('throws REQUEST_FAILED on 401', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(401, '{}', { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.getCart(),
      (err) => {
        assert.equal(err.code, 'REQUEST_FAILED');
        assert.equal(err.status, 401);
        return true;
      }
    );
  });

  it('throws REQUEST_FAILED on 500', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(500, '{}', { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.getCart(),
      (err) => {
        assert.equal(err.code, 'REQUEST_FAILED');
        assert.equal(err.status, 500);
        return true;
      }
    );
  });

  it('sends GET to /cart.js', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, JSON.stringify({ item_count: 0, token: null }), { headers: { 'content-type': 'application/json' } });
    await cart.getCart();
  });

  it('sends Accept: application/json', async () => {
    let capturedHeaders;
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, (opts) => {
        capturedHeaders = opts.headers;
        return JSON.stringify({ item_count: 0 });
      }, { headers: { 'content-type': 'application/json' } });
    await cart.getCart();
    assert.equal(capturedHeaders['Accept'], 'application/json');
  });
});

// ---------------------------------------------------------------------------
// getCheckoutUrl — business logic
// ---------------------------------------------------------------------------

describe('getCheckoutUrl — business logic', () => {
  let agent, pool, cart;

  beforeEach(() => {
    agent = new MockAgent();
    agent.disableNetConnect();
    setGlobalDispatcher(agent);
    pool = agent.get(STORE_ORIGIN);
    cart = createShopifyCart(STORE_URL);
  });

  afterEach(async () => { await agent.close(); });

  it('returns correct URL when cart has items and a token', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, JSON.stringify({ item_count: 1, token: 'tok_abc' }), { headers: { 'content-type': 'application/json' } });
    const url = await cart.getCheckoutUrl();
    assert.equal(url, 'https://test.myshopify.com/cart/c/tok_abc');
  });

  it('throws EMPTY_CART when item_count is 0', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, JSON.stringify({ item_count: 0, token: 'tok' }), { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.getCheckoutUrl(),
      (err) => { assert.equal(err.code, 'EMPTY_CART'); return true; }
    );
  });

  it('throws EMPTY_CART when item_count is missing', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, JSON.stringify({ token: 'tok' }), { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.getCheckoutUrl(),
      (err) => { assert.equal(err.code, 'EMPTY_CART'); return true; }
    );
  });

  it('throws EMPTY_CART when item_count is null', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, JSON.stringify({ item_count: null, token: 'tok' }), { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.getCheckoutUrl(),
      (err) => { assert.equal(err.code, 'EMPTY_CART'); return true; }
    );
  });

  it('throws REQUEST_FAILED when token is missing', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, JSON.stringify({ item_count: 1 }), { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.getCheckoutUrl(),
      (err) => { assert.equal(err.code, 'REQUEST_FAILED'); return true; }
    );
  });

  it('throws REQUEST_FAILED when token is empty string', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, JSON.stringify({ item_count: 1, token: '' }), { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.getCheckoutUrl(),
      (err) => { assert.equal(err.code, 'REQUEST_FAILED'); return true; }
    );
  });

  it('propagates REQUEST_FAILED from getCart HTTP failure', async () => {
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(500, '{}', { headers: { 'content-type': 'application/json' } });
    await assert.rejects(
      () => cart.getCheckoutUrl(),
      (err) => {
        assert.equal(err.code, 'REQUEST_FAILED');
        assert.equal(err.status, 500);
        return true;
      }
    );
  });
});

// ---------------------------------------------------------------------------
// Cookie persistence
// ---------------------------------------------------------------------------

describe('cookie persistence', () => {
  let agent, pool, cart;

  beforeEach(() => {
    agent = new MockAgent();
    agent.disableNetConnect();
    setGlobalDispatcher(agent);
    pool = agent.get(STORE_ORIGIN);
    cart = createShopifyCart(STORE_URL);
  });

  afterEach(async () => { await agent.close(); });

  it('cookies from first response are sent in subsequent request', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(200, JSON.stringify({ id: 1 }), {
        headers: { 'set-cookie': '_shopify_s=sess123; Path=/', 'content-type': 'application/json' },
      });

    let capturedCookieHeader;
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, (opts) => {
        capturedCookieHeader = opts.headers['Cookie'];
        return JSON.stringify({ item_count: 1, token: 'tok' });
      }, { headers: { 'content-type': 'application/json' } });

    await cart.addVariant(1);
    await cart.getCart();
    assert.ok(capturedCookieHeader, 'Cookie header should be present');
    assert.ok(capturedCookieHeader.includes('_shopify_s=sess123'));
  });

  it('no Cookie header sent when jar is empty', async () => {
    let capturedCookieHeader;
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, (opts) => {
        capturedCookieHeader = opts.headers['Cookie'];
        return JSON.stringify({ item_count: 0 });
      }, { headers: { 'content-type': 'application/json' } });

    await cart.getCart();
    assert.ok(!capturedCookieHeader, 'Cookie header should be absent on empty jar');
  });

  it('multiple Set-Cookie headers are all stored and forwarded', async () => {
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(200, JSON.stringify({ id: 1 }), {
        headers: { 'set-cookie': ['_shopify_s=sess123; Path=/', 'cart=abcdef; Path=/'], 'content-type': 'application/json' },
      });

    let capturedCookieHeader;
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, (opts) => {
        capturedCookieHeader = opts.headers['Cookie'];
        return JSON.stringify({ item_count: 1, token: 'tok' });
      }, { headers: { 'content-type': 'application/json' } });

    await cart.addVariant(1);
    await cart.getCart();
    assert.ok(capturedCookieHeader.includes('_shopify_s=sess123'));
    assert.ok(capturedCookieHeader.includes('cart=abcdef'));
  });
});

// ---------------------------------------------------------------------------
// Custom headers (options.headers)
// ---------------------------------------------------------------------------

describe('custom headers (options.headers)', () => {
  let agent, pool;

  beforeEach(() => {
    agent = new MockAgent();
    agent.disableNetConnect();
    setGlobalDispatcher(agent);
    pool = agent.get(STORE_ORIGIN);
  });

  afterEach(async () => { await agent.close(); });

  it('custom headers are forwarded on addVariant', async () => {
    let capturedHeaders;
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(200, (opts) => {
        capturedHeaders = opts.headers;
        return JSON.stringify({ id: 1 });
      }, { headers: { 'content-type': 'application/json' } });

    const cart = createShopifyCart(STORE_URL, { headers: { 'X-Custom': 'foo' } });
    await cart.addVariant(1);
    assert.equal(capturedHeaders['X-Custom'], 'foo');
  });

  it('custom headers are forwarded on getCart', async () => {
    let capturedHeaders;
    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, (opts) => {
        capturedHeaders = opts.headers;
        return JSON.stringify({ item_count: 0 });
      }, { headers: { 'content-type': 'application/json' } });

    const cart = createShopifyCart(STORE_URL, { headers: { 'X-Custom': 'bar' } });
    await cart.getCart();
    assert.equal(capturedHeaders['X-Custom'], 'bar');
  });

  it('custom Content-Type overrides the default (documents spread order)', async () => {
    let capturedHeaders;
    pool.intercept({ path: '/cart/add.js', method: 'POST' })
      .reply(200, (opts) => {
        capturedHeaders = opts.headers;
        return JSON.stringify({ id: 1 });
      }, { headers: { 'content-type': 'application/json' } });

    const cart = createShopifyCart(STORE_URL, { headers: { 'Content-Type': 'text/plain' } });
    await cart.addVariant(1);
    assert.equal(capturedHeaders['Content-Type'], 'text/plain');
  });

  it('two cart instances do not share headers', async () => {
    let headersA, headersB;

    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, (opts) => {
        headersA = opts.headers;
        return JSON.stringify({ item_count: 0 });
      }, { headers: { 'content-type': 'application/json' } });

    pool.intercept({ path: '/cart.js', method: 'GET' })
      .reply(200, (opts) => {
        headersB = opts.headers;
        return JSON.stringify({ item_count: 0 });
      }, { headers: { 'content-type': 'application/json' } });

    const cartA = createShopifyCart(STORE_URL, { headers: { 'X-Instance': 'A' } });
    const cartB = createShopifyCart(STORE_URL, { headers: { 'X-Instance': 'B' } });

    await cartA.getCart();
    await cartB.getCart();

    assert.equal(headersA['X-Instance'], 'A');
    assert.equal(headersB['X-Instance'], 'B');
  });
});
