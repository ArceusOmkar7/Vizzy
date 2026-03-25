import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export { BASE_URL }

export const apiClient = axios.create({ baseURL: BASE_URL })

export interface UploadResponse {
  session_id: string
  filename: string
  rows: number
  columns: number
  memory_mb: number
  null_count: number
}

export interface SessionInfo {
  session_id: string
  filename: string
  rows: number
  columns: number
  memory_mb: number
  null_count: number
}

export interface OverviewResponse {
  quality_score: number
  quality_grade: string
  total_rows: number
  total_columns: number
  total_nulls: number
  duplicate_rows: number
  numeric_columns: number
  categorical_columns: number
  datetime_columns: number
  column_summaries: ColumnSummary[]
}

export interface ColumnSummary {
  name: string
  dtype: string
  null_count: number
  null_pct: number
  unique_count: number
  sample_values: string[]
}

export interface NullsResponse {
  total_nulls: number
  columns_with_nulls: number
  null_columns: NullColumn[]
}

export interface NullColumn {
  column: string
  null_count: number
  null_pct: number
}

export interface DistributionData {
  column: string
  bins: number[]
  counts: number[]
  min: number
  q1: number
  median: number
  q3: number
  max: number
  mean: number
  std: number
  skewness: number
  kurtosis: number
}

export interface DistributionsResponse {
  columns: string[]
  distributions: Record<string, DistributionData>
}

export interface CorrelationsResponse {
  columns: string[]
  matrix: number[][]
  top_pairs: CorrelationPair[]
}

export interface CorrelationPair {
  col1: string
  col2: string
  correlation: number
}

export interface CategoryData {
  value: string
  count: number
  pct: number
}

export interface CategoriesResponse {
  columns: string[]
  categories: Record<string, CategoryData[]>
}

export interface TimeSeriesResponse {
  datetime_columns: string[]
  has_datetime: boolean
  series: Record<string, TimePoint[]>
  value_columns: string[]
}

export interface TimePoint {
  timestamp: string
  value: number
}

export interface PreprocessingSuggestion {
  priority: 'high' | 'medium' | 'low'
  category: string
  description: string
  code_snippet: string
}

export interface PreprocessingResponse {
  suggestions: PreprocessingSuggestion[]
}

export interface QueryResponse {
  question: string
  answer: string
  session_id: string
}

export const uploadFile = (file: File) => {
  const form = new FormData()
  form.append('file', file)
  return apiClient.post<UploadResponse>('/api/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const getSession = (sessionId: string) =>
  apiClient.get<SessionInfo>(`/api/session/${sessionId}`)

export const getOverview = (sessionId: string) =>
  apiClient.get<OverviewResponse>(`/api/analyze/${sessionId}/overview`)

export const getNulls = (sessionId: string) =>
  apiClient.get<NullsResponse>(`/api/analyze/${sessionId}/nulls`)

export const getDistributions = (sessionId: string) =>
  apiClient.get<DistributionsResponse>(`/api/analyze/${sessionId}/distributions`)

export const getCorrelations = (sessionId: string) =>
  apiClient.get<CorrelationsResponse>(`/api/analyze/${sessionId}/correlations`)

export const getCategories = (sessionId: string) =>
  apiClient.get<CategoriesResponse>(`/api/analyze/${sessionId}/categories`)

export const getTimeSeries = (sessionId: string) =>
  apiClient.get<TimeSeriesResponse>(`/api/analyze/${sessionId}/timeseries`)

export const getPreprocessing = (sessionId: string) =>
  apiClient.get<PreprocessingResponse>(`/api/analyze/${sessionId}/preprocessing`)

export const exportPdf = (sessionId: string) =>
  apiClient.get(`/api/export/${sessionId}/pdf`, { responseType: 'blob' })

export const postQuery = (sessionId: string, question: string) =>
  apiClient.post<QueryResponse>(`/api/query/${sessionId}`, { question })
