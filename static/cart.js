// cart.js
document.addEventListener("DOMContentLoaded", () => {
  updateTotal();

  const table = document.querySelector("#table1");

  const observer = new MutationObserver(() => {
    updateTotal();
  });

  observer.observe(table, {
    childList: true,
    subtree: true,
  });

  // Handle quantity changes
  document.querySelectorAll(".quantity").forEach((input, index) => {
    input.addEventListener("change", () => {
      let value = Number(input.value);
      if (value <= 0) {
        alert("Quantity can't be zero or negative.");
        input.value = 1;
        value = 1;
      }

      const priceText = document.querySelectorAll(".price")[index].innerText.trim();
      const price = Number(priceText.replace(/[^\d.]/g, ""));
      const subtotal = price * value;

      document.querySelectorAll(".subtotal")[index].innerText = subtotal;
      updateTotal();
    });
  });

  // Remove item from UI (AJAX or form handling should be used for server-side sync)
  document.querySelectorAll(".cancel-item").forEach((icon) => {
    icon.addEventListener("click", function () {
      this.closest("tr").remove();
      updateTotal();
    });
  });

  // Checkout handler (redirect only)
  document.getElementById("check-out-btn").addEventListener("click", () => {
    // Optionally validate cart here before checkout
    window.location.href = "checkout";
  });

  // Coupon logic
  document.querySelector(".coupon-btn").addEventListener("click", () => {
    const couponText = document.querySelector(".coupon-text").value.trim();
    const validCoupon = "123";
    const totalText = document.querySelector("#total").innerText;
    let total = parseFloat(totalText.replace(/[^\d.]/g, ""));

    if (couponText === validCoupon) {
      if (total > 1100) {
        total -= 1000;
        document.querySelector("#total").innerText = `Rs ${total}`;
        document.querySelector("#finalprice").innerText = `Rs ${total}`;
        alert("Coupon applied successfully!");
      } else {
        alert("Cart total must be greater than Rs 1100 to apply this coupon.");
      }
    } else {
      alert("Invalid coupon code.");
    }
  });

  // Total calculation from current DOM
  function updateTotal() {
    let total = 0;
    document.querySelectorAll(".subtotal").forEach((sub) => {
      total += Number(sub.innerText);
    });
    document.querySelector("#total").innerText = `Rs ${total}`;
    document.querySelector("#finalprice").innerText = `Rs ${total}`;
  }
});
