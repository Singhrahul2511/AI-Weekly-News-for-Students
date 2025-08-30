# AI Weekly Newsletter for Students

A fully automated, production-ready newsletter project that scrapes, summarizes, and sends the latest AI news to subscribers. Built with Python, FastAPI, Gemini, and Mailchimp, and designed for zero-cost deployment on Render and Vercel.

This project is a perfect portfolio piece to demonstrate skills in full-stack development, LLM integration, automation, and deployment.



***

## ✨ Features

-   **Automated Content Curation**: Fetches weekly news from RSS feeds, blogs, and arXiv.
-   **LLM-Powered Summarization**: Uses Google's Gemini API to generate concise, student-friendly summaries.
-   **Resilient Fallback**: Automatically switches to an extractive summarizer (TextRank) if the LLM API fails.
-   **Fully Automated Sending**: A cron job orchestrates the entire process from collection to sending via Mailchimp.
-   **Professional Email Template**: Responsive, single-column HTML email with inlined CSS for maximum compatibility.
-   **Admin Dashboard**: A simple, token-protected web interface to view subscribers and trigger test sends.
-   **Zero-Cost Deployment**: Designed to run entirely on the free tiers of Render, Vercel, and Supabase.
-   **Production-Ready**: Dockerized, configurable via environment variables, and includes basic tests.

***

## 🚀 Live Demo & Quickstart

*(You would replace these with your live URLs after deployment)*
-   **Landing Page**: `https://your-frontend.vercel.app`
-   **Last Issue**: `https://your-backend.render.com/last`
-   **Admin Panel**: `https://your-backend.render.com/admin?token=YOUR_ADMIN_TOKEN`

### Local Setup (5 minutes)

**1. Clone the repository:**

```bash
git clone <your-repo-url>
cd ai_newsletter