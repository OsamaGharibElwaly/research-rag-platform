import type { APIResponse } from "@/types";
import { apiFetch } from "./auth";

export interface IndexStats {
  paper_id: number;
  engine: string;
  vector_count: number;
  dimension: number;
  vectors_indexed: number;
  index_path: string;
  index_size_bytes: number;
  bit_width: number;
  status: string;
  processing_time_ms: number;
}

export interface SearchHit {
  chunk_id: number;
  score: number;
  paper_id: number;
  chunk_index: number;
  chunk_text: string;
}

export interface SearchResult {
  paper_id: number;
  top_k: number;
  engine: string;
  results: SearchHit[];
  search_latency_ms: number;
}

export const vectorApi = {
  buildIndex: (paperId: number, rebuild = false): Promise<APIResponse<IndexStats>> =>
    apiFetch<IndexStats>("/index", {
      method: "POST",
      body: JSON.stringify({ paper_id: paperId, rebuild }),
    }),

  search: (
    paperId: number,
    queryEmbedding: number[],
    topK = 5
  ): Promise<APIResponse<SearchResult>> =>
    apiFetch<SearchResult>("/search", {
      method: "POST",
      body: JSON.stringify({
        paper_id: paperId,
        query_embedding: queryEmbedding,
        top_k: topK,
      }),
    }),
};
