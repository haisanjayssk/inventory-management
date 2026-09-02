<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Warehouse Locations & NFC Hierarchy</h1>
        <p class="text-xs text-slate-400 mt-0.5">Physical storage bins, NFC tag identifiers, and real-time bin occupancy</p>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="openNfcTester"
          class="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-lg border border-slate-700 transition"
        >
          <Radio class="w-4 h-4 text-emerald-400" />
          <span>Test NFC Scan</span>
        </button>

        <button
          @click="showBulkModal = true"
          class="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg shadow transition"
        >
          <Wand2 class="w-3.5 h-3.5" />
          <span>Bulk Location Generator</span>
        </button>
      </div>
    </div>

    <!-- Warehouse Filter & Stats -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-lg flex flex-col sm:flex-row items-center justify-between gap-4">
      <div class="flex items-center gap-3 w-full sm:w-auto">
        <select
          v-model="filterWarehouse"
          @change="loadLocations"
          class="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white font-mono"
        >
          <option value="">All Warehouses</option>
          <option value="E">EMS Warehouse (E)</option>
          <option value="BP">Battery Pack Store (BP)</option>
        </select>

        <select
          v-model="filterStatus"
          @change="loadLocations"
          class="bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
        >
          <option value="">All Statuses</option>
          <option value="ACTIVE">ACTIVE</option>
          <option value="MAINTENANCE">MAINTENANCE</option>
        </select>
      </div>

      <div class="text-xs font-mono text-slate-400 flex gap-4">
        <span>Total: <b class="text-white">{{ locations.length }}</b></span>
        <span>Occupied: <b class="text-emerald-400">{{ occupiedCount }}</b></span>
        <span>Empty: <b class="text-slate-300">{{ locations.length - occupiedCount }}</b></span>
      </div>
    </div>

    <!-- Locations Grid -->
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
      <div
        v-for="loc in locations"
        :key="loc._id"
        class="bg-slate-900 border rounded-2xl p-3.5 shadow transition-all duration-200 hover:scale-[1.02] flex flex-col justify-between"
        :class="loc.is_occupied ? 'border-emerald-500/40 bg-emerald-950/10' : 'border-slate-800'"
      >
        <div>
          <div class="flex items-center justify-between mb-2">
            <span class="font-mono font-black text-sm text-white tracking-wide">{{ loc.location_code }}</span>
            <span
              class="w-2 h-2 rounded-full"
              :class="loc.is_occupied ? 'bg-emerald-400 shadow-sm shadow-emerald-400' : 'bg-slate-700'"
            ></span>
          </div>

          <div class="space-y-0.5 text-[11px] text-slate-400 font-mono">
            <div>Wh: <span class="text-slate-200">{{ loc.warehouse_code }}</span> | Bay: <span class="text-slate-200">{{ loc.bay_number }}</span></div>
            <div>Row: <span class="text-slate-200">{{ loc.row_number }}</span> | Rack: <span class="text-slate-200">{{ loc.rack_number }}</span></div>
            <div>Sec: <span class="text-slate-200">{{ loc.section_code }}</span></div>
          </div>
        </div>

        <div class="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px]">
          <span class="font-mono text-slate-400">{{ loc.total_items }} items</span>
          <button
            @click="openLocationDetail(loc._id)"
            class="text-emerald-400 hover:text-emerald-300 font-semibold"
          >
            Details &rarr;
          </button>
        </div>
      </div>
    </div>

    <!-- Bulk Generator Wizard Modal -->
    <Modal v-model="showBulkModal" title="Warehouse Location Generator Wizard" maxWidth="max-w-2xl">
      <template #icon>
        <Wand2 class="w-5 h-5 text-emerald-400" />
      </template>

      <form @submit.prevent="generateBulkLocations" class="space-y-4">
        <p class="text-xs text-slate-400">
          Automatically generate structured location codes (e.g. <span class="font-mono text-emerald-400">E11-1A</span>) and pre-map default NFC tags (<span class="font-mono text-emerald-400">inventory://location/E11-1A</span>).
        </p>

        <!-- Mode Selector: Uniform vs Custom per Bay -->
        <div class="flex items-center gap-2 p-1 bg-slate-950 rounded-xl border border-slate-800">
          <button
            type="button"
            @click="generatorMode = 'custom'"
            class="flex-1 py-2 text-xs font-bold rounded-lg transition"
            :class="generatorMode === 'custom' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'"
          >
            Custom Rows Per Bay (Flexible)
          </button>
          <button
            type="button"
            @click="generatorMode = 'uniform'"
            class="flex-1 py-2 text-xs font-bold rounded-lg transition"
            :class="generatorMode === 'uniform' ? 'bg-emerald-500 text-slate-950 shadow-md' : 'text-slate-400 hover:text-white'"
          >
            Uniform Layout (Equal Rows)
          </button>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Warehouse Name</label>
            <input
              v-model="bulkForm.warehouse_name"
              type="text"
              required
              placeholder="e.g. EMS Warehouse"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Warehouse Code</label>
            <input
              v-model="bulkForm.warehouse_code"
              type="text"
              placeholder="e.g. E (Auto-derived if blank)"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono uppercase font-bold"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Sections per Rack</label>
            <input
              v-model="bulkForm.sectionsInput"
              type="text"
              required
              placeholder="A, B, C"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Racks per Row (1-20)</label>
            <input
              v-model.number="bulkForm.racks_count"
              type="number"
              min="1"
              max="20"
              required
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
            />
          </div>
        </div>

        <!-- MODE 1: UNIFORM ROWS -->
        <div v-if="generatorMode === 'uniform'" class="grid grid-cols-1 sm:grid-cols-2 gap-4 p-3 bg-slate-950/60 rounded-xl border border-slate-800">
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Bays (Comma Separated)</label>
            <input
              v-model="bulkForm.baysInput"
              type="text"
              required
              placeholder="1, 2, 3"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Rows per Bay (1-20)</label>
            <input
              v-model.number="bulkForm.rows_count"
              type="number"
              min="1"
              max="20"
              required
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
            />
          </div>
        </div>

        <!-- MODE 2: CUSTOM ROWS PER BAY -->
        <div v-else class="space-y-3 p-4 bg-slate-950/70 rounded-2xl border border-emerald-500/30">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                <Layers class="w-4 h-4" />
                Individual Bay & Row Configuration
              </h4>
              <p class="text-[11px] text-slate-400">Specify the exact number of rows for each physical bay</p>
            </div>

            <button
              type="button"
              @click="addBayConfig"
              class="px-2.5 py-1 bg-emerald-950 hover:bg-emerald-900 border border-emerald-700 text-emerald-300 text-xs font-bold rounded-lg flex items-center gap-1 transition"
            >
              <Plus class="w-3.5 h-3.5" />
              <span>Add Bay</span>
            </button>
          </div>

          <div class="space-y-2 max-h-52 overflow-y-auto pr-1">
            <div
              v-for="(cfg, idx) in customBayConfigs"
              :key="idx"
              class="flex items-center gap-3 p-2.5 bg-slate-900 rounded-xl border border-slate-800 hover:border-slate-700 transition"
            >
              <div class="w-24">
                <label class="block text-[10px] uppercase font-bold text-slate-400 mb-1">Bay #</label>
                <input
                  v-model="cfg.bay"
                  type="text"
                  required
                  placeholder="e.g. 1"
                  class="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono font-bold"
                />
              </div>

              <div class="flex-1">
                <label class="block text-[10px] uppercase font-bold text-slate-400 mb-1">Rows in this Bay</label>
                <input
                  v-model.number="cfg.rows_count"
                  type="number"
                  min="1"
                  max="20"
                  required
                  placeholder="e.g. 3"
                  class="w-full bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono font-bold"
                />
              </div>

              <div class="w-36 text-right pt-3">
                <span class="text-[10px] font-mono text-emerald-400 bg-emerald-950/80 border border-emerald-800/60 px-2 py-1 rounded block">
                  {{ (cfg.rows_count || 0) * (bulkForm.racks_count || 0) * parsedSections.length }} Bins (E{{ cfg.bay }}1..E{{ cfg.bay }}{{ cfg.rows_count }})
                </span>
              </div>

              <div class="pt-3">
                <button
                  type="button"
                  @click="removeBayConfig(idx)"
                  :disabled="customBayConfigs.length <= 1"
                  class="p-1.5 text-slate-500 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition disabled:opacity-20"
                  title="Remove Bay"
                >
                  <Trash2 class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="p-3 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-400 flex items-center justify-between">
          <span>Total Locations to Create:</span>
          <span class="text-emerald-400 font-mono font-bold text-sm">{{ estimatedBulkCount }} Bins</span>
        </div>

        <div class="pt-4 border-t border-slate-800 flex justify-end gap-2">
          <button type="button" @click="showBulkModal = false" class="px-4 py-2 bg-slate-800 text-xs font-bold text-slate-300 rounded-xl">Cancel</button>
          <button type="submit" class="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-extrabold rounded-xl shadow">Generate All</button>
        </div>
      </form>
    </Modal>

    <!-- Location Detail Modal -->
    <Modal v-model="showDetailModal" :title="`Location ${selectedLoc?.location_code}`" maxWidth="max-w-lg">
      <div v-if="selectedLoc" class="space-y-4">
        <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs space-y-2 font-mono">
          <div class="flex justify-between"><span class="text-slate-500">Location ID:</span> <span class="text-white">{{ selectedLoc._id }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">NFC Tag Payload:</span> <span class="text-emerald-400">{{ selectedLoc.nfc_tag_uid }}</span></div>
          <div class="flex justify-between"><span class="text-slate-500">Status:</span> <span class="text-emerald-400">{{ selectedLoc.status }}</span></div>
        </div>

        <div>
          <h4 class="text-xs font-bold uppercase text-slate-300 mb-2">Stored Bulk Inventory</h4>
          <div v-if="!selectedLoc.inventory || selectedLoc.inventory.length === 0" class="text-xs text-slate-500">
            No bulk inventory at this location.
          </div>
          <div v-for="inv in selectedLoc.inventory" :key="inv._id" class="p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs flex justify-between">
            <span class="font-mono text-white">{{ inv.part_code || inv.part_id }} (Lot: {{ inv.lot_batch_no || inv.lot_id }})</span>
            <span class="font-mono font-bold text-emerald-400">{{ inv.quantity || inv.available_quantity }} {{ inv.unit_of_measure || 'PCS' }}</span>
          </div>
        </div>

        <div>
          <h4 class="text-xs font-bold uppercase text-slate-300 mb-2">Stored Battery Cells</h4>
          <div v-if="!selectedLoc.cells || selectedLoc.cells.length === 0" class="text-xs text-slate-500">
            No battery cells at this location.
          </div>
          <div class="flex flex-wrap gap-1">
            <span
              v-for="cell in selectedLoc.cells"
              :key="cell._id"
              class="px-2 py-0.5 bg-slate-950 border border-slate-800 rounded text-[11px] font-mono text-emerald-300"
            >
              {{ cell.cell_id }}
            </span>
          </div>
        </div>
      </div>

      <template #footer>
        <button type="button" @click="showDetailModal = false" class="px-4 py-2 bg-slate-800 text-xs font-bold text-slate-300 rounded-xl">Close</button>
        <router-link
          v-if="selectedLoc"
          :to="`/stock-operations?tab=issue&location=${selectedLoc.location_code}`"
          class="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-extrabold rounded-xl shadow-lg shadow-amber-950 flex items-center gap-1.5"
        >
          <span>Issue From Bin</span>
          <ArrowRight class="w-3.5 h-3.5" />
        </router-link>
      </template>
    </Modal>

    <!-- NFC Tester Modal -->
    <NfcReaderModal v-model="showNfcModal" @locationResolved="onNfcResolved" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import locationsApi from '@/api/locations'
import Modal from '@/components/Modal.vue'
import NfcReaderModal from '@/components/NfcReaderModal.vue'
import { useToastStore } from '@/stores/toast'
import { Wand2, Radio, ArrowRight, Layers, Plus, Trash2 } from 'lucide-vue-next'

const locations = ref([])
const filterWarehouse = ref('')
const filterStatus = ref('')
const showBulkModal = ref(false)
const showDetailModal = ref(false)
const showNfcModal = ref(false)
const selectedLoc = ref(null)
const toast = useToastStore()

const generatorMode = ref('custom')

const bulkForm = ref({
  warehouse_name: 'EMS Warehouse',
  warehouse_code: 'E',
  baysInput: '1, 2, 3',
  sectionsInput: 'A, B',
  rows_count: 2,
  racks_count: 2
})

const customBayConfigs = ref([
  { bay: '1', rows_count: 3 },
  { bay: '2', rows_count: 5 },
  { bay: '3', rows_count: 2 }
])

const addBayConfig = () => {
  const nextNum = customBayConfigs.value.length + 1
  customBayConfigs.value.push({ bay: String(nextNum), rows_count: 2 })
}

const removeBayConfig = (index) => {
  if (customBayConfigs.value.length > 1) {
    customBayConfigs.value.splice(index, 1)
  }
}

const occupiedCount = computed(() => {
  return locations.value.filter(l => l.is_occupied).length
})

const parsedSections = computed(() => {
  return (bulkForm.value.sectionsInput || '')
    .split(',')
    .map(s => s.trim().toUpperCase())
    .filter(Boolean)
})

const estimatedBulkCount = computed(() => {
  const racks = bulkForm.value.racks_count || 0
  const secCount = parsedSections.value.length

  if (generatorMode.value === 'custom') {
    return customBayConfigs.value.reduce((acc, cfg) => {
      const rows = Number(cfg.rows_count) || 0
      return acc + (rows * racks * secCount)
    }, 0)
  } else {
    const bays = (bulkForm.value.baysInput || '').split(',').map(s => s.trim()).filter(Boolean)
    const rows = bulkForm.value.rows_count || 0
    return bays.length * rows * racks * secCount
  }
})

const loadLocations = async () => {
  const params = {}
  if (filterWarehouse.value) params.warehouse_code = filterWarehouse.value
  if (filterStatus.value) params.status = filterStatus.value

  const res = await locationsApi.getAll(params)
  locations.value = res.data || []
}

const generateBulkLocations = async () => {
  try {
    const sections = parsedSections.value
    const payload = {
      warehouse_name: bulkForm.value.warehouse_name,
      warehouse_code: bulkForm.value.warehouse_code,
      sections,
      racks_count: bulkForm.value.racks_count
    }

    if (generatorMode.value === 'custom') {
      payload.bay_configs = customBayConfigs.value.map(c => ({
        bay: String(c.bay).trim(),
        rows_count: Number(c.rows_count)
      }))
    } else {
      payload.bays = (bulkForm.value.baysInput || '').split(',').map(s => s.trim()).filter(Boolean)
      payload.rows_count = bulkForm.value.rows_count
    }

    const res = await locationsApi.bulkGenerate(payload)
    toast.success(res.message || 'Locations generated successfully')
    showBulkModal.value = false
    await loadLocations()
  } catch (err) {}
}

const openLocationDetail = async (locId) => {
  const res = await locationsApi.getById(locId)
  selectedLoc.value = res.data
  showDetailModal.value = true
}

const openNfcTester = () => {
  showNfcModal.value = true
}

const onNfcResolved = (loc) => {
  selectedLoc.value = loc
  showDetailModal.value = true
}

onMounted(() => {
  loadLocations()
})
</script>
