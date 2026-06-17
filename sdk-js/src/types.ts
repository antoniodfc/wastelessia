export interface Tags {
  team?: string;
  feature?: string;
  env?: string;
  client?: string;
}

export interface TrackEvent {
  timestamp: string;
  model: string;
  tokens_in: number;
  tokens_out: number;
  cost_usd: number;
  duration_ms: number;
  success: boolean;
  tags: Tags;
}
