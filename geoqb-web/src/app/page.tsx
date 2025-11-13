'use client'

import { motion } from 'framer-motion'
import {
  Globe,
  Database,
  Zap,
  BarChart3,
  ArrowRight,
  CheckCircle2,
  MapPin,
  Network,
  Sparkles
} from 'lucide-react'
import Link from 'next/link'

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-gray-900/80 backdrop-blur-lg border-b border-gray-800 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Globe className="w-8 h-8 text-blue-400" />
              <span className="text-2xl font-bold text-white">GeoQB</span>
            </div>
            <div className="flex items-center space-x-6">
              <Link href="/docs" className="text-gray-300 hover:text-white transition">
                Docs
              </Link>
              <Link href="/pricing" className="text-gray-300 hover:text-white transition">
                Pricing
              </Link>
              <Link href="/auth/login" className="text-gray-300 hover:text-white transition">
                Sign In
              </Link>
              <Link
                href="/auth/signup"
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition font-medium"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center pt-16 px-4">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <motion.div
            className="absolute top-20 left-10 w-72 h-72 bg-blue-500/20 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 8,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
          <motion.div
            className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl"
            animate={{
              scale: [1.2, 1, 1.2],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
              duration: 10,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        </div>

        <div className="relative z-10 max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="inline-block mb-6"
            >
              <span className="inline-flex items-center gap-2 bg-blue-500/10 border border-blue-500/20 rounded-full px-4 py-2 text-blue-300">
                <Sparkles className="w-4 h-4" />
                <span className="text-sm font-medium">Production-Ready Spatial Intelligence</span>
              </span>
            </motion.div>

            <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
              Build Spatial Knowledge Graphs
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                In Minutes, Not Months
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-300 mb-12 max-w-3xl mx-auto">
              Transform OpenStreetMap data into powerful graph databases.
              Analyze accessibility, detect patterns, and unlock spatial insights at scale.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Link
                href="/auth/signup"
                className="group bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg transition font-semibold text-lg flex items-center gap-2"
              >
                Start Free Trial
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition" />
              </Link>
              <Link
                href="/demo"
                className="bg-gray-800 hover:bg-gray-700 text-white px-8 py-4 rounded-lg transition font-semibold text-lg border border-gray-700"
              >
                Watch Demo
              </Link>
            </div>

            <p className="text-gray-400 mt-6">
              No credit card required • Free tier available • 5 layers included
            </p>
          </motion.div>

          {/* Feature Cards */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            className="grid md:grid-cols-3 gap-6 mt-20"
          >
            <FeatureCard
              icon={<Zap className="w-8 h-8" />}
              title="Lightning Fast"
              description="H3 spatial indexing + TigerGraph delivers sub-second queries on millions of features"
            />
            <FeatureCard
              icon={<Database className="w-8 h-8" />}
              title="OSM Integration"
              description="Direct integration with OpenStreetMap. Fresh data, always up-to-date"
            />
            <FeatureCard
              icon={<Network className="w-8 h-8" />}
              title="Graph Analytics"
              description="Accessibility analysis, shortest paths, community detection, and more"
            />
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="relative py-32 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              From Data to Insights in 3 Steps
            </h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
              No DevOps, no infrastructure setup. Just focus on analysis.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            <StepCard
              number="01"
              title="Define Your Layers"
              description="Select OSM features (hospitals, parks, transit) and bounding box. GeoQB handles the rest."
              icon={<MapPin className="w-12 h-12 text-blue-400" />}
            />
            <StepCard
              number="02"
              title="Auto-Ingest & Index"
              description="Data flows from OSM → H3 spatial index → TigerGraph. All automatic."
              icon={<Database className="w-12 h-12 text-purple-400" />}
            />
            <StepCard
              number="03"
              title="Analyze & Visualize"
              description="Run graph queries, compute metrics, visualize on interactive maps."
              icon={<BarChart3 className="w-12 h-12 text-green-400" />}
            />
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="relative py-32 px-4 bg-gray-900/50">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Trusted By Leading Organizations
            </h2>
            <p className="text-xl text-gray-300">
              From urban planning to real estate intelligence
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 gap-8">
            <UseCaseCard
              title="Urban Accessibility Analysis"
              description="Calculate 15-minute city scores, hospital accessibility, transit coverage in real-time."
              metrics={["20M+ locations indexed", "Sub-second queries", "Real-time updates"]}
            />
            <UseCaseCard
              title="Real Estate Intelligence"
              description="Location scoring, amenity proximity, neighborhood analysis for property valuation."
              metrics={["500+ amenity types", "Global coverage", "Custom scoring models"]}
            />
            <UseCaseCard
              title="ESG & Sustainability"
              description="Green space access, EV charger density, sustainable mobility metrics."
              metrics={["Climate risk analysis", "Carbon footprint", "Social equity metrics"]}
            />
            <UseCaseCard
              title="Supply Chain Optimization"
              description="Warehouse placement, delivery routing, demand forecasting with spatial context."
              metrics={["Multi-modal routing", "Cost optimization", "Risk assessment"]}
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-32 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Ready to Build Your Spatial Knowledge Graph?
            </h2>
            <p className="text-xl text-gray-300 mb-12">
              Join developers and researchers building the future of spatial intelligence.
            </p>
            <Link
              href="/auth/signup"
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg transition font-semibold text-lg"
            >
              Start Free Trial
              <ArrowRight className="w-5 h-5" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative border-t border-gray-800 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Globe className="w-6 h-6 text-blue-400" />
                <span className="text-xl font-bold text-white">GeoQB</span>
              </div>
              <p className="text-gray-400">
                Spatial Knowledge Graph Platform
              </p>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Product</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/features">Features</Link></li>
                <li><Link href="/pricing">Pricing</Link></li>
                <li><Link href="/docs">Documentation</Link></li>
                <li><Link href="/api">API</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/blog">Blog</Link></li>
                <li><Link href="/tutorials">Tutorials</Link></li>
                <li><Link href="/community">Community</Link></li>
                <li><Link href="/support">Support</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-white font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/about">About</Link></li>
                <li><Link href="/careers">Careers</Link></li>
                <li><Link href="/privacy">Privacy</Link></li>
                <li><Link href="/terms">Terms</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-12 pt-8 text-center text-gray-400">
            <p>© 2024 GeoQB. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </main>
  )
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }) {
  return (
    <motion.div
      whileHover={{ y: -5 }}
      className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-blue-500/50 transition"
    >
      <div className="text-blue-400 mb-4">{icon}</div>
      <h3 className="text-xl font-semibold text-white mb-2">{title}</h3>
      <p className="text-gray-400">{description}</p>
    </motion.div>
  )
}

function StepCard({ number, title, description, icon }: { number: string; title: string; description: string; icon: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      viewport={{ once: true }}
      className="relative"
    >
      <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-8 hover:border-blue-500/50 transition">
        <div className="flex items-center justify-between mb-6">
          <span className="text-6xl font-bold text-gray-700">{number}</span>
          {icon}
        </div>
        <h3 className="text-2xl font-semibold text-white mb-3">{title}</h3>
        <p className="text-gray-400">{description}</p>
      </div>
    </motion.div>
  )
}

function UseCaseCard({ title, description, metrics }: { title: string; description: string; metrics: string[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.8 }}
      viewport={{ once: true }}
      className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-8 hover:border-blue-500/50 transition"
    >
      <h3 className="text-2xl font-semibold text-white mb-3">{title}</h3>
      <p className="text-gray-400 mb-6">{description}</p>
      <div className="space-y-2">
        {metrics.map((metric, index) => (
          <div key={index} className="flex items-center gap-2 text-sm text-gray-300">
            <CheckCircle2 className="w-4 h-4 text-green-400" />
            <span>{metric}</span>
          </div>
        ))}
      </div>
    </motion.div>
  )
}
