const uploadForm = document.getElementById("csv-upload-form");
const uploadBtn = document.getElementById("upload-btn");
const uploadProgress = document.getElementById("upload-progress");
const uploadStatus = document.getElementById("upload-status");

uploadForm.addEventListener("submit", (event) => {
  event.preventDefault(); // Prevent default form submission

  const formData = new FormData(uploadForm); // Get form data
  const token = localStorage.getItem("token");

  if (!token) {
    alert("Please log in first.");
    window.location.href = "/"; // Redirect to login if not authenticated
    return;
  }

  // Show progress bar and hide upload button
  uploadProgress.style.display = "block";
  uploadBtn.disabled = true;

  // Upload the CSV file
  fetch("http://127.0.0.1:5000/upload/upload_csv", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to upload CSV file.");
      }
      return response.json();
    })
    .then((data) => {
      if (data.task_id) {
        // If task ID is received, start polling for progress
        checkUploadProgress(data.task_id);
      } else {
        alert("Error uploading CSV file.");
        resetUploadForm();
      }
    })
    .catch((error) => {
      console.error("Upload error:", error);
      alert("Failed to upload CSV. Please try again.");
      resetUploadForm();
    });
});

// Poll the server for upload progress
function checkUploadProgress(taskId) {
  const token = localStorage.getItem("token");

  fetch(`http://127.0.0.1:5000/upload/upload_progress/${taskId}`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to check upload progress.");
      }
      return response.json();
    })
    .then((data) => {
      if (data.status === "completed") {
        uploadStatus.textContent = "Upload completed!";
        setTimeout(() => {
          resetUploadForm();
        }, 2000); // Reset the form after a short delay
      } else if (data.status === "in_progress") {
        // Update progress status
        uploadStatus.textContent = `Uploading: ${data.progress}% (${data.uploaded_rows} rows uploaded)`;
        setTimeout(() => {
          checkUploadProgress(taskId); // Continue polling
        }, 1000); // Poll every second
      } else {
        alert("Unknown upload status.");
        resetUploadForm();
      }
    })
    .catch((error) => {
      console.error("Error checking progress:", error);
      alert("Failed to check progress. Please try again.");
      resetUploadForm();
    });
}

// Reset the upload form and progress bar
function resetUploadForm() {
  uploadForm.reset();
  uploadProgress.style.display = "none";
  uploadBtn.disabled = false;
}
