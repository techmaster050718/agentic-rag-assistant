"use client";

import { useCallback, useRef, useState } from "react";
import { Upload, CloudUpload } from "lucide-react";
import { cn } from "@/lib/utils";

interface UploadZoneProps {
  onFilesSelected: (files: File[]) => void;
  accept?: string;
  multiple?: boolean;
  disabled?: boolean;
}

export function UploadZone({
  onFilesSelected,
  accept = ".pdf,.txt,.md,.docx,.csv",
  multiple = true,
  disabled = false,
}: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (disabled) return;
      const files = Array.from(e.dataTransfer.files);
      if (files.length > 0) onFilesSelected(files);
    },
    [disabled, onFilesSelected]
  );

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      onClick={() => !disabled && inputRef.current?.click()}
      className={cn(
        "relative flex flex-col items-center justify-center gap-4 p-12 rounded-3xl border-2 border-dashed transition-all cursor-pointer",
        isDragging
          ? "border-violet-500 bg-violet-500/10 scale-[1.01]"
          : "border-gray-700 hover:border-gray-600 bg-gray-900/40 hover:bg-gray-800/40",
        disabled && "opacity-50 cursor-not-allowed"
      )}
    >
      <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-600/20 to-indigo-600/20 border border-violet-500/30 flex items-center justify-center">
        <CloudUpload className="w-8 h-8 text-violet-400" />
      </div>
      <div className="text-center">
        <p className="text-white font-semibold">Drop files here or click to browse</p>
        <p className="text-sm text-gray-400 mt-1">PDF, TXT, MD, DOCX, CSV · Up to 50MB</p>
      </div>
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        multiple={multiple}
        className="hidden"
        onChange={(e) => {
          const files = Array.from(e.target.files || []);
          if (files.length > 0) onFilesSelected(files);
          e.target.value = "";
        }}
      />
    </div>
  );
}
