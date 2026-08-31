<template>
  <Modal :modelValue="modelValue" @update:modelValue="$emit('update:modelValue', $event)" title="Scan Barcode / QR / 2D DataMatrix" maxWidth="max-w-lg">
    <template #icon>
      <QrCode class="w-5 h-5" />
    </template>

    <div class="space-y-4">
      <!-- Camera Viewfinder -->
      <div class="relative w-full aspect-video bg-black rounded-xl overflow-hidden border border-slate-700 flex items-center justify-center">
        <div id="camera-reader" class="w-full h-full"></div>
        <div v-if="!cameraActive" class="absolute inset-0 flex flex-col items-center justify-center p-4 bg-slate-900/90 text-center gap-3">
          <Camera class="w-10 h-10 text-slate-500 animate-pulse" />
          <p class="text-xs text-slate-400">Position the QR code, DataMatrix, or Barcode in front of your camera</p>
          <button
            @click="startCamera"
            class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg shadow transition"
          >
            Start Camera Scanner
          </button>
        </div>
      </div>

      <!-- Manual Input Fallback / USB HID Scanner Support -->
      <div class="pt-2">
        <label class="block text-xs font-medium text-slate-400 mb-1">
          Or Type / Use USB Hardware Wedge Scanner:
        </label>
        <div class="flex gap-2">
          <input
            v-model="manualCode"
            @keyup.enter="submitManual"
            type="text"
            placeholder="e.g. CELL-2026-000001, E11-1A, RES-10K-0603"
            class="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-emerald-500 font-mono"
            autofocus
          />
          <button
            @click="submitManual"
            class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold rounded-lg transition"
          >
            Confirm
          </button>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref, onBeforeUnmount, watch } from 'vue'
import { Html5Qrcode } from 'html5-qrcode'
import Modal from './Modal.vue'
import { QrCode, Camera } from 'lucide-vue-next'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'scan'])

const cameraActive = ref(false)
const manualCode = ref('')
let html5QrCode = null

const startCamera = async () => {
  try {
    html5QrCode = new Html5Qrcode('camera-reader')
    cameraActive.value = true
    await html5QrCode.start(
      { facingMode: 'environment' },
      {
        fps: 10,
        qrbox: { width: 250, height: 250 }
      },
      (decodedText) => {
        emit('scan', decodedText)
        stopCamera()
        emit('update:modelValue', false)
      },
      () => {}
    )
  } catch (err) {
    cameraActive.value = false
  }
}

const stopCamera = async () => {
  if (html5QrCode && cameraActive.value) {
    try {
      await html5QrCode.stop()
      html5QrCode.clear()
    } catch (e) {}
    cameraActive.value = false
  }
}

const submitManual = () => {
  if (manualCode.value.trim()) {
    emit('scan', manualCode.value.trim())
    manualCode.value = ''
    stopCamera()
    emit('update:modelValue', false)
  }
}

watch(() => props.modelValue, (newVal) => {
  if (!newVal) {
    stopCamera()
  }
})

onBeforeUnmount(() => {
  stopCamera()
})
</script>
