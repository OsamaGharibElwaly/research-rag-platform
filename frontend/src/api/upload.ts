import type { APIResponse } from "@/types";
import { apiFetch } from "./auth";

export interface Paper {
  id: number;
  user_id: number;
  filename: string;
  original_filename: string;
  file_size: number;
  content_type: string;
  created_at: string;
}

export const uploadApi = {
  upload: async (
    file: File,
    onProgress?: (percent: number) => void
  ): Promise<APIResponse<{ paper: Paper }>> => {
    const formData = new FormData();
    formData.append("file", file);

    onProgress?.(10);

    const response = await apiFetch<{ paper: Paper }>("/upload", {
      method: "POST",
      headers: {},
      body: formData,
    });

    onProgress?.(100);
    return response;
  },

  listPapers: (): Promise<APIResponse<{ papers: Paper[] }>> =>
    apiFetch<{ papers: Paper[] }>("/papers"),

  deletePaper: (paperId: number): Promise<APIResponse<{ paper_id: number }>> =>
    apiFetch<{ paper_id: number }>(`/paper/${paperId}`, { method: "DELETE" }),
};
