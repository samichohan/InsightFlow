import { useCallback, useRef, useState } from "react";
import { FolderOpen, UploadCloud, FileCheck2 } from "lucide-react";

const FILE_TYPES = ["CSV", "XLSX", "XLS", "JSON", "PARQUET", "PDF", "TXT"];

export default function UploadZone({ onFile, uploading, progress, uploadedName }) {
  const [isDrag, setIsDrag] = useState(false);
  const inputRef = useRef(null);

  const handleDrop = useCallback((e) => {
    e.preventDefault(); setIsDrag(false);
    const file = e.dataTransfer.files?.[0];
    if (file) onFile(file);
  }, [onFile]);

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDrag(true); }}
      onDragLeave={() => setIsDrag(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={`group relative cursor-pointer rounded-3xl border-2 border-dashed px-8 py-16 text-center transition-all duration-300
        ${isDrag ? "border-accent-blue bg-accent-blue/5 scale-[1.01]" : "border-border-glow bg-bg-card/40 hover:border-accent-blue/50 hover:bg-bg-card/60"}`}
    >
      <input ref={inputRef} type="file" accept=".csv,.xlsx,.xls,.json,.parquet,.pdf,.txt" className="hidden" onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); }} />

      <div className="mx-auto mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-400/20 to-amber-600/10 text-amber-300 transition-transform duration-300 group-hover:scale-110">
        {uploading ? <UploadCloud className="h-8 w-8 animate-bounce" /> : uploadedName ? <FileCheck2 className="h-8 w-8 text-emerald-400" /> : <FolderOpen className="h-8 w-8" />}
      </div>

      {uploading ? (
        <>
          <h3 className="font-display text-2xl font-semibold text-white">Uploading… {progress}%</h3>
          <div className="mx-auto mt-4 h-1.5 w-64 overflow-hidden rounded-full bg-bg-raised">
            <div className="h-full rounded-full bg-gradient-to-r from-accent-blue to-accent-violet transition-all duration-200" style={{ width: `${progress}%` }} />
          </div>
        </>
      ) : uploadedName ? (
        <>
          <h3 className="font-display text-xl font-semibold text-white">{uploadedName}</h3>
          <p className="mt-2 text-sm text-slate-400">Click or drop a new file to replace</p>
        </>
      ) : (
        <>
          <h3 className="font-display text-2xl font-semibold text-white">Drop your dataset here</h3>
          <p className="mt-2 text-sm text-slate-400">or click to browse</p>
        </>
      )}

      <div className="mt-7 flex flex-wrap justify-center gap-2">
        {FILE_TYPES.map(t => (
          <span key={t} className="rounded-lg border border-violet-500/30 bg-violet-500/10 px-3 py-1 font-mono text-xs font-semibold text-violet-300">{t}</span>
        ))}
      </div>
    </div>
  );
}
