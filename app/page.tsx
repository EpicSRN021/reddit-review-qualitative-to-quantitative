"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { SearchSection } from "@/components/search-section"
import { ProductInsights } from "@/components/product-insights"
import { RedditComments } from "@/components/reddit-comments"
import { AISummary } from "@/components/ai-summary"
import { analyzeProduct, type AnalysisResponse } from "@/lib/api"

export default function Home() {
  const [data, setData] = useState<AnalysisResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSearch = async (query: string) => {
    setIsLoading(true)
    setError(null)
    setData(null)
    
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

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#1a1a1b" }}>
      <Header />

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <SearchSection onSearch={handleSearch} isLoading={isLoading} />

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
              Make sure to enter a valid Reddit URL and that your backend is running on port 8000.
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
          </div>
        )}
      </main>
    </div>
  )
}