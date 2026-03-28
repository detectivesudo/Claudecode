import { createVariantScraper, createStockMonitor, ShopifyVariantError } from '../src/shopify-variants.js';

// Replace these with your actual store URL and product handle
const STORE_URL = 'https://your-store.myshopify.com';
const PRODUCT_HANDLE = 'example-product';

// --- Part 1: Scrape all variants ---
try {
  const scraper = createVariantScraper(STORE_URL);
  const variants = await scraper.getVariants(PRODUCT_HANDLE);

  console.log(`Found ${variants.length} variant(s) for "${PRODUCT_HANDLE}":`);
  for (const v of variants) {
    const status = v.available ? 'IN STOCK  ' : 'OUT OF STOCK';
    const opts = [v.option1, v.option2, v.option3].filter(Boolean).join(' / ') || 'Default';
    console.log(`  [${status}] ${opts} — $${(v.price / 100).toFixed(2)} (id: ${v.id})`);
  }
} catch (err) {
  if (err instanceof ShopifyVariantError) {
    console.error(`[${err.code}] ${err.message}`);
    process.exit(1);
  }
  throw err;
}

console.log('');

// --- Part 2: Monitor stock changes ---
const monitor = createStockMonitor(STORE_URL);

await monitor.watch(PRODUCT_HANDLE, (changes, error) => {
  if (error) {
    console.error(`Monitor error [${error.code ?? 'UNKNOWN'}]: ${error.message}`);
    return;
  }

  for (const change of changes) {
    const label = change.type.toUpperCase().replace('_', ' ');
    const opts = [change.variant.option1, change.variant.option2, change.variant.option3]
      .filter(Boolean).join(' / ') || 'Default';
    console.log(`[${label}] ${opts} — id: ${change.variant.id}`);
  }
}, { interval: 5000 });

console.log(`Watching "${PRODUCT_HANDLE}" for stock changes every 5s. Will stop after 60s.`);

setTimeout(() => {
  monitor.unwatch(PRODUCT_HANDLE);
  console.log('Stopped watching. Exiting.');
}, 60_000);
