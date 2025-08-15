
  const form = document.getElementById('product-form');
  const productList = document.getElementById('product-list'); // Make sure this container exists!

  //  1. Render products from localStorage on page load
  function loadSavedProducts() {
    const products = JSON.parse(localStorage.getItem('userProducts')) || [];

    products.forEach(product => {
      const productCard = document.createElement('div');
      productCard.classList.add('product');
      productCard.innerHTML = `
        <img src="${product.image}" alt="${product.name}" />
        <h3>${product.name}</h3>
        <p>Rs. ${product.price}</p>
        <button class="remove-btn">Remove</button>
      `;
      productCard.querySelector('.remove-btn').addEventListener('click', () => {
        productCard.remove();
        removeProductFromLocalStorage(product); // Remove from localStorage too
      });
      productList.appendChild(productCard);
    });
  }

  // Remove product from localStorage when deleted
  function removeProductFromLocalStorage(productToRemove) {
    let products = JSON.parse(localStorage.getItem('userProducts')) || [];
    products = products.filter(p =>
      !(p.name === productToRemove.name &&
        p.price === productToRemove.price &&
        p.image === productToRemove.image)
    );
    localStorage.setItem('userProducts', JSON.stringify(products));
  }

  // Save product from form submission
  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const name = document.getElementById('name').value;
    const price = parseFloat(document.getElementById('price').value).toFixed(2);
    const imageFile = document.getElementById('imageFile').files[0];
    const imageURL = document.getElementById('imageURL').value.trim();
    if(price<50){
        alert("Price cant be less then 50");
        return;
    }
    if (!imageFile && !imageURL) {
      alert("Please provide an image (file or URL).");
      return;
    }

    function saveProduct(imageSrc) {
      const product = {
        name: name,
        price: price,
        image: imageSrc
      };

      const products = JSON.parse(localStorage.getItem('userProducts')) || [];
      products.push(product);
      localStorage.setItem('userProducts', JSON.stringify(products));

      const productCard = document.createElement('div');
      productCard.classList.add('product');
      productCard.innerHTML = `
        <img src="${imageSrc}" alt="${name}" />
        <h3>${name}</h3>
        <p>Rs. ${price}</p>
        <button class="remove-btn">Remove</button>
      `;
      productCard.querySelector('.remove-btn').addEventListener('click', () => {
        productCard.remove();
        removeProductFromLocalStorage(product);
      });
      productList.appendChild(productCard);

      form.reset();
    }

    if (imageFile) {
      const reader = new FileReader();
      reader.onload = function (e) {
        saveProduct(e.target.result);
      };
      reader.readAsDataURL(imageFile);
    } else {
      saveProduct(imageURL);
    }
  });

  //4. Run on page load
  window.addEventListener('DOMContentLoaded', loadSavedProducts);

