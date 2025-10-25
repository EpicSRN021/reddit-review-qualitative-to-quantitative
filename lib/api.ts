// frontend/lib/api.ts - UPDATED
// Calls backend/server.py which runs script.py

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface AnalysisResponse {
  final_rating: number;           // Overall score 0-5 (from script.py final_score)
  subscores: number[];            // [quality, cost, availability, utility] (from script.py final_metrics)
  ai_summary: string;             // AI-generated summary (from script.py summary_task)
  comments: [string, string][];   // [[text, url], ...] (from script.py top5)
}

/**
 * Analyze a product by calling the backend server
 * The server runs script.py with the product keyword
 * 
 * @param productName - Product to search for (e.g., "MacBook Air")
 * @returns Analysis results with rating, subscores, summary, and top comments
 */
export async function analyzeProduct(productName: string): Promise<AnalysisResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        keyword: productName 
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ 
        detail: 'Failed to analyze product. Make sure backend is running on port 8000.' 
      }));
      throw new Error(error.detail || `Server error: ${response.status}`);
    }

    const data: AnalysisResponse = await response.json();
    return data;
    
  } catch (error) {
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new Error('Cannot connect to backend. Make sure server.py is running on port 8000.');
    }
    throw error;
  }
}