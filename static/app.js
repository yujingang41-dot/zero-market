const formatWon = new Intl.NumberFormat("ko-KR", {
  style: "currency",
  currency: "KRW",
  maximumFractionDigits: 0,
});

const state = {
  products: [],
  filtered: [],
  activeCategory: "전체",
  cart: JSON.parse(localStorage.getItem("zero-market-cart") || "{}"),
};

const els = {
  generatedAt: document.querySelector("#generatedAt"),
  productCount: document.querySelector("#productCount"),
  productGrid: document.querySelector("#productGrid"),
  categoryTabs: document.querySelector("#categoryTabs"),
  searchInput: document.querySelector("#searchInput"),
  moodForm: document.querySelector("#moodForm"),
  moodInput: document.querySelector("#moodInput"),
  cartLines: document.querySelector("#cartLines"),
  cartCount: document.querySelector("#cartCount"),
  cartTotal: document.querySelector("#cartTotal"),
  checkoutButton: document.querySelector("#checkoutButton"),
  checkoutResult: document.querySelector("#checkout"),
  receiptTitle: document.querySelector("#receiptTitle"),
  receiptMessage: document.querySelector("#receiptMessage"),
  clearCartButton: document.querySelector("#clearCartButton"),
  productDialog: document.querySelector("#productDialog"),
  dialogBody: document.querySelector("#dialogBody"),
  dialogClose: document.querySelector("#dialogClose"),
};

function refreshIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

function persistCart() {
  localStorage.setItem("zero-market-cart", JSON.stringify(state.cart));
}

function cartLines() {
  return Object.entries(state.cart)
    .map(([id, qty]) => {
      const product = state.products.find((item) => item.id === id);
      return product ? { product, qty } : null;
    })
    .filter(Boolean);
}

function cartTotals() {
  return cartLines().reduce(
    (acc, line) => {
      acc.qty += line.qty;
      acc.total += line.product.price * line.qty;
      return acc;
    },
    { qty: 0, total: 0 },
  );
}

function useFallbackImage(img, productId) {
  if (img.dataset.fallback === "true") return;
  img.dataset.fallback = "true";
  img.onerror = null;
  img.src = `/api/placeholder/${productId}.svg`;
}

function wireProductImage(img, productId) {
  img.addEventListener("load", () => {
    img.dataset.loaded = "true";
  });
  img.addEventListener("error", () => useFallbackImage(img, productId));

  window.setTimeout(() => {
    const visibleSoon = img.getBoundingClientRect().top < window.innerHeight + 120;
    if (visibleSoon && (!img.complete || img.naturalWidth === 0)) {
      useFallbackImage(img, productId);
    }
  }, 15000);
}

function productCard(product) {
  const article = document.createElement("article");
  article.className = "product-card";
  article.innerHTML = `
    <button class="image-button" type="button" data-detail="${product.id}" aria-label="${product.name} 상세 보기">
      <img src="${product.image}" alt="${product.name}" loading="lazy" />
    </button>
    <div class="product-info">
      <div class="product-meta">
        <span>${product.category}</span>
        <span class="price-tier">${product.priceTier}</span>
      </div>
      <h3>${product.name}</h3>
      <p>${product.tone}</p>
      <div class="product-bottom">
        <strong>${formatWon.format(product.price)}</strong>
        <div class="card-actions">
          <button class="icon-button" type="button" data-detail="${product.id}" aria-label="상세 보기">
            <i data-lucide="eye"></i>
          </button>
          <button class="add-button" type="button" data-add="${product.id}">
            <i data-lucide="shopping-bag"></i>
            담기
          </button>
        </div>
      </div>
    </div>
  `;
  wireProductImage(article.querySelector("img"), product.id);
  return article;
}

function renderProducts() {
  const query = els.searchInput.value.trim().toLowerCase();
  state.filtered = state.products
    .filter((product) => {
      const categoryMatch = state.activeCategory === "전체" || product.category === state.activeCategory;
      const querySource = `${product.name} ${product.category} ${product.keyword} ${product.tone}`.toLowerCase();
      return categoryMatch && querySource.includes(query);
    })
    .sort((a, b) => Number(b.isCustom) - Number(a.isCustom) || a.price - b.price);

  els.productGrid.innerHTML = "";
  if (!state.filtered.length) {
    els.productGrid.innerHTML = `
      <div class="empty-state">
        <strong>조건에 맞는 가상 상품이 없습니다.</strong>
        <span>검색어를 줄이거나 새 상품을 생성해보세요.</span>
      </div>
    `;
  } else {
    state.filtered.forEach((product) => els.productGrid.appendChild(productCard(product)));
  }
  refreshIcons();
}

function renderCategories() {
  const categories = ["전체", ...new Set(state.products.map((product) => product.category))];
  els.categoryTabs.innerHTML = categories
    .map(
      (category) => `
        <button type="button" class="${category === state.activeCategory ? "active" : ""}" data-category="${category}">
          ${category}
        </button>
      `,
    )
    .join("");
}

function renderCart() {
  const lines = cartLines();
  const totals = cartTotals();
  els.cartCount.textContent = totals.qty;
  els.cartTotal.textContent = formatWon.format(totals.total);
  els.checkoutButton.disabled = totals.qty === 0;

  if (!lines.length) {
    els.cartLines.innerHTML = `
      <div class="cart-empty">
        <i data-lucide="shopping-cart"></i>
        <span>담긴 상품이 없습니다.</span>
      </div>
    `;
  } else {
    els.cartLines.innerHTML = lines
      .map(
        ({ product, qty }) => `
          <article class="cart-line">
            <img src="${product.image}" alt="${product.name}" data-product-image="${product.id}" />
            <div>
              <strong>${product.name}</strong>
              <span>${formatWon.format(product.price)}</span>
              <div class="qty-control" aria-label="${product.name} 수량 조절">
                <button type="button" data-dec="${product.id}" aria-label="수량 줄이기"><i data-lucide="minus"></i></button>
                <span>${qty}</span>
                <button type="button" data-inc="${product.id}" aria-label="수량 늘리기"><i data-lucide="plus"></i></button>
              </div>
            </div>
          </article>
        `,
      )
      .join("");
    els.cartLines.querySelectorAll("img").forEach((img) => {
      const line = lines.find(({ product }) => product.id === img.dataset.productImage);
      if (line) wireProductImage(img, line.product.id);
    });
  }
  refreshIcons();
}

function renderAll() {
  renderCategories();
  renderProducts();
  renderCart();
}

function setCart(productId, qty) {
  if (qty <= 0) {
    delete state.cart[productId];
  } else {
    state.cart[productId] = Math.min(qty, 9);
  }
  persistCart();
  renderCart();
}

function addToCart(productId) {
  setCart(productId, (state.cart[productId] || 0) + 1);
  els.checkoutResult.hidden = true;
}

function openDetail(productId) {
  const product = state.products.find((item) => item.id === productId);
  if (!product) return;

  els.dialogBody.innerHTML = `
    <div class="dialog-image">
      <img src="${product.image}" alt="${product.name}" />
    </div>
    <div class="dialog-copy">
      <span class="dialog-category">${product.category}</span>
      <h2>${product.name}</h2>
      <p>${product.description}</p>
      <strong class="dialog-price">${formatWon.format(product.price)} <span>${product.priceTier}</span></strong>
      <ul>
        ${product.features.map((feature) => `<li>${feature}</li>`).join("")}
      </ul>
      <div class="dialog-actions">
        <button class="primary-action" type="button" data-add="${product.id}">
          <i data-lucide="shopping-bag"></i>
          장바구니 담기
        </button>
        <button class="ghost-action" type="button" data-close-detail>
          <i data-lucide="arrow-left"></i>
          계속 둘러보기
        </button>
      </div>
    </div>
  `;
  wireProductImage(els.dialogBody.querySelector("img"), product.id);
  refreshIcons();
  els.productDialog.showModal();
}

async function loadProducts() {
  const response = await fetch("/api/products");
  const data = await response.json();
  state.products = data.items;
  state.activeCategory = "전체";
  els.generatedAt.textContent = `생성 시각 ${new Date(data.generatedAt).toLocaleString("ko-KR")}`;
  els.productCount.textContent = `${data.items.length} items`;
  renderAll();
}

async function regenerateProducts(keyword) {
  els.moodForm.classList.add("is-loading");
  const response = await fetch("/api/regenerate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ keyword }),
  });
  const data = await response.json();
  state.products = data.items;
  state.cart = {};
  persistCart();
  els.checkoutResult.hidden = true;
  els.generatedAt.textContent = `생성 시각 ${new Date(data.generatedAt).toLocaleString("ko-KR")}`;
  els.productCount.textContent = `${data.items.length} items`;
  els.moodForm.classList.remove("is-loading");
  els.searchInput.value = "";
  renderAll();
}

async function virtualCheckout() {
  const payload = {
    cart: Object.entries(state.cart).map(([id, qty]) => ({ id, qty })),
  };
  const response = await fetch("/api/checkout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const result = await response.json();
  const order = {
    orderId: result.orderId,
    itemCount: result.itemCount,
    total: result.total,
    completedAt: result.completedAt,
  };
  localStorage.setItem("zero-market-last-order", JSON.stringify(order));
  state.cart = {};
  persistCart();
  window.location.href = `/success?order=${encodeURIComponent(result.orderId)}`;
}

document.addEventListener("click", (event) => {
  const addButton = event.target.closest("[data-add]");
  const detailButton = event.target.closest("[data-detail]");
  const categoryButton = event.target.closest("[data-category]");
  const incButton = event.target.closest("[data-inc]");
  const decButton = event.target.closest("[data-dec]");
  const closeDetail = event.target.closest("[data-close-detail]");

  if (addButton) addToCart(addButton.dataset.add);
  if (detailButton) openDetail(detailButton.dataset.detail);
  if (categoryButton) {
    state.activeCategory = categoryButton.dataset.category;
    renderAll();
  }
  if (incButton) setCart(incButton.dataset.inc, (state.cart[incButton.dataset.inc] || 0) + 1);
  if (decButton) setCart(decButton.dataset.dec, (state.cart[decButton.dataset.dec] || 0) - 1);
  if (closeDetail) els.productDialog.close();
});

els.searchInput.addEventListener("input", renderProducts);
els.moodForm.addEventListener("submit", (event) => {
  event.preventDefault();
  regenerateProducts(els.moodInput.value.trim());
});
els.checkoutButton.addEventListener("click", virtualCheckout);
els.clearCartButton.addEventListener("click", () => {
  state.cart = {};
  persistCart();
  renderCart();
  els.checkoutResult.hidden = true;
});
els.dialogClose.addEventListener("click", () => els.productDialog.close());

loadProducts();
