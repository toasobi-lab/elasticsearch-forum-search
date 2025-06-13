export interface Post {
  id: string;
  title: string;
  content: string;
  tags: string[];
  created_at: string;
}

export interface SearchResponse {
  total: number;
  hits: Post[];
  page: number;
  size: number;
  took_ms?: number;
} 