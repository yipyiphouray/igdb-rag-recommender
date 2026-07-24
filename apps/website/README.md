# Website App

This folder contains the Next.js / React / TypeScript / Tailwind CSS frontend for the final user-facing website.

Streamlit remains the MVP/internal workbench. The website is the polished product interface.

## Setup

```bash
cd apps/website
npm install
```

Create a local environment file:

```bash
copy .env.local.example .env.local
```

Expected value:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Run locally

Terminal 1:

```bash
cd api
uvicorn main:app --reload --port 8000
```

Terminal 2:

```bash
cd apps/website
npm run dev
```

Website URL:

```text
http://localhost:3000
```

## Current Pages

```text
/
/explore
/explore/[game_id]
/hidden-gems
/guide
/insights
/methodology
/recommendations
```

`/guide` is the RAG-backed chatbot page. It calls:

```text
GET  /chat/status
POST /chat
```

## Validate

```bash
cd apps/website
npm run build
```
