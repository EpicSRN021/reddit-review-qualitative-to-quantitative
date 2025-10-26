import { MessageSquare, ExternalLink, Loader2 } from "lucide-react";

interface RedditCommentsProps {
  comments: [string, string][]; // Array of [comment_text, comment_url] tuples
  isGeneratingSummary?: boolean; // Indicates if summary is being generated
}

export function RedditComments({
  comments,
  isGeneratingSummary = false,
}: RedditCommentsProps) {
  if (!comments || comments.length === 0) {
    return (
      <section
        className="rounded-xl p-6 shadow-lg"
        style={{ backgroundColor: "#272729" }}
      >
        <h2 className="text-xl font-semibold mb-6" style={{ color: "#d7dadc" }}>
          Top Reddit Reviews
        </h2>
        <div className="text-center py-8">
          <MessageSquare
            className="h-12 w-12 mx-auto mb-4"
            style={{ color: "#818384" }}
          />
          <p className="text-lg font-medium mb-2" style={{ color: "#d7dadc" }}>
            No Reddit reviews found
          </p>
          <p className="mb-4" style={{ color: "#818384" }}>
            We couldn&apos;t find any Reddit discussions about this product.
          </p>

          {isGeneratingSummary ? (
            <div
              className="flex items-center justify-center gap-2 text-sm"
              style={{ color: "#ff4500" }}
            >
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Generating AI summary...</span>
            </div>
          ) : (
            <p className="text-sm" style={{ color: "#818384" }}>
              Check the AI Summary below for general product information.
            </p>
          )}
        </div>
      </section>
    );
  }

  return (
    <section
      className="rounded-xl p-6 shadow-lg"
      style={{ backgroundColor: "#272729" }}
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold" style={{ color: "#d7dadc" }}>
          Top Reddit Reviews
        </h2>
        <div className="flex items-center gap-2" style={{ color: "#818384" }}>
          <MessageSquare className="h-4 w-4" />
          <span className="text-sm">{comments.length} comments</span>
        </div>
      </div>

      <div className="space-y-4">
        {comments.map(([text, url], index) => (
          <div
            key={index}
            className="pl-4 py-3 rounded transition-colors hover:bg-opacity-50 group"
            style={{
              borderLeft: "2px solid #343536",
              backgroundColor: "rgba(52, 53, 54, 0.3)",
            }}
          >
            <div className="flex items-start justify-between gap-3 mb-2">
              <span
                className="text-sm font-medium"
                style={{ color: "#818384" }}
              >
                Review #{index + 1}
              </span>
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-sm opacity-0 group-hover:opacity-100 transition-opacity"
                style={{ color: "#ff4500" }}
              >
                View on Reddit
                <ExternalLink className="h-3 w-3" />
              </a>
            </div>
            <p className="leading-relaxed" style={{ color: "#d7dadc" }}>
              {text}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
