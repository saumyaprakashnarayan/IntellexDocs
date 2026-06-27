interface CitationPanelProps {
  sources: Array<{ document: string; page: number; chunk_id: number; similarity?: number }>;
}

export default function CitationPanel({ sources }: CitationPanelProps) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-xl font-semibold">Citations</h2>
        <p className="text-sm text-slate-400">Sources referenced by the AI answer.</p>
      </div>
      {sources.length === 0 ? (
        <div className="rounded-3xl border border-slate-800 bg-slate-950 p-4 text-slate-500">No citations yet.</div>
      ) : (
        <div className="space-y-3">
          {sources.map((source, index) => (
            <div key={`${source.document}-${source.page}-${index}`} className="rounded-3xl border border-slate-800 bg-slate-950 p-4">
              <p className="text-sm text-slate-300">{source.document}</p>
              <p className="text-sm text-slate-400">Page {source.page} · Chunk {source.chunk_id}</p>
              {source.similarity !== undefined && (
                <p className="text-sm text-slate-500">Similarity {source.similarity.toFixed(2)}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
