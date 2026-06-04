"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth";
import { api } from "@/lib/api";

interface DashboardData {
  total_revenue_today: number;
  total_orders_today: number;
  avg_order_value: number;
  revenue_growth_pct: number | null;
  reports_delivered: number;
  active_integrations: number;
  subscription_plan: string | null;
  subscription_status: string | null;
}

export default function DashboardPage() {
  const { token, user, hydrate, logout } = useAuthStore();
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  const [businessId, setBusinessId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (!token) return;

    const fetchData = async () => {
      try {
        const businesses = await api.getBusinesses(token);
        if (businesses.length > 0) {
          setBusinessId(businesses[0].id);
          const data = await api.getDashboard(token, businesses[0].id);
          setDashboard(data as DashboardData);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [token]);

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Link href="/login" className="text-primary hover:underline">
          Please sign in
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Nav */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <span className="font-bold">Teqa</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/reports" className="text-sm text-muted-foreground hover:text-foreground">
              Reports
            </Link>
            <Link href="/settings" className="text-sm text-muted-foreground hover:text-foreground">
              Settings
            </Link>
            <Link href="/billing" className="text-sm text-muted-foreground hover:text-foreground">
              Billing
            </Link>
            <button onClick={logout} className="text-sm text-destructive hover:underline">
              Logout
            </button>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-2">
          Good morning, {user?.full_name?.split(" ")[0] || "there"} 👋
        </h1>
        <p className="text-muted-foreground mb-8">Here&apos;s your business overview</p>

        {loading ? (
          <div className="grid md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl p-6 border animate-pulse h-28" />
            ))}
          </div>
        ) : dashboard ? (
          <>
            {/* Metrics */}
            <div className="grid md:grid-cols-4 gap-4 mb-8">
              <MetricCard
                label="Yesterday Revenue"
                value={`EGP ${dashboard.total_revenue_today.toLocaleString()}`}
                change={dashboard.revenue_growth_pct}
              />
              <MetricCard label="Orders" value={String(dashboard.total_orders_today)} />
              <MetricCard
                label="Avg Order Value"
                value={`EGP ${dashboard.avg_order_value.toLocaleString()}`}
              />
              <MetricCard label="Reports Delivered" value={String(dashboard.reports_delivered)} />
            </div>

            {/* Status */}
            <div className="grid md:grid-cols-3 gap-4">
              <div className="bg-white rounded-xl p-6 border">
                <h3 className="font-medium text-sm text-muted-foreground mb-2">Integrations</h3>
                <p className="text-2xl font-bold">{dashboard.active_integrations} connected</p>
                <Link
                  href="/settings"
                  className="text-sm text-primary hover:underline mt-2 inline-block"
                >
                  Manage →
                </Link>
              </div>
              <div className="bg-white rounded-xl p-6 border">
                <h3 className="font-medium text-sm text-muted-foreground mb-2">Subscription</h3>
                <p className="text-2xl font-bold capitalize">
                  {dashboard.subscription_plan || "None"}
                </p>
                <p className="text-sm text-muted-foreground capitalize">
                  {dashboard.subscription_status || "inactive"}
                </p>
              </div>
              <div className="bg-white rounded-xl p-6 border">
                <h3 className="font-medium text-sm text-muted-foreground mb-2">WhatsApp Reports</h3>
                <p className="text-sm text-muted-foreground">Daily at 8:00 AM Cairo time</p>
                <span className="inline-block mt-2 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                  Active
                </span>
              </div>
            </div>
          </>
        ) : (
          <div className="bg-white rounded-xl p-8 border text-center">
            <p className="text-muted-foreground">
              No business found.{" "}
              <Link href="/onboarding" className="text-primary hover:underline">
                Complete onboarding
              </Link>
            </p>
          </div>
        )}
      </main>
    </div>
  );
}

function MetricCard({
  label,
  value,
  change,
}: {
  label: string;
  value: string;
  change?: number | null;
}) {
  return (
    <div className="bg-white rounded-xl p-6 border">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className="text-2xl font-bold mt-1">{value}</p>
      {change !== undefined && change !== null && (
        <p className={`text-sm mt-1 ${change >= 0 ? "text-green-600" : "text-red-600"}`}>
          {change >= 0 ? "+" : ""}
          {change.toFixed(1)}% vs prev day
        </p>
      )}
    </div>
  );
}
