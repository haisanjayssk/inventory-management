<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Suppliers & Vendors Directory</h1>
        <p class="text-xs text-slate-400 mt-0.5">Approved suppliers for passive components, silicon, battery cells, and bus bars</p>
      </div>

      <button
        @click="showModal = true"
        class="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg shadow transition"
      >
        <Plus class="w-3.5 h-3.5" />
        <span>New Vendor</span>
      </button>
    </div>

    <!-- Vendors Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
      <div
        v-for="v in vendors"
        :key="v._id"
        class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg flex flex-col justify-between"
      >
        <div>
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <div>
              <span class="text-sm font-bold text-white block">{{ v.vendor_name }}</span>
              <span class="text-[10px] font-mono text-emerald-400">{{ v._id }}</span>
            </div>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800/60">
              {{ v.status }}
            </span>
          </div>

          <div class="mt-4 space-y-1.5 text-xs text-slate-400">
            <div class="flex items-center gap-2">
              <Mail class="w-3.5 h-3.5 text-slate-500" />
              <span>{{ v.email || 'No email' }}</span>
            </div>
            <div class="flex items-center gap-2">
              <Phone class="w-3.5 h-3.5 text-slate-500" />
              <span>{{ v.contact || 'No phone' }}</span>
            </div>
            <div class="flex items-center gap-2">
              <MapPin class="w-3.5 h-3.5 text-slate-500" />
              <span>{{ v.address || 'Address unlisted' }}, {{ v.country }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create Vendor Modal -->
    <Modal v-model="showModal" title="Register New Vendor" maxWidth="max-w-md">
      <form @submit.prevent="createVendor" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Vendor Name</label>
          <input
            v-model="newVendor.vendor_name"
            type="text"
            required
            placeholder="e.g. Yageo Corporation"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
          />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Email</label>
          <input
            v-model="newVendor.email"
            type="email"
            placeholder="vendor@example.com"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
          />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Contact Phone</label>
          <input
            v-model="newVendor.contact"
            type="text"
            placeholder="+91-44-XXXXXXXX"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
          />
        </div>
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">City / Address</label>
          <input
            v-model="newVendor.address"
            type="text"
            placeholder="Chennai"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
          />
        </div>
        <div class="pt-4 border-t border-slate-800 flex justify-end gap-2">
          <button type="button" @click="showModal = false" class="px-4 py-2 bg-slate-800 text-xs font-bold text-slate-300 rounded-xl">Cancel</button>
          <button type="submit" class="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-extrabold rounded-xl">Create</button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import vendorsApi from '@/api/vendors'
import Modal from '@/components/Modal.vue'
import { useToastStore } from '@/stores/toast'
import { Plus, Mail, Phone, MapPin } from 'lucide-vue-next'

const vendors = ref([])
const showModal = ref(false)
const toast = useToastStore()

const newVendor = ref({
  vendor_name: '',
  email: '',
  contact: '',
  address: '',
  country: 'India'
})

const loadVendors = async () => {
  const res = await vendorsApi.getAll()
  vendors.value = res.data || []
}

const createVendor = async () => {
  try {
    await vendorsApi.create(newVendor.value)
    toast.success('Vendor created')
    showModal.value = false
    await loadVendors()
  } catch (e) {}
}

onMounted(() => {
  loadVendors()
})
</script>
