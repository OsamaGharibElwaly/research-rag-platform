import type { APIResponse } from "@/types";
import { apiFetch } from "./auth";

export interface ChunkStats {
  paper_id: number;
  chunks_created: number;
  average_chunk_size: number;
  largest_chunk: number;
  smallest_chunk: number;
  first_chunk: string;
  last_chunk: string;
}

export const chunkApi = {
  generate: (paperId: number): Promise<APIResponse<ChunkStats>> =>
    apiFetch<ChunkStats>("/chunk", {
      method: "POST",
      body: JSON.stringify({ paper_id: paperId }),
    }),
};
