"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth";
import { api } from "@/lib/api";

export default function SettingsPage() {
  const { token, user, hydrate } = useAuthStore();
  const [integrations, setIntegrations] = useState<Array<{ id: string; type: string; status: string }>>([]);
  const [businessId, setBusinessId] = useState<string | null>(null);

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
          const data = await api.getIntegrations(token, businesses[0].id);
          setIntegrations(data as Array<{ id: string; type: string; status: string }>);
        }
      } catch (err) {
        console.error(err);
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
      <header className="bg-white border-b">
        <div className="container mx-auto px-4 py-4 flex items-center gap-4">
          <Link href="/dashboard" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">T</span>
            </div>
            <span className="font-bold">Teqa</span>
          </Link>
          <span className="text-muted-foreground">/</span>
          <span className="font-medium">Settings</span>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-3xl">
        {/* Profile */}
        <section className="bg-white rounded-xl p-6 border mb-6">
          <h2 className="text-lg font-semibold mb-4">Profile</h2>
          <div className="space-y-3">
            <div>
              <label className="text-sm text-muted-foreground">Name</label>
              <p className="font-medium">{user?.full_name}</p>
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Email</label>
              <p className="font-medium">{user?.email}</p>
            </div>
          </div>
        </section>

        {/* Integrations */}
        <section className="bg-white rounded-xl p-6 border mb-6">
          <h2 className="text-lg font-semibold mb-4">Connected Integrations</h2>
          {integrations.length === 0 ? (
            <p className="text-muted-foreground text-sm">No integrations connected yet.</p>
          ) : (
            <div className="space-y-3">
              {integrations.map((int) => (
                <div key={int.id} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="text-lg">
                      {int.type === "shopify" ? "🛒" : int.type === "paymob" ? "💳" : "📄"}
                    </span>
                    <span className="font-medium capitalize">{int.type}</span>
                  </div>
                  <span
                    className={`text-xs px-2 py-1 rounded-full ${
                      int.status === "connected"
                        ? "bg-green-100 text-green-700"
                        : "bg-red-100 text-red-700"
                    }`}
                  >
                    {int.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* WhatsApp */}
        <section className="bg-white rounded-xl p-6 border">
          <h2 className="text-lg font-semibold mb-4">WhatsApp Delivery</h2>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Daily report delivery</p>
              <p className="font-medium">Every day at 8:00 AM (Cairo)</p>
            </div>
            <span className="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full">
              Active
            </span>
          </div>
        </section>
      </main>
    </div>
  );
}
