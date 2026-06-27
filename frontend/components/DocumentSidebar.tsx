interface DocumentSidebarProps {
  documents: Array<{ id: number; filename: string; upload_date: string }>;
}

export default function DocumentSidebar({ documents }: DocumentSidebarProps) {
  return (
    <aside className="space-y-4 rounded-3xl border border-slate-800 bg-slate-900 p-6">
      <h2 className="text-xl font-semibold">Documents</h2>
      <div className="space-y-3">
        {documents.map((document) => (
          <div key={document.id} className="rounded-3xl border border-slate-800 bg-slate-950 p-4">
            <p className="text-sm font-medium text-slate-100">{document.filename}</p>
            <p className="text-sm text-slate-400">{new Date(document.upload_date).toLocaleDateString()}</p>
          </div>
        ))}
      </div>
    </aside>
  );
}
