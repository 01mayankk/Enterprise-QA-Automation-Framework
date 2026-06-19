# Security & Data Integrity Considerations

This document details the security design decisions made when building the web dashboard and automation runner.

---

## 1. Authentication & Token Management

### 1.1 No LocalStorage Persistence for GitHub PATs
- **Decision**: Storing GitHub Personal Access Tokens (PATs) inside the browser's `localStorage` or `sessionStorage` is **rejected**.
- **Reasoning**: Storing credentials in `localStorage` makes them vulnerable to Cross-Site Scripting (XSS) attacks. If an attacker injects a script, they can read the token.
- **Implementation Solution**:
  - The React frontend uses **public GitHub endpoints** (which do not require authentication) to retrieve workflow statuses, execution histories, and repository files.
  - For writing operations (such as triggering a `workflow_dispatch`), the dashboard uses a **transient React state variable**. The user inputs their token in a secure password-type text field. The token is kept purely in-memory and is wiped when the browser tab is refreshed or closed.

---

## 2. Serverless Architecture (No Backend Server)

- **Decision**: We reject introducing backend architectures like Flask, FastAPI, or Render servers.
- **Reasoning**:
  - **No Token Exposure**: Storing user tokens on a third-party backend server increases the attack surface.
  - **Cost & Maintenance**: Serverless static hosting on Vercel is free, secure, and has 99.9% uptime.
  - **Secret Isolation**: Test secrets (like test passwords or optional SMTP email details) are stored securely as **GitHub Actions Secrets**. They are injected into runner execution blocks at runtime and are never exposed to the Vercel frontend.

---

## 3. Client-Side Artifact Extraction Limits

- **Decision**: We enforce file size boundaries when downloading and parsing ZIP build artifacts:
  - **Zip size <= 20MB**: The dashboard automatically extracts the zip archive using the client-side `jszip` library and renders HTML reports and screenshots directly.
  - **Zip size > 20MB**: The dashboard displays a direct GitHub download link. It disables in-browser extraction.
- **Reasoning**: unzipping large archives in-browser using JavaScript consumes significant CPU and memory. For files over 20MB, browser tabs can lock up or crash. Limiting extraction to 20MB ensures a smooth user experience.
