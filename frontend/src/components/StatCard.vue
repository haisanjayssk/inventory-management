<template>
  <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-lg relative overflow-hidden transition-all duration-200 hover:border-slate-700">
    <div class="flex items-center justify-between">
      <p class="text-xs font-semibold uppercase tracking-wider text-slate-400">{{ title }}</p>
      <div class="p-2.5 rounded-xl bg-slate-800/80 text-emerald-400 border border-slate-700/50">
        <component :is="icon" class="w-5 h-5" />
      </div>
    </div>
    <div class="mt-3 flex items-baseline gap-2">
      <span class="text-2xl lg:text-3xl font-extrabold text-white mono">{{ value }}</span>
      <span v-if="unit" class="text-xs font-semibold text-slate-400">{{ unit }}</span>
    </div>
    <p v-if="subtitle" class="mt-2 text-xs text-slate-400 flex items-center gap-1.5">
      <slot name="subtitle">{{ subtitle }}</slot>
    </p>
    <!-- Background accent glow -->
    <div class="absolute -right-6 -bottom-6 w-24 h-24 bg-emerald-500/5 rounded-full blur-2xl pointer-events-none"></div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: [String, Number],
  unit: String,
  subtitle: String,
  icon: Object
})
</script>
