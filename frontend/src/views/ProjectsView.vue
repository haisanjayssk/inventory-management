<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight flex items-center gap-2">
          <FolderKanban class="w-6 h-6 text-emerald-400" />
          <span>Projects & Work Orders</span>
        </h1>
        <p class="text-xs text-slate-400 mt-0.5">Manufacturing projects, EV assembly work orders, and material requisition targets</p>
      </div>

      <button
        @click="openCreateModal"
        class="flex items-center gap-1.5 px-3.5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-xl shadow-lg transition"
      >
        <Plus class="w-4 h-4" />
        <span>New Project</span>
      </button>
    </div>

    <!-- Metric Summary Cards -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 flex items-center justify-between">
        <div>
          <span class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Active Projects</span>
          <div class="text-2xl font-black text-white font-mono mt-1">{{ projects.length }}</div>
        </div>
        <div class="w-10 h-10 rounded-xl bg-emerald-950/60 border border-emerald-800/50 flex items-center justify-center text-emerald-400">
          <Briefcase class="w-5 h-5" />
        </div>
      </div>

      <div class="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 flex items-center justify-between">
        <div>
          <span class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Responsible Leads</span>
          <div class="text-2xl font-black text-white font-mono mt-1">{{ uniqueLeadsCount }}</div>
        </div>
        <div class="w-10 h-10 rounded-xl bg-blue-950/60 border border-blue-800/50 flex items-center justify-center text-blue-400">
          <User class="w-5 h-5" />
        </div>
      </div>

      <div class="p-4 rounded-2xl bg-slate-900/90 border border-slate-800 flex items-center justify-between">
        <div>
          <span class="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Requisition Ready</span>
          <div class="text-2xl font-black text-emerald-400 font-mono mt-1">100%</div>
        </div>
        <div class="w-10 h-10 rounded-xl bg-purple-950/60 border border-purple-800/50 flex items-center justify-center text-purple-400">
          <ClipboardList class="w-5 h-5" />
        </div>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-lg flex flex-col sm:flex-row items-center justify-between gap-3">
      <div class="relative w-full sm:w-80">
        <Search class="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search project ID, title, lead..."
          class="w-full bg-slate-950 border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-white font-mono focus:outline-none focus:border-emerald-500"
        />
      </div>

      <div class="text-xs font-mono text-slate-400">
        Showing <b class="text-white">{{ filteredProjects.length }}</b> of <b class="text-white">{{ projects.length }}</b> projects
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="p-12 text-center text-slate-400 flex flex-col items-center justify-center gap-3">
      <div class="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
      <span class="text-xs font-mono">Loading projects...</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="filteredProjects.length === 0" class="p-12 text-center bg-slate-900/60 border border-slate-800 rounded-2xl space-y-3">
      <FolderKanban class="w-8 h-8 text-slate-600 mx-auto" />
      <p class="text-xs text-slate-400">No projects found.</p>
      <button
        @click="openCreateModal"
        class="inline-flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-bold rounded-lg shadow transition"
      >
        <Plus class="w-3.5 h-3.5" />
        <span>Create First Project</span>
      </button>
    </div>

    <!-- Projects Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="prj in filteredProjects"
        :key="prj.project_id"
        class="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-2xl p-5 shadow-lg flex flex-col justify-between transition-all duration-200 hover:scale-[1.01]"
      >
        <div>
          <!-- Top Row: Project ID & Actions -->
          <div class="flex items-center justify-between mb-3">
            <span class="px-2.5 py-1 bg-emerald-950 border border-emerald-800/60 rounded-lg text-emerald-400 text-xs font-mono font-black">
              {{ prj.project_id }}
            </span>

            <div class="flex items-center gap-1">
              <button
                @click="openEditModal(prj)"
                class="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition"
                title="Edit Project"
              >
                <Edit3 class="w-3.5 h-3.5" />
              </button>
              <button
                @click="deleteProject(prj)"
                class="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-slate-800 transition"
                title="Delete Project"
              >
                <Trash2 class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <!-- Description -->
          <h3 class="text-sm font-bold text-white mb-2 leading-snug">
            {{ prj.project_desc || 'No description provided' }}
          </h3>

          <!-- Details -->
          <div class="space-y-1.5 text-xs text-slate-400 font-mono">
            <div class="flex items-center gap-2">
              <User class="w-3.5 h-3.5 text-slate-500" />
              <span>Lead: <b class="text-slate-200">{{ prj.responsible_person || 'Unassigned' }}</b></span>
            </div>
            <div class="flex items-center gap-2 text-[11px]">
              <Calendar class="w-3.5 h-3.5 text-slate-500" />
              <span>Created: {{ new Date(prj.created_at).toLocaleDateString() }}</span>
            </div>
          </div>
        </div>

        <!-- Card Footer Actions -->
        <div class="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
          <router-link
            :to="{ path: '/indents', query: { project_id: prj.project_id } }"
            class="text-slate-400 hover:text-slate-200 font-medium text-[11px]"
          >
            View Indents &rarr;
          </router-link>

          <router-link
            :to="{ path: '/indents', query: { new: 'true', project_id: prj.project_id } }"
            class="text-emerald-400 hover:text-emerald-300 font-bold flex items-center gap-1 text-[11px]"
          >
            <span>Raise Indent</span>
            <ArrowRight class="w-3 h-3" />
          </router-link>
        </div>
      </div>
    </div>

    <!-- Create / Edit Modal -->
    <Modal v-model="showModal" :title="isEditing ? 'Edit Project' : 'Create New Project'" maxWidth="max-w-lg">
      <template #icon>
        <FolderKanban class="w-5 h-5 text-emerald-400" />
      </template>

      <form @submit.prevent="saveProject" class="space-y-4">
        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Project ID / Work Order #</label>
          <input
            v-model="form.project_id"
            type="text"
            required
            :disabled="isEditing"
            placeholder="e.g. PRJ-002 or WO-2026-01"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white font-mono uppercase font-bold disabled:opacity-50"
          />
          <span class="text-[10px] text-slate-500 mt-1 block">Unique alphanumeric identifier used across indents and stock issues.</span>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Project Description / Scope</label>
          <textarea
            v-model="form.project_desc"
            rows="3"
            required
            placeholder="e.g. 50kWh High-Voltage Battery Pack Production Batch 2"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-emerald-500"
          ></textarea>
        </div>

        <div>
          <label class="block text-xs font-bold text-slate-300 uppercase mb-1">Responsible Person / Project Lead</label>
          <select
            v-if="usersList.length > 0"
            v-model="form.responsible_person"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
          >
            <option value="">Select Project Lead</option>
            <option v-for="u in usersList" :key="u._id" :value="u.username">
              {{ u.full_name || u.name || u.username }} ({{ u.role }})
            </option>
          </select>
          <input
            v-else
            v-model="form.responsible_person"
            type="text"
            placeholder="e.g. admin or engineer"
            class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3 py-2 text-xs text-white"
          />
        </div>

        <div class="pt-4 border-t border-slate-800 flex justify-end gap-2">
          <button type="button" @click="showModal = false" class="px-4 py-2 bg-slate-800 text-xs font-bold text-slate-300 rounded-xl">Cancel</button>
          <button type="submit" class="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-xs font-extrabold rounded-xl shadow">
            {{ isEditing ? 'Update Project' : 'Create Project' }}
          </button>
        </div>
      </form>
    </Modal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import projectsApi from '@/api/projects'
import apiClient from '@/api/client'
import Modal from '@/components/Modal.vue'
import { useToastStore } from '@/stores/toast'
import { FolderKanban, Briefcase, Plus, Search, Edit3, Trash2, ClipboardList, User, Calendar, ArrowRight } from 'lucide-vue-next'

const projects = ref([])
const usersList = ref([])
const searchQuery = ref('')
const loading = ref(false)
const showModal = ref(false)
const isEditing = ref(false)
const toast = useToastStore()

const form = ref({
  project_id: '',
  project_desc: '',
  responsible_person: ''
})

const loadProjects = async () => {
  loading.value = true
  try {
    const res = await projectsApi.getAll()
    projects.value = res.data || []
  } catch (e) {
  } finally {
    loading.value = false
  }
}

const loadUsers = async () => {
  try {
    const res = await apiClient.get('/users')
    usersList.value = res.data || []
  } catch (e) {}
}

const filteredProjects = computed(() => {
  if (!searchQuery.value) return projects.value
  const q = searchQuery.value.trim().toLowerCase()
  return projects.value.filter(p =>
    (p.project_id && p.project_id.toLowerCase().includes(q)) ||
    (p.project_desc && p.project_desc.toLowerCase().includes(q)) ||
    (p.responsible_person && p.responsible_person.toLowerCase().includes(q))
  )
})

const uniqueLeadsCount = computed(() => {
  const leads = new Set(projects.value.map(p => p.responsible_person).filter(Boolean))
  return leads.size
})

const openCreateModal = () => {
  isEditing.value = false
  form.value = {
    project_id: '',
    project_desc: '',
    responsible_person: usersList.value[0]?.username || 'admin'
  }
  showModal.value = true
}

const openEditModal = (prj) => {
  isEditing.value = true
  form.value = {
    project_id: prj.project_id,
    project_desc: prj.project_desc,
    responsible_person: prj.responsible_person
  }
  showModal.value = true
}

const saveProject = async () => {
  try {
    if (isEditing.value) {
      await projectsApi.update(form.value.project_id, {
        project_desc: form.value.project_desc,
        responsible_person: form.value.responsible_person
      })
      toast.success('Project updated successfully')
    } else {
      await projectsApi.create({
        project_id: form.value.project_id.trim().toUpperCase(),
        project_desc: form.value.project_desc,
        responsible_person: form.value.responsible_person
      })
      toast.success('Project created successfully')
    }
    showModal.value = false
    await loadProjects()
  } catch (err) {}
}

const deleteProject = async (prj) => {
  if (!confirm()) return
  try {
    await projectsApi.delete(prj.project_id)
    toast.success('Project deleted successfully')
    await loadProjects()
  } catch (err) {}
}

onMounted(() => {
  loadProjects()
  loadUsers()
})
</script>
