import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      {/* Header */}
      <header className="container mx-auto px-4 py-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">T</span>
          </div>
          <span className="text-xl font-bold">Teqa</span>
        </div>
        <nav className="hidden md:flex items-center gap-6">
          <Link href="#features" className="text-muted-foreground hover:text-foreground">
            Features
          </Link>
          <Link href="#pricing" className="text-muted-foreground hover:text-foreground">
            Pricing
          </Link>
          <Link href="/login" className="text-muted-foreground hover:text-foreground">
            Login
          </Link>
          <Link
            href="/signup"
            className="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90"
          >
            Get Started
          </Link>
        </nav>
      </header>

      {/* Hero */}
      <section className="container mx-auto px-4 py-20 text-center">
        <h1 className="text-4xl md:text-6xl font-bold tracking-tight max-w-4xl mx-auto">
          Your AI Business Analyst,{" "}
          <span className="text-primary">Delivered via WhatsApp</span>
        </h1>
        <p className="mt-6 text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
          Every morning at 8 AM, get a complete AI summary of your business performance.
          No dashboards. No spreadsheets. Just actionable insights.
        </p>
        <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/signup"
            className="bg-primary text-primary-foreground px-8 py-3 rounded-lg text-lg font-medium hover:opacity-90"
          >
            Start Free Trial
          </Link>
          <Link
            href="#demo"
            className="border border-border px-8 py-3 rounded-lg text-lg font-medium hover:bg-secondary"
          >
            See Demo Report
          </Link>
        </div>
      </section>

      {/* WhatsApp Preview */}
      <section id="demo" className="container mx-auto px-4 py-16">
        <div className="max-w-md mx-auto bg-[#e5ddd5] rounded-2xl p-6 shadow-xl">
          <div className="bg-white rounded-lg p-4 shadow-sm space-y-2 text-sm">
            <p className="font-medium">Good Morning Ahmed ☀️</p>
            <p className="text-muted-foreground mt-3">Yesterday Revenue:</p>
            <p className="text-2xl font-bold">EGP 18,450</p>
            <p className="text-muted-foreground mt-3">Orders:</p>
            <p className="font-medium">52 (+12%)</p>
            <p className="text-muted-foreground mt-3">Average Order Value:</p>
            <p className="font-medium">EGP 355</p>
            <p className="text-muted-foreground mt-3">Top Product:</p>
            <p className="font-medium">Black Hoodie</p>
            <p className="text-muted-foreground mt-3">AI Insight:</p>
            <p className="font-medium">
              Revenue increased because repeat customers purchased 23% more than yesterday.
            </p>
            <p className="text-muted-foreground mt-3">Recommendation:</p>
            <p className="font-medium">Restock Black Hoodie within 2 days.</p>
            <p className="mt-4 text-muted-foreground italic">— Teqa</p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">
          Everything you need to understand your business
        </h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              title: "Connect Your Data",
              desc: "Shopify, Paymob, CSV — connect in minutes.",
              icon: "🔗",
            },
            {
              title: "AI Analysis",
              desc: "GPT-powered insights grounded in your real metrics.",
              icon: "🧠",
            },
            {
              title: "WhatsApp Delivery",
              desc: "Daily reports at 8 AM. No app to open.",
              icon: "📱",
            },
          ].map((f) => (
            <div key={f.title} className="bg-card p-6 rounded-xl border shadow-sm">
              <div className="text-3xl mb-4">{f.icon}</div>
              <h3 className="text-xl font-semibold mb-2">{f.title}</h3>
              <p className="text-muted-foreground">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">Simple Pricing</h2>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {[
            { name: "Starter", price: "499", features: ["1 integration", "Daily reports", "Email support"] },
            { name: "Growth", price: "999", features: ["3 integrations", "Priority support", "Custom insights"], popular: true },
            { name: "Pro", price: "2,499", features: ["Unlimited integrations", "API access", "Dedicated support"] },
          ].map((plan) => (
            <div
              key={plan.name}
              className={`p-6 rounded-xl border ${
                plan.popular ? "border-primary shadow-lg scale-105" : ""
              }`}
            >
              {plan.popular && (
                <span className="text-xs bg-primary text-primary-foreground px-2 py-1 rounded-full">
                  Most Popular
                </span>
              )}
              <h3 className="text-xl font-semibold mt-4">{plan.name}</h3>
              <p className="mt-2">
                <span className="text-3xl font-bold">EGP {plan.price}</span>
                <span className="text-muted-foreground">/month</span>
              </p>
              <ul className="mt-6 space-y-3">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-center gap-2 text-sm">
                    <span className="text-primary">•</span> {f}
                  </li>
                ))}
              </ul>
              <Link
                href="/signup"
                className="mt-6 block text-center bg-primary text-primary-foreground py-2 rounded-lg hover:opacity-90"
              >
                Get Started
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8">
        <div className="container mx-auto px-4 text-center text-muted-foreground text-sm">
          © 2024 Teqa. AI Business Intelligence for Egyptian SMBs.
        </div>
      </footer>
    </div>
  );
}
