<template>
  <Modal :modelValue="modelValue" @update:modelValue="$emit('update:modelValue', $event)" title="NFC Tag Location Reader" maxWidth="max-w-md">
    <template #icon>
      <Radio class="w-5 h-5 text-emerald-400 animate-pulse" />
    </template>

    <div class="space-y-5 text-center">
      <!-- NFC Waves Graphic -->
      <div class="relative w-28 h-28 mx-auto flex items-center justify-center">
        <div class="absolute inset-0 rounded-full bg-emerald-500/10 animate-ping"></div>
        <div class="absolute inset-2 rounded-full bg-emerald-500/20 animate-pulse"></div>
        <div class="w-16 h-16 rounded-full bg-emerald-500/30 border border-emerald-500/50 flex items-center justify-center text-emerald-300 shadow-lg shadow-emerald-500/20">
          <Radio class="w-8 h-8" />
        </div>
      </div>

      <div>
        <h4 class="text-base font-bold text-white">Hold Device Near NFC Tag</h4>
        <p class="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
          Scan the physical NFC tag on the warehouse bin/box to identify and validate location.
        </p>
      </div>

      <!-- Quick Preset Simulation Buttons for Desktop/Demo Testing -->
      <div class="bg-slate-950/60 border border-slate-800 rounded-xl p-3 text-left">
        <span class="text-[11px] font-semibold uppercase tracking-wider text-slate-400 block mb-2">
          Demo / Quick Location Emulators:
        </span>
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="code in demoLocations"
            :key="code"
            @click="handleManualResolve(code)"
            class="px-2.5 py-1 text-xs font-mono bg-slate-800 hover:bg-emerald-950 hover:border-emerald-500/50 border border-slate-700 rounded text-slate-300 hover:text-emerald-300 transition"
          >
            {{ code }}
          </button>
        </div>
      </div>

      <!-- Manual Input Fallback -->
      <div class="text-left pt-1">
        <label class="block text-xs font-medium text-slate-400 mb-1">
          Or Enter NFC Tag UID / Location Code:
        </label>
        <div class="flex gap-2">
          <input
            v-model="inputNfc"
            @keyup.enter="handleManualResolve(inputNfc)"
            type="text"
            placeholder="e.g. inventory://location/E11-1A or E11-1A"
            class="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500 font-mono"
          />
          <button
            @click="handleManualResolve(inputNfc)"
            class="px-3 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold rounded-lg transition"
          >
            Resolve
          </button>
        </div>
      </div>
    </div>
  </Modal>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import Modal from './Modal.vue'
import { Radio } from 'lucide-vue-next'
import { useNfc } from '@/composables/useNfc'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'locationResolved'])

const inputNfc = ref('')
const demoLocations = ['E11-1A', 'E11-1B', 'E11-1C', 'E11-2A', 'E11-2B', 'E12-1A', 'E21-1A']
const { startScan, resolveTag } = useNfc()

const handleManualResolve = async (tag) => {
  if (!tag) return
  const loc = await resolveTag(tag, (resolved) => {
    emit('locationResolved', resolved)
    emit('update:modelValue', false)
  })
  if (loc) {
    emit('locationResolved', loc)
    emit('update:modelValue', false)
  }
}

watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    startScan((resolved) => {
      emit('locationResolved', resolved)
      emit('update:modelValue', false)
    })
  }
})
</script>
