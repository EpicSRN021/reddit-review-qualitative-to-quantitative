import { Star } from "lucide-react"

export function ProductInsights() {
  const rating = 4.5
  const fullStars = Math.floor(rating)
  const hasHalfStar = rating % 1 !== 0

  return (
    <section className="rounded-xl p-6 shadow-lg" style={{ backgroundColor: "#272729" }}>
      <h2 className="text-xl font-semibold mb-4" style={{ color: "#d7dadc" }}>
        Product Overview
      </h2>

      <div className="space-y-3">
        <h3 className="text-2xl font-bold" style={{ color: "white" }}>
          Sony WH-1000XM5 Headphones
        </h3>

        <div className="flex items-center gap-2">
          <div className="flex">
            {[...Array(5)].map((_, i) => (
              <Star
                key={i}
                className="h-5 w-5"
                fill={i < fullStars ? "#ff4500" : "none"}
                stroke={i < fullStars || (i === fullStars && hasHalfStar) ? "#ff4500" : "#818384"}
              />
            ))}
          </div>
          <span className="text-lg font-semibold" style={{ color: "#ff4500" }}>
            {rating}
          </span>
          <span style={{ color: "#818384" }}>(2,847 reviews)</span>
        </div>
      </div>
    </section>
  )
}
