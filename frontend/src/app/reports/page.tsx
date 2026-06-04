"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth";
import { api } from "@/lib/api";

interface Report {
  id: string;
  report_date: string;
  status: string;
  revenue: number;
  orders_count: number;
  avg_order_value: number;
  revenue_growth_pct: number | null;
  top_product: string | null;
  ai_summary: string | null;
  ai_insight: string | null;
  ai_recommendation: string | null;
}

export default function ReportsPage() {
  const { token, hydrate } = useAuthStore();
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    if (!token) return;

    const fetchReports = async () => {
      try {
        const businesses = await api.getBusinesses(token);
        if (businesses.length > 0) {
          const data = await api.getReports(token, businesses[0].id);
          setReports(data as Report[]);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
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
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/dashboard" className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">T</span>
              </div>
              <span className="font-bold">Teqa</span>
            </Link>
            <span className="text-muted-foreground">/</span>
            <span className="font-medium">Reports</span>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold">Report History</h1>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="bg-white rounded-xl p-6 border animate-pulse h-24" />
            ))}
          </div>
        ) : reports.length === 0 ? (
          <div className="bg-white rounded-xl p-8 border text-center">
            <p className="text-muted-foreground">
              No reports yet. Reports are generated daily at 8 AM.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {reports.map((report) => (
              <div key={report.id} className="bg-white rounded-xl p-6 border">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <p className="font-medium">{report.report_date}</p>
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full ${
                        report.status === "delivered"
                          ? "bg-green-100 text-green-700"
                          : report.status === "generated"
                            ? "bg-blue-100 text-blue-700"
                            : "bg-yellow-100 text-yellow-700"
                      }`}
                    >
                      {report.status}
                    </span>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold">EGP {report.revenue.toLocaleString()}</p>
                    <p className="text-sm text-muted-foreground">
                      {report.orders_count} orders
                    </p>
                  </div>
                </div>
                {report.ai_insight && (
                  <p className="text-sm text-muted-foreground mt-2 border-t pt-3">
                    💡 {report.ai_insight}
                  </p>
                )}
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
