<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Quantity-Tracked Inventory</h1>
        <p class="text-xs text-slate-400 mt-0.5">Current stock, allocations, and warehouse bin locations</p>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="exportCsv"
          class="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 border border-slate-800 hover:bg-slate-800 text-xs font-semibold text-slate-300 rounded-lg transition"
        >
          <Download class="w-3.5 h-3.5" />
          <span>Export CSV</span>
        </button>
        <router-link
          to="/stock-operations"
          class="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg shadow transition"
        >
          <Plus class="w-3.5 h-3.5" />
          <span>Receive / Move</span>
        </router-link>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-lg grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      <div class="relative">
        <Search class="w-4 h-4 text-slate-500 absolute left-3 top-3" />
        <input
          v-model="searchQuery"
          @input="loadInventory"
          type="text"
          placeholder="Search by part code, name, lot..."
          class="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
        />
      </div>

      <select
        v-model="selectedPartType"
        @change="loadInventory"
        class="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 font-mono"
      >
        <option value="">All Part Types</option>
        <option v-for="pt in partTypes" :key="pt._id" :value="pt._id">{{ pt.part_type_name }}</option>
      </select>

      <select
        v-model="selectedStatus"
        @change="loadInventory"
        class="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300"
      >
        <option value="">All Stock Statuses</option>
        <option value="AVAILABLE">AVAILABLE</option>
        <option value="OUT_OF_STOCK">OUT_OF_STOCK</option>
      </select>

      <div class="flex items-center justify-end text-xs text-slate-400 font-mono">
        Total Items: <span class="text-emerald-400 font-bold ml-1.5">{{ inventory.length }}</span>
      </div>
    </div>

    <!-- Inventory Table -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
            <tr>
              <th class="p-3.5">Part Code</th>
              <th class="p-3.5">Part Name & Type</th>
              <th class="p-3.5">Lot / Batch</th>
              <th class="p-3.5">Location (NFC)</th>
              <th class="p-3.5 text-right">Total Qty</th>
              <th class="p-3.5 text-right">Available</th>
              <th class="p-3.5 text-right">Reserved</th>
              <th class="p-3.5">Status</th>
              <th class="p-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            <tr v-if="inventory.length === 0">
              <td colspan="9" class="p-8 text-center text-slate-500">
                No matching inventory records found.
              </td>
            </tr>
            <tr
              v-for="item in inventory"
              :key="item._id"
              class="hover:bg-slate-800/40 transition-colors"
            >
              <td class="p-3.5 font-mono font-bold text-emerald-400">{{ item.part_code }}</td>
              <td class="p-3.5">
                <span class="text-white font-medium block">{{ item.part_name }}</span>
                <span class="text-[10px] text-slate-400 uppercase font-mono">{{ item.part_type_name || 'Component' }}</span>
              </td>
              <td class="p-3.5 font-mono text-slate-300">{{ item.lot_batch_no }}</td>
              <td class="p-3.5">
                <span class="px-2.5 py-1 rounded bg-slate-950 border border-slate-800 font-mono font-bold text-white text-[11px]">
                  {{ item.location_code }}
                </span>
              </td>
              <td class="p-3.5 text-right font-mono font-bold text-white text-sm">
                {{ item.quantity?.toLocaleString() }} <span class="text-[10px] text-slate-400 font-normal">{{ item.unit_of_measure }}</span>
              </td>
              <td class="p-3.5 text-right font-mono font-bold text-emerald-400 text-sm">
                {{ item.available_quantity?.toLocaleString() }}
              </td>
              <td class="p-3.5 text-right font-mono text-amber-400">
                {{ item.reserved_quantity?.toLocaleString() }}
                <span v-if="item.reserved_for" class="text-[10px] text-slate-400 block">({{ item.reserved_for }})</span>
              </td>
              <td class="p-3.5">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                  :class="item.quantity > 0 ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60' : 'bg-rose-950 text-rose-400 border border-rose-800/60'"
                >
                  {{ item.status }}
                </span>
              </td>
              <td class="p-3.5 text-right">
                <router-link
                  :to="{ path: '/stock-operations', query: { tab: 'transfer', part: item.part_id } }"
                  class="text-xs text-slate-400 hover:text-emerald-400 font-semibold transition"
                >
                  Move &rarr;
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import inventoryApi from '@/api/inventory'
import partTypesApi from '@/api/partTypes'
import { Search, Download, Plus } from 'lucide-vue-next'

const inventory = ref([])
const partTypes = ref([])
const searchQuery = ref('')
const selectedPartType = ref('')
const selectedStatus = ref('')

const loadInventory = async () => {
  const params = {}
  if (searchQuery.value) params.search = searchQuery.value
  if (selectedPartType.value) params.part_type_id = selectedPartType.value
  if (selectedStatus.value) params.status = selectedStatus.value

  const res = await inventoryApi.getAll(params)
  inventory.value = res.data?.items || []
}

const exportCsv = () => {
  const headers = ['Part Code', 'Part Name', 'Type', 'Lot', 'Location', 'Total Qty', 'Available', 'Reserved', 'Status']
  const rows = inventory.value.map(i => [
    i.part_code,
    `"${i.part_name}"`,
    i.part_type_name,
    i.lot_batch_no,
    i.location_code,
    i.quantity,
    i.available_quantity,
    i.reserved_quantity,
    i.status
  ])
  const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `mes_inventory_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
}

onMounted(async () => {
  const ptRes = await partTypesApi.getAll()
  partTypes.value = ptRes.data || []
  loadInventory()
})
</script>
