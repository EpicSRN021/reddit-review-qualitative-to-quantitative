"use client";

import { Star } from "lucide-react";
import { useState } from "react";

interface ProductInsightsProps {
  rating: number; // 0-5 overall rating
  subscores: number[]; // [quality, cost, availability, utility]
}

export function ProductInsights({ rating, subscores }: ProductInsightsProps) {
  const [showTooltip, setShowTooltip] = useState(false);

  const fullStars = Math.floor(rating);
  const hasHalfStar = rating % 1 >= 0.5;
  const hasNoData = rating === 0 && subscores.every((score) => score === 0);

  const labels = ["Quality", "Cost", "Availability", "Utility"];

  return (
    <section
      className="rounded-xl p-6 shadow-lg"
      style={{ backgroundColor: "#272729" }}
    >
      <h2 className="text-xl font-semibold mb-4" style={{ color: "#d7dadc" }}>
        Product Overview
      </h2>

      <div className="space-y-4">
        {hasNoData ? (
          /* No Data Available Message */
          <div className="text-center py-6">
            <Star
              className="h-12 w-12 mx-auto mb-4"
              style={{ color: "#818384" }}
            />
            <p
              className="text-lg font-medium mb-2"
              style={{ color: "#d7dadc" }}
            >
              No rating data available
            </p>
            <p style={{ color: "#818384" }}>
              We couldn't find Reddit reviews to generate ratings. Check the AI
              Summary below for general product information.
            </p>
          </div>
        ) : (
          /* Star Rating with Hover Tooltip */
          <div className="relative">
            <div
              className="flex items-center gap-2"
              onMouseEnter={() => setShowTooltip(true)}
              onMouseLeave={() => setShowTooltip(false)}
            >
              <div className="flex cursor-help">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className="h-6 w-6 transition-all"
                    fill={
                      i < fullStars || (i === fullStars && hasHalfStar)
                        ? "#ff4500"
                        : "none"
                    }
                    stroke={
                      i < fullStars || (i === fullStars && hasHalfStar)
                        ? "#ff4500"
                        : "#818384"
                    }
                  />
                ))}
              </div>
              <span
                className="text-2xl font-semibold"
                style={{ color: "#ff4500" }}
              >
                {rating.toFixed(1)}
              </span>
              <span className="text-sm" style={{ color: "#818384" }}>
                / 5.0
              </span>
            </div>

            {/* Tooltip with Subscores */}
            {showTooltip && (
              <div
                className="absolute top-full left-0 mt-2 p-4 rounded-lg shadow-xl z-10 min-w-[280px]"
                style={{
                  backgroundColor: "#1a1a1b",
                  border: "1px solid #343536",
                }}
              >
                <p
                  className="text-sm font-semibold mb-3"
                  style={{ color: "#d7dadc" }}
                >
                  Detailed Breakdown:
                </p>
                <div className="space-y-2">
                  {subscores.map((score, i) => (
                    <div
                      key={i}
                      className="flex items-center justify-between gap-4"
                    >
                      <span className="text-sm" style={{ color: "#d7dadc" }}>
                        {labels[i]}:
                      </span>
                      <div className="flex items-center gap-2">
                        <div
                          className="h-2 w-24 rounded-full overflow-hidden"
                          style={{ backgroundColor: "#343536" }}
                        >
                          <div
                            className="h-full transition-all"
                            style={{
                              width: `${(score / 5) * 100}%`,
                              backgroundColor: "#ff4500",
                            }}
                          />
                        </div>
                        <span
                          className="text-sm font-semibold w-8 text-right"
                          style={{ color: "#ff4500" }}
                        >
                          {score.toFixed(1)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Subscores Grid - Only show if we have data */}
        {!hasNoData && (
          <div
            className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t"
            style={{ borderColor: "#343536" }}
          >
            {subscores.map((score, i) => (
              <div key={i} className="text-center">
                <div
                  className="text-2xl font-bold"
                  style={{ color: "#ff4500" }}
                >
                  {score.toFixed(1)}
                </div>
                <div className="text-sm" style={{ color: "#818384" }}>
                  {labels[i]}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
