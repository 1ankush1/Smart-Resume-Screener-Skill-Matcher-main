# Frontend

The public React/Vite page accepts a resume and job description, then displays
the result returned by the Flask API. It has no account screens or credential
requirements.

For local development, run `npm.cmd install` and `npm.cmd run dev` from this folder.
Vite serves the page at <http://localhost:8080> and proxies `/api` requests to
the Flask API on port `5000`.

Run `npm.cmd run build` to create the static frontend in `dist/`.
