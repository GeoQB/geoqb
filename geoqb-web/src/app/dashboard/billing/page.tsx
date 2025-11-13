'use client'

import { useAuthStore } from '@/lib/store'
import { CheckCircle2, Zap, Crown, Building2, CreditCard } from 'lucide-react'

export default function BillingPage() {
  const { user } = useAuthStore()

  const plans = [
    {
      name: 'Free',
      price: 0,
      description: 'Perfect for trying out GeoQB',
      icon: Zap,
      color: 'blue',
      features: [
        '5 spatial layers',
        '100 queries per month',
        '1 workspace',
        'Community support',
        'Basic analytics',
        'API access',
      ],
      limitations: ['No advanced features', 'Limited data retention'],
    },
    {
      name: 'Professional',
      price: 99,
      description: 'For professionals and small teams',
      icon: Crown,
      color: 'purple',
      popular: true,
      features: [
        '50 spatial layers',
        '10,000 queries per month',
        '10 workspaces',
        'Priority email support',
        'Advanced analytics',
        'API access',
        'Custom data integrations',
        'Team collaboration',
      ],
      limitations: [],
    },
    {
      name: 'Business',
      price: 499,
      description: 'For growing businesses',
      icon: Building2,
      color: 'green',
      features: [
        '200 spatial layers',
        '100,000 queries per month',
        'Unlimited workspaces',
        'Priority support',
        'Advanced analytics',
        'API access',
        'Custom integrations',
        'Team collaboration',
        'SSO / SAML',
        'SLA guarantee',
        'Dedicated account manager',
      ],
      limitations: [],
    },
  ]

  const getColorClasses = (color: string, variant: 'bg' | 'text' | 'border' | 'hover') => {
    const colors: Record<string, Record<string, string>> = {
      blue: {
        bg: 'bg-blue-500/10',
        text: 'text-blue-400',
        border: 'border-blue-500',
        hover: 'hover:bg-blue-600',
      },
      purple: {
        bg: 'bg-purple-500/10',
        text: 'text-purple-400',
        border: 'border-purple-500',
        hover: 'hover:bg-purple-600',
      },
      green: {
        bg: 'bg-green-500/10',
        text: 'text-green-400',
        border: 'border-green-500',
        hover: 'hover:bg-green-600',
      },
    }
    return colors[color]?.[variant] || ''
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-12 text-center">
        <h1 className="text-4xl font-bold text-white mb-4">Choose Your Plan</h1>
        <p className="text-xl text-gray-400">
          Unlock the full power of spatial knowledge graphs
        </p>
      </div>

      {/* Current Plan Banner */}
      {user && (
        <div className="mb-12 bg-gradient-to-r from-blue-600/20 to-purple-600/20 border border-blue-500/30 rounded-xl p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm mb-1">Current Plan</p>
              <p className="text-2xl font-bold text-white capitalize">{user.plan}</p>
            </div>
            <div className="flex items-center gap-2">
              <CreditCard className="w-5 h-5 text-gray-400" />
              <span className="text-gray-400">
                {user.plan === 'free' ? 'No payment method required' : '•••• 4242'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
        {plans.map((plan) => {
          const Icon = plan.icon
          const isCurrentPlan = user?.plan === plan.name.toLowerCase()

          return (
            <div
              key={plan.name}
              className={`relative bg-gray-800/50 backdrop-blur-sm border rounded-xl p-8 transition ${
                plan.popular
                  ? 'border-purple-500 shadow-lg shadow-purple-500/20'
                  : 'border-gray-700 hover:border-gray-600'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <span className="bg-gradient-to-r from-purple-600 to-pink-600 text-white text-sm font-bold px-4 py-1 rounded-full">
                    Most Popular
                  </span>
                </div>
              )}

              <div className={`inline-flex p-3 rounded-lg ${getColorClasses(plan.color, 'bg')} mb-4`}>
                <Icon className={`w-6 h-6 ${getColorClasses(plan.color, 'text')}`} />
              </div>

              <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
              <p className="text-gray-400 mb-6">{plan.description}</p>

              <div className="mb-6">
                <span className="text-5xl font-bold text-white">${plan.price}</span>
                <span className="text-gray-400">/month</span>
              </div>

              <button
                disabled={isCurrentPlan}
                className={`w-full py-3 rounded-lg font-semibold transition mb-6 ${
                  isCurrentPlan
                    ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                    : plan.popular
                    ? 'bg-purple-600 hover:bg-purple-700 text-white'
                    : 'bg-blue-600 hover:bg-blue-700 text-white'
                }`}
              >
                {isCurrentPlan ? 'Current Plan' : plan.price === 0 ? 'Get Started' : 'Upgrade'}
              </button>

              <div className="space-y-3 mb-6">
                {plan.features.map((feature, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <CheckCircle2 className={`w-5 h-5 flex-shrink-0 mt-0.5 ${getColorClasses(plan.color, 'text')}`} />
                    <span className="text-gray-300 text-sm">{feature}</span>
                  </div>
                ))}
              </div>

              {plan.limitations.length > 0 && (
                <div className="pt-6 border-t border-gray-700">
                  <p className="text-xs text-gray-500 mb-2">Limitations:</p>
                  {plan.limitations.map((limitation, index) => (
                    <p key={index} className="text-xs text-gray-500">
                      • {limitation}
                    </p>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Enterprise CTA */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 border border-gray-700 rounded-xl p-12 text-center">
        <h2 className="text-3xl font-bold text-white mb-4">Need More?</h2>
        <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
          Enterprise plans with custom features, dedicated support, and flexible pricing
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition">
            Contact Sales
          </button>
          <button className="border border-gray-600 hover:border-gray-500 text-white px-8 py-3 rounded-lg font-semibold transition">
            Schedule Demo
          </button>
        </div>
      </div>

      {/* FAQ Section */}
      <div className="mt-16">
        <h2 className="text-2xl font-bold text-white mb-8 text-center">Frequently Asked Questions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-2">Can I change plans anytime?</h3>
            <p className="text-gray-400 text-sm">
              Yes! You can upgrade or downgrade your plan at any time. Changes take effect immediately.
            </p>
          </div>
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-2">What payment methods do you accept?</h3>
            <p className="text-gray-400 text-sm">
              We accept all major credit cards, debit cards, and can provide invoicing for annual contracts.
            </p>
          </div>
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-2">Is there a free trial?</h3>
            <p className="text-gray-400 text-sm">
              Yes! All paid plans come with a 14-day free trial. No credit card required to start.
            </p>
          </div>
          <div className="bg-gray-800/50 border border-gray-700 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-2">What happens if I exceed my limits?</h3>
            <p className="text-gray-400 text-sm">
              You'll receive notifications as you approach your limits. You can upgrade anytime to avoid interruption.
            </p>
          </div>
        </div>
      </div>

      {/* Payment Method Section (if paid plan) */}
      {user && user.plan !== 'free' && (
        <div className="mt-16">
          <h2 className="text-2xl font-bold text-white mb-6">Payment Method</h2>
          <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="bg-gray-700 rounded-lg p-3">
                  <CreditCard className="w-6 h-6 text-gray-400" />
                </div>
                <div>
                  <p className="text-white font-semibold">•••• •••• •••• 4242</p>
                  <p className="text-sm text-gray-400">Expires 12/2025</p>
                </div>
              </div>
              <button className="text-blue-400 hover:text-blue-300 text-sm font-medium">
                Update
              </button>
            </div>
          </div>

          <div className="mt-6 bg-gray-800/50 border border-gray-700 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Billing History</h3>
            <div className="space-y-3">
              {[
                { date: 'Dec 1, 2024', amount: '$99.00', status: 'Paid' },
                { date: 'Nov 1, 2024', amount: '$99.00', status: 'Paid' },
                { date: 'Oct 1, 2024', amount: '$99.00', status: 'Paid' },
              ].map((invoice, index) => (
                <div key={index} className="flex items-center justify-between py-3 border-b border-gray-700 last:border-0">
                  <div>
                    <p className="text-white font-medium">{invoice.date}</p>
                    <p className="text-sm text-gray-400">{invoice.amount}</p>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-green-400 text-sm font-medium">{invoice.status}</span>
                    <button className="text-blue-400 hover:text-blue-300 text-sm">
                      Download
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
