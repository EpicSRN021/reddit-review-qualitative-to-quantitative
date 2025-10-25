"use client"

import type React from "react"

import { useState } from "react"
import { Search, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"

interface SearchSectionProps {
  onSearch: (query: string) => void
  isLoading: boolean
}

export function SearchSection({ onSearch, isLoading }: SearchSectionProps) {
  const [query, setQuery] = useState("")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      onSearch(query)
    }
  }

  return (
    <section className="flex justify-center items-center py-12">
      <form onSubmit={handleSubmit} className="w-full max-w-2xl">
        <div className="flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search for a product to analyze reviews..."
              className="w-full px-4 py-3 rounded-lg text-base transition-all focus:outline-none focus:ring-2"
              style={{
                backgroundColor: "#272729",
                color: "#d7dadc",
                borderColor: "#343536",
                border: "1px solid #343536",
              }}
              disabled={isLoading}
            />
          </div>
          <Button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="px-6 py-3 rounded-lg font-medium transition-all hover:opacity-90 disabled:opacity-50"
            style={{
              backgroundColor: "#ff4500",
              color: "white",
            }}
          >
            {isLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : <Search className="h-5 w-5" />}
          </Button>
        </div>
      </form>
    </section>
  )
}
