"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth";
import { api } from "@/lib/api";

const PLANS = [
  {
    id: "starter",
    name: "Starter",
    price: 499,
    features: ["1 integration", "Daily WhatsApp reports", "Basic AI insights", "Email support"],
  },
  {
    id: "growth",
    name: "Growth",
    price: 999,
    features: ["3 integrations", "Priority AI insights", "Report history", "Priority support"],
    popular: true,
  },
  {
    id: "pro",
    name: "Pro",
    price: 2499,
    features: [
      "Unlimited integrations",
      "Advanced analytics",
      "API access",
      "Dedicated support",
      "Custom reports",
    ],
  },
];

export default function BillingPage() {
  const { token, hydrate } = useAuthStore();
  const [currentPlan, setCurrentPlan] = useState<string | null>(null);
  const [businessId, setBusinessId] = useState<string | null>(null);
  const [loading, setLoading] = useState<string | null>(null);

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
          const sub = await api.getSubscription(token, businesses[0].id);
          setCurrentPlan((sub as { plan: string | null }).plan);
        }
      } catch (err) {
        console.error(err);
      }
    };

    fetchData();
  }, [token]);

  const handleSubscribe = async (plan: string) => {
    if (!token || !businessId) return;
    setLoading(plan);
    try {
      const result = await api.subscribe(token, businessId, plan);
      window.location.href = result.checkout_url;
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to start subscription");
    } finally {
      setLoading(null);
    }
  };

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
          <span className="font-medium">Billing</span>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-2">Subscription Plans</h1>
        <p className="text-muted-foreground mb-8">Choose the plan that fits your business</p>

        <div className="grid md:grid-cols-3 gap-6 max-w-5xl">
          {PLANS.map((plan) => (
            <div
              key={plan.id}
              className={`bg-white rounded-xl p-6 border ${
                plan.popular ? "border-primary shadow-lg" : ""
              } ${currentPlan === plan.id ? "ring-2 ring-primary" : ""}`}
            >
              {plan.popular && (
                <span className="text-xs bg-primary text-primary-foreground px-2 py-1 rounded-full">
                  Most Popular
                </span>
              )}
              {currentPlan === plan.id && (
                <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full ml-2">
                  Current Plan
                </span>
              )}
              <h3 className="text-xl font-semibold mt-3">{plan.name}</h3>
              <p className="mt-2">
                <span className="text-3xl font-bold">EGP {plan.price.toLocaleString()}</span>
                <span className="text-muted-foreground">/month</span>
              </p>
              <ul className="mt-6 space-y-3">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm">
                    <span className="text-primary">•</span> {f}
                  </li>
                ))}
              </ul>
              <button
                onClick={() => handleSubscribe(plan.id)}
                disabled={currentPlan === plan.id || loading === plan.id}
                className="mt-6 w-full bg-primary text-primary-foreground py-2 rounded-lg font-medium hover:opacity-90 disabled:opacity-50"
              >
                {loading === plan.id
                  ? "Processing..."
                  : currentPlan === plan.id
                    ? "Current Plan"
                    : "Subscribe"}
              </button>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
