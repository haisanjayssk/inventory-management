<template>
  <div class="fixed bottom-5 right-5 z-50 flex flex-col gap-2 max-w-md w-full pointer-events-none px-4">
    <transition-group
      enter-active-class="transform ease-out duration-300 transition"
      enter-from-class="translate-y-2 opacity-0 sm:translate-y-0 sm:translate-x-2"
      enter-to-class="translate-y-0 opacity-100 sm:translate-x-0"
      leave-active-class="transition ease-in duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-for="toast in toastStore.toasts"
        :key="toast.id"
        class="pointer-events-auto flex items-start gap-3 p-4 rounded-xl shadow-2xl border backdrop-blur-md text-sm font-medium"
        :class="getToastClasses(toast.type)"
      >
        <component :is="getIcon(toast.type)" class="w-5 h-5 flex-shrink-0 mt-0.5" />
        <div class="flex-1 leading-snug break-words">
          {{ toast.message }}
        </div>
        <button
          @click="toastStore.remove(toast.id)"
          class="text-slate-400 hover:text-white transition-colors ml-2 p-1"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useToastStore } from '@/stores/toast'
import { CheckCircle2, AlertTriangle, AlertCircle, Info, X } from 'lucide-vue-next'

const toastStore = useToastStore()

const getToastClasses = (type) => {
  switch (type) {
    case 'success':
      return 'bg-emerald-950/90 border-emerald-500/40 text-emerald-100'
    case 'error':
      return 'bg-rose-950/90 border-rose-500/40 text-rose-100'
    case 'warning':
      return 'bg-amber-950/90 border-amber-500/40 text-amber-100'
    default:
      return 'bg-slate-900/90 border-slate-700 text-slate-100'
  }
}

const getIcon = (type) => {
  switch (type) {
    case 'success': return CheckCircle2
    case 'error': return AlertCircle
    case 'warning': return AlertTriangle
    default: return Info
  }
}
</script>
