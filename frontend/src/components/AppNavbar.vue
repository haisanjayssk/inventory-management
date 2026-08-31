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
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { Menu, Cpu, Radio, QrCode, LogOut } from 'lucide-vue-next'
import NfcReaderModal from './NfcReaderModal.vue'
import BarcodeScannerModal from './BarcodeScannerModal.vue'

defineEmits(['toggleSidebar'])

const authStore = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const showNfcModal = ref(false)
const showBarcodeModal = ref(false)

const onLocationResolved = (loc) => {
  toast.success(`Scanned Location: ${loc.location_code}`)
  router.push({ path: '/locations', query: { code: loc.location_code } })
}

const onBarcodeScanned = (code) => {
  if (code.startsWith('CELL-')) {
    router.push({ path: '/cells', query: { search: code } })
  } else {
    toast.info(`Scanned Code: ${code}`)
  }
}
</script>
