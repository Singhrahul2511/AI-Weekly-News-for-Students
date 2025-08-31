# AI Weekly Newsletter for Students

![AI Weekly Newsletter Banner](https://user-images.githubusercontent.com/1092880/203492733-a385429a-21e1-4c2a-9486-42d4ca7a22a3.png)

**A fully automated, AI-powered weekly newsletter that curates, summarizes, and delivers the latest advancements in artificial intelligence directly to students. Built with a modern Python stack and deployed on a zero-cost, production-ready infrastructure.**

---

### **Live Demo**

* **📰 Live Landing Page:** `https://[YOUR-VERCEL-URL].vercel.app/`
* **📬 View the Last Sent Issue:** `https://[YOUR-RENDER-URL]/last`
* **🔑 Admin Panel (Protected):** `https://[YOUR-RENDER-URL]/admin?token=[YOUR_ADMIN_TOKEN]`

---

## 📖 Table of Contents

* [The Problem](#-the-problem)
* [The Solution](#-the-solution)
* [Key Features](#-key-features)
* [System Architecture](#-system-architecture)
* [Tech Stack](#-tech-stack)
* [Getting Started (Local Development)](#-getting-started-local-development)
    * [Prerequisites](#prerequisites)
    * [Installation](#installation)
    * [Running the Application](#running-the-application)
* [Deployment Overview](#-deployment-overview)
* [Project Structure](#-project-structure)
* [Core Code Modules Explained](#-core-code-modules-explained)
* [Scaling and Future Improvements](#-scaling-and-future-improvements)
* [License](#-license)

---

## 🎯 The Problem

The field of Artificial Intelligence is evolving at an unprecedented rate. For students, staying current with the latest breakthroughs, research papers, and open-source tools is a significant challenge. Sifting through dozens of blogs, academic sites, and social media feeds every week is time-consuming and overwhelming.

## 💡 The Solution

This project solves the problem by creating a **fully automated pipeline** that does the heavy lifting. Every week, it scours the internet for the most significant AI news, uses Google's Gemini Pro to generate concise, easy-to-understand summaries, and delivers them in a polished, professional newsletter. This allows students to stay informed in just a few minutes a week.

*(Here is where you can embed a GIF showing the script running and the final newsletter)*
`![Project Demo GIF]`

---

## ✨ Key Features

* 🤖 **Automated Content Curation**: Scrapes RSS feeds from top AI blogs (Google, OpenAI) and arXiv for the latest research papers.
* ✨ **LLM-Powered Summarization**: Leverages the **Google Gemini API** to create abstractive, student-friendly summaries of complex topics.
* 🛡️ **Resilient by Design**: Includes a fallback extractive summarizer (TextRank) and gracefully skips content sections if an external API fails, ensuring the newsletter is always sent.
* 🚀 **Zero-Cost Deployment**: Architected to run entirely on the free tiers of **Render** (backend), **Supabase** (database), and **GitHub Actions** (automation).
* 📧 **Professional Email Delivery**: Integrates with the **Mailchimp API** for reliable, high-deliverability email campaigns.
* ⚙️ **Automated Scheduling**: A **GitHub Actions** workflow triggers the entire pipeline every Sunday, requiring zero manual intervention.
* 🔑 **Secure & Configurable**: Manages all API keys and secrets using environment variables, with a token-protected admin endpoint.

---

## 🏗️ System Architecture

This project is built on a modern, decoupled architecture. The automation, backend, and database are all separate, scalable components.

```mermaid
flowchart TD
    A[GitHub Actions Scheduler <br> (Every Sunday at 20:00 UTC)] --> B{POST Request};
    B --> C[Render Web Service <br> /tasks/run-weekly-job];
    C --> D[Background Task];
    D -- Fetches Content --> E[Internet <br> (RSS, GitHub API, X API)];
    D -- Summarizes Using --> F[Google Gemini API];
    D -- Stores Data --> G[Supabase <br> (PostgreSQL Database)];
    D -- Sends Campaign --> H[Mailchimp API];
    H -- Delivers Email --> I[Subscriber Inboxes];
    J[User] --> K[Render Web Service <br> (Landing Page & Subscription)];
    K -- Writes Data --> G;
🛠️ Tech Stack
Category	Technology
Backend	Python, FastAPI, SQLAlchemy
Database	PostgreSQL (hosted on Supabase)
AI / LLM	Google Gemini API
Email	Mailchimp API
Scheduler	GitHub Actions
Deployment	Docker, Render, Supabase
Core Libs	requests, feedparser, tweepy, premailer, sumy

Export to Sheets
🚀 Getting Started (Local Development)
Follow these instructions to set up and run the project on your local machine.

Prerequisites
Python 3.11+

A code editor (e.g., VS Code)

API keys for:

Google Gemini

Mailchimp

X (Twitter) API (Optional)

GitHub PAT (Optional, for higher rate limits)

Installation
Clone the repository:

Bash

git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name
Create a virtual environment:

Bash

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies:

Bash

pip install -r requirements.txt
Set up environment variables:

Copy the example file: cp .env.example .env

Edit the .env file and add all your API keys and secrets.

Running the Application
Run the web server:

This will start the FastAPI application, making the landing page and API available locally.

Bash

  uvicorn web.app:app --reload
Open http://127.0.0.1:8000 in your browser.

Run the newsletter pipeline (Dry Run):

This is the primary command for testing. It runs the entire process and generates a preview HTML file without sending any emails.

Bash

  python -m tasks.run_weekly --dry-run
Check the generated file at out/last_preview.html.

☁️ Deployment Overview
The application is deployed using a free-tier, multi-cloud strategy:

Backend (Render): The FastAPI application is containerized with Docker and deployed as a Web Service on Render. This handles the API, serves the main landing page, and runs the background tasks.

Database (Supabase): A free PostgreSQL instance on Supabase acts as the production database.

Scheduler (GitHub Actions): A workflow defined in .github/workflows/scheduler.yml runs on a weekly cron schedule. It sends a secure POST request to a protected endpoint on the Render backend to trigger the newsletter generation and sending process.

This setup ensures a clean separation of concerns and leverages the strengths of each platform, all while remaining free.

📁 Project Structure
├── .github/workflows/      # Contains the GitHub Actions scheduler
├── modules/                # Core Python modules for each task
│   ├── collector.py        # Fetches content from RSS, GitHub, X
│   ├── summarizer.py       # Handles Gemini API calls and fallback
│   ├── categorizer.py      # Selects and categorizes content
│   ├── mailer.py           # Integrates with the Mailchimp API
│   ├── storage.py          # Defines database models (SQLAlchemy)
│   └── templater.py        # Renders the HTML email template
├── tasks/                  # Executable scripts
│   └── run_weekly.py       # Main orchestration script
├── templates/              # Jinja2 HTML templates
│   └── email_templates/
├── web/                    # FastAPI application
│   ├── app.py              # Defines API routes and serves the frontend
│   └── static/             # Contains the static index.html
├── .env.example            # Template for environment variables
├── config.py               # Pydantic settings management
├── Dockerfile              # Docker configuration for deployment
└── README.md               # This file
🧠 Core Code Modules Explained
tasks/run_weekly.py: The "brain" of the operation. This script is called by the scheduler and orchestrates the entire weekly process: it calls the collector, then the summarizer, then the categorizer, and finally the mailer.

modules/collector.py: The "hands and eyes." This module is responsible for reaching out to the internet (RSS feeds, APIs) to gather the raw content for the newsletter. It's designed to be resilient, with retries and custom headers.

modules/summarizer.py: The "AI core." This module takes the raw content and sends it to the Google Gemini API for summarization. It also contains the crucial fallback logic to a simpler summarizer if the API fails.

web/app.py: The "front door." This FastAPI application serves the public-facing landing page and provides the secure API endpoints for subscriptions and for the GitHub Actions scheduler to trigger the weekly job.

modules/storage.py: The "memory." It defines the database structure using SQLAlchemy ORM and provides all the functions needed to read from and write to the database.

📈 Scaling and Future Improvements
This project is built on a solid foundation, but here's how it could be scaled and improved for a larger audience:

Task Queuing: For thousands of subscribers, the sending process could take a long time. I would replace the current background task with a robust task queue system like Celery with Redis or RabbitMQ. This would allow for better management of long-running jobs, automatic retries, and the ability to scale workers independently.

Email Service at Scale: Mailchimp's free tier is limited. I would migrate to AWS SES (Simple Email Service) or SendGrid, which offer much lower costs at high volumes and provide more detailed deliverability analytics. The mailer.py module is designed to be easily extensible with a new SESMailer class.

Advanced Content Curation: The current curation is based on trusted sources. To improve quality, I would implement a ranking algorithm that scores articles based on factors like social media engagement, keyword relevance, and recency, ensuring only the absolute best content makes it into the newsletter.

A/B Testing: I would add functionality to A/B test different subject lines or content formats. The orchestration script could generate two versions of the campaign and send them to small segments of the audience, with the winner being sent to the rest.

Dedicated Frontend: While the FastAPI-served page is efficient, a dedicated frontend framework like Next.js or Vue.js would allow for a richer user experience, including an archive of past issues and user account management.