# Website App

This folder contains the first Next.js / React / TypeScript / Tailwind CSS
foundation for the final user-facing website.

Streamlit remains the MVP, internal analytics workbench, and backup demo. This
website is the polished final-product direction.

## Setup

```text
cd apps/website
npm install
```

Create a local environment file:

```text
cp .env.local.example .env.local
```

Expected value:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Run locally

Terminal 1:

```text
cd api
uvicorn main:app --reload --port 8000
```

Terminal 2:

```text
cd apps/website
npm run dev
```

Website URL:

```text
http://localhost:3000
```

Implemented first-slice pages:

```text
/
/explore
/recommendations
/methodology
```
