<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Parts Master Catalog</h1>
        <p class="text-xs text-slate-400 mt-0.5">Component specifications, dynamic electrical/mechanical attributes, and tracking modes</p>
      </div>

      <div class="flex items-center gap-2">
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
            <div v-for="field in selectedTypeFields" :key="field._id">
              <label class="block text-[11px] font-semibold text-slate-300 mb-1">
                {{ field.field_name }} <span v-if="field.unit" class="text-slate-400">({{ field.unit }})</span>
                <span v-if="field.required" class="text-rose-400">*</span>
              </label>

              <!-- Select Option -->
              <select
                v-if="field.data_type === 'SELECT'"
                v-model="newPartForm.attributes[field.field_key]"
                :required="field.required"
                class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono"
              >
                <option value="" disabled>Select option</option>
                <option v-for="opt in field.options" :key="opt" :value="opt">{{ opt }}</option>
              </select>

              <!-- Number / Decimal -->
              <input
                v-else-if="field.data_type === 'NUMBER' || field.data_type === 'DECIMAL'"
                v-model.number="newPartForm.attributes[field.field_key]"
                type="number"
                step="any"
                :required="field.required"
                class="w-full bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white font-mono"
              />

              <!-- Text / Default -->
              <input
                v-else
                v-model="newPartForm.attributes[field.field_key]"
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
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import partsApi from '@/api/parts'
import partTypesApi from '@/api/partTypes'
import vendorsApi from '@/api/vendors'
import Modal from '@/components/Modal.vue'
import { useToastStore } from '@/stores/toast'
import { Plus, Layers } from 'lucide-vue-next'

const parts = ref([])
const partTypes = ref([])
const vendors = ref([])
const showModal = ref(false)
const toast = useToastStore()

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

onMounted(() => {
  loadData()
})
</script>
