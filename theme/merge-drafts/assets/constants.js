const ON_CHANGE_DEBOUNCE_TIMER = 300;

const PUB_SUB_EVENTS = {
  cartUpdate: 'cart-update',
  quantityUpdate: 'quantity-update',
  optionValueSelectionChange: 'option-value-selection-change',
  variantChange: 'variant-change',
  cartError: 'cart-error',
};

/* SC order cap (8 Nov 2026): at most 5 physical items per order. Digital items, NFTs and gift vouchers are not counted.
   Added to this small file because it loads on every page. To undo, delete everything below this line. */
(function () {
  var CAP = 5;
  var cart = null;
  var shipsByVariant = null;
  var timer = null;

  function physical(c) {
    var n = 0;
    ((c && c.items) || []).forEach(function (i) { if (i.requires_shipping) n += i.quantity; });
    return n;
  }

  function note(key, text, before) {
    if (!before || !before.parentNode) return;
    var el = before.parentNode.querySelector('[data-sc-cap="' + key + '"]');
    if (!text) { if (el) el.remove(); return; }
    if (!el) {
      el = document.createElement('div');
      el.setAttribute('data-sc-cap', key);
      el.setAttribute('role', 'alert');
      el.style.cssText = 'margin:1rem 0;padding:1rem 1.2rem;border:2px solid #b00020;background:#fff3f3;color:#7a0016;font-weight:600;line-height:1.4;text-align:left;';
      before.parentNode.insertBefore(el, before);
    }
    if (el.textContent !== text) el.textContent = text;
  }

  function cartText(n) {
    return 'Order limit: ' + CAP + ' items per order. Your basket has ' + n + ', please remove ' + (n - CAP) + ' to check out. Need a bigger order? Email hq@stiffcompetition.shop.';
  }

  function applyCart(n) {
    var over = n > CAP;
    document.querySelectorAll('button[name="checkout"], #checkout').forEach(function (b) {
      if (over) { b.disabled = true; b.setAttribute('data-sc-off', '1'); }
      else if (b.getAttribute('data-sc-off')) { b.disabled = false; b.removeAttribute('data-sc-off'); }
      note('checkout', over ? cartText(n) : '', b);
    });
    document.querySelectorAll('.additional-checkout-buttons, shopify-accelerated-checkout-cart').forEach(function (e) {
      e.style.display = over ? 'none' : '';
    });
    document.querySelectorAll('cart-items, cart-drawer-items').forEach(function (e) {
      note('top', over ? cartText(n) : '', e);
    });
    document.querySelectorAll('.quantity__input[data-quantity-variant-id]').forEach(function (inp) {
      var id = Number(inp.getAttribute('data-quantity-variant-id'));
      var line = ((cart && cart.items) || []).filter(function (i) { return i.variant_id === id; })[0];
      if (line && line.requires_shipping) inp.max = String(line.quantity + Math.max(CAP - n, 0));
    });
  }

  function applyProduct(n) {
    if (location.pathname.indexOf('/products/') < 0) return;
    document.querySelectorAll('form[action*="/cart/add"]').forEach(function (f) {
      var vid = f.querySelector('[name="id"]');
      var qty = f.querySelector('input[name="quantity"]');
      var add = f.querySelector('button[name="add"], button[type="submit"]');
      if (!vid || !add) return;
      if (shipsByVariant && shipsByVariant[vid.value] === false) return;
      var left = Math.max(CAP - n, 0);
      if (qty) {
        qty.max = String(Math.max(left, 1));
        if (Number(qty.value) > left && left > 0) qty.value = String(left);
      }
      add.setAttribute('data-sc-cap-left', String(left));
      note('product', left === 0
        ? 'Order limit: ' + CAP + ' items per order. Your basket already has ' + n + '. Check out first, or remove something to add more.'
        : 'Limit ' + CAP + ' items per order. You can add up to ' + left + ' more.', add.closest('.product-form__buttons') || add);
    });
  }

  function apply() {
    try {
      if (!cart) return;
      var n = physical(cart);
      applyCart(n);
      applyProduct(n);
    } catch (e) {}
  }

  function refresh() {
    fetch('/cart.js', { credentials: 'same-origin', headers: { Accept: 'application/json' } })
      .then(function (r) { return r.json(); })
      .then(function (c) { cart = c; apply(); })
      .catch(function () {});
  }

  function later(ms) { clearTimeout(timer); timer = setTimeout(refresh, ms); }

  function loadProduct() {
    var m = location.pathname.match(/\/products\/([^\/?#]+)/);
    if (!m) return;
    fetch('/products/' + m[1] + '.js', { credentials: 'same-origin' })
      .then(function (r) { return r.json(); })
      .then(function (p) {
        shipsByVariant = {};
        (p.variants || []).forEach(function (v) { shipsByVariant[String(v.id)] = v.requires_shipping !== false; });
        apply();
      })
      .catch(function () {});
  }

  document.addEventListener('click', function (e) {
    var b = e.target.closest && e.target.closest('button[name="checkout"], #checkout');
    if (b && cart && physical(cart) > CAP) { e.preventDefault(); e.stopPropagation(); }
  }, true);

  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f || !f.matches) return;
    if (f.matches('form[action*="/cart/add"]')) {
      var add = f.querySelector('button[name="add"], button[type="submit"]');
      var left = add ? Number(add.getAttribute('data-sc-cap-left')) : NaN;
      var qty = f.querySelector('input[name="quantity"]');
      var want = qty ? Number(qty.value) || 1 : 1;
      if (!isNaN(left) && want > left) { e.preventDefault(); e.stopImmediatePropagation(); }
    } else if (cart && physical(cart) > CAP && e.submitter && e.submitter.name === 'checkout') {
      e.preventDefault(); e.stopImmediatePropagation();
    }
  }, true);

  var origFetch = window.fetch;
  window.fetch = function () {
    var url = String(arguments[0] && arguments[0].url ? arguments[0].url : arguments[0]);
    var p = origFetch.apply(this, arguments);
    if (/\/cart\/(add|change|update|clear)/.test(url)) p.then(function () { later(500); }, function () {});
    return p;
  };

  document.addEventListener('change', function () { later(400); });
  document.addEventListener('DOMContentLoaded', function () {
    refresh();
    loadProduct();
    new MutationObserver(function () { clearTimeout(window.__scCapT); window.__scCapT = setTimeout(apply, 150); })
      .observe(document.body, { childList: true, subtree: true });
  });
})();
