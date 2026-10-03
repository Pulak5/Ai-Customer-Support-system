import { Button } from "@/components/ui/Button";

type AiDraftViewerProps = {
  reply: string;
  generating: boolean;
  sending: boolean;
  escalationRequired: boolean;
  canExplicitlyResolve: boolean;
  isResolved: boolean;
  error: string;
  onGenerate: () => void;
  onReplyChange: (reply: string) => void;
  onSend: () => void;
  onResolve: () => void;
};

export function AiDraftViewer({ reply, generating, sending, escalationRequired, canExplicitlyResolve, isResolved, error, onGenerate, onReplyChange, onSend, onResolve }: AiDraftViewerProps) {
  return (
    <section className="draft-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">AI suggested reply</p>
          <h3>Agent response</h3>
        </div>
        <Button disabled={isResolved} loading={generating} onClick={onGenerate}>{reply.trim() ? "Regenerate reply" : "Generate reply"}</Button>
      </div>
      {error && <p className="form-error">{error}</p>}
      <textarea
        aria-label="Agent reply"
        className="reply-input"
        placeholder="Write a reply, or generate an AI draft to edit."
        rows={7}
        value={reply}
        disabled={isResolved}
        onChange={(event) => onReplyChange(event.target.value)}
      />
      <div className="draft-actions">
        <p className="muted">{isResolved ? "This ticket is resolved. Use the saved response as the record of the completed case." : "Review and edit this AI suggestion before sending it to the customer."}</p>
        {!isResolved && <div className="reply-actions"><Button loading={sending} disabled={!reply.trim()} onClick={onSend}>{escalationRequired ? "Send response" : "Send & resolve"}</Button>{canExplicitlyResolve && <Button className="secondary" loading={sending} onClick={onResolve}>Resolve ticket</Button>}</div>}
      </div>
    </section>
  );
}
