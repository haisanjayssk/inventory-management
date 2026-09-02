<template>
  <header class="h-16 bg-slate-900 border-b border-slate-800 px-4 sm:px-6 flex items-center justify-between flex-shrink-0 z-30">
    <!-- Left: Hamburger toggle + App Title -->
    <div class="flex items-center gap-3">
      <button
        @click="$emit('toggleSidebar')"
        class="lg:hidden p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
      >
        <Menu class="w-5 h-5" />
      </button>

      <div class="flex items-center gap-2.5">
        <div class="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-slate-950 font-black shadow-lg shadow-emerald-500/20">
          <Cpu class="w-5 h-5" />
        </div>
        <div>
          <span class="text-sm font-extrabold text-white tracking-wide">MES INVENTORY</span>
          <span class="hidden sm:inline text-[10px] font-semibold text-emerald-400 bg-emerald-950/80 border border-emerald-800/60 px-1.5 py-0.5 rounded ml-2">PROD 2026</span>
        </div>
      </div>
    </div>

    <!-- Right: Action shortcuts + User Profile -->
    <div class="flex items-center gap-2 sm:gap-4">
      <!-- Quick NFC Trigger Button -->
      <button
        @click="showNfcModal = true"
        class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-emerald-950/60 hover:bg-emerald-900 border border-emerald-700/50 text-emerald-300 rounded-lg transition"
        title="Scan NFC Tag"
      >
        <Radio class="w-4 h-4 animate-pulse text-emerald-400" />
        <span class="hidden md:inline">Scan NFC</span>
      </button>

      <!-- Quick Barcode Trigger Button -->
      <button
        @click="showBarcodeModal = true"
        class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 rounded-lg transition"
        title="Scan Barcode / QR"
      >
        <QrCode class="w-4 h-4 text-slate-400" />
        <span class="hidden md:inline">Scan QR</span>
      </button>

      <!-- User Chip -->
      <div v-if="authStore.user" class="flex items-center gap-2.5 pl-2 border-l border-slate-800">
        <div class="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 text-xs font-bold uppercase">
          {{ authStore.user.username?.substring(0, 2) }}
        </div>
        <div class="hidden sm:block text-left">
          <p class="text-xs font-bold text-white leading-none">{{ authStore.user.full_name || authStore.user.username }}</p>
          <span class="text-[10px] font-semibold tracking-wider text-emerald-400 uppercase">
            {{ authStore.user.role }}
          </span>
        </div>

        <button
          @click="authStore.logout()"
          class="p-2 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition"
          title="Sign Out"
        >
          <LogOut class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Modals -->
    <NfcReaderModal v-model="showNfcModal" @locationResolved="onLocationResolved" />
    <BarcodeScannerModal v-model="showBarcodeModal" @scan="onBarcodeScanned" />

    <!-- Location Operation Chooser Modal (Receive vs Issue) -->
    <Modal v-model="showActionModal" :title="`Location ${selectedActionLoc?.location_code}`" maxWidth="max-w-md">
      <template #icon>
        <MapPin class="w-5 h-5 text-emerald-400" />
      </template>

      <div v-if="selectedActionLoc" class="space-y-4">
        <!-- Location Header Summary -->
        <div class="p-3.5 bg-slate-950 rounded-xl border border-slate-800 text-xs flex items-center justify-between">
          <div>
            <span class="text-[10px] uppercase font-bold text-slate-500 block">Warehouse Bin</span>
            <span class="text-sm font-black font-mono text-white">{{ selectedActionLoc.location_code }}</span>
          </div>
          <div class="text-right text-[11px] text-slate-400 font-mono">
            <div>Wh: <span class="text-slate-200">{{ selectedActionLoc.warehouse_code }}</span> | Bay {{ selectedActionLoc.bay_number }}</div>
            <div>Rack {{ selectedActionLoc.rack_number }} | Sec {{ selectedActionLoc.section_code }}</div>
          </div>
        </div>

        <p class="text-xs text-slate-300 font-semibold text-center">
          What operation would you like to perform for this location?
        </p>

        <!-- Two Action Choices: Receive vs Issue -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <!-- Choice 1: Receive Material -->
          <button
            @click="navigateToAction('receive')"
            class="group p-4 bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-700/50 hover:border-emerald-500 rounded-2xl text-left transition-all duration-200 hover:scale-[1.02] flex flex-col justify-between space-y-3 shadow-lg shadow-emerald-950/30"
          >
            <div class="w-10 h-10 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-500 group-hover:text-slate-950 transition-colors">
              <Download class="w-5 h-5" />
            </div>
            <div>
              <h4 class="text-sm font-black text-white group-hover:text-emerald-300 transition-colors">
                Receive Material
              </h4>
              <p class="text-[11px] text-slate-400 mt-0.5 leading-snug">
                Intake & deposit incoming parts or battery cells into this bin.
              </p>
            </div>
            <div class="text-xs font-bold text-emerald-400 flex items-center gap-1 pt-1">
              <span>Start Receive &rarr;</span>
            </div>
          </button>

          <!-- Choice 2: Issue Material -->
          <button
            @click="navigateToAction('issue')"
            class="group p-4 bg-amber-950/40 hover:bg-amber-900/60 border border-amber-700/50 hover:border-amber-500 rounded-2xl text-left transition-all duration-200 hover:scale-[1.02] flex flex-col justify-between space-y-3 shadow-lg shadow-amber-950/30"
          >
            <div class="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/40 flex items-center justify-center text-amber-400 group-hover:bg-amber-500 group-hover:text-slate-950 transition-colors">
              <Upload class="w-5 h-5" />
            </div>
            <div>
              <h4 class="text-sm font-black text-white group-hover:text-amber-300 transition-colors">
                Issue Stock
              </h4>
              <p class="text-[11px] text-slate-400 mt-0.5 leading-snug">
                Pick & deduct stored parts for production work orders.
              </p>
            </div>
            <div class="text-xs font-bold text-amber-400 flex items-center gap-1 pt-1">
              <span>Start Issue &rarr;</span>
            </div>
          </button>
        </div>
      </div>
    </Modal>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { Menu, Cpu, Radio, QrCode, LogOut, MapPin, Download, Upload } from 'lucide-vue-next'
import locationsApi from '@/api/locations'
import Modal from './Modal.vue'
import NfcReaderModal from './NfcReaderModal.vue'
import BarcodeScannerModal from './BarcodeScannerModal.vue'

defineEmits(['toggleSidebar'])

const authStore = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const showNfcModal = ref(false)
const showBarcodeModal = ref(false)
const showActionModal = ref(false)
const selectedActionLoc = ref(null)

const onLocationResolved = (loc) => {
  selectedActionLoc.value = loc
  showActionModal.value = true
}

const navigateToAction = (type) => {
  if (!selectedActionLoc.value) return
  const locCode = selectedActionLoc.value.location_code
  showActionModal.value = false
  if (type === 'receive') {
    toast.success(`Location ${locCode} selected → Opening Receive form`)
    router.push({ path: '/stock-operations', query: { tab: 'receive', location: locCode, t: Date.now() } })
  } else {
    toast.success(`Location ${locCode} selected → Opening Issue form`)
    router.push({ path: '/stock-operations', query: { tab: 'issue', location: locCode, t: Date.now() } })
  }
}

const onBarcodeScanned = async (code) => {
  const cleanCode = (code || '').trim()
  if (!cleanCode) return

  if (cleanCode.startsWith('CELL-')) {
    router.push({ path: '/cells', query: { search: cleanCode } })
    return
  }

  // Attempt to resolve as warehouse location
  try {
    const locTag = cleanCode.replace('inventory://location/', '').trim()
    let locRes = null
    try {
      locRes = await locationsApi.getByCode(locTag)
    } catch {
      locRes = await locationsApi.getByNfc(cleanCode)
    }
    if (locRes && (locRes.data || locRes._id)) {
      const locData = locRes.data || locRes
      selectedActionLoc.value = locData
      showActionModal.value = true
      return
    }
  } catch (e) {
    // If not a location, fallback to toast
  }

  toast.info(`Scanned Code: ${cleanCode}`)
}
</script>
