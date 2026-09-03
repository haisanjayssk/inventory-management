<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">User & Access Management</h1>
        <p class="text-xs text-slate-400 mt-0.5">Manage operator accounts, access roles, credentials, and authentication security</p>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="openCreateModal"
          class="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg shadow transition"
        >
          <UserPlus class="w-3.5 h-3.5" />
          <span>New User</span>
        </button>
      </div>
    </div>

    <!-- Metrics Stat Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard
        title="Total Accounts"
        :value="users.length"
        :icon="Users"
        subtitle="Registered system users"
      />
      <StatCard
        title="Active Users"
        :value="activeUsersCount"
        :icon="UserCheck"
        subtitle="Enabled & authenticated"
      />
      <StatCard
        title="Administrators"
        :value="adminCount"
        :icon="Shield"
        subtitle="Full administrative control"
      />
      <StatCard
        title="Floor Operators"
        :value="operatorCount"
        :icon="Key"
        subtitle="Store & MES operations"
      />
    </div>

    <!-- Filters & Search Bar -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-xl flex flex-col md:flex-row items-center justify-between gap-3">
      <div class="relative w-full md:w-80">
        <Search class="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          v-model="searchQuery"
          @input="fetchUsers"
          type="text"
          placeholder="Search by name, username, or email..."
          class="w-full bg-slate-950 border border-slate-700 rounded-xl pl-9 pr-3.5 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition"
        />
      </div>

      <div class="flex items-center gap-2.5 w-full md:w-auto">
        <select
          v-model="roleFilter"
          @change="fetchUsers"
          class="bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
        >
          <option value="">All Roles</option>
          <option value="ADMIN">ADMIN</option>
          <option value="INVENTORY_MANAGER">INVENTORY_MANAGER</option>
          <option value="STORE_OPERATOR">STORE_OPERATOR</option>
          <option value="VIEWER">VIEWER</option>
        </select>

        <select
          v-model="statusFilter"
          @change="fetchUsers"
          class="bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
        >
          <option value="">All Statuses</option>
          <option value="true">Active Only</option>
          <option value="false">Disabled Only</option>
        </select>

        <button
          @click="resetFilters"
          title="Reset Filters"
          class="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
        >
          <RefreshCw class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Users Table -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider font-semibold">
            <tr>
              <th class="p-3.5">User</th>
              <th class="p-3.5">Email</th>
              <th class="p-3.5">Role</th>
              <th class="p-3.5">Status</th>
              <th class="p-3.5">Created</th>
              <th class="p-3.5 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            <tr v-if="loading">
              <td colspan="6" class="p-8 text-center text-slate-400">
                <div class="flex items-center justify-center gap-2">
                  <RefreshCw class="w-4 h-4 animate-spin text-emerald-400" />
                  <span>Loading user accounts...</span>
                </div>
              </td>
            </tr>
            <tr v-else-if="users.length === 0">
              <td colspan="6" class="p-8 text-center text-slate-500">
                No users found matching current filters.
              </td>
            </tr>
            <tr
              v-for="user in users"
              :key="user._id"
              class="hover:bg-slate-800/40 transition-colors"
            >
              <!-- Avatar & Name -->
              <td class="p-3.5">
                <div class="flex items-center gap-3">
                  <div
                    class="w-8 h-8 rounded-xl flex items-center justify-center font-bold text-xs shadow"
                    :class="getAvatarClass(user.role)"
                  >
                    {{ getInitials(user.full_name || user.username) }}
                  </div>
                  <div>
                    <span class="text-white font-bold block">{{ user.full_name || user.username }}</span>
                    <span class="text-[10px] text-slate-400 font-mono">@{{ user.username }} • {{ user._id }}</span>
                  </div>
                </div>
              </td>

              <!-- Email -->
              <td class="p-3.5 text-slate-300 font-mono">{{ user.email }}</td>

              <!-- Role -->
              <td class="p-3.5">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-mono font-bold border"
                  :class="getRoleBadgeClass(user.role)"
                >
                  {{ user.role }}
                </span>
              </td>

              <!-- Status -->
              <td class="p-3.5">
                <span
                  class="px-2 py-0.5 rounded text-[10px] font-bold border inline-flex items-center gap-1.5"
                  :class="user.active ? 'bg-emerald-950 text-emerald-400 border-emerald-800/60' : 'bg-rose-950 text-rose-400 border-rose-800/60'"
                >
                  <span class="w-1.5 h-1.5 rounded-full" :class="user.active ? 'bg-emerald-400' : 'bg-rose-400'"></span>
                  {{ user.active ? 'ACTIVE' : 'DISABLED' }}
                </span>
              </td>

              <!-- Created -->
              <td class="p-3.5 text-slate-400 font-mono text-[11px]">
                {{ formatDate(user.created_at) }}
              </td>

              <!-- Actions -->
              <td class="p-3.5 text-right">
                <div class="flex items-center justify-end gap-1.5">
                  <button
                    @click="openEditModal(user)"
                    title="Edit Profile & Role"
                    class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition"
                  >
                    <Pencil class="w-3.5 h-3.5" />
                  </button>
                  <button
                    @click="openResetPasswordModal(user)"
                    title="Reset Password"
                    class="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-amber-400 transition"
                  >
                    <Key class="w-3.5 h-3.5" />
                  </button>
                  <button
                    v-if="user.active"
                    @click="toggleUserStatus(user)"
                    title="Deactivate User"
                    class="p-1.5 rounded-lg bg-slate-800 hover:bg-rose-950 text-slate-400 hover:text-rose-400 transition"
                  >
                    <UserX class="w-3.5 h-3.5" />
                  </button>
                  <button
                    v-else
                    @click="toggleUserStatus(user)"
                    title="Reactivate User"
                    class="p-1.5 rounded-lg bg-slate-800 hover:bg-emerald-950 text-slate-400 hover:text-emerald-400 transition"
                  >
                    <UserCheck class="w-3.5 h-3.5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Modal: Create New User -->
    <Modal v-model="showCreateModal" title="Add New User Account" maxWidth="max-w-md">
      <template #icon>
        <UserPlus class="w-5 h-5 text-emerald-400" />
      </template>

      <form @submit.prevent="handleCreateUser" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Full Name <span class="text-rose-400">*</span></label>
          <input
            v-model="createForm.full_name"
            type="text"
            required
            placeholder="e.g. John Doe"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Username <span class="text-rose-400">*</span></label>
          <input
            v-model="createForm.username"
            type="text"
            required
            placeholder="e.g. jdoe"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Email Address <span class="text-rose-400">*</span></label>
          <input
            v-model="createForm.email"
            type="email"
            required
            placeholder="e.g. jdoe@mes.com"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Password <span class="text-rose-400">*</span></label>
          <input
            v-model="createForm.password"
            type="password"
            required
            minlength="6"
            placeholder="Minimum 6 characters"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Access Role <span class="text-rose-400">*</span></label>
          <select
            v-model="createForm.role"
            required
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
          >
            <option value="STORE_OPERATOR">STORE_OPERATOR (Floor actions, scans, transfers)</option>
            <option value="INVENTORY_MANAGER">INVENTORY_MANAGER (Catalog, intake, approvals)</option>
            <option value="ADMIN">ADMIN (Full administrative privileges)</option>
            <option value="VIEWER">VIEWER (Read-only audit reports)</option>
          </select>
        </div>

        <div class="pt-4 border-t border-slate-800 flex justify-end gap-2">
          <button
            type="button"
            @click="showCreateModal = false"
            class="px-4 py-2 bg-slate-800 text-slate-300 text-xs font-bold rounded-xl"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="submitting"
            class="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 text-slate-950 text-xs font-extrabold rounded-xl shadow"
          >
            {{ submitting ? 'Creating...' : 'Create Account' }}
          </button>
        </div>
      </form>
    </Modal>

    <!-- Modal: Edit User -->
    <Modal v-model="showEditModal" title="Edit User Profile & Role" maxWidth="max-w-md">
      <template #icon>
        <Pencil class="w-5 h-5 text-blue-400" />
      </template>

      <form @submit.prevent="handleUpdateUser" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Full Name</label>
          <input
            v-model="editForm.full_name"
            type="text"
            required
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Email Address</label>
          <input
            v-model="editForm.email"
            type="email"
            required
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Access Role</label>
          <select
            v-model="editForm.role"
            required
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
          >
            <option value="STORE_OPERATOR">STORE_OPERATOR</option>
            <option value="INVENTORY_MANAGER">INVENTORY_MANAGER</option>
            <option value="ADMIN">ADMIN</option>
            <option value="VIEWER">VIEWER</option>
          </select>
        </div>

        <div class="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800">
          <div>
            <p class="text-xs font-bold text-white">Account Status</p>
            <p class="text-[10px] text-slate-400">Allow this user to sign in to the platform</p>
          </div>
          <input
            type="checkbox"
            v-model="editForm.active"
            class="w-4 h-4 rounded text-emerald-500 bg-slate-900 border-slate-700 focus:ring-0"
          />
        </div>

        <div class="pt-4 border-t border-slate-800 flex justify-end gap-2">
          <button
            type="button"
            @click="showEditModal = false"
            class="px-4 py-2 bg-slate-800 text-slate-300 text-xs font-bold rounded-xl"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="submitting"
            class="px-5 py-2 bg-blue-500 hover:bg-blue-400 disabled:opacity-50 text-slate-950 text-xs font-extrabold rounded-xl shadow"
          >
            {{ submitting ? 'Saving...' : 'Save Changes' }}
          </button>
        </div>
      </form>
    </Modal>

    <!-- Modal: Reset Password -->
    <Modal v-model="showResetPasswordModal" title="Reset User Password" maxWidth="max-w-md">
      <template #icon>
        <Key class="w-5 h-5 text-amber-400" />
      </template>

      <form @submit.prevent="handleResetPassword" class="space-y-4">
        <div class="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs">
          <p class="text-slate-400">Resetting credentials for:</p>
          <p class="font-bold text-white mt-0.5">{{ selectedUser?.full_name }} (@{{ selectedUser?.username }})</p>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">New Password <span class="text-rose-400">*</span></label>
          <input
            v-model="resetPasswordForm.new_password"
            type="password"
            required
            minlength="6"
            placeholder="Enter new password (min 6 characters)"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
          />
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Confirm New Password <span class="text-rose-400">*</span></label>
          <input
            v-model="resetPasswordForm.confirm_password"
            type="password"
            required
            minlength="6"
            placeholder="Confirm new password"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono"
          />
        </div>

        <div class="pt-4 border-t border-slate-800 flex justify-end gap-2">
          <button
            type="button"
            @click="showResetPasswordModal = false"
            class="px-4 py-2 bg-slate-800 text-slate-300 text-xs font-bold rounded-xl"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="submitting"
            class="px-5 py-2 bg-amber-500 hover:bg-amber-400 disabled:opacity-50 text-slate-950 text-xs font-extrabold rounded-xl shadow"
          >
            {{ submitting ? 'Resetting...' : 'Update Password' }}
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import authApi from '@/api/auth'
import StatCard from '@/components/StatCard.vue'
import Modal from '@/components/Modal.vue'
import { useToastStore } from '@/stores/toast'
import {
  Users,
  UserPlus,
  UserCheck,
  UserX,
  Shield,
  Key,
  Pencil,
  Search,
  RefreshCw
} from 'lucide-vue-next'

const users = ref([])
const loading = ref(false)
const submitting = ref(false)
const toast = useToastStore()

const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')

const showCreateModal = ref(false)
const showEditModal = ref(false)
const showResetPasswordModal = ref(false)

const selectedUser = ref(null)

const createForm = ref({
  full_name: '',
  username: '',
  email: '',
  password: '',
  role: 'STORE_OPERATOR'
})

const editForm = ref({
  full_name: '',
  email: '',
  role: 'STORE_OPERATOR',
  active: true
})

const resetPasswordForm = ref({
  new_password: '',
  confirm_password: ''
})

// Metrics
const activeUsersCount = computed(() => users.value.filter(u => u.active).length)
const adminCount = computed(() => users.value.filter(u => u.role === 'ADMIN').length)
const operatorCount = computed(() => users.value.filter(u => u.role === 'STORE_OPERATOR' || u.role === 'INVENTORY_MANAGER').length)

const fetchUsers = async () => {
  loading.value = true
  try {
    const params = {}
    if (searchQuery.value) params.search = searchQuery.value
    if (roleFilter.value) params.role = roleFilter.value
    if (statusFilter.value !== '') params.active = statusFilter.value

    const res = await authApi.getAllUsers(params)
    users.value = res.data || []
  } catch (err) {
    // Error handled by global interceptor
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  searchQuery.value = ''
  roleFilter.value = ''
  statusFilter.value = ''
  fetchUsers()
}

const openCreateModal = () => {
  createForm.value = {
    full_name: '',
    username: '',
    email: '',
    password: '',
    role: 'STORE_OPERATOR'
  }
  showCreateModal.value = true
}

const handleCreateUser = async () => {
  submitting.value = true
  try {
    await authApi.register(createForm.value)
    toast.success(`User @${createForm.value.username} created successfully`)
    showCreateModal.value = false
    await fetchUsers()
  } catch (err) {
    // Handled by toast interceptor
  } finally {
    submitting.value = false
  }
}

const openEditModal = (user) => {
  selectedUser.value = user
  editForm.value = {
    full_name: user.full_name || '',
    email: user.email || '',
    role: user.role || 'STORE_OPERATOR',
    active: user.active !== false
  }
  showEditModal.value = true
}

const handleUpdateUser = async () => {
  if (!selectedUser.value) return
  submitting.value = true
  try {
    await authApi.updateUser(selectedUser.value._id, editForm.value)
    toast.success('User updated successfully')
    showEditModal.value = false
    await fetchUsers()
  } catch (err) {
    // Handled by toast interceptor
  } finally {
    submitting.value = false
  }
}

const openResetPasswordModal = (user) => {
  selectedUser.value = user
  resetPasswordForm.value = {
    new_password: '',
    confirm_password: ''
  }
  showResetPasswordModal.value = true
}

const handleResetPassword = async () => {
  if (!selectedUser.value) return
  if (resetPasswordForm.value.new_password !== resetPasswordForm.value.confirm_password) {
    toast.error('Passwords do not match')
    return
  }
  submitting.value = true
  try {
    await authApi.resetPassword(selectedUser.value._id, resetPasswordForm.value.new_password)
    toast.success(`Password reset successfully for @${selectedUser.value.username}`)
    showResetPasswordModal.value = false
  } catch (err) {
    // Handled by toast interceptor
  } finally {
    submitting.value = false
  }
}

const toggleUserStatus = async (user) => {
  try {
    await authApi.updateUser(user._id, { active: !user.active })
    toast.success(`User @${user.username} is now ${!user.active ? 'active' : 'disabled'}`)
    await fetchUsers()
  } catch (err) {
    // Handled by toast interceptor
  }
}

const getInitials = (name) => {
  if (!name) return 'U'
  const parts = name.trim().split(' ')
  if (parts.length >= 2) {
    return (parts[0][0] + parts[1][0]).toUpperCase()
  }
  return name.slice(0, 2).toUpperCase()
}

const getAvatarClass = (role) => {
  switch (role) {
    case 'ADMIN':
      return 'bg-rose-500/20 text-rose-400 border border-rose-500/40'
    case 'INVENTORY_MANAGER':
      return 'bg-purple-500/20 text-purple-400 border border-purple-500/40'
    case 'STORE_OPERATOR':
      return 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
    default:
      return 'bg-slate-700 text-slate-300 border border-slate-600'
  }
}

const getRoleBadgeClass = (role) => {
  switch (role) {
    case 'ADMIN':
      return 'bg-rose-950 text-rose-300 border-rose-800/50'
    case 'INVENTORY_MANAGER':
      return 'bg-purple-950 text-purple-300 border-purple-800/50'
    case 'STORE_OPERATOR':
      return 'bg-emerald-950 text-emerald-300 border-emerald-800/50'
    default:
      return 'bg-slate-800 text-slate-300 border-slate-700'
  }
}

const formatDate = (isoStr) => {
  if (!isoStr) return 'N/A'
  try {
    const d = new Date(isoStr)
    return d.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return isoStr
  }
}

onMounted(() => {
  fetchUsers()
})
</script>
