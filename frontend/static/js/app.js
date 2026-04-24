/**
 * NEXMART — Frontend JavaScript (Single-Page Application)
 * ========================================================
 * All API calls go to Flask at /api/*
 * State is managed in simple JS objects (no framework needed).
 */

// ── App State ──────────────────────────────────────────────────────────────
const state = {
  user:       null,    // current logged-in user
  products:   [],      // cached product list
  categories: [],      // category list
  cartCount:  0,
  currentProductId: null,
  detailQty:  1,
  activeCategory: null,
};

// ── Category Emoji Map ─────────────────────────────────────────────────────
const CAT_EMOJI = {
  'men':          '👔',
  'women':        '👗',
  'electronics':  '💻',
  'sports':       '⚽',
  'home-living':  '🏠',
};

// ═══════════════════════════════════════════════════════════════════════════
// PAGE NAVIGATION
// ═══════════════════════════════════════════════════════════════════════════

function showPage(name) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  const page = document.getElementById(`page-${name}`);
  if (page) page.classList.add('active');
  window.scrollTo({ top: 0, behavior: 'smooth' });

  // Lazy-load page data
  if (name === 'home')           loadHome();
  if (name === 'products')       loadProducts();
  if (name === 'cart')           loadCart();
  if (name === 'orders')         loadOrders();
  if (name === 'admin')          loadAdmin();
  if (name === 'product-detail') loadProductDetail(state.currentProductId);
}

function filterCategory(slug) {
  state.activeCategory = slug;
  showPage('products');
}

// ═══════════════════════════════════════════════════════════════════════════
// API HELPER
// ═══════════════════════════════════════════════════════════════════════════

async function api(method, path, body = null) {
  const opts = {
    method,
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',   // send session cookie
  };
  if (body) opts.body = JSON.stringify(body);

  const res  = await fetch(`/api${path}`, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
}

// ═══════════════════════════════════════════════════════════════════════════
// AUTHENTICATION
// ═══════════════════════════════════════════════════════════════════════════

async function checkAuth() {
  try {
    const { user } = await api('GET', '/auth/me');
    state.user = user;
    updateAuthUI();
    refreshCartBadge();
  } catch {
    state.user = null;
    updateAuthUI();
  }
}

function updateAuthUI() {
  const u = state.user;
  document.getElementById('authNav').classList.toggle('hidden', !!u);
  document.getElementById('userNav').classList.toggle('hidden', !u);
  if (u) {
    document.getElementById('userGreeting').textContent = `Hi, ${u.name.split(' ')[0]}!`;
    document.getElementById('adminNavBtn').classList.toggle('hidden', u.role !== 'admin');
  }
}

async function login() {
  const email    = document.getElementById('loginEmail').value;
  const password = document.getElementById('loginPassword').value;
  const msgEl    = document.getElementById('loginMsg');

  try {
    const { user } = await api('POST', '/auth/login', { email, password });
    state.user = user;
    updateAuthUI();
    closeModal('loginModal');
    showToast(`Welcome back, ${user.name.split(' ')[0]}! 👋`);
    refreshCartBadge();
  } catch (err) {
    showMsg(msgEl, err.message, 'error');
  }
}

async function signup() {
  const name     = document.getElementById('signupName').value;
  const email    = document.getElementById('signupEmail').value;
  const password = document.getElementById('signupPassword').value;
  const msgEl    = document.getElementById('signupMsg');

  try {
    const { user } = await api('POST', '/auth/signup', { name, email, password });
    state.user = user;
    updateAuthUI();
    closeModal('signupModal');
    showToast(`Account created! Welcome, ${user.name.split(' ')[0]}! 🎉`);
    refreshCartBadge();
  } catch (err) {
    showMsg(msgEl, err.message, 'error');
  }
}

async function logout() {
  await api('POST', '/auth/logout');
  state.user = null;
  state.cartCount = 0;
  updateAuthUI();
  document.getElementById('cartBadge').textContent = '0';
  showToast('Logged out. See you soon!');
  showPage('home');
}

// ═══════════════════════════════════════════════════════════════════════════
// HOME PAGE
// ═══════════════════════════════════════════════════════════════════════════

async function loadHome() {
  await loadCategories();
  renderCategoryGrid();
  await loadFeatured();
}

async function loadCategories() {
  try {
    const { categories } = await api('GET', '/products/categories');
    state.categories = categories;
  } catch {}
}

function renderCategoryGrid() {
  const grid = document.getElementById('categoriesGrid');
  if (!grid) return;
  grid.innerHTML = state.categories.map(c => `
    <div class="cat-card" onclick="filterCategory('${c.slug}')">
      <div class="cat-emoji">${CAT_EMOJI[c.slug] || '🏷️'}</div>
      <div class="cat-name">${c.name}</div>
      <div class="cat-count">${c.product_count} products</div>
    </div>
  `).join('');
}

async function loadFeatured() {
  const grid = document.getElementById('featuredGrid');
  if (!grid) return;
  grid.innerHTML = '<div class="loader"><div class="spinner"></div></div>';
  try {
    const { products } = await api('GET', '/products/?sort=rating');
    const featured = products.slice(0, 8);
    grid.innerHTML = featured.map(productCard).join('');
  } catch {
    grid.innerHTML = '<p style="color:#999;padding:24px">Could not load products.</p>';
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// PRODUCTS PAGE
// ═══════════════════════════════════════════════════════════════════════════

async function loadProducts() {
  await loadCategories();   // ✅ ADD THIS LINE
  renderSidebarCats();
  await applyFilters();
}
function renderSidebarCats() {
  const el = document.getElementById('catFilters');
  if (!el) return;
  const all = `<button class="cat-filter-btn ${!state.activeCategory ? 'active' : ''}" onclick="setCat(null)">All</button>`;
  const cats = state.categories.map(c => `
    <button class="cat-filter-btn ${state.activeCategory === c.slug ? 'active' : ''}"
            onclick="setCat('${c.slug}')">${CAT_EMOJI[c.slug] || ''} ${c.name}</button>
  `).join('');
  el.innerHTML = all + cats;
}

function setCat(slug) {
  state.activeCategory = slug || null;

  // remove active class from all buttons
  document.querySelectorAll('.cat-filter-btn').forEach(b => b.classList.remove('active'));

  // set active button correctly
  const buttons = document.querySelectorAll('.cat-filter-btn');
  buttons.forEach(btn => {
    if (
      (slug === null && btn.innerText.trim() === 'All') ||
      (slug && btn.innerText.toLowerCase().includes(slug))
    ) {
      btn.classList.add('active');
    }
  });

  applyFilters();
}

async function applyFilters() {
  const grid    = document.getElementById('productsGrid');
  const empty   = document.getElementById('productsEmpty');
  const heading = document.getElementById('productsHeading');
  const countEl = document.getElementById('productCount');
  if (!grid) return;

  grid.innerHTML = '<div class="loader"><div class="spinner"></div></div>';
  empty?.classList.add('hidden');

  const search   = document.getElementById('searchInput')?.value || '';
  const minPrice = document.getElementById('minPrice')?.value || '';
  const maxPrice = document.getElementById('maxPrice')?.value || '';
  const sort     = document.getElementById('sortSelect')?.value || 'newest';

  let qs = `?sort=${sort}`;
  if (search)            qs += `&search=${encodeURIComponent(search)}`;
  if (state.activeCategory) qs += `&category=${state.activeCategory}`;
  if (minPrice)          qs += `&min_price=${minPrice}`;
  if (maxPrice)          qs += `&max_price=${maxPrice}`;

  try {
    const { products, count } = await api('GET', `/products/${qs}`);
    state.products = products;

    heading.textContent = state.activeCategory
      ? state.categories.find(c => c.slug === state.activeCategory)?.name || 'Products'
      : 'All Products';
    countEl.textContent = `${count} items`;

    if (!products.length) {
      grid.innerHTML = '';
      empty?.classList.remove('hidden');
    } else {
      grid.innerHTML = products.map(productCard).join('');
    }
  } catch {
    grid.innerHTML = '<p style="padding:24px;color:#999">Failed to load products.</p>';
  }
}

let searchTimer;
function liveSearch() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => {
    if (document.getElementById('page-products').classList.contains('active')) {
      applyFilters();
    } else {
      showPage('products');
    }
  }, 350);
}

// ═══════════════════════════════════════════════════════════════════════════
// PRODUCT CARD (shared renderer)
// ═══════════════════════════════════════════════════════════════════════════

function productCard(p) {
  const stars = '★'.repeat(Math.round(p.rating || 4)) + '☆'.repeat(5 - Math.round(p.rating || 4));
  return `
    <div class="product-card" onclick="openProduct(${p.id})">
      <div class="product-img-wrap">
        <img src="${p.image_url || 'https://via.placeholder.com/400x400?text=No+Image'}"
             alt="${p.name}" loading="lazy" onerror="this.src='https://via.placeholder.com/400x400?text=No+Image'" />
        <div class="product-overlay">
          <button onclick="event.stopPropagation(); quickAddToCart(${p.id})">Quick Add 🛒</button>
        </div>
        ${p.rating >= 4.7 ? '<div class="product-tag">Top Rated</div>' : ''}
      </div>
      <div class="product-info">
        <div class="product-category">${p.category_name || ''}</div>
        <div class="product-name" title="${p.name}">${p.name}</div>
        <div class="product-bottom">
          <div class="product-price">₹${Number(p.price).toFixed(2)}</div>
          <div class="product-rating">${stars} ${p.rating || ''}</div>
        </div>
      </div>
    </div>`;
}

// ═══════════════════════════════════════════════════════════════════════════
// PRODUCT DETAIL
// ═══════════════════════════════════════════════════════════════════════════

function openProduct(id) {
  state.currentProductId = id;
  state.detailQty = 1;
  showPage('product-detail');
}

async function loadProductDetail(id) {
  const el = document.getElementById('productDetail');
  if (!el || !id) return;
  el.innerHTML = '<div class="loader"><div class="spinner"></div></div>';

  try {
    const { product: p } = await api('GET', `/products/${id}`);
    const stars = '★'.repeat(Math.round(p.rating)) + '☆'.repeat(5 - Math.round(p.rating));
    el.innerHTML = `
      <button class="back-btn" onclick="history.back()">← Back</button>
      <div class="detail-grid">
        <div class="detail-img-wrap">
          <img src="${p.image_url || 'https://via.placeholder.com/600x600'}"
               alt="${p.name}"
               onerror="this.src='https://via.placeholder.com/600x600?text=No+Image'" />
        </div>
        <div class="detail-info">
          <div class="detail-category">${p.category_name}</div>
          <h1 class="detail-name">${p.name}</h1>
          <div class="detail-rating">${stars} &nbsp;${p.rating} / 5.0</div>
          <div class="detail-price">₹${Number(p.price).toFixed(2)}</div>
          <p class="detail-desc">${p.description || 'No description available.'}</p>
          <div class="detail-stock">${p.stock > 0 ? `✔ In Stock (${p.stock} available)` : '✗ Out of Stock'}</div>
          <div class="qty-control">
            <button class="qty-btn" onclick="changeDetailQty(-1)">−</button>
            <span class="qty-num" id="detailQtyNum">1</span>
            <button class="qty-btn" onclick="changeDetailQty(1)">+</button>
          </div>
          <button class="btn btn-primary btn-full" onclick="addToCart(${p.id})" ${p.stock === 0 ? 'disabled' : ''}>
            🛒 Add to Cart
          </button>
        </div>
      </div>`;
  } catch {
    el.innerHTML = '<p style="padding:40px;color:#999">Product not found.</p>';
  }
}

function changeDetailQty(delta) {
  state.detailQty = Math.max(1, state.detailQty + delta);
  const el = document.getElementById('detailQtyNum');
  if (el) el.textContent = state.detailQty;
}

// ═══════════════════════════════════════════════════════════════════════════
// CART
// ═══════════════════════════════════════════════════════════════════════════

async function addToCart(productId, qty = null) {
  if (!state.user) { showModal('loginModal'); return; }
  const quantity = qty || state.detailQty;
  try {
    await api('POST', '/cart/add', { product_id: productId, quantity });
    showToast('Added to cart! 🛒');
    refreshCartBadge();
  } catch (err) {
    showToast('❌ ' + err.message);
  }
}

async function quickAddToCart(productId) {
  await addToCart(productId, 1);
}

async function refreshCartBadge() {
  if (!state.user) return;
  try {
    const { items } = await api('GET', '/cart/');
    const count = items.reduce((s, i) => s + i.quantity, 0);
    state.cartCount = count;
    document.getElementById('cartBadge').textContent = count;
  } catch {}
}

async function loadCart() {
  const itemsEl  = document.getElementById('cartItems');
  const summaryEl = document.getElementById('cartSummary');
  const emptyEl  = document.getElementById('cartEmpty');
  const layoutEl = document.querySelector('.cart-layout');

  if (!state.user) {
    itemsEl.innerHTML = '';
    summaryEl.innerHTML = '';
    emptyEl.classList.remove('hidden');
    layoutEl?.classList.add('hidden');
    emptyEl.innerHTML = `
      <div class="empty-icon">🔐</div>
      <h3>Please login to view cart</h3>
      <button class="btn btn-primary" onclick="showModal('loginModal')">Login</button>`;
    return;
  }

  try {
    const { items, total } = await api('GET', '/cart/');
    if (!items.length) {
      itemsEl.innerHTML = '';
      summaryEl.innerHTML = '';
      layoutEl?.classList.add('hidden');
      emptyEl.classList.remove('hidden');
      return;
    }
    layoutEl?.classList.remove('hidden');
    emptyEl.classList.add('hidden');

    itemsEl.innerHTML = items.map(item => `
      <div class="cart-item" id="cart-item-${item.cart_id}">
        <div class="cart-item-img">
          <img src="${item.image_url || ''}" alt="${item.name}"
               onerror="this.src='https://via.placeholder.com/90x90'" />
        </div>
        <div class="cart-item-info">
          <div class="cart-item-name">${item.name}</div>
          <div class="cart-item-price">₹${Number(item.price).toFixed(2)} each</div>
          <div class="cart-qty-row">
            <button class="cart-qty-btn" onclick="updateCartItem(${item.cart_id}, ${item.quantity - 1})">−</button>
            <span>${item.quantity}</span>
            <button class="cart-qty-btn" onclick="updateCartItem(${item.cart_id}, ${item.quantity + 1})">+</button>
          </div>
        </div>
        <div class="cart-item-total">₹${(item.price * item.quantity).toFixed(2)}</div>
        <button class="cart-item-remove" onclick="removeCartItem(${item.cart_id})">✕ Remove</button>
      </div>
    `).join('');

    const shipping = total > 999 ? 0 : 99;
    const tax      = +(total * 0.18).toFixed(2);
    const grand    = +(total + shipping + tax).toFixed(2);

    summaryEl.innerHTML = `
      <h3>Order Summary</h3>
      <div class="summary-row"><span>Subtotal (${items.length} items)</span><span>₹${total.toFixed(2)}</span></div>
      <div class="summary-row"><span>Shipping</span><span>${shipping === 0 ? 'FREE' : '₹' + shipping}</span></div>
      <div class="summary-row"><span>GST (18%)</span><span>₹${tax}</span></div>
      <div class="summary-row total"><span>Total</span><span>₹${grand}</span></div>
      <button class="place-order-btn" onclick="placeOrder()">Place Order →</button>
      <p style="font-size:.75rem;color:var(--muted);margin-top:10px;text-align:center">🔒 Secure checkout</p>`;
  } catch {
    itemsEl.innerHTML = '<p style="color:#999;padding:24px">Failed to load cart.</p>';
  }
}

async function updateCartItem(cartId, qty) {
  try {
    await api('PUT', '/cart/update', { cart_id: cartId, quantity: qty });
    loadCart();
    refreshCartBadge();
  } catch (err) {
    showToast('❌ ' + err.message);
  }
}

async function removeCartItem(cartId) {
  try {
    await api('DELETE', `/cart/remove/${cartId}`);
    loadCart();
    refreshCartBadge();
    showToast('Item removed from cart');
  } catch {}
}

async function placeOrder() {
  if (!state.user) { showModal('loginModal'); return; }
  try {
    const { order_id } = await api('POST', '/orders/place');
    showToast(`✅ Order #${order_id} placed successfully!`);
    refreshCartBadge();
    showPage('orders');
  } catch (err) {
    showToast('❌ ' + err.message);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// ORDERS
// ═══════════════════════════════════════════════════════════════════════════

async function loadOrders() {
  const el    = document.getElementById('ordersList');
  const empty = document.getElementById('ordersEmpty');
  if (!el) return;

  if (!state.user) {
    el.innerHTML = '';
    empty.classList.remove('hidden');
    empty.innerHTML = `
      <div class="empty-icon">🔐</div><h3>Please login to see orders</h3>
      <button class="btn btn-primary" onclick="showModal('loginModal')">Login</button>`;
    return;
  }

  el.innerHTML = '<div class="loader"><div class="spinner"></div></div>';
  try {
    const { orders } = await api('GET', '/orders/');
    if (!orders.length) {
      el.innerHTML = '';
      empty.classList.remove('hidden');
      return;
    }
    empty.classList.add('hidden');
    el.innerHTML = orders.map(order => `
      <div class="order-card">
        <div class="order-header">
          <div>
            <div class="order-id">Order #${order.id}</div>
            <div class="order-date">${new Date(order.created_at).toLocaleDateString('en-IN', {year:'numeric',month:'long',day:'numeric'})}</div>
          </div>
          <span class="order-status status-${order.status}">${order.status}</span>
          <div class="order-total">₹${Number(order.total_amount).toFixed(2)}</div>
        </div>
        <div class="order-items-list">
          ${order.items.map(i => `
            <div class="order-item">
              <img src="${i.image_url || ''}" alt="${i.name}" onerror="this.src='https://via.placeholder.com/56x56'" />
              <div class="order-item-info">
                <strong>${i.name}</strong>
                <span>Qty: ${i.quantity} × ₹${Number(i.unit_price).toFixed(2)}</span>
              </div>
            </div>`).join('')}
        </div>
      </div>
    `).join('');
  } catch {
    el.innerHTML = '<p style="color:#999;padding:24px">Failed to load orders.</p>';
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// ADMIN
// ═══════════════════════════════════════════════════════════════════════════

async function loadAdmin() {
  if (!state.user || state.user.role !== 'admin') {
    showToast('❌ Admin access required');
    showPage('home');
    return;
  }
  loadAdminStats();
  loadAdminProducts();
  populateAdminCategorySelect();
}

async function loadAdminStats() {
  const el = document.getElementById('adminStats');
  try {
    const s = await api('GET', '/admin/stats');
    el.innerHTML = `
      <div class="stat-card"><div class="stat-val">${s.users}</div><div class="stat-label">Users</div></div>
      <div class="stat-card"><div class="stat-val">${s.products}</div><div class="stat-label">Products</div></div>
      <div class="stat-card"><div class="stat-val">${s.orders}</div><div class="stat-label">Orders</div></div>
      <div class="stat-card"><div class="stat-val">₹${Number(s.revenue).toFixed(0)}</div><div class="stat-label">Revenue</div></div>`;
  } catch {}
}

async function loadAdminProducts() {
  const tbody = document.getElementById('adminProductsBody');
  try {
    const { products } = await api('GET', '/admin/products');
    tbody.innerHTML = products.map(p => `
      <tr>
        <td>#${p.id}</td>
        <td>${p.name}</td>
        <td>${p.category_name}</td>
        <td>₹${Number(p.price).toFixed(2)}</td>
        <td>${p.stock}</td>
        <td>${p.rating}★</td>
        <td>
          <div class="table-actions">
            <button class="btn-edit" onclick="editProduct(${p.id})">Edit</button>
            <button class="btn-del"  onclick="deleteProduct(${p.id})">Delete</button>
          </div>
        </td>
      </tr>`).join('');
  } catch {}
}

function populateAdminCategorySelect() {
  const sel = document.getElementById('ap-category');
  if (!sel) return;
  sel.innerHTML = state.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
}

async function addProduct() {
  const msgEl = document.getElementById('addProductMsg');
  const body  = {
    category_id:  document.getElementById('ap-category').value,
    name:         document.getElementById('ap-name').value,
    description:  document.getElementById('ap-description').value,
    price:        document.getElementById('ap-price').value,
    stock:        document.getElementById('ap-stock').value,
    image_url:    document.getElementById('ap-image').value,
  };
  try {
    await api('POST', '/admin/products', body);
    showMsg(msgEl, 'Product added successfully!', 'success');
    setTimeout(() => { closeModal('addProductModal'); loadAdminProducts(); }, 1000);
  } catch (err) {
    showMsg(msgEl, err.message, 'error');
  }
}

async function deleteProduct(id) {
  if (!confirm('Delete this product?')) return;
  try {
    await api('DELETE', `/admin/products/${id}`);
    showToast('Product deleted');
    loadAdminProducts();
  } catch (err) {
    showToast('❌ ' + err.message);
  }
}

async function editProduct(id) {
  const name = prompt('New product name (leave blank to skip):');
  const price = prompt('New price (leave blank to skip):');
  const stock = prompt('New stock (leave blank to skip):');

  const body = {};
  if (name)  body.name  = name;
  if (price) body.price = parseFloat(price);
  if (stock) body.stock = parseInt(stock);

  if (!Object.keys(body).length) return;

  try {
    await api('PUT', `/admin/products/${id}`, body);
    showToast('Product updated ✅');
    loadAdminProducts();
  } catch (err) {
    showToast('❌ ' + err.message);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// MODALS
// ═══════════════════════════════════════════════════════════════════════════

function showModal(id) {
  document.getElementById(id).classList.remove('hidden');
}
function closeModal(id) {
  document.getElementById(id).classList.add('hidden');
}
function switchModal(from, to) {
  closeModal(from);
  showModal(to);
}

// Close modal on overlay click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', e => {
    if (e.target === overlay) overlay.classList.add('hidden');
  });
});

// ═══════════════════════════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

function showToast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 3000);
}

function showMsg(el, msg, type) {
  el.textContent = msg;
  el.className   = `msg ${type}`;
  el.classList.remove('hidden');
}

function toggleMobileMenu() {
  document.getElementById('navLinks').classList.toggle('open');
}

// ═══════════════════════════════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════════════════════════════

(async function init() {
  await checkAuth();
  await loadCategories();
  await loadProducts();   // 🔥 ADD THIS LINE
  showPage('home');
})();
