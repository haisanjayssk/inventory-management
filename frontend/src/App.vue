<template>
  <div class="h-full min-h-screen bg-slate-950 flex flex-col font-sans">
    <!-- Navbar (shown only when authenticated) -->
    <AppNavbar v-if="authStore.isAuthenticated" @toggleSidebar="sidebarOpen = !sidebarOpen" />

    <!-- Main Body Container -->
    <div class="flex-1 flex overflow-hidden">
      <!-- Sidebar Navigation -->
      <AppSidebar
        v-if="authStore.isAuthenticated"
        :isOpen="sidebarOpen"
        @close="sidebarOpen = false"
      />

      <!-- Content Area -->
      <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8 bg-slate-950">
        <div class="max-w-7xl mx-auto">
          <router-view />
        </div>
      </main>
    </div>

    <!-- Global Toast Alert Container -->
    <ToastContainer />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import AppNavbar from '@/components/AppNavbar.vue'
import AppSidebar from '@/components/AppSidebar.vue'
import ToastContainer from '@/components/ToastContainer.vue'

const authStore = useAuthStore()
const sidebarOpen = ref(false)
</script>
