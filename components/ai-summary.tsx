import { Sparkles } from "lucide-react"

interface AISummaryProps {
  summary: string
  isLoading: boolean
}

export function AISummary({ summary, isLoading }: AISummaryProps) {
  return (
    <section className="rounded-xl p-6 shadow-lg" style={{ backgroundColor: "#272729" }}>
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="h-5 w-5" style={{ color: "#ff4500" }} />
        <h2 className="text-xl font-semibold" style={{ color: "#d7dadc" }}>
          AI-Powered Summary
        </h2>
      </div>

      {isLoading ? (
        <div className="space-y-3 animate-pulse">
          <div className="h-4 rounded" style={{ backgroundColor: "#343536" }} />
          <div className="h-4 rounded w-5/6" style={{ backgroundColor: "#343536" }} />
          <div className="h-4 rounded w-4/6" style={{ backgroundColor: "#343536" }} />
        </div>
      ) : (
        <div 
          className="leading-relaxed whitespace-pre-wrap" 
          style={{ color: "#d7dadc" }}
        >
          {summary}
        </div>
      )}
    </section>
  )
}