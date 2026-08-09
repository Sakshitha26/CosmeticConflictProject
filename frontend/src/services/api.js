const API_URL = "http://127.0.0.1:5000";

export async function analyzeProducts(image1, image2) {
  const formData = new FormData();

  formData.append("image1", image1);
  formData.append("image2", image2);

  const response = await fetch(
    `${API_URL}/api/analyze`,
    {
      method: "POST",
      body: formData
    }
  );

  if (!response.ok) {
    throw new Error("Analysis failed");
  }

  return await response.json();
}