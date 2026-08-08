const API_URL = "http://127.0.0.1:5000";

export async function analyzeProducts(product1, product2) {

    const formData = new FormData();

    formData.append("product1", product1);
    formData.append("product2", product2);

    const response = await fetch(`${API_URL}/analyze`, {

        method: "POST",

        body: formData

    });

    if (!response.ok) {
        throw new Error("Analysis failed");
    }

    return await response.json();

}