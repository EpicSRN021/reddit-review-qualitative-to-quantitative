import { Sparkles, Loader2 } from "lucide-react";

interface AISummaryProps {
  summary: string;
  isLoading: boolean;
  isGptFallback?: boolean; // Indicates if this is a GPT-generated summary due to no Reddit data
  isGeneratingSummary?: boolean; // Indicates if summary is currently being generated
}

export function AISummary({
  summary,
  isLoading,
  isGptFallback = false,
  isGeneratingSummary = false,
}: AISummaryProps) {
  return (
    <section
      className="rounded-xl p-6 shadow-lg"
      style={{ backgroundColor: "#272729" }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="h-5 w-5" style={{ color: "#ff4500" }} />
        <h2 className="text-xl font-semibold" style={{ color: "#d7dadc" }}>
          {isGptFallback
            ? "AI-Generated Product Summary"
            : "AI-Powered Summary"}
        </h2>
        {isGptFallback && (
          <span
            className="text-xs px-2 py-1 rounded-full"
            style={{ backgroundColor: "#343536", color: "#818384" }}
          >
            General Info
          </span>
        )}
      </div>

      {isLoading || isGeneratingSummary ? (
        <div className="space-y-4">
          {isGeneratingSummary ? (
            <div className="flex items-center justify-center gap-2 py-8">
              <Loader2
                className="h-5 w-5 animate-spin"
                style={{ color: "#ff4500" }}
              />
              <span style={{ color: "#d7dadc" }}>
                {isGptFallback
                  ? "Generating AI summary..."
                  : "Analyzing Reddit data..."}
              </span>
            </div>
          ) : (
            <div className="space-y-3 animate-pulse">
              <div
                className="h-4 rounded"
                style={{ backgroundColor: "#343536" }}
              />
              <div
                className="h-4 rounded w-5/6"
                style={{ backgroundColor: "#343536" }}
              />
              <div
                className="h-4 rounded w-4/6"
                style={{ backgroundColor: "#343536" }}
              />
            </div>
          )}
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
  );
}
