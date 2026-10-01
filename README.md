# Ai-Customer-Support-system
AI-powered customer support ticket system with automated ticket classification, sentiment and priority analysis, RAG-based knowledge retrieval, and AI-assisted response generation.

## Run the backend with Gemini

1. Install the backend dependencies: `pip install -r backend/requirements.txt`.
2. Add your Gemini API key to `backend/.env` as `GOOGLE_API_KEY=your-key`.
   You can create a key in [Google AI Studio](https://aistudio.google.com/apikey).
3. From the `backend` directory, run `python -m app.ai.rag.embedder` once to index the sample knowledge base with Gemini embeddings.
4. Start the API from the `backend` directory with `uvicorn main:app --reload`.

The Gemini vector collection is separate from the previous OpenAI collection, so knowledge-base documents need to be indexed once after switching providers. Draft replies retry Gemini once and then use `gemini-3.5-flash-lite` if the primary model is temporarily busy.

## Run the frontend

1. Keep the backend running at `http://127.0.0.1:8000`.
2. In a second terminal, run `npm run dev` from the `frontend` directory.
3. Open `http://localhost:3000` and choose the customer portal or agent workspace.

Set `NEXT_PUBLIC_API_URL` if the backend uses a different address. The default is `http://127.0.0.1:8000/api/v1`.

## Send resolved replies by email

Add these values to `backend/.env` and restart the backend:

```env
SMTP_ENABLED=true
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=support@your-domain.com
SMTP_USE_TLS=true
```

After configuration, **Send & resolve** saves the reply, closes the ticket, and sends the reply to the customer. The agent workspace shows whether the delivery was sent, failed, or has not been configured.
