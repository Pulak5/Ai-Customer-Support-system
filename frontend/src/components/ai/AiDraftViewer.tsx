import { Button } from "@/components/ui/Button";

type AiDraftViewerProps = {
  reply: string;
  generating: boolean;
  sending: boolean;
  error: string;
  onGenerate: () => void;
  onReplyChange: (reply: string) => void;
  onSend: () => void;
};

export function AiDraftViewer({ reply, generating, sending, error, onGenerate, onReplyChange, onSend }: AiDraftViewerProps) {
  return (
    <section className="draft-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Gemini assistant</p>
          <h3>Suggested reply</h3>
        </div>
        <Button loading={generating} onClick={onGenerate}>Generate reply</Button>
      </div>
      {error && <p className="form-error">{error}</p>}
      <textarea
        aria-label="Agent reply"
        className="reply-input"
        placeholder="Write a reply, or generate an AI draft to edit."
        rows={7}
        value={reply}
        onChange={(event) => onReplyChange(event.target.value)}
      />
      <div className="draft-actions">
        <p className="muted">Review and edit the reply before resolving the ticket.</p>
        <Button loading={sending} disabled={!reply.trim()} onClick={onSend}>Send & resolve</Button>
      </div>
    </section>
  );
}
