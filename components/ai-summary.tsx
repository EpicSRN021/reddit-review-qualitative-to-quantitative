interface AISummaryProps {
    isLoading: boolean
  }
  
  export function AISummary({ isLoading }: AISummaryProps) {
    return (
      <section className="rounded-xl p-6 shadow-lg" style={{ backgroundColor: "#272729" }}>
        <h2 className="text-xl font-semibold mb-4" style={{ color: "#d7dadc" }}>
          AI-Powered Product Summary
        </h2>
  
        {isLoading ? (
          <div className="space-y-3 animate-pulse">
            <div className="h-4 rounded" style={{ backgroundColor: "#343536" }} />
            <div className="h-4 rounded w-5/6" style={{ backgroundColor: "#343536" }} />
            <div className="h-4 rounded w-4/6" style={{ backgroundColor: "#343536" }} />
          </div>
        ) : (
          <div className="space-y-4" style={{ color: "#d7dadc" }}>
            <p className="leading-relaxed">
              Based on analysis of 2,847 Reddit reviews, the Sony WH-1000XM5 headphones receive overwhelmingly positive
              feedback. Users consistently praise the industry-leading noise cancellation, exceptional sound quality, and
              impressive battery life.
            </p>
            <p className="leading-relaxed">
              <strong style={{ color: "white" }}>Key Strengths:</strong> Superior noise cancellation, comfortable for
              extended wear, excellent battery life (30+ hours), premium build quality, and outstanding audio performance.
            </p>
            <p className="leading-relaxed">
              <strong style={{ color: "white" }}>Minor Concerns:</strong> Higher price point and a learning curve for
              touch controls. However, most users agree the quality justifies the investment.
            </p>
          </div>
        )}
      </section>
    )
  }
  