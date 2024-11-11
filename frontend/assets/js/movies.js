document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("token");

  if (!token) {
    window.location.href = "/";
  } else {
    fetchUserInfo(token);
  }

  // Handle logout
  document.getElementById("logout-btn").addEventListener("click", logout);

  // Initialize pagination and fetch movies
  let currentPage = 1;
  let moviesData = JSON.parse(sessionStorage.getItem("moviesData")) || [];

  if (moviesData.length === 0) {
    console.warn("No movies data found in sessionStorage.");
  }

  displayMovies(moviesData, currentPage);

  // Event listeners for pagination
  document.getElementById("next-page-btn").addEventListener("click", () => {
    currentPage++;
    displayMovies(moviesData, currentPage);
  });

  document.getElementById("prev-page-btn").addEventListener("click", () => {
    if (currentPage > 1) {
      currentPage--;
      displayMovies(moviesData, currentPage);
    }
  });

  // Event listeners for sorting
  document.getElementById("sort-asc").addEventListener("click", () => {
    sortMovies(moviesData, "asc");
    displayMovies(moviesData, currentPage);
  });

  document.getElementById("sort-desc").addEventListener("click", () => {
    sortMovies(moviesData, "desc");
    displayMovies(moviesData, currentPage);
  });

  document.getElementById("sort-by").addEventListener("change", () => {
    const sortBy = document.getElementById("sort-by").value;
    sortMovies(moviesData, "asc", sortBy);
    displayMovies(moviesData, currentPage);
  });
});

function fetchUserInfo(token) {
  try {
    const user = jwt_decode(token);
    document.getElementById("username").innerText =
      `Logged in as: ${user.email}`;
  } catch (error) {
    console.error("Failed to decode user info", error);
    window.location.href = "/";
  }
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "/";
}

function displayMovies(moviesData, page) {
  const moviesPerPage = 20;
  const startIndex = (page - 1) * moviesPerPage;
  const endIndex = Math.min(startIndex + moviesPerPage, moviesData.length);
  const moviesTableBody = document.getElementById("movies-table-body");

  moviesTableBody.innerHTML = ""; // Clear previous rows

  for (let i = startIndex; i < endIndex; i++) {
    const movie = moviesData[i];
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${movie.title}</td>
      <td>${movie.genre}</td>
      <td>${movie.date_added}</td>
      <td>${movie.release_date}</td>
      <td>${movie.duration}</td>
    `;
    moviesTableBody.appendChild(row);
  }
}

function sortMovies(moviesData, order, sortBy = "title") {
  moviesData.sort((a, b) => {
    if (order === "asc") {
      return a[sortBy] > b[sortBy] ? 1 : -1;
    } else {
      return a[sortBy] < b[sortBy] ? 1 : -1;
    }
  });
}
