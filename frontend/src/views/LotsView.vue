<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Lots & Supplier Batches</h1>
        <p class="text-xs text-slate-400 mt-0.5">Track manufacturing batches, dates of production, and expiration dates</p>
      </div>

      <router-link
        to="/stock-operations"
        class="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg shadow transition"
      >
        <Plus class="w-3.5 h-3.5" />
        <span>Receive New Lot</span>
      </router-link>
    </div>

    <!-- Lots Table -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
            <tr>
              <th class="p-3.5">Lot ID</th>
              <th class="p-3.5">Lot / Batch No</th>
              <th class="p-3.5">Part Reference</th>
              <th class="p-3.5">Vendor</th>
              <th class="p-3.5">Mfg Date</th>
              <th class="p-3.5">Received Date</th>
              <th class="p-3.5">Expiry Date</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            <tr v-if="lots.length === 0">
              <td colspan="7" class="p-8 text-center text-slate-500">No lots recorded.</td>
            </tr>
            <tr
              v-for="lot in lots"
              :key="lot._id"
              class="hover:bg-slate-800/40 transition-colors"
            >
              <td class="p-3.5 font-mono text-slate-400">{{ lot._id }}</td>
              <td class="p-3.5 font-mono font-bold text-white text-sm">{{ lot.lot_batch_no }}</td>
              <td class="p-3.5">
                <span class="font-mono text-emerald-400 font-bold block">{{ lot.part_code }}</span>
                <span class="text-[10px] text-slate-400">{{ lot.part_name }}</span>
              </td>
              <td class="p-3.5 text-slate-300">{{ lot.vendor_name || 'N/A' }}</td>
              <td class="p-3.5 font-mono text-slate-400">{{ lot.manufacturing_date || 'N/A' }}</td>
              <td class="p-3.5 font-mono text-slate-300">{{ lot.received_date || 'N/A' }}</td>
              <td class="p-3.5 font-mono text-slate-400">{{ lot.expiry_date || 'N/A' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import lotsApi from '@/api/lots'
import { Plus } from 'lucide-vue-next'

const lots = ref([])

onMounted(async () => {
  const res = await lotsApi.getAll()
  lots.value = res.data || []
})
</script>
