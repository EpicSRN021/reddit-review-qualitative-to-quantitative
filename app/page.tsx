"use client"

import { useState } from "react"
import { Header } from "@/components/header"
import { SearchSection } from "@/components/search-section"
import { ProductInsights } from "@/components/product-insights"
import { RedditComments } from "@/components/reddit-comments"
import { AISummary } from "@/components/ai-summary"

export default function Home() {
  const [isSearched, setIsSearched] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  const handleSearch = async (query: string) => {
    setIsLoading(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500))
    setIsLoading(false)
    setIsSearched(true)
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: "#1a1a1b" }}>
      <Header />

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <SearchSection onSearch={handleSearch} isLoading={isLoading} />

        {isSearched && (
          <div className="space-y-6 mt-8 animate-in fade-in duration-500">
            <ProductInsights />
            <RedditComments />
            <AISummary isLoading={isLoading} />
          </div>
        )}
      </main>
    </div>
  )
}
