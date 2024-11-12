async function apiRequest(url, method = "GET", data = null) {
  // Prepare the options for the fetch request
  const options = {
    method,
    headers: {
      Authorization: `Bearer ${localStorage.getItem("token")}`,
      "Content-Type": "application/json",
    },
  };

  // If data is provided, include it in the request body
  if (data) {
    options.body = JSON.stringify(data);
  }

  try {
    // Send the request and wait for the response
    const response = await fetch(url, options);

    // Check if the response is okay (status in the range 200-299)
    if (!response.ok) {
      const errorResult = await response.json();
      throw new Error(errorResult.message || "Something went wrong");
    }

    // If the response is successful, parse and return the JSON data
    return await response.json();
  } catch (error) {
    // Log the error to the console and throw it for the caller to handle
    console.error("API Request failed:", error);
    throw error; // Re-throw the error
  }
}
