const params = new URLSearchParams(window.location.search);
const storedOrder = JSON.parse(localStorage.getItem("zero-market-last-order") || "{}");

const trackingForm = document.querySelector("#trackingForm");
const trackingInput = document.querySelector("#trackingInput");
const trackingResult = document.querySelector("#trackingResult");
const routeFill = document.querySelector("#routeFill");
const truckMarker = document.querySelector("#truckMarker");
const trackingOrderId = document.querySelector("#trackingOrderId");
const trackingHeadline = document.querySelector("#trackingHeadline");
const trackingMessage = document.querySelector("#trackingMessage");
const trackingSteps = document.querySelector("#trackingSteps");

const steps = [
  {
    title: "가상 주문 접수",
    message: "주문번호가 생성되었고 결제 체험이 완료되었습니다.",
  },
  {
    title: "상품 준비 중",
    message: "담았던 상품들을 가상 포장대에 올려두었습니다.",
  },
  {
    title: "제로 물류센터 도착",
    message: "실제 물류 이동 없이 배송 화면만 진행됩니다.",
  },
  {
    title: "배송 출발",
    message: "주소로 향하는 것처럼 보이는 가상 경로입니다.",
  },
  {
    title: "문 앞 도착 예정",
    message: "체험용 상태이며 실제 상품은 배송되지 않습니다.",
  },
];

function normalizeOrderId(value) {
  return value.trim().toUpperCase().replace(/\s+/g, "");
}

function progressIndex(orderId) {
  const total = Array.from(orderId).reduce((acc, char, index) => acc + char.charCodeAt(0) * (index + 1), 0);
  return Math.max(0, total % steps.length);
}

function renderTracking(orderId) {
  const normalized = normalizeOrderId(orderId);
  if (!normalized) return;

  const currentIndex = progressIndex(normalized);
  const percent = currentIndex === steps.length - 1 ? 92 : 12 + currentIndex * 20;
  const current = steps[currentIndex];

  trackingInput.value = normalized;
  trackingResult.hidden = false;
  trackingOrderId.textContent = normalized;
  trackingHeadline.textContent = current.title;
  trackingMessage.textContent = `${current.message} 이 배송 조회는 실제 택배사와 연결되어 있지 않습니다.`;
  routeFill.style.width = `${percent}%`;
  truckMarker.style.left = `${percent}%`;
  trackingSteps.innerHTML = steps
    .map((step, index) => {
      const status = index < currentIndex ? "done" : index === currentIndex ? "current" : "pending";
      return `
        <li class="${status}">
          <span>${index + 1}</span>
          <div>
            <strong>${step.title}</strong>
            <p>${step.message}</p>
          </div>
        </li>
      `;
    })
    .join("");

  if (window.lucide) {
    window.lucide.createIcons();
  }
}

trackingForm.addEventListener("submit", (event) => {
  event.preventDefault();
  renderTracking(trackingInput.value);
});

const initialOrderId = params.get("order") || storedOrder.orderId || "";
if (initialOrderId) {
  renderTracking(initialOrderId);
}

if (window.lucide) {
  window.lucide.createIcons();
}
