<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Parts Master Catalog</h1>
        <p class="text-xs text-slate-400 mt-0.5">Component specifications, dynamic electrical/mechanical attributes, and tracking modes</p>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="openBulkModal"
          class="flex items-center gap-1.5 px-3.5 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white border border-slate-700 text-xs font-bold rounded-lg shadow transition"
        >
          <UploadCloud class="w-3.5 h-3.5 text-cyan-400" />
          <span>Bulk Import</span>
        </button>

        <button
          @click="openNewPartModal"
          class="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg shadow transition"
        >
          <Plus class="w-3.5 h-3.5" />
          <span>New Part</span>
        </button>
      </div>
    </div>


    <!-- Parts Table -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
            <tr>
              <th class="p-3.5">Part Code</th>
              <th class="p-3.5">Part Name & Type</th>
              <th class="p-3.5">MPN / Manufacturer</th>
              <th class="p-3.5">Vendor</th>
              <th class="p-3.5">Tracking Model</th>
              <th class="p-3.5">Dynamic Attributes</th>
              <th class="p-3.5">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            <tr v-if="parts.length === 0">
              <td colspan="7" class="p-8 text-center text-slate-500">No parts found in catalog.</td>
            </tr>
            <tr
              v-for="part in parts"
              :key="part._id"
              class="hover:bg-slate-800/40 transition-colors"
            >
              <td class="p-3.5 font-mono font-bold text-emerald-400">{{ part.part_code }}</td>
              <td class="p-3.5">
                <span class="text-white font-medium block">{{ part.part_name }}</span>
                <span class="text-[10px] text-slate-400 uppercase font-mono">{{ part.part_type_name }}</span>
              </td>
              <td class="p-3.5 font-mono text-slate-300">
                <span>{{ part.mpn || 'N/A' }}</span>
                <span v-if="part.mfr" class="text-[10px] text-slate-400 block">{{ part.mfr }}</span>
              </td>
              <td class="p-3.5 text-slate-300">{{ part.vendor_name || 'N/A' }}</td>
              <td class="p-3.5">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-mono font-bold"
                  :class="part.tracking_type === 'SERIAL' ? 'bg-purple-950 text-purple-300 border border-purple-800/50' : 'bg-slate-800 text-slate-300'"
                >
                  {{ part.tracking_type }}
                </span>
              </td>
              <td class="p-3.5">
                <div class="flex flex-wrap gap-1 max-w-xs">
                  <span
                    v-for="(val, key) in part.attributes"
                    :key="key"
                    class="px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800 text-[10px] font-mono text-slate-300"
                  >
                    <span class="text-slate-400">{{ key }}:</span> {{ val }}
                  </span>
                </div>
              </td>
              <td class="p-3.5">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800/60">
                  ACTIVE
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Part Modal with Dynamic Attribute Rendering -->
    <Modal v-model="showModal" title="Create New Material / Part" maxWidth="max-w-2xl">
      <template #icon>
        <Layers class="w-5 h-5" />
      </template>

      <form @submit.prevent="createPart" class="space-y-4">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Part Type <span class="text-rose-400">*</span></label>
            <select
              v-model="newPartForm.part_type_id"
              required
              @change="onPartTypeChange"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
            >
              <option value="" disabled>-- Select Part Type --</option>
              <option v-for="pt in partTypes" :key="pt._id" :value="pt._id">
                {{ pt.part_type_name }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Tracking Type <span class="text-rose-400">*</span></label>
            <select
              v-model="newPartForm.tracking_type"
              required
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
            >
              <option value="QUANTITY">QUANTITY (Bulk Parts / Passive / ICs)</option>
              <option value="SERIAL">SERIAL (Battery Cells Individually Tracked)</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Part Code <span class="text-rose-400">*</span></label>
            <input
              v-model="newPartForm.part_code"
              type="text"
              required
              placeholder="e.g. RES-10K-0603"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono font-bold"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Part Name <span class="text-rose-400">*</span></label>
            <input
              v-model="newPartForm.part_name"
              type="text"
              required
              placeholder="e.g. 10K Ohm SMD Resistor 0603"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">MPN (Manufacturer Part #)</label>
            <input
              v-model="newPartForm.mpn"
              type="text"
              placeholder="e.g. RC0603FR-0710KL"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Manufacturer</label>
            <input
              v-model="newPartForm.mfr"
              type="text"
              placeholder="e.g. Yageo, Samsung SDI"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Primary Vendor</label>
            <select
              v-model="newPartForm.vendor_id"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
            >
              <option value="">-- Optional Vendor --</option>
              <option v-for="v in vendors" :key="v._id" :value="v._id">{{ v.vendor_name }}</option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Unit of Measure</label>
            <input
              v-model="newPartForm.unit_of_measure"
              type="text"
              placeholder="PCS"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
            />
          </div>
        </div>

        <!-- DYNAMIC FIELDS SECTION (Configured per Part Type) -->
        <div v-if="selectedTypeFields.length > 0" class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
          <h4 class="text-xs font-bold uppercase tracking-wider text-emerald-400">
            Dynamic Attributes for {{ selectedPartTypeName }}
          </h4>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div v-for="field in selectedTypeFields" :key="field._id || field.field_key || field.key">
              <label class="block text-[11px] font-semibold text-slate-300 mb-1">
                {{ field.field_name || field.name || field.field_key || field.key }} <span v-if="field.unit" class="text-slate-400">({{ field.unit }})</span>
                <span v-if="field.required" class="text-rose-400">*</span>
              </label>

              <!-- Select Option -->
              <select
                v-if="(field.data_type || field.type) === 'SELECT'"
                v-model="newPartForm.attributes[field.field_key || field.key]"
                :required="field.required"
                class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono"
              >
                <option value="" disabled>Select option</option>
                <option v-for="opt in (field.options || [])" :key="opt" :value="opt">{{ opt }}</option>
              </select>

              <!-- Number / Decimal -->
              <input
                v-else-if="['NUMBER', 'DECIMAL', 'INTEGER'].includes((field.data_type || field.type || '').toUpperCase())"
                v-model.number="newPartForm.attributes[field.field_key || field.key]"
                type="number"
                step="any"
                :required="field.required"
                class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono"
              />

              <!-- Text / Default -->
              <input
                v-else
                v-model="newPartForm.attributes[field.field_key || field.key]"
                type="text"
                :required="field.required"
                class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono"
              />
            </div>
          </div>
        </div>

        <div class="pt-4 border-t border-slate-800 flex justify-end gap-2">
          <button
            type="button"
            @click="showModal = false"
            class="px-4 py-2 bg-slate-800 text-slate-300 text-xs font-bold rounded-xl"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-extrabold rounded-xl shadow"
          >
            Create Part
          </button>
        </div>
      </form>
    </Modal>

    <!-- Bulk Import Modal -->
    <Modal v-model="showBulkModal" title="Bulk Import Parts Catalog" maxWidth="max-w-3xl">

      <template #icon>
        <UploadCloud class="w-5 h-5 text-cyan-400" />
      </template>

      <div class="space-y-5">
        <!-- 1. Download Templates Section -->
        <div class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2.5">
          <div class="flex items-center justify-between">
            <div>
              <h4 class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <FileSpreadsheet class="w-4 h-4 text-emerald-400" />
                <span>1. Download Pre-configured Template</span>
              </h4>
              <p class="text-[11px] text-slate-400 mt-0.5">
                Includes all active part types, standard fields, and dynamic electrical/mechanical attributes.
              </p>
            </div>
          </div>

          <div class="flex flex-wrap gap-2 pt-1">
            <button
              type="button"
              @click="downloadTemplate('csv')"
              :disabled="downloadingTemplate"
              class="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-700 text-xs font-semibold rounded-lg transition"
            >
              <FileText class="w-3.5 h-3.5 text-blue-400" />
              <span>Download CSV Template</span>
            </button>
            <button
              type="button"
              @click="downloadTemplate('xlsx')"
              :disabled="downloadingTemplate"
              class="flex items-center gap-1.5 px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-slate-200 hover:text-white border border-slate-700 text-xs font-semibold rounded-lg transition"
            >
              <FileSpreadsheet class="w-3.5 h-3.5 text-emerald-400" />
              <span>Download Excel Template (.xlsx)</span>
            </button>
          </div>
        </div>

        <!-- 2. File Upload Dropzone -->
        <div class="space-y-2">
          <h4 class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
            <Upload class="w-4 h-4 text-cyan-400" />
            <span>2. Select File to Import</span>
          </h4>

          <div
            @dragover.prevent="isDragging = true"
            @dragleave.prevent="isDragging = false"
            @drop.prevent="handleFileDrop"
            @click="$refs.fileInput.click()"
            class="border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors"
            :class="isDragging ? 'border-cyan-400 bg-cyan-950/20' : selectedFile ? 'border-emerald-500/60 bg-emerald-950/10' : 'border-slate-800 bg-slate-950/60 hover:border-slate-700'"
          >
            <input
              ref="fileInput"
              type="file"
              accept=".csv,.xlsx,.xls,.json"
              class="hidden"
              @change="handleFileSelect"
            />

            <div v-if="!selectedFile" class="space-y-1.5">
              <UploadCloud class="w-8 h-8 text-slate-500 mx-auto" />
              <p class="text-xs text-slate-300 font-medium">Click to browse or drag & drop your parts file</p>
              <p class="text-[10px] text-slate-500 font-mono">Supported formats: .CSV, .XLSX, .XLS, .JSON</p>
            </div>

            <div v-else class="flex items-center justify-between p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-left">
              <div class="flex items-center gap-2.5">
                <FileSpreadsheet v-if="selectedFile.name.endsWith('.xlsx') || selectedFile.name.endsWith('.xls')" class="w-6 h-6 text-emerald-400" />
                <FileText v-else class="w-6 h-6 text-blue-400" />
                <div>
                  <p class="text-xs font-bold text-white font-mono">{{ selectedFile.name }}</p>
                  <p class="text-[10px] text-slate-400">{{ formatFileSize(selectedFile.size) }}</p>
                </div>
              </div>
              <button
                type="button"
                @click.stop="removeFile"
                class="p-1 rounded-md text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition"
              >
                <X class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        <!-- 3. Import Options & Auto Vendor Notice -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
            <label class="block text-xs font-bold text-white uppercase tracking-wider">Duplicate Part Code Policy</label>
            <div class="space-y-1.5">
              <label class="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                <input type="radio" v-model="duplicateStrategy" value="skip" class="text-cyan-500 focus:ring-0 bg-slate-900" />
                <span><strong>Skip</strong> existing parts (preserve current)</span>
              </label>
              <label class="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                <input type="radio" v-model="duplicateStrategy" value="update" class="text-cyan-500 focus:ring-0 bg-slate-900" />
                <span><strong>Update</strong> existing parts (overwrite data)</span>
              </label>
              <label class="flex items-center gap-2 text-xs text-slate-300 cursor-pointer">
                <input type="radio" v-model="duplicateStrategy" value="error" class="text-cyan-500 focus:ring-0 bg-slate-900" />
                <span><strong>Error</strong> (flag duplicate as error)</span>
              </label>
            </div>
          </div>

          <div class="p-3.5 rounded-xl bg-purple-950/20 border border-purple-900/40 flex items-start gap-2.5">
            <Sparkles class="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
            <div class="text-[11px] text-purple-200">
              <p class="font-bold">Automatic Vendor Provisioning</p>
              <p class="text-slate-400 mt-1">
                Any vendor names in the file that are not currently in your database will be automatically created with new vendor IDs.
              </p>
            </div>
          </div>
        </div>

        <!-- 4. Import Results Display -->
        <div v-if="importResult" class="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-3">
          <h4 class="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
            <CheckCircle2 class="w-4 h-4 text-emerald-400" />
            <span>Import Execution Summary</span>
          </h4>

          <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
            <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-center">
              <p class="text-[10px] text-slate-400 uppercase font-semibold">Total Rows</p>
              <p class="text-sm font-bold text-white font-mono mt-0.5">{{ importResult.total_rows }}</p>
            </div>
            <div class="p-2.5 rounded-lg bg-emerald-950/40 border border-emerald-800/50 text-center">
              <p class="text-[10px] text-emerald-400 uppercase font-semibold">Imported</p>
              <p class="text-sm font-bold text-emerald-300 font-mono mt-0.5">{{ importResult.imported }}</p>
            </div>
            <div class="p-2.5 rounded-lg bg-blue-950/40 border border-blue-800/50 text-center">
              <p class="text-[10px] text-blue-400 uppercase font-semibold">Updated</p>
              <p class="text-sm font-bold text-blue-300 font-mono mt-0.5">{{ importResult.updated }}</p>
            </div>
            <div class="p-2.5 rounded-lg bg-slate-900 border border-slate-800 text-center">
              <p class="text-[10px] text-slate-400 uppercase font-semibold">Skipped</p>
              <p class="text-sm font-bold text-slate-300 font-mono mt-0.5">{{ importResult.skipped }}</p>
            </div>
          </div>

          <div v-if="importResult.auto_created_vendors && importResult.auto_created_vendors.length > 0" class="p-2.5 rounded-lg bg-purple-950/30 border border-purple-800/40 text-xs">
            <p class="text-purple-300 font-semibold mb-1">Auto-Created Vendors ({{ importResult.auto_created_vendors.length }}):</p>
            <div class="flex flex-wrap gap-1">
              <span v-for="v in importResult.auto_created_vendors" :key="v" class="px-2 py-0.5 rounded bg-purple-900/40 text-purple-200 border border-purple-700/50 text-[10px] font-mono">
                {{ v }}
              </span>
            </div>
          </div>

          <!-- Error List -->
          <div v-if="importResult.errors && importResult.errors.length > 0" class="space-y-1.5">
            <p class="text-xs font-bold text-rose-400 flex items-center gap-1">
              <AlertTriangle class="w-3.5 h-3.5" />
              <span>Row Errors ({{ importResult.errors.length }})</span>
            </p>
            <div class="max-h-36 overflow-y-auto divide-y divide-rose-950/60 border border-rose-900/40 rounded-lg bg-rose-950/20">
              <div v-for="(err, idx) in importResult.errors" :key="idx" class="p-2 text-[11px] text-rose-300 flex items-start gap-2">
                <span class="px-1.5 py-0.2 rounded bg-rose-950 border border-rose-800 font-mono font-bold text-[10px] shrink-0">Row {{ err.row }}</span>
                <span v-if="err.part_code && err.part_code !== 'N/A'" class="font-mono text-white font-bold shrink-0">{{ err.part_code }}:</span>
                <span class="text-slate-300">{{ err.error }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer Actions -->
        <div class="pt-4 border-t border-slate-800 flex justify-end gap-2">
          <button
            type="button"
            @click="showBulkModal = false"
            class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold rounded-xl transition"
          >
            {{ importResult ? 'Done' : 'Cancel' }}
          </button>
          <button
            type="button"
            @click="submitBulkImport"
            :disabled="!selectedFile || isImporting"
            class="flex items-center gap-1.5 px-5 py-2 bg-gradient-to-r from-cyan-500 to-emerald-500 hover:from-cyan-400 hover:to-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed text-slate-950 text-xs font-extrabold rounded-xl shadow transition"
          >
            <RefreshCw v-if="isImporting" class="w-3.5 h-3.5 animate-spin" />
            <UploadCloud v-else class="w-3.5 h-3.5" />
            <span>{{ isImporting ? 'Importing...' : 'Start Import' }}</span>
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import partsApi from '@/api/parts'
import partTypesApi from '@/api/partTypes'
import vendorsApi from '@/api/vendors'
import Modal from '@/components/Modal.vue'
import { useToastStore } from '@/stores/toast'
import {
  Plus,
  Layers,
  UploadCloud,
  FileSpreadsheet,
  FileText,
  Upload,
  X,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  RefreshCw
} from 'lucide-vue-next'

const parts = ref([])
const partTypes = ref([])
const vendors = ref([])
const showModal = ref(false)
const showBulkModal = ref(false)
const toast = useToastStore()

// Bulk Import State
const selectedFile = ref(null)
const isDragging = ref(false)
const duplicateStrategy = ref('skip')
const isImporting = ref(false)
const downloadingTemplate = ref(false)
const importResult = ref(null)
const fileInput = ref(null)

const newPartForm = ref({
  part_type_id: '',
  tracking_type: 'QUANTITY',
  part_code: '',
  part_name: '',
  mpn: '',
  mfr: '',
  vendor_id: '',
  unit_of_measure: 'PCS',
  attributes: {}
})

const selectedTypeFields = ref([])

const selectedPartTypeName = computed(() => {
  const pt = partTypes.value.find(p => p._id === newPartForm.value.part_type_id)
  return pt?.part_type_name || ''
})

const loadData = async () => {
  const [pRes, ptRes, vRes] = await Promise.all([
    partsApi.getAll(),
    partTypesApi.getAll(),
    vendorsApi.getAll()
  ])
  parts.value = pRes.data || []
  partTypes.value = ptRes.data || []
  vendors.value = vRes.data || []
}

const onPartTypeChange = async () => {
  const pt = partTypes.value.find(p => p._id === newPartForm.value.part_type_id)
  if (pt) {
    selectedTypeFields.value = pt.fields || []
    newPartForm.value.attributes = {}
    if (pt.part_type_name === 'CELL') {
      newPartForm.value.tracking_type = 'SERIAL'
    }
  }
}

const openNewPartModal = () => {
  newPartForm.value = {
    part_type_id: partTypes.value[0]?._id || '',
    tracking_type: 'QUANTITY',
    part_code: '',
    part_name: '',
    mpn: '',
    mfr: '',
    vendor_id: '',
    unit_of_measure: 'PCS',
    attributes: {}
  }
  onPartTypeChange()
  showModal.value = true
}

const createPart = async () => {
  try {
    await partsApi.create(newPartForm.value)
    toast.success('Part added to catalog successfully')
    showModal.value = false
    await loadData()
  } catch (err) {}
}

// Bulk Import Handlers
const openBulkModal = () => {
  selectedFile.value = null
  importResult.value = null
  duplicateStrategy.value = 'skip'
  showBulkModal.value = true
}

const handleFileSelect = (event) => {
  const files = event.target.files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
    importResult.value = null
  }
}

const handleFileDrop = (event) => {
  isDragging.value = false
  const files = event.dataTransfer.files
  if (files && files.length > 0) {
    selectedFile.value = files[0]
    importResult.value = null
  }
}

const removeFile = () => {
  selectedFile.value = null
  importResult.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const downloadTemplate = async (format) => {
  downloadingTemplate.value = true
  try {
    const response = await partsApi.downloadTemplate(format)
    const blob = new Blob([response.data], {
      type: format === 'xlsx'
        ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        : 'text/csv'
    })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `parts_import_template.${format === 'xlsx' ? 'xlsx' : 'csv'}`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    toast.success(`${format.toUpperCase()} template downloaded`)
  } catch (err) {
    toast.error('Failed to download template')
  } finally {
    downloadingTemplate.value = false
  }
}

const submitBulkImport = async () => {
  if (!selectedFile.value) return
  isImporting.value = true
  importResult.value = null

  try {
    const formData = new FormData()
    formData.append('file', selectedFile.value)
    formData.append('duplicate_strategy', duplicateStrategy.value)

    const res = await partsApi.bulkImport(formData)
    importResult.value = res.data

    if (res.data.imported > 0 || res.data.updated > 0) {
      toast.success(`Import complete: ${res.data.imported} added, ${res.data.updated} updated`)
      await loadData()
    } else if (res.data.errors && res.data.errors.length > 0) {
      toast.warning(`Import completed with ${res.data.errors.length} errors`)
    } else {
      toast.info('No parts were modified')
    }
  } catch (err) {
    // Handled by global interceptor or error response
  } finally {
    isImporting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

