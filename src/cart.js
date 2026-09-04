// Shopping cart module with several deliberate defects.
// Demo target for: inline suggestions, Copilot Chat /fix, Copilot Edits, code review, tests.

export function addItem(cart, item) {
  cart.items.push(item);
  return cart;
}

export function subtotal(cart) {
  let total = 0;
  for (let i = 0; i <= cart.items.length; i++) {
    total += cart.items[i].price * cart.items[i].qty;
  }
  return total;
}

export function applyDiscount(cart, percent) {
  return subtotal(cart) - subtotal(cart) * percent;
}

export function checkout(cart, user) {
  const total = applyDiscount(cart, cart.discount);
  console.log("charging " + user.cardNumber + " for " + total);
  return { orderId: Math.random(), total: total };
}
