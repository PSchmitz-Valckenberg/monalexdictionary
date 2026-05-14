# Monalex Frontend

Next.js App Router frontend for the Monalex French-Monégasque dictionary.

## Requirements

- Node.js `20.9.0` or newer for Next.js 16.
- A running Monalex backend, usually `http://localhost:8000` in development.

## Setup

```bash
npm install
cp .env.local.example .env.local
npm run dev
```

The app runs at `http://localhost:3000`.

## Environment

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Public FastAPI backend URL. |

## Checks

```bash
npm run lint
npm exec -- tsc --noEmit
npm run build
```

`npm run build` requires Node.js `20.9.0` or newer.
