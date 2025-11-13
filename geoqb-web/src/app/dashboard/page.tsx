'use client'

import { useQuery } from '@tanstack/react-query'
import { Layers, MapPin, Activity, TrendingUp, Plus } from 'lucide-react'
import Link from 'next/link'
import { workspaceApi, layerApi } from '@/lib/api'
import { useAuthStore } from '@/lib/store'

export default function DashboardPage() {
  const user = useAuthStore((state) => state.user)

  const { data: workspaces, isLoading: workspacesLoading } = useQuery({
    queryKey: ['workspaces'],
    queryFn: workspaceApi.list,
  })

  // Get total layer count across all workspaces
  const totalLayers = workspaces?.reduce((sum, ws) => sum + ws.layer_count, 0) || 0

  const stats = [
    {
      name: 'Workspaces',
      value: workspaces?.length || 0,
      icon: Layers,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
    },
    {
      name: 'Total Layers',
      value: totalLayers,
      icon: MapPin,
      color: 'text-purple-400',
      bgColor: 'bg-purple-500/10',
    },
    {
      name: 'Queries This Month',
      value: 0, // TODO: Implement usage tracking
      icon: Activity,
      color: 'text-green-400',
      bgColor: 'bg-green-500/10',
    },
    {
      name: 'Current Plan',
      value: user?.plan.toUpperCase() || 'FREE',
      icon: TrendingUp,
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/10',
    },
  ]

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">
          Welcome back, {user?.full_name}!
        </h1>
        <p className="text-gray-400">
          Here's an overview of your spatial knowledge graphs
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div
              key={stat.name}
              className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-blue-500/50 transition"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
              </div>
              <p className="text-gray-400 text-sm mb-1">{stat.name}</p>
              <p className="text-2xl font-bold text-white">{stat.value}</p>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <Link
          href="/dashboard/workspaces"
          className="group bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl p-8 hover:from-blue-700 hover:to-blue-800 transition"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-white mb-2">Create Workspace</h3>
              <p className="text-blue-100">
                Start a new project and organize your spatial layers
              </p>
            </div>
            <Plus className="w-8 h-8 text-white group-hover:scale-110 transition-transform" />
          </div>
        </Link>

        <Link
          href="/docs"
          className="group bg-gradient-to-br from-purple-600 to-purple-700 rounded-xl p-8 hover:from-purple-700 hover:to-purple-800 transition"
        >
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-xl font-bold text-white mb-2">View Documentation</h3>
              <p className="text-purple-100">
                Learn how to build spatial knowledge graphs
              </p>
            </div>
            <Activity className="w-8 h-8 text-white group-hover:scale-110 transition-transform" />
          </div>
        </Link>
      </div>

      {/* Recent Workspaces */}
      <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold text-white">Your Workspaces</h2>
          <Link
            href="/dashboard/workspaces"
            className="text-blue-400 hover:text-blue-300 text-sm font-medium"
          >
            View All
          </Link>
        </div>

        {workspacesLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : workspaces && workspaces.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {workspaces.slice(0, 6).map((workspace) => (
              <Link
                key={workspace.id}
                href={`/dashboard/workspaces/${workspace.id}`}
                className="bg-gray-900/50 border border-gray-700 rounded-lg p-4 hover:border-blue-500/50 transition group"
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-white font-semibold group-hover:text-blue-400 transition">
                    {workspace.name}
                  </h3>
                  <span className="text-xs text-gray-400 bg-gray-800 px-2 py-1 rounded">
                    {workspace.layer_count} layers
                  </span>
                </div>
                {workspace.description && (
                  <p className="text-sm text-gray-400 line-clamp-2">
                    {workspace.description}
                  </p>
                )}
                <p className="text-xs text-gray-500 mt-2">
                  Updated {new Date(workspace.updated_at).toLocaleDateString()}
                </p>
              </Link>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Layers className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-400 mb-2">
              No workspaces yet
            </h3>
            <p className="text-gray-500 mb-6">
              Create your first workspace to start building spatial knowledge graphs
            </p>
            <Link
              href="/dashboard/workspaces"
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition font-medium"
            >
              <Plus className="w-4 h-4" />
              Create Workspace
            </Link>
          </div>
        )}
      </div>

      {/* Plan Usage */}
      {user?.plan === 'free' && (
        <div className="mt-8 bg-gradient-to-r from-blue-600/10 to-purple-600/10 border border-blue-500/30 rounded-xl p-6">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="text-lg font-semibold text-white mb-2">
                Upgrade to Professional
              </h3>
              <p className="text-gray-300 mb-4">
                Get 50 layers, 10,000 queries/month, and priority support
              </p>
              <Link
                href="/dashboard/billing"
                className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition font-medium"
              >
                View Plans
              </Link>
            </div>
            <div className="text-right">
              <p className="text-3xl font-bold text-white mb-1">$99</p>
              <p className="text-gray-400 text-sm">per month</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
