<template>
  <div class="space-y-6">
    <!-- Top Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Manufacturing Inventory Dashboard</h1>
        <p class="text-xs text-slate-400 mt-0.5">Real-time electronics & battery stock overview</p>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="loadMetrics"
          class="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-xs font-semibold text-slate-300 rounded-lg transition"
        >
          <RotateCw class="w-3.5 h-3.5" :class="{ 'animate-spin': loading }" />
          <span>Refresh</span>
        </button>

        <router-link
          to="/stock-operations"
          class="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg shadow-lg shadow-emerald-950 transition"
        >
          <ArrowLeftRight class="w-3.5 h-3.5" />
          <span>New Stock Operation</span>
        </router-link>
      </div>
    </div>

    <!-- KPI Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total Parts Catalog"
        :value="metrics.summary?.total_parts || 0"
        subtitle="Across all part types"
        :icon="Layers"
      />
      <StatCard
        title="Total Quantity In Stock"
        :value="(metrics.summary?.total_stock_quantity || 0).toLocaleString()"
        unit="PCS"
        subtitle="Bulk passive & active components"
        :icon="Boxes"
      />
      <StatCard
        title="Battery Cells (Tracked)"
        :value="(metrics.summary?.total_cells || 0).toLocaleString()"
        unit="CELLS"
        subtitle="Individually serialized"
        :icon="BatteryCharging"
      />
      <StatCard
        title="Reserved Stock"
        :value="(metrics.summary?.total_reserved_quantity || 0).toLocaleString()"
        unit="PCS"
        subtitle="Allocated for Work Orders"
        :icon="Lock"
      />
    </div>

    <!-- Middle Row: Warehouse Occupancy & Stock Movements -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Warehouse Locations Occupancy Card -->
      <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-sm font-bold text-white flex items-center gap-2">
              <MapPin class="w-4 h-4 text-emerald-400" />
              Warehouse Occupancy
            </h3>
            <span class="text-xs font-mono font-bold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/50">
              {{ metrics.summary?.occupancy_rate || 0 }}% OCCUPIED
            </span>
          </div>

          <!-- Progress Bar -->
          <div class="w-full bg-slate-950 h-3 rounded-full overflow-hidden border border-slate-800 mb-4">
            <div
              class="bg-gradient-to-r from-emerald-500 to-teal-400 h-full transition-all duration-500"
              :style="{ width: `${metrics.summary?.occupancy_rate || 0}%` }"
            ></div>
          </div>

          <div class="grid grid-cols-3 gap-2 text-center text-xs">
            <div class="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
              <span class="text-slate-400 block text-[10px] uppercase font-semibold">Total</span>
              <span class="font-mono font-bold text-white text-base">{{ metrics.summary?.total_locations || 0 }}</span>
            </div>
            <div class="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
              <span class="text-slate-400 block text-[10px] uppercase font-semibold">Occupied</span>
              <span class="font-mono font-bold text-emerald-400 text-base">{{ metrics.summary?.occupied_locations || 0 }}</span>
            </div>
            <div class="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
              <span class="text-slate-400 block text-[10px] uppercase font-semibold">Empty</span>
              <span class="font-mono font-bold text-slate-300 text-base">{{ metrics.summary?.empty_locations || 0 }}</span>
            </div>
          </div>
        </div>

        <div class="mt-4 pt-3 border-t border-slate-800 flex justify-end items-center text-xs">
          <router-link to="/locations" class="text-emerald-400 hover:text-emerald-300 font-semibold">
            Manage Locations &rarr;
          </router-link>
        </div>

      </div>

      <!-- Movement Operations Ratio -->
      <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg">
        <h3 class="text-sm font-bold text-white flex items-center gap-2 mb-4">
          <Activity class="w-4 h-4 text-emerald-400" />
          Stock Movement Breakdown
        </h3>

        <div class="space-y-3">
          <div>
            <div class="flex justify-between text-xs mb-1">
              <span class="text-slate-300 flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-emerald-400"></span> Receive Transactions
              </span>
              <span class="font-mono font-bold text-white">{{ metrics.movement_counts?.receive || 0 }}</span>
            </div>
            <div class="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
              <div class="bg-emerald-500 h-full" :style="{ width: getPercentage(metrics.movement_counts?.receive) + '%' }"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-xs mb-1">
              <span class="text-slate-300 flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-blue-400"></span> Transfer Movements
              </span>
              <span class="font-mono font-bold text-white">{{ metrics.movement_counts?.transfer || 0 }}</span>
            </div>
            <div class="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
              <div class="bg-blue-500 h-full" :style="{ width: getPercentage(metrics.movement_counts?.transfer) + '%' }"></div>
            </div>
          </div>

          <div>
            <div class="flex justify-between text-xs mb-1">
              <span class="text-slate-300 flex items-center gap-1.5">
                <span class="w-2 h-2 rounded-full bg-amber-400"></span> Issue Orders
              </span>
              <span class="font-mono font-bold text-white">{{ metrics.movement_counts?.issue || 0 }}</span>
            </div>
            <div class="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
              <div class="bg-amber-500 h-full" :style="{ width: getPercentage(metrics.movement_counts?.issue) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Low Stock Alerts -->
      <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg">
        <h3 class="text-sm font-bold text-white flex items-center gap-2 mb-3">
          <AlertTriangle class="w-4 h-4 text-amber-400" />
          Low-Stock Attention Required
        </h3>

        <div v-if="metrics.low_stock_alerts?.length === 0" class="text-center py-6 text-slate-500 text-xs">
          <CheckCircle2 class="w-8 h-8 mx-auto text-emerald-500/40 mb-1" />
          All components have healthy stock levels.
        </div>

        <div v-else class="space-y-2 max-h-48 overflow-y-auto">
          <div
            v-for="item in metrics.low_stock_alerts"
            :key="item.part_code"
            class="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 border border-amber-500/20 text-xs"
          >
            <div>
              <span class="font-mono font-bold text-white block">{{ item.part_code }}</span>
              <span class="text-[11px] text-slate-400 truncate">{{ item.part_name }}</span>
            </div>
            <span class="px-2 py-0.5 rounded bg-amber-950 border border-amber-700/50 text-amber-400 font-mono font-bold">
              {{ item.available_quantity }} {{ item.unit }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Live Recent Transactions Stream -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-sm font-bold text-white flex items-center gap-2">
          <History class="w-4 h-4 text-emerald-400" />
          Live Stock Transactions Feed
        </h3>
        <router-link to="/transactions" class="text-xs text-emerald-400 hover:text-emerald-300 font-semibold">
          View Complete Audit Log &rarr;
        </router-link>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead>
            <tr class="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
              <th class="pb-2">TXN ID</th>
              <th class="pb-2">Type</th>
              <th class="pb-2">Material / Part</th>
              <th class="pb-2">Quantity</th>
              <th class="pb-2">From &rarr; To</th>
              <th class="pb-2">Operator</th>
              <th class="pb-2">Timestamp</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            <tr v-for="txn in metrics.recent_transactions" :key="txn._id" class="hover:bg-slate-800/40">
              <td class="py-2.5 font-mono text-slate-400">{{ txn._id }}</td>
              <td class="py-2.5">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                  :class="getTxnBadgeClass(txn.transaction_type)"
                >
                  {{ txn.transaction_type }}
                </span>
              </td>
              <td class="py-2.5 font-semibold text-white">
                {{ txn.cell_serial_no || txn.part_code || 'Bulk' }}
                <span v-if="txn.lot_batch_no" class="text-slate-400 font-mono text-[11px] block">Lot: {{ txn.lot_batch_no }}</span>
              </td>
              <td class="py-2.5 font-mono font-bold text-white">{{ txn.quantity }}</td>
              <td class="py-2.5 font-mono text-slate-300">
                <span>{{ txn.from_location_code || 'External' }}</span>
                <span class="text-slate-500 mx-1">&rarr;</span>
                <span class="text-emerald-400 font-semibold">{{ txn.to_location_code || 'Issued' }}</span>
              </td>
              <td class="py-2.5 text-slate-300">{{ txn.username }}</td>
              <td class="py-2.5 text-slate-400 font-mono">{{ formatDate(txn.timestamp) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dashboardApi from '@/api/dashboard'
import StatCard from '@/components/StatCard.vue'
import {
  Layers, Boxes, BatteryCharging, Lock, MapPin, Activity,
  AlertTriangle, CheckCircle2, History, RotateCw, ArrowLeftRight
} from 'lucide-vue-next'

const metrics = ref({})
const loading = ref(false)

const loadMetrics = async () => {
  loading.value = true
  try {
    const res = await dashboardApi.getMetrics()
    metrics.value = res.data
  } finally {
    loading.value = false
  }
}

const getPercentage = (count) => {
  const total = (metrics.value.movement_counts?.receive || 0) +
                (metrics.value.movement_counts?.transfer || 0) +
                (metrics.value.movement_counts?.issue || 0)
  return total > 0 ? Math.round(((count || 0) / total) * 100) : 0
}

const getTxnBadgeClass = (type) => {
  switch (type) {
    case 'RECEIVE': return 'bg-emerald-950 text-emerald-400 border border-emerald-800/60'
    case 'ISSUE': return 'bg-amber-950 text-amber-400 border border-amber-800/60'
    case 'TRANSFER': return 'bg-blue-950 text-blue-400 border border-blue-800/60'
    case 'RESERVE': return 'bg-purple-950 text-purple-400 border border-purple-800/60'
    default: return 'bg-slate-800 text-slate-300'
  }
}

const formatDate = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadMetrics()
})
</script>
