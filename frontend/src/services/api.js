// src/services/api.js
// src/services/api.js
import { API_BASE_URL } from "../config";

export async function uploadProjectZip(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/api/upload`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("Upload failed");
  }

  return await response.json();
}
