"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/store/auth";

const INDUSTRIES = [
  "Fashion & Retail",
  "Electronics",
  "Pharmacy",
  "Cafe & Restaurant",
  "Grocery",
  "Beauty & Cosmetics",
  "E-commerce",
  "Other",
];

export default function OnboardingPage() {
  const router = useRouter();
  const { token } = useAuthStore();
  const [step, setStep] = useState(1);
  const [businessName, setBusinessName] = useState("");
  const [industry, setIndustry] = useState("");
  const [whatsappNumber, setWhatsappNumber] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      router.push("/login");
      return;
    }
    setError("");
    setLoading(true);

    try {
      await api.createBusiness(token, {
        name: businessName,
        industry,
        whatsapp_number: whatsappNumber,
        country: "Egypt",
        currency: "EGP",
        timezone: "Africa/Cairo",
      });
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create business");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 px-4">
      <div className="w-full max-w-lg bg-white rounded-2xl shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold">Set up your business</h1>
          <p className="text-muted-foreground mt-1">
            Step {step} of 2 — {step === 1 ? "Business details" : "Connect data"}
          </p>
          <div className="flex gap-2 justify-center mt-4">
            <div className={`h-1 w-16 rounded ${step >= 1 ? "bg-primary" : "bg-muted"}`} />
            <div className={`h-1 w-16 rounded ${step >= 2 ? "bg-primary" : "bg-muted"}`} />
          </div>
        </div>

        {step === 1 && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setStep(2);
            }}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium mb-1">Business Name</label>
              <input
                type="text"
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                placeholder="Hassan Fashion Store"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Industry</label>
              <select
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                required
              >
                <option value="">Select industry...</option>
                {INDUSTRIES.map((ind) => (
                  <option key={ind} value={ind}>
                    {ind}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">WhatsApp Number</label>
              <input
                type="tel"
                value={whatsappNumber}
                onChange={(e) => setWhatsappNumber(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-primary/20 focus:border-primary outline-none"
                placeholder="+201001234567"
                required
              />
            </div>

            <button
              type="submit"
              className="w-full bg-primary text-primary-foreground py-2 rounded-lg font-medium hover:opacity-90"
            >
              Continue
            </button>
          </form>
        )}

        {step === 2 && (
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="bg-destructive/10 text-destructive text-sm p-3 rounded-lg">
                {error}
              </div>
            )}

            <p className="text-sm text-muted-foreground">
              Connect a data source to start receiving reports. You can add more later.
            </p>

            <div className="grid gap-3">
              {[
                { name: "Shopify", desc: "Connect your Shopify store", icon: "🛒" },
                { name: "Paymob", desc: "Connect Paymob payments", icon: "💳" },
                { name: "CSV Upload", desc: "Upload transaction data", icon: "📄" },
              ].map((source) => (
                <button
                  key={source.name}
                  type="button"
                  className="flex items-center gap-3 p-4 border rounded-lg hover:border-primary hover:bg-primary/5 text-left transition"
                >
                  <span className="text-2xl">{source.icon}</span>
                  <div>
                    <p className="font-medium">{source.name}</p>
                    <p className="text-xs text-muted-foreground">{source.desc}</p>
                  </div>
                </button>
              ))}
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="flex-1 border py-2 rounded-lg font-medium hover:bg-secondary"
              >
                Back
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-primary text-primary-foreground py-2 rounded-lg font-medium hover:opacity-90 disabled:opacity-50"
              >
                {loading ? "Setting up..." : "Complete Setup"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
