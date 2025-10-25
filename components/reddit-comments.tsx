import { ArrowUp } from "lucide-react"

const DUMMY_COMMENTS = [
  {
    id: 1,
    username: "audiophile_mike",
    upvotes: 1247,
    text: "Best noise cancellation I've ever experienced. Worth every penny for frequent travelers.",
  },
  {
    id: 2,
    username: "tech_reviewer_99",
    upvotes: 892,
    text: "Sound quality is incredible, but the touch controls take some getting used to. Overall very satisfied.",
  },
  {
    id: 3,
    username: "commuter_daily",
    upvotes: 654,
    text: "Battery life is insane - easily lasts my entire work week without charging.",
  },
  {
    id: 4,
    username: "music_lover_2024",
    upvotes: 521,
    text: "The comfort level is unmatched. I can wear these for 8+ hours without any discomfort.",
  },
  {
    id: 5,
    username: "budget_conscious",
    upvotes: 387,
    text: "Pricey, but the quality justifies the cost. These will last you years.",
  },
]

export function RedditComments() {
  return (
    <section className="rounded-xl p-6 shadow-lg" style={{ backgroundColor: "#272729" }}>
      <h2 className="text-xl font-semibold mb-6" style={{ color: "#d7dadc" }}>
        Top Reddit Reviews
      </h2>

      <div className="space-y-4">
        {DUMMY_COMMENTS.map((comment) => (
          <div
            key={comment.id}
            className="pl-4 py-3 rounded transition-colors hover:bg-opacity-50"
            style={{
              borderLeft: "2px solid #343536",
              backgroundColor: "rgba(52, 53, 54, 0.3)",
            }}
          >
            <div className="flex items-center gap-3 mb-2">
              <span className="font-medium" style={{ color: "#818384" }}>
                u/{comment.username}
              </span>
              <div className="flex items-center gap-1">
                <ArrowUp className="h-4 w-4" style={{ color: "#ff4500" }} />
                <span className="text-sm font-semibold" style={{ color: "#ff4500" }}>
                  {comment.upvotes.toLocaleString()}
                </span>
              </div>
            </div>
            <p className="leading-relaxed" style={{ color: "#d7dadc" }}>
              {comment.text}
            </p>
          </div>
        ))}
      </div>
    </section>
  )
}
