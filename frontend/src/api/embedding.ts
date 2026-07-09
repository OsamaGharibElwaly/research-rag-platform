import type { APIResponse } from "@/types";
import { apiFetch } from "./auth";

export interface EmbedStats {
  paper_id: number;
  chunks_embedded: number;
  embedding_dimension: number;
  model: string;
  processing_time_ms: number;
}

export const embeddingApi = {
  generate: (paperId: number): Promise<APIResponse<EmbedStats>> =>
    apiFetch<EmbedStats>("/embed", {
      method: "POST",
      body: JSON.stringify({ paper_id: paperId }),
    }),
};
