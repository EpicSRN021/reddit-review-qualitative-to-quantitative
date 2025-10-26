"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { SearchSection } from "@/components/search-section"
import { ProductInsights } from "@/components/product-insights"
import { RedditComments } from "@/components/reddit-comments"
import { AISummary } from "@/components/ai-summary"
import { SimilarProducts } from "@/components/similar-products"
import { analyzeProduct, type AnalysisResponse } from "@/lib/api"

export default function Home() {
  const [data, setData] = useState<AnalysisResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [currentQuery, setCurrentQuery] = useState<string>("")

  const handleSearch = async (query: string) => {
    setIsLoading(true)
    setError(null)
    setData(null)
    setCurrentQuery(query)  // Update current query
    
    try {
      const result = await analyzeProduct(query)
      setData(result)
    } catch (err) {
      console.error('Analysis error:', err)
      setError(err instanceof Error ? err.message : 'Failed to analyze product')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSimilarProductClick = (productName: string) => {
    // Scroll to top smoothly
    window.scrollTo({ top: 0, behavior: 'smooth' })
    // Trigger new search after brief delay
    setTimeout(() => {
      handleSearch(productName)
    }, 500)
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#1a1a1b" }}>
      <Header />

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <SearchSection 
          onSearch={handleSearch} 
          isLoading={isLoading}
          currentQuery={currentQuery}
        />

        {error && (
          <div 
            className="mt-4 p-4 rounded-lg border"
            style={{ 
              backgroundColor: "#3a1f1f", 
              borderColor: "#ff4500",
              color: "#ff6b6b" 
            }}
          >
            <p className="font-semibold">Error:</p>
            <p>{error}</p>
            <p className="text-sm mt-2" style={{ color: "#d7dadc" }}>
              Make sure to enter a valid product name and that your backend is running on port 8000.
            </p>
          </div>
        )}

        {data && (
          <div className="space-y-6 mt-8 animate-in fade-in duration-500">
            <ProductInsights 
              rating={data.final_rating}
              subscores={data.subscores}
            />
            <RedditComments comments={data.comments} />
            <AISummary 
              summary={data.ai_summary}
              isLoading={isLoading}
            />
            
            {/* Similar Products Section */}
            {data.similar_products && data.similar_products.length > 0 && (
              <SimilarProducts 
                products={data.similar_products}
                onProductClick={handleSimilarProductClick}
              />
            )}
          </div>
        )}
      </main>
    </div>
  )
}