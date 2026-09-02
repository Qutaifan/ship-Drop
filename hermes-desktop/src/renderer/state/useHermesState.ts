import { create } from "zustand";

export interface IntelligenceRing {
  name: string;
  value: any;
  status: "GREEN" | "YELLOW" | "ORANGE" | "RED" | "BLUE";
}

export interface TelemetryOverview {
  timestamp: string;
  system_state: string;
  intelligence_rings: {
    ring_1_stability: IntelligenceRing;
    ring_2_volatility: IntelligenceRing;
    ring_3_lifecycle: IntelligenceRing;
    ring_4_network: IntelligenceRing;
    ring_5_economic: IntelligenceRing;
  };
  system_vitals: {
    monthly_gross_revenue: number;
    monthly_net_margin: number;
    blended_cogs_multiple: number;
    autonomous_window_active: boolean;
    active_nodes: number;
  };
}

export interface HermesState {
  apiBaseUrl: string;
  isPolling: boolean;
  overview: TelemetryOverview | null;
  skus: any[];
  networkGraph: any | null;
  portfolio: any | null;
  activeWindows: any[];
  replayLogs: any[];
  selectedSupplier: any | null;
  error: string | null;

  setApiBaseUrl: (url: string) => void;
  fetchTelemetry: () => Promise<void>;
  grantAutonomousWindow: (hours: number, cap: number) => Promise<void>;
  revokeAutonomousWindow: (windowId: string) => Promise<void>;
  selectSupplier: (supplierId: string) => Promise<void>;
}

export const useHermesState = create<HermesState>((set, get) => ({
  apiBaseUrl: "http://127.0.0.1:8080/api/v1",
  isPolling: false,
  overview: null,
  skus: [],
  networkGraph: null,
  portfolio: null,
  activeWindows: [],
  replayLogs: [],
  selectedSupplier: null,
  error: null,

  setApiBaseUrl: (url: string) => set({ apiBaseUrl: url }),

  fetchTelemetry: async () => {
    const { apiBaseUrl } = get();
    try {
      const [ovRes, skuRes, graphRes, portRes, winRes, logRes] = await Promise.all([
        fetch(`${apiBaseUrl}/telemetry/overview`).catch(() => null),
        fetch(`${apiBaseUrl}/sourcing/skus`).catch(() => null),
        fetch(`${apiBaseUrl}/network/graph`).catch(() => null),
        fetch(`${apiBaseUrl}/economic/portfolio`).catch(() => null),
        fetch(`${apiBaseUrl}/governance/windows`).catch(() => null),
        fetch(`${apiBaseUrl}/telemetry/replay`).catch(() => null),
      ]);

      const overview = ovRes && ovRes.ok ? await ovRes.json() : null;
      const skus = skuRes && skuRes.ok ? (await skuRes.json()).skus : [];
      const networkGraph = graphRes && graphRes.ok ? await graphRes.json() : null;
      const portfolio = portRes && portRes.ok ? await portRes.json() : null;
      const activeWindows = winRes && winRes.ok ? (await winRes.json()).active_windows : [];
      const replayLogs = logRes && logRes.ok ? (await logRes.json()).events : [];

      set({
        overview,
        skus,
        networkGraph,
        portfolio,
        activeWindows,
        replayLogs,
        error: null,
      });
    } catch (err: any) {
      set({ error: err.message });
    }
  },

  grantAutonomousWindow: async (hours: number, cap: number) => {
    const { apiBaseUrl, fetchTelemetry } = get();
    await fetch(`${apiBaseUrl}/governance/window/grant`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ actor: "Founder", hours, spend_cap: cap }),
    });
    await fetchTelemetry();
  },

  revokeAutonomousWindow: async (windowId: string) => {
    const { apiBaseUrl, fetchTelemetry } = get();
    await fetch(`${apiBaseUrl}/governance/window/revoke`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ window_id: windowId }),
    });
    await fetchTelemetry();
  },

  selectSupplier: async (supplierId: string) => {
    const { apiBaseUrl } = get();
    try {
      const res = await fetch(`${apiBaseUrl}/sourcing/supplier/${supplierId}`);
      if (res.ok) {
        const data = await res.json();
        set({ selectedSupplier: data });
      }
    } catch (e) {
      console.error(e);
    }
  },
}));
