import type { APIResponse } from "@/types";
import { apiFetch } from "./auth";

export interface ParseResult {
  paper_id: number;
  title: string;
  authors: string[];
  abstract: string;
  pages: number;
  metadata: Record<string, string>;
  references: string[];
  text: string;
  status: string;
}

export const parserApi = {
  parse: (paperId: number): Promise<APIResponse<ParseResult>> =>
    apiFetch<ParseResult>("/parse", {
      method: "POST",
      body: JSON.stringify({ paper_id: paperId }),
    }),
};
