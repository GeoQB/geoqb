'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useRouter } from 'next/navigation'
import {
  ArrowLeft,
  Plus,
  Trash2,
  RefreshCw,
  MapPin,
  Clock,
  AlertCircle,
  CheckCircle2,
  Loader2
} from 'lucide-react'
import Link from 'next/link'
import { workspaceApi, layerApi, Layer } from '@/lib/api'

export default function WorkspaceDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const queryClient = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newLayer, setNewLayer] = useState({
    name: '',
    layer_type: 'amenity',
    tags: { amenity: 'hospital' },
    bbox: [52.4, 13.2, 52.6, 13.5],
    resolution: 9
  })

  const { data: workspace, isLoading: workspaceLoading } = useQuery({
    queryKey: ['workspace', params.id],
    queryFn: () => workspaceApi.get(params.id),
  })

  const { data: layers, isLoading: layersLoading } = useQuery({
    queryKey: ['layers', params.id],
    queryFn: () => layerApi.list(params.id),
  })

  const createMutation = useMutation({
    mutationFn: (data: any) => layerApi.create(params.id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['layers', params.id] })
      queryClient.invalidateQueries({ queryKey: ['workspace', params.id] })
      setShowCreateModal(false)
      setNewLayer({
        name: '',
        layer_type: 'amenity',
        tags: { amenity: 'hospital' },
        bbox: [52.4, 13.2, 52.6, 13.5],
        resolution: 9
      })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (layerId: string) => layerApi.delete(params.id, layerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['layers', params.id] })
      queryClient.invalidateQueries({ queryKey: ['workspace', params.id] })
    },
  })

  const reingestMutation = useMutation({
    mutationFn: (layerId: string) => layerApi.reingest(params.id, layerId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['layers', params.id] })
    },
  })

  const handleCreateLayer = (e: React.FormEvent) => {
    e.preventDefault()
    createMutation.mutate(newLayer)
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-400 bg-green-500/10'
      case 'processing': return 'text-blue-400 bg-blue-500/10'
      case 'failed': return 'text-red-400 bg-red-500/10'
      default: return 'text-gray-400 bg-gray-500/10'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle2 className="w-4 h-4" />
      case 'processing': return <Loader2 className="w-4 h-4 animate-spin" />
      case 'failed': return <AlertCircle className="w-4 h-4" />
      default: return <Clock className="w-4 h-4" />
    }
  }

  if (workspaceLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="/dashboard/workspaces"
          className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Workspaces
        </Link>

        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">{workspace?.name}</h1>
            {workspace?.description && (
              <p className="text-gray-400">{workspace.description}</p>
            )}
            <p className="text-sm text-gray-500 mt-2">
              TigerGraph: {workspace?.tigergraph_graphname}
            </p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition font-medium"
          >
            <Plus className="w-5 h-5" />
            Add Layer
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
          <p className="text-gray-400 text-sm mb-1">Total Layers</p>
          <p className="text-3xl font-bold text-white">{layers?.length || 0}</p>
        </div>
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
          <p className="text-gray-400 text-sm mb-1">Total Features</p>
          <p className="text-3xl font-bold text-white">
            {layers?.reduce((sum, l) => sum + l.feature_count, 0) || 0}
          </p>
        </div>
        <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
          <p className="text-gray-400 text-sm mb-1">Processing</p>
          <p className="text-3xl font-bold text-white">
            {layers?.filter(l => l.status === 'processing').length || 0}
          </p>
        </div>
      </div>

      {/* Layers List */}
      <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-6">Layers</h2>

        {layersLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
          </div>
        ) : layers && layers.length > 0 ? (
          <div className="space-y-4">
            {layers.map((layer) => (
              <LayerCard
                key={layer.id}
                layer={layer}
                onDelete={() => {
                  if (confirm('Are you sure you want to delete this layer?')) {
                    deleteMutation.mutate(layer.id)
                  }
                }}
                onReingest={() => {
                  if (confirm('Re-ingest this layer? This will fetch fresh data from OSM.')) {
                    reingestMutation.mutate(layer.id)
                  }
                }}
                getStatusColor={getStatusColor}
                getStatusIcon={getStatusIcon}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-16">
            <MapPin className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-400 mb-2">No layers yet</h3>
            <p className="text-gray-500 mb-6">
              Add your first spatial layer to start analyzing data
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition font-medium"
            >
              <Plus className="w-5 h-5" />
              Add Layer
            </button>
          </div>
        )}
      </div>

      {/* Create Layer Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 p-4">
          <div className="bg-gray-800 border border-gray-700 rounded-xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <h2 className="text-2xl font-bold text-white mb-6">Add New Layer</h2>

            <form onSubmit={handleCreateLayer} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Layer Name
                </label>
                <input
                  type="text"
                  required
                  value={newLayer.name}
                  onChange={(e) => setNewLayer({ ...newLayer, name: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., Berlin Hospitals"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Layer Type
                </label>
                <select
                  value={newLayer.layer_type}
                  onChange={(e) => setNewLayer({ ...newLayer, layer_type: e.target.value })}
                  className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="amenity">Amenity</option>
                  <option value="building">Building</option>
                  <option value="highway">Highway</option>
                  <option value="landuse">Land Use</option>
                  <option value="natural">Natural</option>
                  <option value="shop">Shop</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  OSM Tag Value
                </label>
                <input
                  type="text"
                  required
                  value={Object.values(newLayer.tags)[0] as string}
                  onChange={(e) => setNewLayer({
                    ...newLayer,
                    tags: { [newLayer.layer_type]: e.target.value }
                  })}
                  className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="e.g., hospital, school, restaurant"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Bounding Box (min lat, min lon)
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="number"
                      step="0.001"
                      required
                      value={newLayer.bbox[0]}
                      onChange={(e) => setNewLayer({
                        ...newLayer,
                        bbox: [parseFloat(e.target.value), newLayer.bbox[1], newLayer.bbox[2], newLayer.bbox[3]]
                      })}
                      className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Lat"
                    />
                    <input
                      type="number"
                      step="0.001"
                      required
                      value={newLayer.bbox[1]}
                      onChange={(e) => setNewLayer({
                        ...newLayer,
                        bbox: [newLayer.bbox[0], parseFloat(e.target.value), newLayer.bbox[2], newLayer.bbox[3]]
                      })}
                      className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Lon"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Bounding Box (max lat, max lon)
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="number"
                      step="0.001"
                      required
                      value={newLayer.bbox[2]}
                      onChange={(e) => setNewLayer({
                        ...newLayer,
                        bbox: [newLayer.bbox[0], newLayer.bbox[1], parseFloat(e.target.value), newLayer.bbox[3]]
                      })}
                      className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Lat"
                    />
                    <input
                      type="number"
                      step="0.001"
                      required
                      value={newLayer.bbox[3]}
                      onChange={(e) => setNewLayer({
                        ...newLayer,
                        bbox: [newLayer.bbox[0], newLayer.bbox[1], newLayer.bbox[2], parseFloat(e.target.value)]
                      })}
                      className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Lon"
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  H3 Resolution (6-15)
                </label>
                <input
                  type="number"
                  min="6"
                  max="15"
                  required
                  value={newLayer.resolution}
                  onChange={(e) => setNewLayer({ ...newLayer, resolution: parseInt(e.target.value) })}
                  className="w-full px-4 py-3 bg-gray-900/50 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Higher resolution = more detail, but more data. Recommended: 9
                </p>
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
                  {createMutation.isPending ? 'Creating...' : 'Create Layer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

function LayerCard({
  layer,
  onDelete,
  onReingest,
  getStatusColor,
  getStatusIcon
}: {
  layer: Layer
  onDelete: () => void
  onReingest: () => void
  getStatusColor: (status: string) => string
  getStatusIcon: (status: string) => React.ReactNode
}) {
  return (
    <div className="bg-gray-900/50 border border-gray-700 rounded-lg p-6 hover:border-blue-500/50 transition">
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-white mb-1">{layer.name}</h3>
          <p className="text-sm text-gray-400">
            {layer.layer_type}: {JSON.stringify(layer.tags)}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {layer.status !== 'processing' && (
            <button
              onClick={onReingest}
              className="p-2 text-gray-400 hover:text-blue-400 hover:bg-blue-500/10 rounded-lg transition"
              title="Re-ingest data"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
          <button
            onClick={onDelete}
            className="p-2 text-gray-400 hover:text-red-400 hover:bg-red-500/10 rounded-lg transition"
            title="Delete layer"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div>
          <p className="text-xs text-gray-500 mb-1">Status</p>
          <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(layer.status)}`}>
            {getStatusIcon(layer.status)}
            <span className="capitalize">{layer.status}</span>
          </div>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Features</p>
          <p className="text-sm font-semibold text-white">{layer.feature_count.toLocaleString()}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Resolution</p>
          <p className="text-sm font-semibold text-white">H3-{layer.resolution}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 mb-1">Created</p>
          <p className="text-sm font-semibold text-white">
            {new Date(layer.created_at).toLocaleDateString()}
          </p>
        </div>
      </div>

      {layer.error_message && (
        <div className="mt-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-300">{layer.error_message}</p>
          </div>
        </div>
      )}

      <div className="mt-4 pt-4 border-t border-gray-700">
        <p className="text-xs text-gray-500">
          Bbox: [{layer.bbox.map(n => n.toFixed(3)).join(', ')}]
        </p>
      </div>
    </div>
  )
}
