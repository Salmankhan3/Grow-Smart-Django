document.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector('.shop-section');
      const products = JSON.parse(localStorage.getItem('userProducts')) || [];

      products.forEach((product, index) => {
        const box = document.createElement('div');
        box.className = 'box';
        box.onclick = () => {
          const query = `productpage.html?name=${encodeURIComponent(product.name)}&price=${product.price}&image=${encodeURIComponent(product.image)}`;
          window.location.href = query;
        };
        box.innerHTML = `
          <div class="box-img" style="background-image: url('${product.image}');"></div>
          <p class="product-name" style="color: #170388;font-weight: 600;font-size: 15px; margin-left: 10px">${product.name}</p>
          <p id="price" style="margin-top: 24px;color: #2D2E2Efc; font-weight:600; margin-left: 10px">Rs. ${product.price}</p>
          <div class="add-to-cart">
          <div class=" tooltip">
          <i class="fa-solid fa-cart-shopping add-to-cart-icon"></i>
          <span class="tooltip-text">Add to Cart</span>
      </div>
      </div>
      </div>
        `;
        container.appendChild(box);
      });
  const addtocart_btns = document.querySelectorAll(".add-to-cart-icon");

  if (addtocart_btns.length === 0) {
    console.warn("No 'add to cart' icons found");
    return;
  }

  addtocart_btns.forEach(btn => {
    btn.addEventListener("click", (event) => {
      event.stopPropagation(); // Prevents box redirect

      const box = btn.closest(".box"); //  Get the parent box

      const name = box.querySelector(".product-name").innerText;
      const priceText = box.querySelector("#price").innerText; // e.g. "Rs. 600"
      const price = priceText.split(" ")[1]; // "600"

      const bgImageStyle = box.querySelector(".box-img").style.backgroundImage;
      const imageUrl = bgImageStyle.slice(5, -2); // remove url('...') wrapper

      // Create a product object
      const product = {
        name,
        price,
        quantity: 1, // default to 1
        image: imageUrl,
        subtotal: Number(price),
      };

      // Get current cart from localStorage
      const cartItems = JSON.parse(localStorage.getItem("cartItems")) || [];

      // Add new product
      cartItems.push(product);

      // Save to localStorage
      localStorage.setItem("cartItems", JSON.stringify(cartItems));
      alert("item added succesfully")

      // Redirect to cart
    //  window.location.href = "cart.html";
    });
  });
// product from former.html
 
});
//localStorage.clear();
// logic for chat bot
  const chatIcon = document.getElementById('chatbot-icon');
  const chatbotWindow = document.getElementById('chatbot-window');

  chatIcon.addEventListener('click', () => {
    chatbotWindow.style.display = chatbotWindow.style.display === 'none' || chatbotWindow.style.display === '' 
      ? 'block' 
      : 'none';
        });