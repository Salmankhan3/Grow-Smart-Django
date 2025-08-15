document.getElementById("contactForm").addEventListener("submit", function (e) {
  e.preventDefault();

  const nameInput = document.getElementById("name");
  const emailInput = document.getElementById("email");
  const messageInput = document.getElementById("message");
  const formMessage = document.getElementById("formMessage");

  let hasError = false;

  // Reset errors
  document.querySelectorAll(".error-message").forEach(el => el.style.display = "none");

  if (nameInput.value.trim() === "") {
    showError(nameInput, "Name is required.");
    hasError = true;
  }

  if (!isValidEmail(emailInput.value.trim())) {
    showError(emailInput, "Enter a valid email.");
    hasError = true;
  }

  if (messageInput.value.trim() === "") {
    showError(messageInput, "Message cannot be empty.");
    hasError = true;
  }

  if (hasError) return;

  formMessage.innerText = "Thank you! Your message has been sent.";
  formMessage.style.color = "green";

  // Clear form
  document.getElementById("contactForm").reset();
});

function showError(input, message) {
  const errorElement = input.nextElementSibling;
  errorElement.textContent = message;
  errorElement.style.display = "block";
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
