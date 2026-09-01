/**
 * Hermes Sourcing Ranker (TypeScript implementation)
 * Evaluates, tiers, and prioritizes competing suppliers in real-time.
 */

export type SupplierTier =
  | "PREFERRED_DOMESTIC"
  | "QUALIFIED_BACKUP"
  | "HIGH_RISK_MONITOR"
  | "REJECTED_UNVIABLE";

export type RankingMetric =
  | "stability_score"
  | "net_margin"
  | "lead_time"
  | "cogs_multiple";

export interface SupplierMetrics {
  landed_cost: number;
  projected_net_margin: number;
  cogs_multiple: number;
  stock_level: number;
  lead_days_max: number;
  warehouse_country: string;
  warehouse_type: "domestic" | "international_transit";
  defect_rate_percent: number;
}

export interface RankedSupplier {
  rank: number;
  supplier_id: string;
  supplier_name: string;
  stability_score: number;
  actionability_score: number;
  metrics: SupplierMetrics;
  tier: SupplierTier;
  canary_eligible: boolean;
  reconciliation_status: "MARGIN_STABLE" | "MARGIN_COMPRESSED";
}

export interface SourcingRankerResult {
  $schema?: string;
  version: "1.0.0";
  candidate_id: string;
  ranked_at: string;
  evaluation_market: "US" | "EU";
  primary_ranking_metric: RankingMetric;
  suppliers: RankedSupplier[];
  selected_supplier_id: string;
  recommended_allocation_percent: number;
  ranking_notes?: string;
}

export function computeStabilityScore(
  priceDriftPercent: number,
  stockLevel: number,
  defectRatePercent: number,
  warehouseType: "domestic" | "international_transit"
): number {
  const pPrice = 0.4 * (1.0 - Math.min(1.0, Math.abs(priceDriftPercent)));
  const pStock = 0.3 * Math.min(1.0, stockLevel / 200.0);
  const pDefect = 0.2 * Math.max(0.0, 1.0 - defectRatePercent / 10.0);
  const pDomestic = warehouseType === "domestic" ? 0.1 : 0.0;
  return Math.round((pPrice + pStock + pDefect + pDomestic) * 100) / 100;
}

export function calculateActionabilityScore(
  stabilityScore: number,
  marginDelta: number,
  retailPrice: number,
  severity: "HIGH" | "MEDIUM" | "LOW" = "MEDIUM"
): number {
  const sevWeight = severity === "HIGH" ? 1.2 : severity === "LOW" ? 0.7 : 1.0;
  const stabilityPenalty = Math.max(0.0, 1.0 - stabilityScore);
  const marginRatio = retailPrice > 0 ? Math.abs(marginDelta) / retailPrice : 0.0;
  const rawScore = sevWeight * stabilityPenalty * 100.0 * (1.0 + marginRatio);
  return Math.round(Math.min(100.0, Math.max(0.0, rawScore)) * 10) / 10;
}

export function determineSupplierTier(
  stability: number,
  metrics: SupplierMetrics,
  isDomestic: boolean,
  reconciliationStatus: "MARGIN_STABLE" | "MARGIN_COMPRESSED"
): SupplierTier {
  if (
    metrics.stock_level < 30 ||
    metrics.projected_net_margin < 10.0 ||
    stability < 0.4 ||
    reconciliationStatus === "MARGIN_COMPRESSED"
  ) {
    return "REJECTED_UNVIABLE";
  }

  if (
    isDomestic &&
    stability >= 0.85 &&
    metrics.lead_days_max <= 5 &&
    metrics.defect_rate_percent <= 2.0 &&
    metrics.projected_net_margin >= 12.0 &&
    metrics.stock_level >= 100
  ) {
    return "PREFERRED_DOMESTIC";
  }

  if (isDomestic && stability >= 0.75 && metrics.lead_days_max <= 7 && metrics.projected_net_margin >= 10.0) {
    return "QUALIFIED_BACKUP";
  }

  return "HIGH_RISK_MONITOR";
}
