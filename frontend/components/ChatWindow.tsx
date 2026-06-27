interface ChatWindowProps {
  answer: string;
}

export default function ChatWindow({ answer }: ChatWindowProps) {
  return (
    <div className="rounded-3xl border border-slate-800 bg-slate-950 p-6 text-slate-200">
      <h2 className="text-xl font-semibold">Answer</h2>
      <div className="mt-4 whitespace-pre-wrap text-slate-200">{answer || "Submit a question to see a response."}</div>
    </div>
  );
}
