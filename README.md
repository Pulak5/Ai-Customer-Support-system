# AI Customer Support Ticket System

A full-stack customer-support ticket system that uses **Google Gemini** to triage tickets and help agents prepare grounded responses.

Customers can submit and track support requests. Support agents can review AI analysis, relevant company-policy sources, a suggested reply, email delivery state, and escalation decisions before responding.

## Features

- Customer ticket submission and tracking by ticket ID and email address
- Gemini category, priority, sentiment, team-assignment, and escalation analysis
- Retrieval-augmented generation (RAG) using local support-policy documents
- Agent workspace with source excerpts and relevance scores
- Editable AI reply suggestions and reply regeneration
- Separate saved agent replies and AI suggestions
- Safe escalation workflow: escalated tickets require an explicit human resolution
- SMTP email delivery, delivery status, and retry
- SQLite database created automatically for local development
- Safe fallback behavior when AI, RAG, or email delivery is unavailable

## Architecture

```text
Next.js customer portal and agent workspace
                |
                v
FastAPI API (ticket workflow and email handling)
                |
      +---------+----------+
      |                    |
      v                    v
SQLite ticket database   Gemini + Chroma RAG index
                              |
                              v
                   Local policy documents in data/knowledge_base
```

## Prerequisites

- Git
- Python 3.10 or later
- Node.js 20.9 or later and npm
- A Google Gemini API key for AI triage, embeddings, and reply generation
- An SMTP account only if you want to send response emails

## Clone the repository

```bash
git clone https://github.com/Pulak5/Ai-Customer-Support-system.git
cd Ai-Customer-Support-system
```

## Run with Docker (recommended for a full local demo)

Docker runs the frontend and backend in separate containers, keeps ticket data and the RAG index in Docker volumes, and starts both services with one command.

### 1. Install Docker Desktop

Install and start [Docker Desktop](https://www.docker.com/products/docker-desktop/). Confirm it is running before continuing.

### 2. Configure Gemini and optional email

Create the private backend environment file from the project root:

**Windows PowerShell**

```powershell
Copy-Item .env.example backend/.env
```

Add your `GOOGLE_API_KEY` to `backend/.env`. Configure the SMTP values in the same file only if you want email delivery.

### 3. Build and start the application

```bash
docker compose up --build
```

On the first start, Docker automatically creates the database and builds the RAG index from the policy documents included in `data/knowledge_base`.

Open:

- Customer portal: `http://localhost:3000`
- Agent workspace: `http://localhost:3000/workspace`
- API documentation: `http://localhost:8000/docs`

To run it in the background, use `docker compose up --build -d`. Stop the containers with `docker compose down`. Your tickets and RAG index remain in Docker volumes after stopping.

### Rebuild the RAG index after editing policy documents

```bash
docker compose exec backend rm /app/app/chroma_db/.initialized
docker compose restart backend
```

The index is rebuilt on the next backend start. Re-indexing replaces the previous collection, so duplicate documents are not created.

### Deploying a Docker image

Docker is the right packaging choice for this application. The project produces two images: one for the frontend and one for the backend.

To publish both images to Docker Hub, sign in first and set your Docker Hub username:

**Windows PowerShell**

```powershell
docker login
$env:DOCKERHUB_USERNAME = "your-docker-hub-username"
docker compose build
docker compose push
```

The images will be published as:

```text
your-docker-hub-username/ai-customer-support-backend:latest
your-docker-hub-username/ai-customer-support-frontend:latest
```

For public deployment, deploy the images to a service such as Render, Railway, Google Cloud Run, Fly.io, or a VPS. Set `NEXT_PUBLIC_API_URL` to the public backend URL while building the frontend, and set `CORS_ORIGINS` in the backend environment file to the public frontend URL.

## Configure and run the backend

### 1. Create a Python virtual environment

**Windows PowerShell**

```powershell
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, run this once in the same terminal and then activate the environment again:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

**macOS or Linux**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 2. Create the environment file

From the project root, copy the example file into the backend folder.

**Windows PowerShell**

```powershell
Copy-Item .env.example backend/.env
```

**macOS or Linux**

```bash
cp .env.example backend/.env
```

Open `backend/.env` and add your Gemini API key:

```env
GOOGLE_API_KEY=your-gemini-api-key
```

`backend/.env` contains private credentials and is ignored by Git. Never commit it.

### 3. Build the local RAG index

The project includes sample policy documents in `data/knowledge_base`. With the backend virtual environment active, run this once from the `backend` folder:

```bash
python -m app.ai.rag.embedder
```

This creates a local Chroma index in `backend/app/chroma_db`. The index is generated data and is ignored by Git, so every new machine must run this command after setting `GOOGLE_API_KEY`. Run it again after changing the policy documents; it replaces the previous index.

### 4. Start the API

From the `backend` folder with the virtual environment active:

```bash
uvicorn main:app --reload
```

The backend starts at `http://127.0.0.1:8000`. You can inspect the API at `http://127.0.0.1:8000/docs`.

The SQLite database file, `backend/tickets.db`, is created automatically the first time the backend starts.

## Configure and run the frontend

Open a second terminal from the project root:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

- **Customer portal:** submit a ticket and track it using ticket ID and email.
- **Agent workspace:** review the ticket queue, AI decision, retrieved knowledge, response, and email status.

The default frontend API address is `http://127.0.0.1:8000/api/v1`. To use a different address, create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1
```

## Optional SMTP email delivery

Email delivery is optional. Without SMTP configuration, the agent reply is still saved and displayed in the customer portal.

Add these values to `backend/.env` and restart the backend to enable email:

```env
SMTP_ENABLED=true
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=support@your-domain.com
SMTP_USE_TLS=true
```

If delivery fails, the response remains saved, the customer can still see it in the portal, and the agent can use **Retry email**.

## Ticket workflow

1. A customer submits a ticket.
2. Gemini classifies it and assigns a team, priority, sentiment, and escalation decision.
3. The system retrieves relevant policy excerpts from the local knowledge base.
4. An agent reviews or regenerates the AI suggestion, then edits the final response.
5. For a normal ticket, **Send & resolve** saves the reply and resolves the ticket.
6. For an escalated ticket, **Send response** saves the reply but keeps the ticket escalated. A human agent must select **Resolve ticket** when the case is actually complete.
7. The customer can track the latest status and saved response from the customer portal.

## Environment variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | No | SQLite connection string. Defaults to `sqlite:///./tickets.db`. |
| `KNOWLEDGE_BASE_DIR` | No | Policy-document folder. Docker sets this automatically. |
| `CORS_ORIGINS` | No | Comma-separated frontend addresses permitted to call the API. |
| `GOOGLE_API_KEY` | Yes for AI and RAG | Gemini API key. |
| `GEMINI_CHAT_MODEL` | No | Main Gemini model used for triage and replies. |
| `GEMINI_FALLBACK_CHAT_MODEL` | No | Fallback model when the main Gemini model is temporarily busy. |
| `GEMINI_EMBEDDING_MODEL` | No | Gemini embedding model for the knowledge base. |
| `SMTP_ENABLED` | No | Set to `true` to enable outbound email. |
| `SMTP_HOST`, `SMTP_PORT` | With SMTP | SMTP server address and port. |
| `SMTP_USERNAME`, `SMTP_PASSWORD` | With SMTP | SMTP credentials. |
| `SMTP_FROM_EMAIL` | With SMTP | Sender email address. |
| `SMTP_USE_TLS` | No | Uses TLS when set to `true`. |
| `NEXT_PUBLIC_API_URL` | No | Frontend API address; set in `frontend/.env.local`. |

## API endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/tickets/` | Submit a customer ticket. |
| `GET` | `/api/v1/tickets/` | List tickets for the agent queue. |
| `GET` | `/api/v1/tickets/{id}?customer_email=...` | Track a customer ticket. |
| `GET` | `/api/v1/tickets/{id}/draft-reply` | Generate an AI-assisted draft. |
| `POST` | `/api/v1/tickets/{id}/reply` | Save and send an agent response. |
| `POST` | `/api/v1/tickets/{id}/resolve` | Explicitly resolve an escalated ticket. |
| `POST` | `/api/v1/tickets/{id}/retry-email` | Retry delivery of the saved reply. |
| `POST` | `/api/v1/tickets/{id}/reanalyze` | Re-run AI triage and RAG retrieval. |

## Testing and production check

Run the backend workflow tests:

```bash
cd backend
python -m pytest tests/test_ticket_workflow.py -q
```

Build the frontend:

```bash
cd frontend
npm run build
```

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Gemini analysis or RAG is unavailable | Confirm `GOOGLE_API_KEY` is present in `backend/.env`, then restart the backend and rebuild the RAG index. |
| No knowledge sources appear | Run `python -m app.ai.rag.embedder` from the `backend` folder after configuring the Gemini key. |
| Frontend cannot contact the API | Start the backend first and confirm the frontend API URL is `http://127.0.0.1:8000/api/v1`. |
| Email delivery fails | Check the SMTP values, provider security settings, and credentials. The saved reply remains available and can be retried. |
| Port is already in use | Stop the process using port 3000 or 8000, or configure a different port and update `NEXT_PUBLIC_API_URL`. |
