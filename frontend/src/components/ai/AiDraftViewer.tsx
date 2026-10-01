import { Button } from "@/components/ui/Button";

type AiDraftViewerProps = {
  draft: string;
  loading: boolean;
  error: string;
  onGenerate: () => void;
};

export function AiDraftViewer({ draft, loading, error, onGenerate }: AiDraftViewerProps) {
  return (
    <section className="draft-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Gemini assistant</p>
          <h3>Suggested reply</h3>
        </div>
        <Button loading={loading} onClick={onGenerate}>Generate reply</Button>
      </div>
      {error && <p className="form-error">{error}</p>}
      {draft ? <p className="draft-copy">{draft}</p> : <p className="muted">Generate a reply using the ticket and relevant knowledge-base articles.</p>}
    </section>
  );
}
