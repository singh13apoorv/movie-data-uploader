document.addEventListener("DOMContentLoaded", function () {
  // Signup listener
  const signupForm = document.getElementById("signupForm");
  if (signupForm) {
    signupForm.addEventListener("submit", function (event) {
      event.preventDefault(); // Prevent default form submission
      signup(); // Call the signup function
    });
  }

  // Login listener
  const loginForm = document.getElementById("loginForm");
  if (loginForm) {
    loginForm.addEventListener("submit", function (event) {
      event.preventDefault(); // Prevent default form submission
      login(); // Call the login function
    });
  }

  // Logout listener (assuming you have a button or link with id 'logoutButton')
  const logoutButton = document.getElementById("logoutButton");
  if (logoutButton) {
    logoutButton.addEventListener("click", function (event) {
      event.preventDefault(); // Prevent default action
      logout(); // Call the logout function
    });
  }
});

async function signup() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;
  const confirmPassword = document.getElementById("confirmPassword").value;

  if (password !== confirmPassword) {
    document.getElementById("error-message").innerText =
      "Passwords do not match!";
    return;
  }

  const response = await fetch("http://127.0.0.1:5000/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const result = await response.json();
  if (response.ok) {
    window.location.href = "index.html"; // Redirect to login page after signup
  } else {
    document.getElementById("error-message").innerText = result.message;
  }
}

async function login() {
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const response = await fetch("http://127.0.0.1:5000/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const result = await response.json();
  console.log("Response status:", response.status); // Log the status code
  console.log("Response body:", result); // Log the response body

  if (response.ok) {
    // Save token to localStorage
    localStorage.setItem("token", result.token);
    // Redirect to the dashboard
    window.location.href = "dashboard.html";
  } else {
    // Handle error and display message
    document.getElementById("error-message").innerText = result.message;
  }
}

function logout() {
  localStorage.removeItem("token"); // Remove token from localStorage
  window.location.href = "index.html"; // Redirect to login page after logout
}
