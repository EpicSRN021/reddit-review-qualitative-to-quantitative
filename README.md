## 🚀 Overview

RedditRadar is a fully deployed web application that helps users find unbiased, community-driven product reviews — all in one place.

When researching a product (say, a MacBook Pro), people often turn to Reddit for authentic opinions. But manually searching, opening multiple posts, skimming countless comments, and trying to make sense of scattered feedback is time-consuming and inefficient.

RedditRadar automates this process by collecting, analyzing, and summarizing Reddit discussions into quantitative metrics and actionable insights.

## 💡 Motivation

Product research on Reddit gives some of the most honest opinions — but at the cost of effort. RedditRadar simplifies this by:

Aggregating relevant Reddit posts and comments about a product.

Analyzing community feedback using AI.

Turning unstructured qualitative data into structured, quantitative insights.

This saves users time and gives them both data-driven scores and authentic user context.

## ⚙️ How It Works
1. Data Collection

When a user searches for a product (e.g., “MacBook Pro”), RedditRadar:

Collects related Reddit posts and comments via Reddit’s API.

Filters for relevant discussions.

2. AI-Powered Analysis

Each comment is analyzed and scored out of 5 across four key metrics:

Performance

Usability

Reliability

Value

Each comment’s weight is then determined by:

Upvotes

User karma

Time since posted

A final weighted score is calculated to represent the community’s sentiment toward the product.

⚠️ Note: Currently, the model relies on OpenAI’s API for comment analysis. We planned to fine-tune or deploy our own transformer-based model for this task, but due to the hackathon’s time constraints, this was not implemented yet.

## 📊 Features
🔹 Product Dashboard

Displays an overall product score and subscores for each metric.

Shows a quick, digestible summary of community sentiment.

🔹 Relevant Reddit Comments

Shows the most informative and relevant comments.

Each comment is clickable, linking directly to the original Reddit post for context.

🔹 AI Summary

Generates a concise AI-written summary of the top comments for quick reading.

Highlights main themes in user feedback.

🔹 Pros and Cons

Extracts the most common pros and cons of the product.

Each pro/con is clickable, linking to the original comment it was derived from.

🔹 Alternatives

Suggests similar products with their own RedditRadar reviews.

Helps users compare before making a purchase decision.

## 🧠 Tech Stack
Category	Technology
Frontend	React.js, Tailwind CSS
Backend	Flask / FastAPI
AI & NLP	OpenAI API (planned: in-house transformer fine-tuning)
Data Source	Reddit API
Deployment	[Your platform, e.g., Vercel / Render / Azure]
#  🧩 Future Improvements

Train and integrate a custom transformer model for comment scoring.

Add topic clustering for comment grouping.

Improve data caching and parallelization for faster API calls.

Expand metrics for more nuanced evaluations (e.g., build quality, customer support).
