export interface AskRequest {
  question: string;
  additional_context?: string;
  temperature?: number;
}

export interface SourceChunk {
  label: string;
  chapter?: string;
  book_title?: string;
  file_name?: string;
  source_path?: string;
  text: string;
}

export interface AskResponse {
  answer: string;
  citations: string[];
  sources: SourceChunk[];
}
