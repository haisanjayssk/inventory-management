<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Immutable Stock Movement Audit Trail</h1>
        <p class="text-xs text-slate-400 mt-0.5">Cryptographically sound, non-deletable records of all material transactions</p>
      </div>

      <select
        v-model="selectedType"
        @change="loadTransactions"
        class="bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-xs text-white font-mono"
      >
        <option value="">All Movement Types</option>
        <option value="RECEIVE">RECEIVE</option>
        <option value="ISSUE">ISSUE</option>
        <option value="TRANSFER">TRANSFER</option>
        <option value="RESERVE">RESERVE</option>
        <option value="RELEASE">RELEASE</option>
      </select>
    </div>

    <!-- Transactions Table -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
            <tr>
              <th class="p-3.5">Txn ID</th>
              <th class="p-3.5">Type</th>
              <th class="p-3.5">Material / Serial</th>
              <th class="p-3.5">Lot Batch</th>
              <th class="p-3.5 text-right">Quantity</th>
              <th class="p-3.5">Origin &rarr; Destination</th>
              <th class="p-3.5">Operator</th>
              <th class="p-3.5">Reference ID</th>
              <th class="p-3.5">Timestamp</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            <tr v-if="transactions.length === 0">
              <td colspan="9" class="p-8 text-center text-slate-500">No transactions recorded.</td>
            </tr>
            <tr
              v-for="txn in transactions"
              :key="txn._id"
              class="hover:bg-slate-800/40 transition-colors"
            >
              <td class="p-3.5 font-mono text-slate-400">{{ txn._id }}</td>
              <td class="p-3.5">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                  :class="getBadgeClass(txn.transaction_type)"
                >
                  {{ txn.transaction_type }}
                </span>
              </td>
              <td class="p-3.5 font-bold text-white font-mono">
                {{ txn.cell_serial_no || txn.part_code || txn.part_id }}
                <span v-if="txn.part_name" class="text-[10px] text-slate-400 font-sans block font-normal">{{ txn.part_name }}</span>
              </td>
              <td class="p-3.5 font-mono text-slate-300">{{ txn.lot_batch_no || 'N/A' }}</td>
              <td class="p-3.5 text-right font-mono font-bold text-white">{{ txn.quantity }}</td>
              <td class="p-3.5 font-mono text-slate-300">
                <span :class="txn.from_location_code ? 'text-slate-200' : 'text-slate-500'">{{ txn.from_location_code || 'External' }}</span>
                <span class="text-slate-500 mx-1">&rarr;</span>
                <span :class="txn.to_location_code ? 'text-emerald-400 font-bold' : 'text-slate-500'">{{ txn.to_location_code || 'Issued' }}</span>
              </td>
              <td class="p-3.5 text-slate-300 font-medium">{{ txn.username }}</td>
              <td class="p-3.5 font-mono text-slate-400">{{ txn.reference_id || '-' }}</td>
              <td class="p-3.5 font-mono text-slate-400 text-[11px]">{{ new Date(txn.timestamp).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import transactionsApi from '@/api/transactions'

const transactions = ref([])
const selectedType = ref('')

const loadTransactions = async () => {
  const params = { limit: 100 }
  if (selectedType.value) params.transaction_type = selectedType.value
  const res = await transactionsApi.getAll(params)
  transactions.value = res.data?.items || []
}

const getBadgeClass = (type) => {
  switch (type) {
    case 'RECEIVE': return 'bg-emerald-950 text-emerald-400 border border-emerald-800/60'
    case 'ISSUE': return 'bg-amber-950 text-amber-400 border border-amber-800/60'
    case 'TRANSFER': return 'bg-blue-950 text-blue-400 border border-blue-800/60'
    case 'RESERVE': return 'bg-purple-950 text-purple-400 border border-purple-800/60'
    case 'RELEASE': return 'bg-teal-950 text-teal-400 border border-teal-800/60'
    default: return 'bg-slate-800 text-slate-300'
  }
}

onMounted(() => {
  loadTransactions()
})
</script>
