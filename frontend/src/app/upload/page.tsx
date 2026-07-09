"use client";

import { useCallback, useEffect, useState } from "react";
import { uploadApi, type Paper } from "@/api/upload";
import { parserApi, type ParseResult } from "@/api/parser";
import { chunkApi, type ChunkStats } from "@/api/chunk";
import { useAuthGuard } from "@/hooks/useAuthGuard";

export default function UploadPage() {
  const { isReady } = useAuthGuard();
  const [papers, setPapers] = useState<Paper[]>([]);
  const [parseResults, setParseResults] = useState<Record<number, ParseResult>>({});
  const [chunkResults, setChunkResults] = useState<Record<number, ChunkStats>>({});
  const [parsingId, setParsingId] = useState<number | null>(null);
  const [chunkingId, setChunkingId] = useState<number | null>(null);
  const [parseErrors, setParseErrors] = useState<Record<number, string>>({});
  const [chunkErrors, setChunkErrors] = useState<Record<number, string>>({});
  const [error, setError] = useState("");
  const [progress, setProgress] = useState(0);
  const [uploading, setUploading] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  const loadPapers = useCallback(async () => {
    try {
      const response = await uploadApi.listPapers();
      setPapers(response.data.papers);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to load papers";
      setError(message);
    }
  }, []);

  useEffect(() => {
    if (!isReady) return;
    loadPapers();
  }, [isReady, loadPapers]);

  const validateFile = (file: File): string | null => {
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      return "Only PDF files are allowed";
    }
    if (file.size > 10 * 1024 * 1024) {
      return "File exceeds 10MB limit";
    }
    return null;
  };

  const handleUpload = async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setError("");
    setUploading(true);
    setProgress(0);

    try {
      await uploadApi.upload(file, setProgress);
      await loadPapers();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Upload failed";
      setError(message);
    } finally {
      setUploading(false);
      setProgress(0);
    }
  };

  const onFileSelected = (fileList: FileList | null) => {
    if (!fileList?.length) return;
    handleUpload(fileList[0]);
  };

  const onDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragOver(false);
    onFileSelected(event.dataTransfer.files);
  };

  const onDelete = async (paperId: number) => {
    try {
      await uploadApi.deletePaper(paperId);
      setParseResults((prev) => {
        const next = { ...prev };
        delete next[paperId];
        return next;
      });
      setChunkResults((prev) => {
        const next = { ...prev };
        delete next[paperId];
        return next;
      });
      await loadPapers();
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Delete failed";
      setError(message);
    }
  };

  const onParse = async (paperId: number) => {
    setParsingId(paperId);
    setParseErrors((prev) => {
      const next = { ...prev };
      delete next[paperId];
      return next;
    });

    try {
      const response = await parserApi.parse(paperId);
      setParseResults((prev) => ({ ...prev, [paperId]: response.data }));
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Parse failed";
      setParseErrors((prev) => ({ ...prev, [paperId]: message }));
    } finally {
      setParsingId(null);
    }
  };

  const onChunk = async (paperId: number) => {
    setChunkingId(paperId);
    setChunkErrors((prev) => {
      const next = { ...prev };
      delete next[paperId];
      return next;
    });

    try {
      const response = await chunkApi.generate(paperId);
      setChunkResults((prev) => ({ ...prev, [paperId]: response.data }));
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Chunk generation failed";
      setChunkErrors((prev) => ({ ...prev, [paperId]: message }));
    } finally {
      setChunkingId(null);
    }
  };

  if (!isReady) {
    return <div style={{ padding: 40, textAlign: "center" }}>Loading...</div>;
  }

  return (
    <div style={{ maxWidth: 900, margin: "40px auto", padding: 24 }}>
      <h1>Upload Papers</h1>

      {error && (
        <div data-testid="upload-error" style={{ color: "red", marginBottom: 12 }}>
          {error}
        </div>
      )}

      <div
        data-testid="upload-dropzone"
        onDragOver={(event) => {
          event.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={onDrop}
        style={{
          border: `2px dashed ${dragOver ? "#333" : "#aaa"}`,
          borderRadius: 8,
          padding: 32,
          textAlign: "center",
          marginBottom: 16,
        }}
      >
        <p>Drag and drop a PDF here</p>
        <input
          data-testid="upload-file-input"
          type="file"
          accept=".pdf,application/pdf"
          onChange={(event) => onFileSelected(event.target.files)}
          disabled={uploading}
        />
      </div>

      {uploading && (
        <div data-testid="upload-progress" style={{ marginBottom: 16 }}>
          Uploading... {progress}%
        </div>
      )}

      <h2>Uploaded Papers</h2>
      <ul data-testid="papers-list" style={{ listStyle: "none", padding: 0 }}>
        {papers.map((paper) => {
          const result = parseResults[paper.id];
          const chunkResult = chunkResults[paper.id];
          const parseError = parseErrors[paper.id];
          const chunkError = chunkErrors[paper.id];
          const isParsing = parsingId === paper.id;
          const isChunking = chunkingId === paper.id;

          return (
            <li
              key={paper.id}
              style={{ border: "1px solid #ddd", borderRadius: 8, padding: 16, marginBottom: 16 }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span>
                  {paper.original_filename} ({paper.file_size} bytes)
                </span>
                <div style={{ display: "flex", gap: 8 }}>
                  <button
                    data-testid={`parse-paper-${paper.id}`}
                    onClick={() => onParse(paper.id)}
                    disabled={isParsing || isChunking}
                  >
                    {isParsing ? "Parsing..." : "Parse"}
                  </button>
                  <button
                    data-testid={`chunk-paper-${paper.id}`}
                    onClick={() => onChunk(paper.id)}
                    disabled={isParsing || isChunking}
                  >
                    {isChunking ? "Chunking..." : "Generate Chunks"}
                  </button>
                  <button
                    data-testid={`delete-paper-${paper.id}`}
                    onClick={() => onDelete(paper.id)}
                  >
                    Delete
                  </button>
                </div>
              </div>

              {isParsing && (
                <div data-testid={`parse-progress-${paper.id}`} style={{ marginTop: 12, color: "#666" }}>
                  Parsing in progress...
                </div>
              )}

              {parseError && (
                <div data-testid={`parse-error-${paper.id}`} style={{ marginTop: 12, color: "red" }}>
                  {parseError}
                </div>
              )}

              {isChunking && (
                <div data-testid={`chunk-progress-${paper.id}`} style={{ marginTop: 12, color: "#666" }}>
                  Generating chunks...
                </div>
              )}

              {chunkError && (
                <div data-testid={`chunk-error-${paper.id}`} style={{ marginTop: 12, color: "red" }}>
                  {chunkError}
                </div>
              )}

              {chunkResult && (
                <div data-testid={`chunk-result-${paper.id}`} style={{ marginTop: 16 }}>
                  <h4 style={{ margin: "0 0 8px" }}>Chunk Statistics</h4>
                  <p><strong>Chunks:</strong> {chunkResult.chunks_created}</p>
                  <p><strong>Average size:</strong> {chunkResult.average_chunk_size} chars</p>
                  <p><strong>Largest:</strong> {chunkResult.largest_chunk} chars</p>
                  <p><strong>Smallest:</strong> {chunkResult.smallest_chunk} chars</p>
                  <p><strong>First chunk preview:</strong></p>
                  <pre style={{ whiteSpace: "pre-wrap", fontSize: 12 }}>{chunkResult.first_chunk || "N/A"}</pre>
                  <p><strong>Last chunk preview:</strong></p>
                  <pre style={{ whiteSpace: "pre-wrap", fontSize: 12 }}>{chunkResult.last_chunk || "N/A"}</pre>
                </div>
              )}

              {result && (
                <div data-testid={`parse-result-${paper.id}`} style={{ marginTop: 16 }}>
                  <h4 style={{ margin: "0 0 8px" }}>Parsed Metadata</h4>
                  <p><strong>Title:</strong> {result.title || "N/A"}</p>
                  <p><strong>Authors:</strong> {result.authors.length ? result.authors.join(", ") : "N/A"}</p>
                  <p><strong>Pages:</strong> {result.pages}</p>
                  <p><strong>Abstract:</strong> {result.abstract || "N/A"}</p>
                  {result.references.length > 0 && (
                    <p><strong>References:</strong> {result.references.length} found</p>
                  )}
                  <p style={{ color: "#666", fontSize: 13 }}>
                    Text extracted: {result.text.length} characters
                  </p>
                </div>
              )}
            </li>
          );
        })}
      </ul>
      {!papers.length && <p>No papers uploaded yet.</p>}
    </div>
  );
}
