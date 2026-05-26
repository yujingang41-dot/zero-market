const orderFormatter = new Intl.NumberFormat("ko-KR", {
  style: "currency",
  currency: "KRW",
  maximumFractionDigits: 0,
});

const params = new URLSearchParams(window.location.search);
const storedOrder = JSON.parse(localStorage.getItem("zero-market-last-order") || "{}");
const orderId = params.get("order") || storedOrder.orderId || "ZERO-READY";

const successOrderId = document.querySelector("#successOrderId");
const successItemCount = document.querySelector("#successItemCount");
const successTotal = document.querySelector("#successTotal");
const trackingLink = document.querySelector("#trackingLink");
const copyOrderButton = document.querySelector("#copyOrderButton");
const confettiField = document.querySelector("#confettiField");

successOrderId.textContent = orderId;
successItemCount.textContent = `${storedOrder.itemCount || 0}개`;
successTotal.textContent = orderFormatter.format(storedOrder.total || 0);
trackingLink.href = `/tracking?order=${encodeURIComponent(orderId)}`;

function makeConfetti() {
  const colors = ["#1167d8", "#f8485e", "#0f9f7a", "#f5b942", "#7c3aed"];
  for (let index = 0; index < 54; index += 1) {
    const piece = document.createElement("span");
    piece.style.left = `${Math.random() * 100}%`;
    piece.style.background = colors[index % colors.length];
    piece.style.animationDelay = `${Math.random() * 1.1}s`;
    piece.style.animationDuration = `${2.6 + Math.random() * 1.8}s`;
    piece.style.transform = `rotate(${Math.random() * 180}deg)`;
    confettiField.appendChild(piece);
  }
}

copyOrderButton.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(orderId);
    copyOrderButton.setAttribute("aria-label", "복사 완료");
  } catch {
    copyOrderButton.setAttribute("aria-label", "복사 실패");
  }
});

makeConfetti();

if (window.lucide) {
  window.lucide.createIcons();
}
