<template>
  <div class="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Ambient background glow -->
    <div class="absolute -top-40 -left-40 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl pointer-events-none"></div>

    <div class="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
      <div class="flex justify-center">
        <div class="w-14 h-14 rounded-2xl bg-emerald-500 flex items-center justify-center text-slate-950 font-black shadow-xl shadow-emerald-500/30">
          <Cpu class="w-8 h-8" />
        </div>
      </div>
      <h2 class="mt-4 text-center text-2xl font-extrabold text-white tracking-tight">
        MES Inventory System
      </h2>
      <p class="mt-1 text-center text-xs text-slate-400">
        Electronics & Battery Cell Manufacturing Platform
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10 px-4">
      <div class="bg-slate-900/90 border border-slate-800 py-8 px-6 shadow-2xl rounded-2xl sm:px-10 backdrop-blur-xl">
        <form class="space-y-5" @submit.prevent="handleLogin">
          <div>
            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-300">
              Username or Email
            </label>
            <div class="mt-1">
              <input
                v-model="usernameOrEmail"
                type="text"
                required
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition"
                placeholder="admin@mes.com or admin"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-300">
              Password
            </label>
            <div class="mt-1">
              <input
                v-model="password"
                type="password"
                required
                class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-lg shadow-emerald-900/40 text-sm font-bold text-slate-950 bg-emerald-400 hover:bg-emerald-300 focus:outline-none transition disabled:opacity-50"
          >
            <span v-if="!loading">Sign In</span>
            <span v-else class="flex items-center gap-2">
              <span class="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
              Authenticating...
            </span>
          </button>
        </form>

        <!-- Quick Demo Profiles Switcher -->
        <div class="mt-6 pt-6 border-t border-slate-800">
          <p class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2 text-center">
            Demo Test Accounts (One-Click Fill)
          </p>
          <div class="grid grid-cols-2 gap-2">
            <button
              v-for="role in demoAccounts"
              :key="role.name"
              @click="fillAccount(role)"
              class="p-2 text-left bg-slate-950/80 hover:bg-slate-800 border border-slate-800 hover:border-slate-700 rounded-lg transition text-xs"
            >
              <div class="font-bold text-white">{{ role.name }}</div>
              <div class="text-[10px] text-emerald-400 font-mono">{{ role.role }}</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToastStore } from '@/stores/toast'
import { Cpu } from 'lucide-vue-next'

const usernameOrEmail = ref('admin')
const password = ref('Admin@123')
const loading = ref(false)

const authStore = useAuthStore()
const toast = useToastStore()
const router = useRouter()

const demoAccounts = [
  { name: 'Administrator', user: 'admin', pass: 'Admin@123', role: 'ADMIN' },
  { name: 'Inv. Manager', user: 'inventory_manager', pass: 'Manager@123', role: 'MANAGER' },
  { name: 'Store Operator', user: 'operator', pass: 'Operator@123', role: 'OPERATOR' },
  { name: 'Quality Viewer', user: 'viewer', pass: 'Viewer@123', role: 'VIEWER' }
]



const fillAccount = (acc) => {
  usernameOrEmail.value = acc.user
  password.value = acc.pass
}

const handleLogin = async () => {
  loading.value = true
  try {
    const user = await authStore.login(usernameOrEmail.value, password.value)
    toast.success(`Welcome back, ${user.full_name}!`)
    router.push('/')
  } catch (err) {
    // Handled in Axios interceptor
  } finally {
    loading.value = false
  }
}
</script>
