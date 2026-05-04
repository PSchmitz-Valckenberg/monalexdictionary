# Contributing

Thanks for improving Monalex. Keep changes focused, testable, and respectful of
the dictionary data.

## Local Workflow

```bash
python -m venv .venv
source .venv/bin/activate
make install
cp .env.example .env
make check
```

Run the app:

```bash
make run
```

## Database Changes

- Keep schema changes compatible with `dictionary.sql`.
- Do not commit real credentials or local `.env` files.
- If a code change depends on new environment variables, update
  `.env.example`, `README.md`, and `docs/ARCHITECTURE.md`.

## Pull Request Checklist

- `make check` passes.
- New routes or response formats are covered by tests.
- User-facing text stays consistent with the existing French/Monégasque tone.
- Large generated files, virtualenvs, caches, and local exports are not tracked.
