<template>
  <teleport to="body">
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="modelValue"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm overflow-y-auto"
        @click.self="closeOnBackdrop && $emit('update:modelValue', false)"
      >
        <div
          class="relative w-full rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl p-6 overflow-hidden my-8"
          :class="maxWidthClass"
        >
          <!-- Modal Header -->
          <div class="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
            <div class="flex items-center gap-3">
              <div v-if="$slots.icon" class="p-2 rounded-lg bg-slate-800 text-emerald-400">
                <slot name="icon" />
              </div>
              <h3 class="text-lg font-bold text-white tracking-wide">{{ title }}</h3>
            </div>
            <button
              @click="$emit('update:modelValue', false)"
              class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
            >
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Modal Body -->
          <div class="max-h-[75vh] overflow-y-auto pr-1">
            <slot />
          </div>

          <!-- Modal Footer -->
          <div v-if="$slots.footer" class="mt-6 pt-4 border-t border-slate-800 flex justify-end gap-3">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script setup>
import { computed } from 'vue'
import { X } from 'lucide-vue-next'

const props = defineProps({
  modelValue: Boolean,
  title: String,
  maxWidth: {
    type: String,
    default: 'max-w-xl'
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  }
})

defineEmits(['update:modelValue'])

const maxWidthClass = computed(() => {
  return props.maxWidth || 'max-w-xl'
})
</script>
