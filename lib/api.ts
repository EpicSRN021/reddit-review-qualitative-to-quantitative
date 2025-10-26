// frontend/lib/api.ts
// Calls backend/server.py which runs script.py

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface AnalysisResponse {
  final_rating: number; // Overall score 0-5
  subscores: number[]; // [quality, cost, availability, utility]
  ai_summary: string; // AI-generated summary
  comments: [string, string][]; // [[text, url], ...]
  pros: [string, string | null][]; // List of pros with URLs from Reddit comments
  cons: [string, string | null][]; // List of cons with URLs from Reddit comments
  similar_products: string[]; // List of similar product names
}

/**
 * Analyze a product by calling the backend server
 */
export async function analyzeProduct(
  productName: string
): Promise<AnalysisResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        keyword: productName,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        detail: "Failed to analyze product. Please check your backend server.",
      }));
      throw new Error(error.detail || `Server error: ${response.status}`);
    }

    const data: AnalysisResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new Error(
        "Cannot connect to backend. Please check your backend server."
      );
    }
    throw error;
  }
}
