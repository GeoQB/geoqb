'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Trash2, Edit, Layers as LayersIcon } from 'lucide-react'
import Link from 'next/link'
import { workspaceApi } from '@/lib/api'

export default function WorkspacesPage() {
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newWorkspace, setNewWorkspace] = useState({ name: '', description: '' })

  const { data: workspaces, isLoading } = useQuery({
    queryKey: ['workspaces'],
    queryFn: workspaceApi.list,
  })

  const createMutation = useMutation({
    mutationFn: workspaceApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
      setShowCreateModal(false)
      setNewWorkspace({ name: '', description: '' })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: workspaceApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['workspaces'] })
    },
  })

  const filteredWorkspaces = workspaces?.filter((ws) =>
    ws.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(newWorkspace)
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Workspaces</h1>
          <p className="text-gray-400">
            Organize your spatial layers into workspaces
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="mt-4 sm:mt-0 inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition font-medium"
        >
          <Plus className="w-5 h-5" />
          New Workspace
        </button>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search workspaces..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-12 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Workspaces Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      ) : filteredWorkspaces && filteredWorkspaces.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredWorkspaces.map((workspace) => (
            <div
              key={workspace.id}
              className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-blue-500/50 transition group"
            >
              <div className="flex items-start justify-between mb-4">
                <Link
                  href={`/dashboard/workspaces/${workspace.id}`}
                  className="flex-1"
                >
                  <h3 className="text-xl font-semibold text-white group-hover:text-blue-400 transition mb-2">
                    {workspace.name}
                  </h3>
                  {workspace.description && (
                    <p className="text-sm text-gray-400 line-clamp-2">
                      {workspace.description}
                    </p>
                  )}
                </Link>
                <button
                  onClick={() => {
                    if (confirm('Are you sure you want to delete this workspace?')) {
                      deleteMutation.mutate(workspace.id)
                    }
                  }}
                  className="text-gray-400 hover:text-red-400 transition"
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-gray-700">
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <LayersIcon className="w-4 h-4" />
                  <span>{workspace.layer_count} layers</span>
                </div>
                <Link
                  href={`/dashboard/workspaces/${workspace.id}`}
                  className="text-blue-400 hover:text-blue-300 text-sm font-medium"
                >
                  Open →
                </Link>
              </div>

              <p className="text-xs text-gray-500 mt-3">
                Updated {new Date(workspace.updated_at).toLocaleDateString()}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-16 bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl">
          <LayersIcon className="w-16 h-16 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-400 mb-2">
            {searchTerm ? 'No workspaces found' : 'No workspaces yet'}
          </h3>
          <p className="text-gray-500 mb-6">
            {searchTerm
              ? 'Try a different search term'
              : 'Create your first workspace to get started'}
          </p>
          {!searchTerm && (
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition font-medium"
            >
              <Plus className="w-5 h-5" />
              Create Workspace
            </button>
          )}
        </div>
      )}

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 max-w-md w-full">
            <h2 className="text-2xl font-bold text-white mb-6">Create Workspace</h2>

            <form onSubmit={handleCreate} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Workspace Name
                </label>
                <input
                  type="text"
                  required
                  value={newWorkspace.name}
                  onChange={(e) =>
                    setNewWorkspace({ ...newWorkspace, name: e.target.value })
                  }
                  className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="My Spatial Project"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Description (Optional)
                </label>
                <textarea
                  value={newWorkspace.description}
                  onChange={(e) =>
                    setNewWorkspace({ ...newWorkspace, description: e.target.value })
                  }
                  className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Describe your workspace..."
                  rows={3}
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={createMutation.isPending}
                  className="flex-1 px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 text-white rounded-lg transition font-medium"
                >
                  {createMutation.isPending ? 'Creating...' : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
