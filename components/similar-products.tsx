import { Lightbulb, ArrowRight } from "lucide-react"

interface SimilarProductsProps {
  products: string[]
  onProductClick: (productName: string) => void
}

export function SimilarProducts({ products, onProductClick }: SimilarProductsProps) {
  if (!products || products.length === 0) {
    return null
  }

  return (
    <section className="rounded-xl p-6 shadow-lg" style={{ backgroundColor: "#272729" }}>
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="h-5 w-5" style={{ color: "#fbbf24" }} />
        <h2 className="text-xl font-semibold" style={{ color: "#d7dadc" }}>
          Similar Products You Might Like
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {products.map((product, index) => (
          <button
            key={index}
            onClick={() => onProductClick(product)}
            className="group relative overflow-hidden rounded-lg p-4 transition-all hover:scale-105 hover:shadow-xl"
            style={{
              backgroundColor: "#1a1a1b",
              border: "2px solid #343536",
            }}
          >
            {/* Hover gradient effect */}
            <div 
              className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity"
              style={{
                background: "linear-gradient(135deg, rgba(255, 69, 0, 0.1) 0%, rgba(255, 69, 0, 0.05) 100%)"
              }}
            />
            
            <div className="relative z-10">
              <div className="flex items-start justify-between mb-2">
                <span 
                  className="text-xs font-semibold px-2 py-1 rounded"
                  style={{ 
                    backgroundColor: "rgba(251, 191, 36, 0.2)",
                    color: "#fbbf24"
                  }}
                >
                  Alternative {index + 1}
                </span>
                <ArrowRight 
                  className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity"
                  style={{ color: "#ff4500" }}
                />
              </div>
              
              <h3 
                className="text-base font-semibold mb-1 line-clamp-2"
                style={{ color: "#d7dadc" }}
              >
                {product}
              </h3>
              
              <p 
                className="text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                style={{ color: "#818384" }}
              >
                Click to analyze this product
              </p>
            </div>
          </button>
        ))}
      </div>
    </section>
  )
}