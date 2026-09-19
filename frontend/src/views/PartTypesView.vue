<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Part Types & Dynamic Fields</h1>
        <p class="text-xs text-slate-400 mt-0.5">Define custom dynamic attribute schemas without changing database structure</p>
      </div>

      <button
        @click="openNewTypeModal"
        class="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg shadow transition"
      >
        <Plus class="w-3.5 h-3.5" />
        <span>New Part Type</span>
      </button>
    </div>

    <!-- Part Types Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div
        v-for="pt in partTypes"
        :key="pt._id"
        class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg flex flex-col justify-between"
      >
        <div>
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <span class="text-base font-black font-mono text-emerald-400">{{ pt.part_type_name }}</span>
              <p class="text-xs text-slate-400 mt-0.5">{{ pt.description || 'No description' }}</p>
            </div>
            <button
              @click="openAddFieldModal(pt)"
              class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-xs text-white font-semibold rounded-lg border border-slate-700 flex items-center gap-1"
            >
              <Plus class="w-3 h-3" />
              <span>Add Field</span>
            </button>
          </div>

          <!-- Configured Dynamic Fields List -->
          <div class="mt-4 space-y-2">
            <span class="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
              Configured Custom Fields ({{ pt.fields?.length || 0 }})
            </span>

            <div v-if="!pt.fields || pt.fields.length === 0" class="text-xs text-slate-500 py-2">
              No custom fields configured.
            </div>

            <div
              v-for="f in pt.fields"
              :key="f._id || f.field_key || f.key"
              class="flex items-center justify-between p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs"
            >
              <div>
                <span class="font-bold text-white font-mono">{{ f.field_name || f.name }}</span>
                <span class="text-[10px] text-slate-400 font-mono ml-2">key: {{ f.field_key || f.key }}</span>
                <div class="flex items-center gap-1.5 mt-0.5">
                  <span class="px-1.5 py-0.2 rounded bg-slate-800 text-[10px] font-mono text-emerald-400">{{ f.data_type || f.type || 'STRING' }}</span>
                  <span v-if="f.unit" class="text-[10px] text-slate-400">Unit: {{ f.unit }}</span>
                  <span v-if="f.required" class="text-[10px] text-rose-400 font-bold uppercase tracking-wider">Required</span>
                </div>
              </div>

              <button
                @click="deleteField(f._id)"
                class="text-slate-500 hover:text-rose-400 p-1 transition"
                title="Delete Field"
              >
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Part Type Modal -->
    <Modal v-model="showTypeModal" title="Create Part Type" maxWidth="max-w-md">
      <form @submit.prevent="createPartType" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Type Name (e.g. SENSOR, RELAY)</label>
          <input
            v-model="newTypeForm.part_type_name"
            type="text"
            required
            placeholder="e.g. SENSOR"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono uppercase font-bold"
          />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Description</label>
          <input
            v-model="newTypeForm.description"
            type="text"
            placeholder="Temperature & humidity sensors"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
          />
        </div>
        <div class="pt-4 border-t border-slate-800 flex justify-end gap-2">
          <button type="button" @click="showTypeModal = false" class="px-4 py-2 bg-slate-800 text-xs font-bold text-slate-300 rounded-xl">Cancel</button>
          <button type="submit" class="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-extrabold rounded-xl">Save</button>
        </div>
      </form>
    </Modal>

    <!-- Add Field Modal -->
    <Modal v-model="showFieldModal" :title="`Add Field to ${currentPt?.part_type_name}`" maxWidth="max-w-md">
      <form @submit.prevent="addField" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Field Label Name</label>
          <input
            v-model="newFieldForm.field_name"
            type="text"
            required
            placeholder="e.g. Operating Temperature"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
          />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Field Key (Snake Case)</label>
          <input
            v-model="newFieldForm.field_key"
            type="text"
            required
            placeholder="e.g. operating_temp"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
          />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Data Type</label>
          <select
            v-model="newFieldForm.data_type"
            required
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
          >
            <option value="STRING">STRING</option>
            <option value="NUMBER">NUMBER (Integer)</option>
            <option value="DECIMAL">DECIMAL (Float)</option>
            <option value="BOOLEAN">BOOLEAN</option>
            <option value="SELECT">SELECT (Options list)</option>
          </select>
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Unit (e.g. OHM, V, mAh, mm)</label>
          <input
            v-model="newFieldForm.unit"
            type="text"
            placeholder="e.g. C, V, A"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
          />
        </div>
        <div class="flex items-center gap-2 pt-2">
          <input
            type="checkbox"
            id="fieldReq"
            v-model="newFieldForm.required"
            class="rounded bg-slate-950 border-slate-700 text-emerald-500 focus:ring-0"
          />
          <label for="fieldReq" class="text-xs font-bold text-slate-300">Required Field on Part Creation</label>
        </div>
        <div class="pt-4 border-t border-slate-800 flex justify-end gap-2">
          <button type="button" @click="showFieldModal = false" class="px-4 py-2 bg-slate-800 text-xs font-bold text-slate-300 rounded-xl">Cancel</button>
          <button type="submit" class="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-extrabold rounded-xl">Add Field</button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import partTypesApi from '@/api/partTypes'
import Modal from '@/components/Modal.vue'
import { useToastStore } from '@/stores/toast'
import { Plus, Trash2 } from 'lucide-vue-next'

const partTypes = ref([])
const showTypeModal = ref(false)
const showFieldModal = ref(false)
const currentPt = ref(null)
const toast = useToastStore()

const newTypeForm = ref({
  part_type_name: '',
  description: ''
})

const newFieldForm = ref({
  field_name: '',
  field_key: '',
  data_type: 'DECIMAL',
  unit: '',
  required: false
})

const loadPartTypes = async () => {
  const res = await partTypesApi.getAll()
  partTypes.value = res.data || []
}

const openNewTypeModal = () => {
  newTypeForm.value = { part_type_name: '', description: '' }
  showTypeModal.value = true
}

const openAddFieldModal = (pt) => {
  currentPt.value = pt
  newFieldForm.value = { field_name: '', field_key: '', data_type: 'DECIMAL', unit: '', required: false }
  showFieldModal.value = true
}

const createPartType = async () => {
  try {
    await partTypesApi.create(newTypeForm.value)
    toast.success('Part type registered')
    showTypeModal.value = false
    await loadPartTypes()
  } catch (e) {}
}

const addField = async () => {
  try {
    await partTypesApi.addField(currentPt.value._id, newFieldForm.value)
    toast.success('Dynamic field added')
    showFieldModal.value = false
    await loadPartTypes()
  } catch (e) {}
}

const deleteField = async (fieldId) => {
  if (confirm('Are you sure you want to delete this custom field?')) {
    await partTypesApi.deleteField(fieldId)
    toast.success('Field deleted')
    await loadPartTypes()
  }
}

onMounted(() => {
  loadPartTypes()
})
</script>
