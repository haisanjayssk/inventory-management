<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Battery Cells & MES Traceability</h1>
        <p class="text-xs text-slate-400 mt-0.5">Individual serial-number tracking, warehouse location, and manufacturing lifecycle</p>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="openScanner"
          class="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg shadow transition"
        >
          <QrCode class="w-4 h-4" />
          <span>Scan Cell Barcode / DataMatrix</span>
        </button>
      </div>
    </div>

    <!-- Search & Filters -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-lg flex flex-col sm:flex-row gap-3 items-center">
      <div class="relative flex-1 w-full">
        <Search class="w-4 h-4 text-slate-500 absolute left-3 top-3" />
        <input
          v-model="searchQuery"
          @keyup.enter="loadCells"
          type="text"
          placeholder="Search by exact cell serial (e.g. CELL-2026-000001)..."
          class="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono font-bold"
        />
      </div>

      <select
        v-model="selectedStatus"
        @change="loadCells"
        class="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 w-full sm:w-48"
      >
        <option value="">All Statuses</option>
        <option value="AVAILABLE">AVAILABLE</option>
        <option value="IN_USE">IN_USE</option>
        <option value="DEFECTIVE">DEFECTIVE</option>
      </select>

      <button
        @click="loadCells"
        class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-bold rounded-xl transition w-full sm:w-auto"
      >
        Filter
      </button>
    </div>

    <!-- Cells Table -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
            <tr>
              <th class="p-3.5">Cell Serial No</th>
              <th class="p-3.5">Cell Model / Part</th>
              <th class="p-3.5">Lot Batch</th>
              <th class="p-3.5">Current Location</th>
              <th class="p-3.5">Date Code</th>
              <th class="p-3.5">Status</th>
              <th class="p-3.5 text-right">MES Traceability</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            <tr v-if="cells.length === 0">
              <td colspan="7" class="p-8 text-center text-slate-500">
                No battery cells found matching criteria.
              </td>
            </tr>
            <tr
              v-for="cell in cells"
              :key="cell._id"
              class="hover:bg-slate-800/40 transition-colors"
            >
              <td class="p-3.5 font-mono font-bold text-emerald-400 flex items-center gap-2">
                <Battery class="w-3.5 h-3.5 text-emerald-400" />
                <span>{{ cell.cell_serial_no }}</span>
              </td>
              <td class="p-3.5">
                <span class="text-white font-medium block">{{ cell.part_code }}</span>
                <span class="text-[10px] text-slate-400">{{ cell.part_name }}</span>
              </td>
              <td class="p-3.5 font-mono text-slate-300">{{ cell.lot_batch_no }}</td>
              <td class="p-3.5">
                <span class="px-2.5 py-1 rounded bg-slate-950 border border-slate-800 font-mono font-bold text-white text-[11px]">
                  {{ cell.location_code || 'Unassigned' }}
                </span>
              </td>
              <td class="p-3.5 font-mono text-slate-400">{{ cell.date_code || cell.manufacturing_date || 'N/A' }}</td>
              <td class="p-3.5">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider"
                  :class="cell.status === 'AVAILABLE' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800/60' : 'bg-amber-950 text-amber-400 border border-amber-800/60'"
                >
                  {{ cell.status }}
                </span>
              </td>
              <td class="p-3.5 text-right">
                <button
                  @click="openCellDetail(cell.cell_serial_no)"
                  class="px-3 py-1 bg-emerald-950 hover:bg-emerald-900 border border-emerald-700/50 text-emerald-300 text-xs font-bold rounded-lg transition"
                >
                  Trace Cell &rarr;
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Cell Traceability Modal (Full MES Journey Timeline) -->
    <Modal v-model="showDetailModal" title="Cell Traceability & MES History" maxWidth="max-w-2xl">
      <template #icon>
        <BatteryCharging class="w-5 h-5" />
      </template>

      <div v-if="selectedCell" class="space-y-6">
        <!-- Cell Info Card -->
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-950 p-4 rounded-xl border border-slate-800 text-xs">
          <div>
            <span class="text-slate-500 uppercase text-[10px] block">Serial No</span>
            <span class="font-mono font-bold text-emerald-400 text-sm">{{ selectedCell.cell?.cell_serial_no }}</span>
          </div>
          <div>
            <span class="text-slate-500 uppercase text-[10px] block">Part Model</span>
            <span class="font-bold text-white">{{ selectedCell.cell?.part_code }}</span>
          </div>
          <div>
            <span class="text-slate-500 uppercase text-[10px] block">Current Location</span>
            <span class="font-mono font-bold text-white bg-slate-900 px-1.5 py-0.5 rounded border border-slate-800">
              {{ selectedCell.cell?.location?.location_code || 'N/A' }}
            </span>
          </div>
          <div>
            <span class="text-slate-500 uppercase text-[10px] block">Status</span>
            <span class="font-bold text-emerald-400">{{ selectedCell.cell?.status }}</span>
          </div>
        </div>

        <!-- MES Integration Readiness Timeline -->
        <div>
          <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center gap-1.5">
            <GitBranch class="w-4 h-4 text-emerald-400" />
            Manufacturing Lifecycle Journey (MES Ready)
          </h4>

          <div class="space-y-3 relative pl-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
            <div
              v-for="(step, idx) in selectedCell.mes_traceability"
              :key="idx"
              class="relative"
            >
              <div
                class="absolute -left-6 top-1 w-4 h-4 rounded-full border-2 flex items-center justify-center text-[10px]"
                :class="step.status === 'COMPLETED' ? 'bg-emerald-500 border-emerald-400 text-slate-950 font-bold' : 'bg-slate-900 border-slate-700 text-slate-500'"
              >
                <Check v-if="step.status === 'COMPLETED'" class="w-2.5 h-2.5" />
              </div>
              <div class="bg-slate-950/60 border border-slate-800 rounded-xl p-3 text-xs">
                <div class="flex items-center justify-between">
                  <span class="font-bold font-mono text-white">{{ step.step }}</span>
                  <span
                    class="text-[10px] font-mono px-2 py-0.5 rounded font-bold"
                    :class="step.status === 'COMPLETED' ? 'text-emerald-400 bg-emerald-950' : 'text-slate-400 bg-slate-900'"
                  >
                    {{ step.status }}
                  </span>
                </div>
                <p class="text-slate-400 mt-1 text-[11px]">{{ step.notes }}</p>
                <span v-if="step.timestamp" class="text-[10px] text-slate-400 font-mono mt-1 block">
                  {{ new Date(step.timestamp).toLocaleString() }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Inventory Transaction History Log -->
        <div>
          <h4 class="text-xs font-bold uppercase tracking-wider text-slate-300 mb-2 flex items-center gap-1.5">
            <History class="w-4 h-4 text-emerald-400" />
            Physical Movement History
          </h4>

          <div class="space-y-2">
            <div
              v-for="txn in selectedCell.history"
              :key="txn._id"
              class="p-2.5 rounded-xl bg-slate-950/40 border border-slate-800 text-xs flex items-center justify-between"
            >
              <div>
                <span class="font-bold text-white font-mono mr-2">[{{ txn.transaction_type }}]</span>
                <span class="text-slate-300 font-mono">
                  {{ txn.from_location_code || 'Origin' }} &rarr; {{ txn.to_location_code || 'Destination' }}
                </span>
                <p class="text-[10px] text-slate-400 mt-0.5">{{ txn.description }}</p>
              </div>
              <span class="text-[10px] text-slate-400 font-mono">{{ new Date(txn.timestamp).toLocaleString() }}</span>
            </div>
          </div>
        </div>
      </div>
    </Modal>

    <BarcodeScannerModal v-model="showScannerModal" @scan="onBarcodeScanned" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import cellsApi from '@/api/cells'
import Modal from '@/components/Modal.vue'
import BarcodeScannerModal from '@/components/BarcodeScannerModal.vue'
import {
  Battery, BatteryCharging, QrCode, Search, GitBranch,
  Check, History
} from 'lucide-vue-next'

const cells = ref([])
const searchQuery = ref('')
const selectedStatus = ref('')
const showScannerModal = ref(false)
const showDetailModal = ref(false)
const selectedCell = ref(null)

const loadCells = async () => {
  const params = { limit: 100 }
  if (searchQuery.value) params.search = searchQuery.value
  if (selectedStatus.value) params.status = selectedStatus.value

  const res = await cellsApi.getAll(params)
  cells.value = res.data?.items || []
}

const openScanner = () => {
  showScannerModal.value = true
}

const onBarcodeScanned = (code) => {
  searchQuery.value = code
  loadCells()
  openCellDetail(code)
}

const openCellDetail = async (serialNo) => {
  const res = await cellsApi.getBySerial(serialNo)
  selectedCell.value = res.data
  showDetailModal.value = true
}

onMounted(() => {
  loadCells()
})
</script>
