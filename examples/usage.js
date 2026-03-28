import { createShopifyCart, ShopifyCartError } from '../src/shopify-cart.js';

// Replace these with your actual store URL and variant ID
const STORE_URL = 'https://your-store.myshopify.com';
const VARIANT_ID = 123456789; // numeric variant ID from Shopify
const QUANTITY = 1;

try {
  const cart = createShopifyCart(STORE_URL);

  console.log(`Adding variant ${VARIANT_ID} (qty: ${QUANTITY}) to cart...`);
  const lineItem = await cart.addVariant(VARIANT_ID, QUANTITY);
  console.log(`Added: ${lineItem.title} — ${lineItem.variant_title ?? 'default'}`);

  const cartState = await cart.getCart();
  console.log(`Cart now has ${cartState.item_count} item(s)`);
  console.log(`Total: ${(cartState.total_price / 100).toFixed(2)} ${cartState.currency}`);

  const checkoutUrl = await cart.getCheckoutUrl();
  console.log(`\nCheckout URL:\n${checkoutUrl}`);
} catch (err) {
  if (err instanceof ShopifyCartError) {
    console.error(`ShopifyCartError [${err.code}]: ${err.message}`);
    if (err.status) console.error(`HTTP status: ${err.status}`);
  } else {
    throw err;
  }
}
