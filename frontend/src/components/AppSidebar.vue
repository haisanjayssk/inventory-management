<template>
  <aside
    class="fixed inset-y-0 left-0 z-40 w-64 bg-slate-900 border-r border-slate-800 flex flex-col transition-transform duration-300 lg:static lg:translate-x-0"
    :class="isOpen ? 'translate-x-0' : '-translate-x-full'"
  >
    <!-- App Header in Sidebar for mobile -->
    <div class="h-16 flex items-center justify-between px-6 border-b border-slate-800 lg:hidden">
      <div class="flex items-center gap-2 text-white font-bold">
        <Cpu class="w-5 h-5 text-emerald-400" />
        <span>MES Inventory</span>
      </div>
      <button @click="$emit('close')" class="text-slate-400 hover:text-white">
        <X class="w-5 h-5" />
      </button>
    </div>

    <!-- Navigation Links -->
    <div class="flex-1 overflow-y-auto py-4 px-3 space-y-1">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        @click="$emit('close')"
        class="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all group"
        :class="$route.path === item.path ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/30' : 'text-slate-400 hover:bg-slate-800/80 hover:text-white'"
      >
        <component
          :is="item.icon"
          class="w-4 h-4 flex-shrink-0 transition-transform group-hover:scale-110"
          :class="$route.path === item.path ? 'text-white' : 'text-slate-400 group-hover:text-emerald-400'"
        />
        <span>{{ item.label }}</span>
        <span
          v-if="item.badge"
          class="ml-auto text-[10px] px-1.5 py-0.5 rounded-md font-mono font-bold"
          :class="$route.path === item.path ? 'bg-emerald-700 text-white' : 'bg-slate-800 text-emerald-400 border border-slate-700'"
        >
          {{ item.badge }}
        </span>
      </router-link>
    </div>

    <!-- System Status Footer -->
    <div class="p-3 border-t border-slate-800 text-[11px] text-slate-400 bg-slate-950/40">
      <div class="flex items-center justify-between">
        <span class="font-medium">NFC Engine</span>
        <span class="inline-flex items-center gap-1 text-emerald-400 font-mono">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
          ACTIVE
        </span>
      </div>
    </div>
  </aside>

</template>

<script setup>
import { computed } from 'vue'
import {
  LayoutDashboard, ArrowLeftRight, Boxes, BatteryCharging,
  Layers, Sliders, MapPin, Building2, History, BarChart3, Users, X, Cpu
} from 'lucide-vue-next'

defineProps({
  isOpen: Boolean
})

defineEmits(['close'])

const navItems = [
  { label: 'Dashboard', path: '/', icon: LayoutDashboard },
  { label: 'Stock Operations', path: '/stock-operations', icon: ArrowLeftRight, badge: 'CORE' },
  { label: 'Inventory', path: '/inventory', icon: Boxes },
  { label: 'Battery Cells (MES)', path: '/cells', icon: BatteryCharging },
  { label: 'Parts Catalog', path: '/parts', icon: Layers },
  { label: 'Part Types & Fields', path: '/part-types', icon: Sliders },
  { label: 'Warehouse & NFC', path: '/locations', icon: MapPin },
  { label: 'Lots & Batches', path: '/lots', icon: Layers },
  { label: 'Vendors', path: '/vendors', icon: Building2 },
  { label: 'Transactions Audit', path: '/transactions', icon: History },
  { label: 'Reports', path: '/reports', icon: BarChart3 },
  { label: 'User Management', path: '/users', icon: Users, badge: 'ADMIN' },
]
</script>

