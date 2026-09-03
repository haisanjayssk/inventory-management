<template>
  <div class="space-y-6">
    <!-- Header -->
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

    <!-- Search, Filters & View Mode Switcher -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-lg flex flex-col md:flex-row gap-3 items-center justify-between">
      <div class="relative flex-1 w-full">
        <Search class="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          v-model="searchQuery"
          @keyup.enter="loadCells"
          type="text"
          placeholder="Search by serial number (e.g. CELL-2026-000001), part code, or lot..."
          class="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
        />
      </div>

      <div class="flex items-center gap-2 w-full md:w-auto">
        <select
          v-model="selectedStatus"
          @change="loadCells"
          class="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 w-full sm:w-36"
        >
          <option value="">All Statuses</option>
          <option value="AVAILABLE">AVAILABLE</option>
          <option value="IN_USE">IN_USE</option>
          <option value="DEFECTIVE">DEFECTIVE</option>
        </select>

        <!-- View Mode Switcher -->
        <div class="flex items-center bg-slate-950 border border-slate-800 rounded-xl p-0.5">
          <button
            @click="viewMode = 'box'"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition"
            :class="viewMode === 'box' ? 'bg-emerald-500 text-slate-950 shadow' : 'text-slate-400 hover:text-white'"
          >
            <Boxes class="w-3.5 h-3.5" />
            <span class="hidden sm:inline">Boxes / Trays</span>
          </button>
          <button
            @click="viewMode = 'list'"
            class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition"
            :class="viewMode === 'list' ? 'bg-emerald-500 text-slate-950 shadow' : 'text-slate-400 hover:text-white'"
          >
            <List class="w-3.5 h-3.5" />
            <span class="hidden sm:inline">Flat Table</span>
          </button>
        </div>

        <button
          v-if="viewMode === 'box' && cellBoxes.length > 0"
          @click="toggleAllBoxes"
          class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl transition whitespace-nowrap"
        >
          {{ allBoxesExpanded ? 'Collapse All' : 'Expand All' }}
        </button>
      </div>
    </div>

    <!-- 1. COMBINED BOX / TRAY VIEW (Expandable Containers) -->
    <div v-if="viewMode === 'box'" class="space-y-4">
      <div v-if="loading" class="bg-slate-900/90 border border-slate-800 rounded-2xl p-12 text-center text-slate-400">
        <div class="flex items-center justify-center gap-2">
          <span class="w-4 h-4 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></span>
          <span>Loading battery cell batches...</span>
        </div>
      </div>

      <div v-else-if="cellBoxes.length === 0" class="bg-slate-900/90 border border-slate-800 rounded-2xl p-12 text-center text-slate-500">
        No battery cells found matching criteria.
      </div>

      <!-- Box Container Cards -->
      <div
        v-for="box in cellBoxes"
        :key="box.id"
        class="bg-slate-900/90 border transition-all duration-200 rounded-2xl overflow-hidden shadow-xl"
        :class="isBoxExpanded(box.id) ? 'border-emerald-500/50 ring-1 ring-emerald-500/20 shadow-emerald-950/20' : 'border-slate-800 hover:border-slate-700'"
      >
        <!-- Box Header (Click to Expand / Collapse) -->
        <div
          @click="toggleBox(box.id)"
          class="p-4 sm:p-5 cursor-pointer bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 hover:bg-slate-850 transition select-none flex flex-col md:flex-row items-start md:items-center justify-between gap-4"
        >
          <div class="flex items-start sm:items-center gap-3.5">
            <!-- Icon Box -->
            <div
              class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0 border transition-transform duration-200"
              :class="isBoxExpanded(box.id) ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400 scale-105' : 'bg-slate-800 border-slate-700 text-slate-300'"
            >
              <BatteryCharging class="w-6 h-6" />
            </div>

            <!-- Box Info & Model -->
            <div class="space-y-1">
              <div class="flex flex-wrap items-center gap-2">
                <span class="text-sm sm:text-base font-black text-white tracking-wide font-mono">{{ box.part_code }}</span>
                <span class="text-xs text-slate-400 font-medium">&bull; {{ box.part_name }}</span>
              </div>

              <!-- Metadata Badges -->
              <div class="flex flex-wrap items-center gap-2 pt-0.5 text-xs">
                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-300">
                  <Tag class="w-3 h-3 text-purple-400" />
                  <span>Lot: <strong>{{ box.lot_batch_no }}</strong></span>
                </span>

                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-slate-950 border border-slate-800 font-mono text-[11px] text-white">
                  <MapPin class="w-3 h-3 text-cyan-400" />
                  <span>Loc: <strong class="text-emerald-400">{{ box.location_code }}</strong></span>
                </span>

                <span v-if="box.date_code" class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-400">
                  <Calendar class="w-3 h-3 text-slate-500" />
                  <span>Date: {{ box.date_code }}</span>
                </span>

                <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-lg bg-slate-950/80 border border-slate-800/80 font-mono text-[10px] text-slate-400">
                  <span>Range:</span>
                  <span class="text-emerald-400/90 font-bold">{{ box.serial_start }}</span>
                  <span>&rarr;</span>
                  <span class="text-emerald-400/90 font-bold">{{ box.serial_end }}</span>
                </span>
              </div>
            </div>
          </div>

          <!-- Quantity Stats & Expand Button -->
          <div class="flex items-center justify-between w-full md:w-auto gap-4 pt-2 md:pt-0 border-t md:border-t-0 border-slate-800/80">
            <!-- Cell Count Metrics -->
            <div class="text-right flex items-center md:flex-col md:items-end gap-2 md:gap-0.5">
              <div class="flex items-baseline gap-1.5">
                <span class="text-lg sm:text-xl font-black text-white font-mono">{{ box.cells.length }}</span>
                <span class="text-[11px] font-bold text-slate-400 uppercase">Cells</span>
              </div>
              <span class="px-2 py-0.5 rounded-md text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800/60 font-mono">
                {{ box.available_count }} AVAILABLE
              </span>
            </div>

            <!-- Expand / Collapse Toggle Pill -->
            <button
              type="button"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold transition shadow-sm"
              :class="isBoxExpanded(box.id) ? 'bg-emerald-500 text-slate-950 border-emerald-400' : 'bg-slate-800 hover:bg-slate-750 text-slate-300 border-slate-700'"
            >
              <span>{{ isBoxExpanded(box.id) ? 'Hide Cells' : 'Expand Cells' }}</span>
              <ChevronDown
                class="w-4 h-4 transition-transform duration-200"
                :class="isBoxExpanded(box.id) ? 'rotate-180' : ''"
              />
            </button>
          </div>
        </div>

        <!-- Expanded Box Body (Visible ONLY when box is expanded) -->
        <div v-if="isBoxExpanded(box.id)" class="border-t border-slate-800 bg-slate-950/70 p-4 sm:p-5 space-y-4">
          <!-- Box Action Header -->
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800/80">
            <div class="flex items-center gap-2">
              <span class="text-xs font-bold text-white uppercase tracking-wider">Serialized Cell Units in this Tray:</span>
              <span class="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[11px] font-mono text-emerald-400 font-bold">
                {{ box.cells.length }} Total
              </span>
            </div>

            <div class="text-xs text-slate-400">
              Click any serial number to inspect its full MES manufacturing lifecycle journey.
            </div>
          </div>

          <!-- Interactive Serial Number Grid Pills -->
          <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-2">
            <div
              v-for="cell in box.cells"
              :key="cell._id"
              @click="openCellDetail(cell.cell_serial_no)"
              class="group relative flex items-center justify-between p-2.5 rounded-xl bg-slate-900 border border-slate-800/90 hover:border-emerald-500 hover:bg-slate-850 hover:shadow-lg hover:shadow-emerald-950/30 cursor-pointer transition-all duration-150"
            >
              <div class="flex items-center gap-1.5 min-w-0">
                <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="cell.status === 'AVAILABLE' ? 'bg-emerald-400' : 'bg-amber-400'"></span>
                <span class="font-mono text-[11px] font-bold text-slate-200 group-hover:text-emerald-400 truncate">
                  {{ cell.cell_serial_no }}
                </span>
              </div>
              <ArrowUpRight class="w-3.5 h-3.5 text-slate-500 group-hover:text-emerald-400 opacity-0 group-hover:opacity-100 transition shrink-0 ml-1" />
            </div>
          </div>

          <!-- Compact Detailed Table toggle option inside box -->
          <div class="pt-2">
            <details class="text-xs group">
              <summary class="cursor-pointer text-slate-400 hover:text-white font-semibold flex items-center gap-1 select-none">
                <span class="group-open:hidden">Show Line-by-Line Table View &darr;</span>
                <span class="hidden group-open:inline">Hide Table View &uarr;</span>
              </summary>

              <div class="mt-3 overflow-x-auto border border-slate-800/80 rounded-xl bg-slate-900">
                <table class="w-full text-left text-xs">
                  <thead class="bg-slate-950 border-b border-slate-800 text-slate-400 uppercase text-[10px] font-semibold">
                    <tr>
                      <th class="p-2.5">Serial No</th>
                      <th class="p-2.5">Location</th>
                      <th class="p-2.5">Date Code</th>
                      <th class="p-2.5">Status</th>
                      <th class="p-2.5 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-slate-800/50">
                    <tr v-for="cell in box.cells" :key="cell._id" class="hover:bg-slate-800/40">
                      <td class="p-2.5 font-mono font-bold text-emerald-400">{{ cell.cell_serial_no }}</td>
                      <td class="p-2.5 font-mono text-white">{{ cell.location_code }}</td>
                      <td class="p-2.5 font-mono text-slate-400">{{ cell.date_code || cell.manufacturing_date || 'N/A' }}</td>
                      <td class="p-2.5">
                        <span class="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                          {{ cell.status }}
                        </span>
                      </td>
                      <td class="p-2.5 text-right">
                        <button
                          @click="openCellDetail(cell.cell_serial_no)"
                          class="px-2 py-0.5 bg-slate-800 hover:bg-emerald-900 text-emerald-300 text-[10px] font-bold rounded"
                        >
                          Trace &rarr;
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. FLAT TABLE VIEW (Classic List Mode) -->
    <div v-else class="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
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
import { ref, computed, onMounted } from 'vue'
import cellsApi from '@/api/cells'
import Modal from '@/components/Modal.vue'
import BarcodeScannerModal from '@/components/BarcodeScannerModal.vue'
import {
  Battery,
  BatteryCharging,
  QrCode,
  Search,
  GitBranch,
  Check,
  History,
  Boxes,
  List,
  ChevronDown,
  Tag,
  MapPin,
  Calendar,
  ArrowUpRight
} from 'lucide-vue-next'

const cells = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedStatus = ref('')
const viewMode = ref('box') // 'box' or 'list'
const expandedBoxIds = ref(new Set())

const showScannerModal = ref(false)
const showDetailModal = ref(false)
const selectedCell = ref(null)

// Group cells into Combined Boxes / Trays by Part + Lot + Location
const cellBoxes = computed(() => {
  const groups = {}

  for (const cell of cells.value) {
    const partKey = cell.part_code || cell.part_id || 'UNKNOWN_PART'
    const lotKey = cell.lot_batch_no || cell.lot_id || 'DEFAULT_LOT'
    const locKey = cell.location_code || 'UNASSIGNED'
    const boxId = `${partKey}__${lotKey}__${locKey}`

    if (!groups[boxId]) {
      groups[boxId] = {
        id: boxId,
        part_code: cell.part_code || 'Cell Model',
        part_name: cell.part_name || '',
        lot_batch_no: cell.lot_batch_no || 'N/A',
        location_code: cell.location_code || 'Unassigned',
        date_code: cell.date_code || cell.manufacturing_date || '',
        available_count: 0,
        in_use_count: 0,
        defective_count: 0,
        serial_start: cell.cell_serial_no,
        serial_end: cell.cell_serial_no,
        cells: []
      }
    }

    groups[boxId].cells.push(cell)
    if (cell.status === 'AVAILABLE') groups[boxId].available_count++
    else if (cell.status === 'IN_USE') groups[boxId].in_use_count++
    else if (cell.status === 'DEFECTIVE') groups[boxId].defective_count++

    // Update serial start / end for range display
    if (cell.cell_serial_no < groups[boxId].serial_start) {
      groups[boxId].serial_start = cell.cell_serial_no
    }
    if (cell.cell_serial_no > groups[boxId].serial_end) {
      groups[boxId].serial_end = cell.cell_serial_no
    }
  }

  return Object.values(groups)
})

const isBoxExpanded = (boxId) => {
  return expandedBoxIds.value.has(boxId)
}

const toggleBox = (boxId) => {
  if (expandedBoxIds.value.has(boxId)) {
    expandedBoxIds.value.delete(boxId)
  } else {
    expandedBoxIds.value.add(boxId)
  }
}

const allBoxesExpanded = computed(() => {
  return cellBoxes.value.length > 0 && cellBoxes.value.every(b => expandedBoxIds.value.has(b.id))
})

const toggleAllBoxes = () => {
  if (allBoxesExpanded.value) {
    expandedBoxIds.value.clear()
  } else {
    for (const b of cellBoxes.value) {
      expandedBoxIds.value.add(b.id)
    }
  }
}

const loadCells = async () => {
  loading.value = true
  try {
    const params = { limit: 500 }
    if (searchQuery.value) params.search = searchQuery.value
    if (selectedStatus.value) params.status = selectedStatus.value

    const res = await cellsApi.getAll(params)
    cells.value = res.data?.items || []

    // If search query is entered, auto-expand matching boxes
    if (searchQuery.value && cellBoxes.value.length > 0) {
      expandedBoxIds.value.clear()
      for (const b of cellBoxes.value) {
        expandedBoxIds.value.add(b.id)
      }
    }
  } catch (err) {
    // Handled by toast
  } finally {
    loading.value = false
  }
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
