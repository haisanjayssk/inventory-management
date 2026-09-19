<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight flex items-center gap-2">
          <History class="w-6 h-6 text-emerald-400" />
          <span>Stock Movement Audit Trail</span>
        </h1>
        <p class="text-xs text-slate-400 mt-0.5">Cryptographically sound, immutable records of all inventory transactions</p>
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
          <ArrowRightLeft class="w-3.5 h-3.5" />
          <span>Stock Operations</span>
        </router-link>
      </div>
    </div>

    <!-- Movement Summary Metrics -->
    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
      <div
        @click="selectFilterType('')"
        class="p-4 rounded-2xl border transition-all cursor-pointer select-none"
        :class="selectedType === '' ? 'bg-emerald-950/30 border-emerald-500 shadow-md shadow-emerald-950/20 ring-1 ring-emerald-500/30' : 'bg-slate-900/90 border-slate-800 hover:border-slate-700'"
      >
        <span class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Total Movements</span>
        <div class="text-2xl font-black text-white font-mono mt-1">{{ totalCount }}</div>
      </div>

      <div
        @click="selectFilterType('RECEIVE')"
        class="p-4 rounded-2xl border transition-all cursor-pointer select-none"
        :class="selectedType === 'RECEIVE' ? 'bg-emerald-950/30 border-emerald-500 shadow-md shadow-emerald-950/20 ring-1 ring-emerald-500/30' : 'bg-slate-900/90 border-slate-800 hover:border-slate-700'"
      >
        <span class="text-[10px] uppercase font-bold text-emerald-400 tracking-wider">Received</span>
        <div class="text-2xl font-black text-white font-mono mt-1">{{ receiveCount }}</div>
      </div>

      <div
        @click="selectFilterType('ISSUE')"
        class="p-4 rounded-2xl border transition-all cursor-pointer select-none"
        :class="selectedType === 'ISSUE' ? 'bg-amber-950/30 border-amber-500 shadow-md shadow-amber-950/20 ring-1 ring-amber-500/30' : 'bg-slate-900/90 border-slate-800 hover:border-slate-700'"
      >
        <span class="text-[10px] uppercase font-bold text-amber-400 tracking-wider">Issued</span>
        <div class="text-2xl font-black text-white font-mono mt-1">{{ issueCount }}</div>
      </div>

      <div
        @click="selectFilterType('TRANSFER')"
        class="p-4 rounded-2xl border transition-all cursor-pointer select-none"
        :class="selectedType === 'TRANSFER' ? 'bg-blue-950/30 border-blue-500 shadow-md shadow-blue-950/20 ring-1 ring-blue-500/30' : 'bg-slate-900/90 border-slate-800 hover:border-slate-700'"
      >
        <span class="text-[10px] uppercase font-bold text-blue-400 tracking-wider">Transferred</span>
        <div class="text-2xl font-black text-white font-mono mt-1">{{ transferCount }}</div>
      </div>
    </div>

    <!-- Filters Bar -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-lg flex flex-col sm:flex-row items-center justify-between gap-3">
      <div class="flex flex-wrap items-center gap-3 w-full sm:w-auto">
        <div class="relative min-w-[220px]">
          <Search class="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search material, serial, ref, user..."
            class="w-full bg-slate-950 border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-emerald-500"
          />
        </div>

        <select
          v-model="selectedType"
          class="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-emerald-500"
        >
          <option value="">All Movement Types</option>
          <option value="RECEIVE">RECEIVE</option>
          <option value="ISSUE">ISSUE (Standard & Indent)</option>
          <option value="TRANSFER">TRANSFER</option>
          <option value="RESERVE">RESERVE</option>
          <option value="RELEASE">RELEASE</option>
        </select>
      </div>

      <div class="text-xs font-mono text-slate-400 flex items-center gap-2">
        <span>Records: <b class="text-emerald-400">{{ filteredTransactions.length }}</b></span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-3">
      <div class="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
      <span class="text-xs font-mono">Loading transaction audit trail...</span>
    </div>

    <!-- Transactions Table -->
    <div v-else class="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
            <tr>
              <th class="p-3.5">Txn ID</th>
              <th class="p-3.5">Type</th>
              <th class="p-3.5">Material / Serial</th>
              <th class="p-3.5">Lot / Batch</th>
              <th class="p-3.5 text-right">Quantity</th>
              <th class="p-3.5">Origin &rarr; Destination</th>
              <th class="p-3.5">Operator</th>
              <th class="p-3.5">Reference ID</th>
              <th class="p-3.5">Timestamp</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            <tr v-if="filteredTransactions.length === 0">
              <td colspan="9" class="p-8 text-center text-slate-500">No transactions recorded matching current filters.</td>
            </tr>
            <tr
              v-for="txn in filteredTransactions"
              :key="txn._id"
              @click="openDetail(txn)"
              class="hover:bg-slate-800/40 transition-colors cursor-pointer"
            >
              <td class="p-3.5 font-mono text-slate-400">{{ txn.t_id || txn._id }}</td>
              <td class="p-3.5">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                  :class="getBadgeClass(txn.transaction_type)"
                >
                  {{ txn.transaction_type }}
                </span>
              </td>
              <td class="p-3.5 font-bold text-white font-mono">
                {{ txn.cell_serial_no || txn.serial_number || txn.part_code || txn.item_code || txn.part_id }}
                <span v-if="txn.part_name || txn.item_name" class="text-[10px] text-slate-400 font-sans block font-normal">
                  {{ txn.part_name || txn.item_name }}
                </span>
              </td>
              <td class="p-3.5 font-mono text-slate-300">{{ txn.lot_batch_no || txn.lot_number || 'N/A' }}</td>
              <td class="p-3.5 text-right font-mono font-bold text-white text-sm">{{ txn.quantity?.toLocaleString() }}</td>
              <td class="p-3.5 font-mono text-slate-300">
                <span :class="txn.from_location_code ? 'text-slate-200' : 'text-slate-500'">{{ txn.from_location_code || 'External / Supplier' }}</span>
                <span class="text-slate-500 mx-1">&rarr;</span>
                <span :class="txn.to_location_code ? 'text-emerald-400 font-bold' : 'text-slate-500'">{{ txn.to_location_code || 'Issued Out' }}</span>
              </td>
              <td class="p-3.5 text-slate-300 font-medium">{{ txn.username || txn.performed_by }}</td>
              <td class="p-3.5 font-mono text-slate-400">{{ txn.reference_id || txn.reference?.po_number || txn.reference?.indent_number || '-' }}</td>
              <td class="p-3.5 font-mono text-slate-400 text-[11px]">{{ new Date(txn.timestamp).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Detail Modal -->
    <Modal v-model="showDetailModal" :title="`Transaction ${selectedTxn?.t_id || selectedTxn?._id}`" maxWidth="max-w-lg">
      <div v-if="selectedTxn" class="space-y-4">
        <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-2 font-mono">
          <div class="flex justify-between"><span class="text-slate-500">Type:</span> <span class="text-emerald-400 font-bold">{{ selectedTxn.transaction_type }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Material:</span> <span class="text-white">{{ selectedTxn.item_code || selectedTxn.part_code }} ({{ selectedTxn.item_name || selectedTxn.part_name }})</span></div>
          <div v-if="selectedTxn.serial_number" class="flex justify-between"><span class="text-slate-500">Serial:</span> <span class="text-emerald-300">{{ selectedTxn.serial_number }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Lot:</span> <span class="text-white">{{ selectedTxn.lot_number || selectedTxn.lot_batch_no || 'N/A' }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Quantity:</span> <span class="text-emerald-400 font-bold">{{ selectedTxn.quantity }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">From Location:</span> <span class="text-slate-300">{{ selectedTxn.from_location_code || 'External' }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">To Location:</span> <span class="text-slate-300">{{ selectedTxn.to_location_code || 'Issued Out' }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Performed By:</span> <span class="text-white">{{ selectedTxn.username || selectedTxn.performed_by }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Timestamp:</span> <span class="text-slate-400">{{ new Date(selectedTxn.timestamp).toLocaleString() }}</span></div>
          <div v-if="selectedTxn.remarks" class="pt-2 border-t border-slate-800 text-slate-300 font-sans">
            <span class="text-slate-500 text-[10px] block font-mono uppercase">Remarks:</span>
            {{ selectedTxn.remarks }}
          </div>
        </div>
      </div>

      <template #footer>
        <button type="button" @click="showDetailModal = false" class="px-4 py-2 bg-slate-800 text-xs font-bold text-slate-300 rounded-xl">Close</button>
      </template>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import transactionsApi from '@/api/transactions'
import Modal from '@/components/Modal.vue'
import { History, Download, ArrowRightLeft, Search } from 'lucide-vue-next'

const allTransactions = ref([])
const selectedType = ref('')
const searchQuery = ref('')
const loading = ref(false)
const showDetailModal = ref(false)
const selectedTxn = ref(null)

const loadTransactions = async () => {
  loading.value = true
  try {
    const res = await transactionsApi.getAll({ limit: 500 })
    allTransactions.value = res.data?.items || []
  } catch (e) {
    console.error('Failed to load transactions audit', e)
  } finally {
    loading.value = false
  }
}

const selectFilterType = (type) => {
  if (selectedType.value === type) {
    selectedType.value = ''
  } else {
    selectedType.value = type
  }
}

const totalCount = computed(() => allTransactions.value.length)
const receiveCount = computed(() => allTransactions.value.filter(t => t.transaction_type === 'RECEIVE').length)
const issueCount = computed(() => allTransactions.value.filter(t => t.transaction_type === 'ISSUE' || t.transaction_type === 'INDENT_ISSUE').length)
const transferCount = computed(() => allTransactions.value.filter(t => t.transaction_type === 'TRANSFER').length)

const filteredTransactions = computed(() => {
  let list = allTransactions.value

  if (selectedType.value) {
    if (selectedType.value === 'ISSUE') {
      list = list.filter(t => t.transaction_type === 'ISSUE' || t.transaction_type === 'INDENT_ISSUE')
    } else {
      list = list.filter(t => t.transaction_type === selectedType.value)
    }
  }

  if (!searchQuery.value) return list
  const q = searchQuery.value.trim().toLowerCase()
  return list.filter(t =>
    (t.t_id && t.t_id.toLowerCase().includes(q)) ||
    (t._id && t._id.toLowerCase().includes(q)) ||
    (t.part_code && t.part_code.toLowerCase().includes(q)) ||
    (t.item_code && t.item_code.toLowerCase().includes(q)) ||
    (t.part_name && t.part_name.toLowerCase().includes(q)) ||
    (t.item_name && t.item_name.toLowerCase().includes(q)) ||
    (t.serial_number && t.serial_number.toLowerCase().includes(q)) ||
    (t.lot_number && t.lot_number.toLowerCase().includes(q)) ||
    (t.lot_batch_no && t.lot_batch_no.toLowerCase().includes(q)) ||
    (t.username && t.username.toLowerCase().includes(q)) ||
    (t.performed_by && t.performed_by.toLowerCase().includes(q)) ||
    (t.reference_id && String(t.reference_id).toLowerCase().includes(q)) ||
    (t.remarks && t.remarks.toLowerCase().includes(q))
  )
})

const openDetail = (txn) => {
  selectedTxn.value = txn
  showDetailModal.value = true
}

const exportCsv = () => {
  const headers = ['Txn ID', 'Type', 'Part Code', 'Part Name', 'Serial', 'Lot', 'Qty', 'From Loc', 'To Loc', 'User', 'Ref', 'Timestamp']
  const rows = filteredTransactions.value.map(t => [
    t.t_id || t._id,
    t.transaction_type,
    t.item_code || t.part_code,
    `"${t.item_name || t.part_name || ''}"`,
    t.serial_number || '',
    t.lot_number || t.lot_batch_no || '',
    t.quantity,
    t.from_location_code || 'External',
    t.to_location_code || 'Issued',
    t.username || t.performed_by,
    t.reference_id || '',
    t.timestamp
  ])
  const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement('a')
  link.setAttribute('href', encodedUri)
  link.setAttribute('download', `mes_transactions_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
}

const getBadgeClass = (type) => {
  switch (type) {
    case 'RECEIVE': return 'bg-emerald-950 text-emerald-400 border border-emerald-800/60'
    case 'ISSUE':
    case 'INDENT_ISSUE': return 'bg-amber-950 text-amber-400 border border-amber-800/60'
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
