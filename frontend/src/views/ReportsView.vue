<template>
  <div class="space-y-6">
    <div>
      <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Inventory & Warehouse Reports</h1>
      <p class="text-xs text-slate-400 mt-0.5">Aggregated stock analytics, location distribution, and inventory valuation</p>
    </div>

    <!-- Stock By Part Summary -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl p-5 space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-bold text-white flex items-center gap-2">
          <BarChart3 class="w-4 h-4 text-emerald-400" />
          Stock Aggregation by Part Number
        </h3>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
            <tr>
              <th class="p-3">Part Code</th>
              <th class="p-3">Part Name</th>
              <th class="p-3 text-right">Total Stock</th>
              <th class="p-3 text-right">Available</th>
              <th class="p-3 text-right">Reserved</th>
              <th class="p-3 text-right">Bins Count</th>
              <th class="p-3 text-right">Lots Count</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60 font-mono">
            <tr v-for="r in stockReport" :key="r.part_id" class="hover:bg-slate-800/40">
              <td class="p-3 font-bold text-emerald-400">{{ r.part_code }}</td>
              <td class="p-3 font-sans text-white">{{ r.part_name }}</td>
              <td class="p-3 text-right font-bold text-white">{{ r.total_quantity?.toLocaleString() }} {{ r.unit }}</td>
              <td class="p-3 text-right font-bold text-emerald-400">{{ r.available_quantity?.toLocaleString() }}</td>
              <td class="p-3 text-right text-amber-400">{{ r.reserved_quantity?.toLocaleString() }}</td>
              <td class="p-3 text-right text-slate-300">{{ r.locations_count }}</td>
              <td class="p-3 text-right text-slate-300">{{ r.lots_count }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import reportsApi from '@/api/reports'
import { BarChart3 } from 'lucide-vue-next'

const stockReport = ref([])

onMounted(async () => {
  const res = await reportsApi.getStockByPart()
  stockReport.value = res.data || []
})
</script>
