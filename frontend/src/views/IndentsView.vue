<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Indent & Material Dispatch System</h1>
        <p class="text-xs text-slate-400 mt-0.5">Project material requisition, multi-level approvals, store issuance & return lifecycle</p>
      </div>

      <div class="flex items-center gap-2">
        <button
          @click="openCreateReturnModal()"
          class="flex items-center gap-1.5 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-bold rounded-xl transition"
        >
          <RotateCcw class="w-4 h-4 text-amber-400" />
          <span>Raise Return</span>
        </button>
        <button
          @click="openCreateIndentModal()"
          class="flex items-center gap-1.5 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-xl shadow-lg shadow-emerald-950 transition"
        >
          <Plus class="w-4 h-4" />
          <span>Raise Indent</span>
        </button>
      </div>
    </div>

    <!-- Stat Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-5 gap-3">
      <div class="bg-slate-900 border border-slate-800 rounded-xl p-3.5 flex items-center gap-3">
        <div class="p-2.5 rounded-lg bg-slate-800 text-slate-300">
          <ClipboardList class="w-5 h-5" />
        </div>
        <div>
          <p class="text-[11px] font-medium text-slate-400 uppercase tracking-wider">Total Indents</p>
          <p class="text-lg font-extrabold text-white">{{ stats.total }}</p>
        </div>
      </div>

      <div class="bg-slate-900 border border-amber-900/40 rounded-xl p-3.5 flex items-center gap-3">
        <div class="p-2.5 rounded-lg bg-amber-950/60 text-amber-400 border border-amber-800/40">
          <Clock class="w-5 h-5" />
        </div>
        <div>
          <p class="text-[11px] font-medium text-amber-400/90 uppercase tracking-wider">Pending Approval</p>
          <p class="text-lg font-extrabold text-amber-400">{{ stats.pending }}</p>
        </div>
      </div>

      <div class="bg-slate-900 border border-emerald-900/40 rounded-xl p-3.5 flex items-center gap-3">
        <div class="p-2.5 rounded-lg bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
          <PackageCheck class="w-5 h-5" />
        </div>
        <div>
          <p class="text-[11px] font-medium text-emerald-400/90 uppercase tracking-wider">Ready to Issue</p>
          <p class="text-lg font-extrabold text-emerald-400">{{ stats.approved }}</p>
        </div>
      </div>

      <div class="bg-slate-900 border border-blue-900/40 rounded-xl p-3.5 flex items-center gap-3">
        <div class="p-2.5 rounded-lg bg-blue-950/60 text-blue-400 border border-blue-800/40">
          <CheckCircle2 class="w-5 h-5" />
        </div>
        <div>
          <p class="text-[11px] font-medium text-blue-400/90 uppercase tracking-wider">Fully Issued</p>
          <p class="text-lg font-extrabold text-blue-400">{{ stats.issued }}</p>
        </div>
      </div>

      <div class="bg-slate-900 border border-purple-900/40 rounded-xl p-3.5 flex items-center gap-3 col-span-2 lg:col-span-1">
        <div class="p-2.5 rounded-lg bg-purple-950/60 text-purple-400 border border-purple-800/40">
          <RotateCcw class="w-5 h-5" />
        </div>
        <div>
          <p class="text-[11px] font-medium text-purple-400/90 uppercase tracking-wider">Returns Queue</p>
          <p class="text-lg font-extrabold text-purple-400">{{ stats.returnsPending }}</p>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs & Filter Bar -->
    <div class="bg-slate-900 border border-slate-800 rounded-2xl p-4 shadow-xl space-y-4">
      <div class="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <!-- Status Tabs -->
        <div class="flex flex-wrap gap-1.5">
          <button
            v-for="tab in filterTabs"
            :key="tab.id"
            @click="currentFilterTab = tab.id"
            class="px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5"
            :class="currentFilterTab === tab.id ? 'bg-emerald-600 text-white shadow-md' : 'text-slate-400 hover:text-white hover:bg-slate-800'"
          >
            <component :is="tab.icon" class="w-3.5 h-3.5" />
            <span>{{ tab.label }}</span>
            <span
              v-if="tab.count !== undefined"
              class="text-[10px] px-1.5 py-0.2 rounded-full"
              :class="currentFilterTab === tab.id ? 'bg-emerald-800 text-white' : 'bg-slate-800 text-slate-300'"
            >
              {{ tab.count }}
            </span>
          </button>
        </div>

        <!-- Search Input -->
        <div class="relative w-full sm:w-64">
          <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search indent, project, requester..."
            class="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      <!-- MAIN TABLE (INDENTS LIST) -->
      <div v-if="currentFilterTab !== 'RETURNS'" class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead>
            <tr class="border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider">
              <th class="py-3 px-3">Indent #</th>
              <th class="py-3 px-3">Project & Head</th>
              <th class="py-3 px-3">Requester</th>
              <th class="py-3 px-3">Priority</th>
              <th class="py-3 px-3">Status</th>
              <th class="py-3 px-3">Items Summary</th>
              <th class="py-3 px-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            <tr v-if="loadingIndents" class="text-center">
              <td colspan="7" class="py-8 text-slate-500 animate-pulse">Loading indents...</td>
            </tr>
            <tr v-else-if="filteredIndents.length === 0" class="text-center">
              <td colspan="7" class="py-8 text-slate-500">No indents found in this view.</td>
            </tr>
            <tr
              v-for="indent in filteredIndents"
              :key="indent._id"
              class="hover:bg-slate-800/40 transition-colors group"
            >
              <!-- Indent # & Date -->
              <td class="py-3 px-3">
                <div class="font-mono font-bold text-emerald-400">{{ indent.indent_number }}</div>
                <div class="text-[10px] text-slate-400">{{ formatDate(indent.created_at) }}</div>
              </td>

              <!-- Project -->
              <td class="py-3 px-3">
                <div class="font-bold text-white">{{ indent.project_id }}</div>
                <div class="text-[11px] text-slate-400 truncate max-w-[160px]">{{ indent.project_name || 'Project' }}</div>
                <div class="text-[10px] text-slate-400 mt-0.5">Head: {{ indent.project_head_name || indent.project_head_id }}</div>
              </td>

              <!-- Requester -->
              <td class="py-3 px-3">
                <div class="font-medium text-slate-200">{{ indent.requester_name }}</div>
                <div class="text-[10px] text-slate-400">{{ indent.requester_email || indent.requester_id }}</div>
              </td>

              <!-- Priority -->
              <td class="py-3 px-3">
                <span
                  class="px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase border"
                  :class="getPriorityClass(indent.priority)"
                >
                  {{ indent.priority || 'MEDIUM' }}
                </span>
              </td>

              <!-- Status -->
              <td class="py-3 px-3">
                <span
                  class="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase border flex items-center gap-1.5 w-fit"
                  :class="getStatusClass(indent.status)"
                >
                  <span class="w-1.5 h-1.5 rounded-full" :class="getStatusDot(indent.status)"></span>
                  {{ formatStatus(indent.status) }}
                </span>
              </td>

              <!-- Items Summary -->
              <td class="py-3 px-3">
                <div class="space-y-0.5">
                  <div class="text-[11px] text-slate-200 font-semibold">
                    {{ indent.items?.length || 0 }} Part{{ indent.items?.length > 1 ? 's' : '' }} Requested
                  </div>
                  <div class="text-[10px] text-slate-400">
                    Issued: <span class="text-emerald-400 font-mono font-bold">{{ getTotalIssued(indent) }}</span> /
                    {{ getTotalRequested(indent) }} units
                  </div>
                </div>
              </td>

              <!-- Actions -->
              <td class="py-3 px-3 text-right">
                <div class="flex items-center justify-end gap-1.5">
                  <button
                    @click="viewIndentDetails(indent)"
                    class="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition"
                    title="View Details"
                  >
                    <Eye class="w-4 h-4" />
                  </button>

                  <!-- Submit if Draft -->
                  <button
                    v-if="indent.status === 'DRAFT'"
                    @click="submitDraftIndent(indent)"
                    class="px-2 py-1 bg-blue-900/60 hover:bg-blue-800 border border-blue-700/60 text-blue-300 text-[11px] font-bold rounded-lg transition flex items-center gap-1"
                  >
                    <Send class="w-3 h-3" />
                    <span>Submit</span>
                  </button>

                  <!-- Approve / Reject if Pending -->
                  <template v-if="indent.status === 'PENDING_APPROVAL'">
                    <button
                      @click="openApprovalModal(indent)"
                      class="px-2 py-1 bg-emerald-950 hover:bg-emerald-900 border border-emerald-700/60 text-emerald-400 text-[11px] font-bold rounded-lg transition flex items-center gap-1"
                    >
                      <CheckCircle2 class="w-3 h-3" />
                      <span>Review</span>
                    </button>
                  </template>

                  <!-- Issue if Approved / Partially Issued -->
                  <template v-if="['APPROVED', 'PARTIALLY_ISSUED'].includes(indent.status)">
                    <button
                      @click="openIssueModal(indent)"
                      class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-bold rounded-lg shadow-sm transition flex items-center gap-1"
                    >
                      <PackageCheck class="w-3 h-3" />
                      <span>Issue</span>
                    </button>
                  </template>

                  <!-- Return if Issued -->
                  <button
                    v-if="['ISSUED', 'PARTIALLY_ISSUED'].includes(indent.status)"
                    @click="openReturnForIndent(indent)"
                    class="px-2 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-[11px] font-bold rounded-lg transition flex items-center gap-1"
                    title="Return Surplus Material"
                  >
                    <RotateCcw class="w-3 h-3 text-amber-400" />
                    <span>Return</span>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- RETURNS TABLE -->
      <div v-else class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead>
            <tr class="border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider">
              <th class="py-3 px-3">Return #</th>
              <th class="py-3 px-3">Indent & Project</th>
              <th class="py-3 px-3">Requester</th>
              <th class="py-3 px-3">Returned Items</th>
              <th class="py-3 px-3">Status</th>
              <th class="py-3 px-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/60">
            <tr v-if="loadingReturns" class="text-center">
              <td colspan="6" class="py-8 text-slate-500 animate-pulse">Loading material returns...</td>
            </tr>
            <tr v-else-if="returnsList.length === 0" class="text-center">
              <td colspan="6" class="py-8 text-slate-500">No return requests found.</td>
            </tr>
            <tr
              v-for="ret in returnsList"
              :key="ret._id"
              class="hover:bg-slate-800/40 transition-colors"
            >
              <td class="py-3 px-3">
                <div class="font-mono font-bold text-amber-400">{{ ret.return_number }}</div>
                <div class="text-[10px] text-slate-400">{{ formatDate(ret.created_at) }}</div>
              </td>

              <td class="py-3 px-3">
                <div class="font-bold text-white">Indent: {{ ret.indent_number }}</div>
                <div class="text-[11px] text-slate-400">Project: {{ ret.project_id }}</div>
              </td>

              <td class="py-3 px-3">
                <div class="font-medium text-slate-200">{{ ret.requester_name }}</div>
                <div class="text-[10px] text-slate-400">{{ ret.reason || 'Material Return' }}</div>
              </td>

              <td class="py-3 px-3">
                <div v-for="it in ret.items" :key="it.part_id" class="text-[11px]">
                  <span class="font-mono text-white">{{ it.part_code }}</span>:
                  <span class="text-emerald-400 font-bold">{{ it.returned_quantity }}</span> units
                  <span
                    class="ml-1 text-[9px] px-1.5 py-0.2 rounded border font-bold uppercase"
                    :class="it.condition === 'GOOD' ? 'bg-emerald-950 border-emerald-700 text-emerald-400' : 'bg-red-950 border-red-700 text-red-400'"
                  >
                    {{ it.condition }}
                  </span>
                </div>
              </td>

              <td class="py-3 px-3">
                <span
                  class="px-2.5 py-1 rounded-lg text-[10px] font-bold uppercase border"
                  :class="ret.status === 'ACCEPTED' ? 'bg-emerald-950/80 border-emerald-700 text-emerald-400' : (ret.status === 'REJECTED' ? 'bg-red-950/80 border-red-700 text-red-400' : 'bg-amber-950/80 border-amber-700 text-amber-400')"
                >
                  {{ ret.status }}
                </span>
              </td>

              <td class="py-3 px-3 text-right">
                <button
                  v-if="ret.status === 'PENDING_INSPECTION'"
                  @click="openInspectReturnModal(ret)"
                  class="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-500 text-white text-[11px] font-bold rounded-lg shadow transition flex items-center gap-1 ml-auto"
                >
                  <CheckCircle2 class="w-3.5 h-3.5" />
                  <span>Inspect & Restock</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL 1: RAISE INDENT -->
    <Modal v-model="showCreateModal" title="Raise New Material Indent" maxWidth="max-w-3xl">
      <template #icon><ClipboardList class="w-5 h-5" /></template>
      <form @submit.prevent="submitCreateIndent" class="space-y-4 text-xs">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block font-bold text-slate-300 mb-1">Target Project *</label>
            <select
              v-model="newIndent.project_id"
              required
              class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="" disabled>Select Project</option>
              <option v-for="prj in projectsList" :key="prj.project_id" :value="prj.project_id">
                {{ prj.project_id }} - {{ prj.project_desc || prj.project_id }}
              </option>
            </select>
          </div>

          <div>
            <label class="block font-bold text-slate-300 mb-1">Project Head / Approver *</label>
            <select
              v-model="newIndent.project_head_id"
              required
              class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="" disabled>Select Project Head</option>
              <option v-for="u in usersList" :key="u._id" :value="u._id">
                {{ u.name || u.username }} ({{ u.role }})
              </option>
            </select>
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div>
            <label class="block font-bold text-slate-300 mb-1">Priority</label>
            <select
              v-model="newIndent.priority"
              class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="LOW">LOW</option>
              <option value="MEDIUM">MEDIUM</option>
              <option value="HIGH">HIGH</option>
              <option value="URGENT">URGENT</option>
            </select>
          </div>

          <div>
            <label class="block font-bold text-slate-300 mb-1">Required By Date</label>
            <input
              v-model="newIndent.required_by_date"
              type="date"
              class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-emerald-500"
            />
          </div>

          <div>
            <label class="block font-bold text-slate-300 mb-1">Purpose</label>
            <input
              v-model="newIndent.purpose"
              type="text"
              placeholder="e.g. Battery Module Production"
              class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-emerald-500"
            />
          </div>
        </div>

        <!-- Parts Requisition Items -->
        <div class="border-t border-slate-800 pt-3 space-y-2">
          <div class="flex items-center justify-between">
            <span class="font-bold text-slate-200">Requisition Items *</span>
            <button
              type="button"
              @click="addIndentItemRow"
              class="px-2.5 py-1 bg-emerald-950 border border-emerald-800 text-emerald-400 text-[11px] font-bold rounded-lg hover:bg-emerald-900 transition flex items-center gap-1"
            >
              <Plus class="w-3.5 h-3.5" />
              <span>Add Part</span>
            </button>
          </div>

          <div
            v-for="(item, idx) in newIndent.items"
            :key="idx"
            class="p-3 bg-slate-950 rounded-xl border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center gap-2"
          >
            <div class="flex-1 w-full sm:w-auto">
              <select
                v-model="item.part_id"
                required
                class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white text-xs"
              >
                <option value="" disabled>Select Part / Item</option>
                <option v-for="p in partsList" :key="p._id" :value="p._id">
                  {{ p.part_code || p.code }} - {{ p.part_name || p.name }}
                </option>
              </select>
            </div>

            <div class="w-full sm:w-28">
              <input
                v-model.number="item.requested_quantity"
                type="number"
                step="any"
                min="0.001"
                required
                placeholder="Qty"
                class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white text-xs"
              />
            </div>

            <div class="flex-1 w-full sm:w-auto">
              <input
                v-model="item.notes"
                type="text"
                placeholder="Notes / specs"
                class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white text-xs"
              />
            </div>

            <button
              v-if="newIndent.items.length > 1"
              type="button"
              @click="removeIndentItemRow(idx)"
              class="text-red-400 hover:text-red-300 p-1.5"
            >
              <Trash2 class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-4 border-t border-slate-800">
          <button
            type="button"
            @click="showCreateModal = false"
            class="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl font-bold hover:bg-slate-700"
          >
            Cancel
          </button>
          <button
            type="button"
            @click="saveAsDraft"
            class="px-4 py-2 bg-slate-800 border border-slate-700 text-slate-200 rounded-xl font-bold hover:bg-slate-700"
          >
            Save Draft
          </button>
          <button
            type="submit"
            class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold shadow-lg shadow-emerald-950"
          >
            Submit Indent
          </button>
        </div>
      </form>
    </Modal>

    <!-- MODAL 2: APPROVE / REJECT INDENT -->
    <Modal v-model="showApprovalModal" :title="'Review Indent ' + selectedIndent?.indent_number" maxWidth="max-w-lg">
      <template #icon><CheckCircle2 class="w-5 h-5 text-amber-400" /></template>
      <div class="space-y-4 text-xs">
        <div class="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-1">
          <p class="text-white font-bold">Project: <span class="text-emerald-400">{{ selectedIndent?.project_id }}</span></p>
          <p class="text-slate-300">Requester: {{ selectedIndent?.requester_name }}</p>
          <p class="text-slate-300">Purpose: {{ selectedIndent?.purpose || 'None specified' }}</p>
          <div class="pt-2 border-t border-slate-900">
            <span class="text-slate-400 font-semibold">Requested Parts:</span>
            <ul class="list-disc list-inside mt-1 text-slate-300">
              <li v-for="it in selectedIndent?.items" :key="it.part_id">
                {{ it.part_code }}: <span class="text-white font-bold">{{ it.requested_quantity }}</span> units
              </li>
            </ul>
          </div>
        </div>

        <div>
          <label class="block font-bold text-slate-300 mb-1">Approval / Rejection Comments</label>
          <textarea
            v-model="approvalComments"
            rows="3"
            placeholder="Add comments or specific instructions..."
            class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-emerald-500"
          ></textarea>
        </div>

        <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
          <button
            @click="rejectIndentAction"
            class="px-4 py-2 bg-red-950/80 hover:bg-red-900 border border-red-800/60 text-red-300 rounded-xl font-bold"
          >
            Reject Indent
          </button>
          <button
            @click="approveIndentAction"
            class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold shadow-lg"
          >
            Approve Indent
          </button>
        </div>
      </div>
    </Modal>

    <!-- MODAL 3: STORE MATERIAL ISSUE -->
    <Modal v-model="showIssueModal" :title="'Issue Material for ' + selectedIndent?.indent_number" maxWidth="max-w-2xl">
      <template #icon><PackageCheck class="w-5 h-5 text-emerald-400" /></template>
      <form @submit.prevent="submitIssueStock" class="space-y-4 text-xs">
        <div class="p-3 bg-slate-950 rounded-xl border border-slate-800 flex items-center justify-between">
          <div>
            <p class="text-white font-bold">Project: <span class="text-emerald-400">{{ selectedIndent?.project_id }}</span></p>
            <p class="text-slate-400">Requester: {{ selectedIndent?.requester_name }}</p>
          </div>
          <div v-if="selectedIndent?.status" class="text-right">
            <span class="px-2.5 py-1 text-[11px] font-bold rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {{ selectedIndent.status }}
            </span>
          </div>
        </div>

        <div class="space-y-4">
          <div
            v-for="(item, idx) in issueForm.items"
            :key="item.part_id"
            class="p-4 bg-slate-950 rounded-2xl border border-slate-800 space-y-3"
          >
            <!-- Part Header & Remaining Quantity -->
            <div class="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
              <div>
                <span class="font-black text-white font-mono text-sm tracking-wide">
                  {{ item.part_code }}
                </span>
                <span class="text-xs text-slate-400 font-normal ml-2">({{ item.part_name }})</span>
              </div>
              <div class="text-xs text-slate-400">
                Remaining to issue: <strong class="text-emerald-400 font-bold font-mono">{{ item.max_issue }}</strong> units
              </div>
            </div>

            <!-- Stored Places & Active Inventory -->
            <div>
              <div class="flex items-center justify-between mb-1.5">
                <span class="text-[10px] uppercase font-bold text-slate-400 tracking-wider flex items-center gap-1">
                  <MapPin class="w-3 h-3 text-emerald-400" />
                  <span>Stored Locations & Stock (Click to Select)</span>
                </span>
                <span v-if="item.inventoryLocations?.length" class="text-[10px] text-emerald-400 font-bold">
                  {{ item.inventoryLocations.length }} storage place(s) available
                </span>
              </div>

              <!-- Loading State -->
              <div v-if="item.loadingLots" class="p-3 bg-slate-900/60 rounded-xl border border-slate-800 flex items-center gap-2 text-xs text-slate-400">
                <Clock class="w-4 h-4 animate-spin text-emerald-400" />
                <span>Checking storage locations and active batches...</span>
              </div>

              <!-- Storage Location Chips -->
              <div v-else-if="item.inventoryLocations && item.inventoryLocations.length > 0" class="flex flex-wrap gap-2">
                <button
                  v-for="(inv, iIdx) in item.inventoryLocations"
                  :key="iIdx"
                  type="button"
                  @click="selectLocationLot(item, inv)"
                  class="flex items-center gap-2 px-3 py-2 rounded-xl border text-left text-xs transition-all"
                  :class="(item.location_code === inv.location_code && (item.lot_number === inv.lot_number || item.lot_number === inv.lot_batch_no))
                    ? 'bg-emerald-950/50 border-emerald-500 text-white ring-1 ring-emerald-500/40 shadow-sm shadow-emerald-950/50'
                    : 'bg-slate-900 hover:bg-slate-800/80 border-slate-800 text-slate-300'"
                >
                  <MapPin
                    class="w-3.5 h-3.5 flex-shrink-0"
                    :class="(item.location_code === inv.location_code && (item.lot_number === inv.lot_number || item.lot_number === inv.lot_batch_no)) ? 'text-emerald-400' : 'text-slate-500'"
                  />
                  <div>
                    <div class="font-bold font-mono text-white flex items-center gap-1.5">
                      <span>{{ inv.location_code }}</span>
                      <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-normal">
                        Lot: {{ inv.lot_number || inv.lot_batch_no || 'STANDARD' }}
                      </span>
                    </div>
                    <div class="text-[10px] text-slate-400">
                      Stock: <strong class="text-emerald-400 font-mono">{{ (inv.available_quantity ?? inv.quantity)?.toLocaleString() }}</strong> units
                    </div>
                  </div>
                </button>
              </div>

              <!-- No Stock Found Banner -->
              <div v-else class="p-2.5 bg-amber-950/20 border border-amber-800/40 rounded-xl text-amber-300 text-xs">
                <span>⚠️ No active stock location found for this part. You can manually enter location and lot below.</span>
              </div>
            </div>

            <!-- Input Fields Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
              <!-- Source Location -->
              <div>
                <label class="block text-[10px] text-slate-300 uppercase font-bold mb-1">Source Location *</label>
                <input
                  v-model="item.location_code"
                  type="text"
                  required
                  placeholder="e.g. E11-1A"
                  class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white text-xs font-mono font-bold focus:outline-none focus:border-emerald-500"
                />
              </div>

              <!-- Lot / Batch Selection Dropdown -->
              <div>
                <label class="block text-[10px] text-slate-300 uppercase font-bold mb-1">Lot / Batch No *</label>
                <select
                  v-if="item.inventoryLocations && item.inventoryLocations.length > 0"
                  v-model="item.lot_number"
                  @change="onIssueLotChanged(item)"
                  class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white text-xs font-mono focus:outline-none focus:border-emerald-500"
                >
                  <option value="">-- Select Available Lot --</option>
                  <option
                    v-for="(inv, iIdx) in item.inventoryLocations"
                    :key="iIdx"
                    :value="inv.lot_number || inv.lot_batch_no || 'STANDARD'"
                  >
                    {{ inv.lot_number || inv.lot_batch_no || 'STANDARD' }} (Loc: {{ inv.location_code }}, Avail: {{ (inv.available_quantity ?? inv.quantity)?.toLocaleString() }})
                  </option>
                </select>
                <input
                  v-else
                  v-model="item.lot_number"
                  type="text"
                  placeholder="e.g. LOT-001 (Optional)"
                  class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white text-xs font-mono focus:outline-none focus:border-emerald-500"
                />
              </div>

              <!-- Issue Quantity -->
              <div>
                <label class="block text-[10px] text-slate-300 uppercase font-bold mb-1">Issue Quantity *</label>
                <input
                  v-model.number="item.issued_quantity"
                  type="number"
                  step="any"
                  :max="item.max_issue"
                  min="0.001"
                  required
                  class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white text-xs font-bold font-mono focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="block font-bold text-slate-300 mb-1">Dispatch Remarks</label>
          <input
            v-model="issueForm.comments"
            type="text"
            placeholder="e.g. Dispatched to Assembly Station 2"
            class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
          <button
            type="button"
            @click="showIssueModal = false"
            class="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-bold transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold shadow-lg transition-colors"
          >
            Confirm Issue & Deduct Stock
          </button>
        </div>
      </form>
    </Modal>

    <!-- MODAL 4: RAISE MATERIAL RETURN -->
    <Modal v-model="showReturnModal" title="Raise Material Return" maxWidth="max-w-2xl">
      <template #icon><RotateCcw class="w-5 h-5 text-amber-400" /></template>
      <form @submit.prevent="submitCreateReturn" class="space-y-4 text-xs">
        <div>
          <label class="block font-bold text-slate-300 mb-1">Select Issued Indent *</label>
          <select
            v-model="returnForm.indent_id"
            @change="onReturnIndentSelected"
            required
            class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-emerald-500"
          >
            <option value="" disabled>Select Indent</option>
            <option
              v-for="ind in issuedIndents"
              :key="ind._id"
              :value="ind._id"
            >
              {{ ind.indent_number }} - Project {{ ind.project_id }} ({{ ind.requester_name }})
            </option>
          </select>
        </div>

        <div v-if="returnForm.items.length > 0" class="space-y-3">
          <p class="font-bold text-slate-200">Return Quantities & Material Condition</p>
          <div
            v-for="item in returnForm.items"
            :key="item.part_id"
            class="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-2"
          >
            <div class="flex items-center justify-between">
              <span class="font-bold text-white font-mono">{{ item.part_code }}</span>
              <span class="text-[11px] text-slate-400">
                Max Returnable: <strong class="text-amber-400">{{ item.max_returnable }}</strong> units
              </span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <div>
                <label class="block text-[10px] text-slate-400 uppercase font-bold mb-0.5">Return Quantity</label>
                <input
                  v-model.number="item.returned_quantity"
                  type="number"
                  step="any"
                  :max="item.max_returnable"
                  min="0"
                  class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white text-xs font-bold"
                />
              </div>

              <div>
                <label class="block text-[10px] text-slate-400 uppercase font-bold mb-0.5">Material Condition</label>
                <select
                  v-model="item.condition"
                  class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white text-xs font-bold"
                >
                  <option value="GOOD">GOOD (Reusable)</option>
                  <option value="DEFECTIVE">DEFECTIVE (Quarantine)</option>
                  <option value="SCRAP">SCRAP (Disposal)</option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="block font-bold text-slate-300 mb-1">Reason for Return</label>
          <input
            v-model="returnForm.reason"
            type="text"
            placeholder="e.g. Surplus unused materials after assembly"
            class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
          <button
            type="button"
            @click="showReturnModal = false"
            class="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl font-bold"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold shadow-lg"
          >
            Submit Return Request
          </button>
        </div>
      </form>
    </Modal>

    <!-- MODAL 5: INSPECT & ACCEPT RETURN -->
    <Modal v-model="showInspectReturnModal" :title="'Inspect & Accept Return ' + selectedReturn?.return_number" maxWidth="max-w-2xl">
      <template #icon><CheckCircle2 class="w-5 h-5 text-emerald-400" /></template>
      <form @submit.prevent="submitAcceptReturn" class="space-y-4 text-xs">
        <div class="p-3 bg-slate-950 rounded-xl border border-slate-800">
          <p class="text-white font-bold">Indent: <span class="text-emerald-400">{{ selectedReturn?.indent_number }}</span></p>
          <p class="text-slate-400">Requester: {{ selectedReturn?.requester_name }} &bull; Reason: {{ selectedReturn?.reason }}</p>
        </div>

        <div class="space-y-3">
          <div
            v-for="it in inspectForm.items"
            :key="it.part_id"
            class="p-3 bg-slate-950 rounded-xl border border-slate-800 space-y-2"
          >
            <div class="flex items-center justify-between">
              <span class="font-mono font-bold text-white">{{ it.part_code }}</span>
              <span class="text-[11px] text-slate-400">Claimed: {{ it.returned_quantity }} units</span>
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-2">
              <div>
                <label class="block text-[10px] text-slate-400 uppercase font-bold mb-0.5">Verified Qty *</label>
                <input
                  v-model.number="it.accepted_quantity"
                  type="number"
                  step="any"
                  min="0.001"
                  required
                  class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white text-xs font-bold"
                />
              </div>

              <div>
                <label class="block text-[10px] text-slate-400 uppercase font-bold mb-0.5">Inspection State</label>
                <select
                  v-model="it.condition"
                  class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white text-xs font-bold"
                >
                  <option value="GOOD">GOOD (Restock)</option>
                  <option value="DEFECTIVE">DEFECTIVE (Quarantine)</option>
                  <option value="SCRAP">SCRAP (Write-off)</option>
                </select>
              </div>

              <div v-if="it.condition === 'GOOD'">
                <label class="block text-[10px] text-slate-400 uppercase font-bold mb-0.5">Restock Bin *</label>
                <input
                  v-model="it.restock_location_code"
                  type="text"
                  required
                  placeholder="e.g. E11-1A"
                  class="w-full bg-slate-900 border border-slate-800 rounded-lg p-2 text-white text-xs font-mono"
                />
              </div>
            </div>
          </div>
        </div>

        <div>
          <label class="block font-bold text-slate-300 mb-1">Store Inspection Notes</label>
          <input
            v-model="inspectForm.inspection_notes"
            type="text"
            placeholder="e.g. Resistors inspected, count verified, intact in reels"
            class="w-full bg-slate-950 border border-slate-800 rounded-xl p-2.5 text-white focus:outline-none focus:border-emerald-500"
          />
        </div>

        <div class="flex items-center justify-end gap-2 pt-3 border-t border-slate-800">
          <button
            type="button"
            @click="showInspectReturnModal = false"
            class="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl font-bold"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="px-5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl font-bold shadow-lg"
          >
            Accept Return & Restock Inventory
          </button>
        </div>
      </form>
    </Modal>

    <!-- MODAL 6: INDENT DETAILS VIEW DRAWER -->
    <Modal v-model="showDetailsModal" :title="'Indent Details: ' + selectedIndent?.indent_number" maxWidth="max-w-3xl">
      <template #icon><Eye class="w-5 h-5 text-emerald-400" /></template>
      <div v-if="selectedIndent" class="space-y-4 text-xs">
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 p-3 bg-slate-950 rounded-xl border border-slate-800">
          <div>
            <span class="text-[10px] text-slate-400 uppercase font-bold">Project</span>
            <p class="font-bold text-white">{{ selectedIndent.project_id }}</p>
          </div>
          <div>
            <span class="text-[10px] text-slate-400 uppercase font-bold">Requester</span>
            <p class="font-medium text-slate-200">{{ selectedIndent.requester_name }}</p>
          </div>
          <div>
            <span class="text-[10px] text-slate-400 uppercase font-bold">Project Head</span>
            <p class="font-medium text-slate-200">{{ selectedIndent.project_head_name }}</p>
          </div>
          <div>
            <span class="text-[10px] text-slate-400 uppercase font-bold">Status</span>
            <p class="font-bold uppercase text-emerald-400">{{ selectedIndent.status }}</p>
          </div>
        </div>

        <!-- Items Table -->
        <div class="border border-slate-800 rounded-xl overflow-hidden">
          <table class="w-full text-left text-xs">
            <thead class="bg-slate-950 text-slate-400 uppercase font-bold">
              <tr>
                <th class="py-2.5 px-3">Part Code</th>
                <th class="py-2.5 px-3">Part Name</th>
                <th class="py-2.5 px-3 text-right">Requested</th>
                <th class="py-2.5 px-3 text-right">Issued</th>
                <th class="py-2.5 px-3 text-right">Returned</th>
                <th class="py-2.5 px-3">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800">
              <tr v-for="it in selectedIndent.items" :key="it.part_id">
                <td class="py-2.5 px-3 font-mono font-bold text-emerald-400">{{ it.part_code }}</td>
                <td class="py-2.5 px-3 text-white">{{ it.part_name }}</td>
                <td class="py-2.5 px-3 text-right font-mono font-bold text-white">{{ it.requested_quantity }}</td>
                <td class="py-2.5 px-3 text-right font-mono font-bold text-emerald-400">{{ it.issued_quantity || 0 }}</td>
                <td class="py-2.5 px-3 text-right font-mono font-bold text-amber-400">{{ it.returned_quantity || 0 }}</td>
                <td class="py-2.5 px-3">
                  <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-300">
                    {{ it.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Issue History -->
        <div v-if="selectedIndent.issue_history?.length" class="space-y-2">
          <h4 class="font-bold text-white text-xs uppercase tracking-wider">Store Dispatch History</h4>
          <div
            v-for="(hist, hIdx) in selectedIndent.issue_history"
            :key="hIdx"
            class="p-2.5 bg-slate-950 rounded-lg border border-slate-800/80 text-[11px]"
          >
            <div class="flex items-center justify-between text-slate-400">
              <span>Dispatched by <strong class="text-white">{{ hist.issued_by_name }}</strong></span>
              <span>{{ formatDate(hist.issued_at) }}</span>
            </div>
            <div v-if="hist.comments" class="text-slate-300 italic mt-0.5">{{ hist.comments }}</div>
          </div>
        </div>

        <div class="flex justify-end pt-3 border-t border-slate-800">
          <button
            @click="showDetailsModal = false"
            class="px-4 py-2 bg-slate-800 text-white rounded-xl font-bold"
          >
            Close
          </button>
        </div>
      </div>
    </Modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import {
  ClipboardList, Clock, PackageCheck, CheckCircle2, RotateCcw,
  Plus, Search, Eye, Send, Trash2, MapPin
} from 'lucide-vue-next'
import { useToastStore } from '@/stores/toast'
import indentsApi from '@/api/indents'
import indentReturnsApi from '@/api/indentReturns'
import authApi from '@/api/auth'
import itemsApi from '@/api/items'
import partsApi from '@/api/parts'
import lotsApi from '@/api/lots'
import inventoryApi from '@/api/inventory'
import projectsApi from '@/api/projects'
import apiClient from '@/api/client'
import Modal from '@/components/Modal.vue'

const toast = useToastStore()

// State
const indentsList = ref([])
const returnsList = ref([])
const partsList = ref([])
const projectsList = ref([])
const usersList = ref([])
const loadingIndents = ref(false)
const loadingReturns = ref(false)
const searchQuery = ref('')
const currentFilterTab = ref('ALL')

// Modals State
const showCreateModal = ref(false)
const showApprovalModal = ref(false)
const showIssueModal = ref(false)
const showReturnModal = ref(false)
const showInspectReturnModal = ref(false)
const showDetailsModal = ref(false)
const selectedIndent = ref(null)
const selectedReturn = ref(null)
const approvalComments = ref('')

// Forms
const newIndent = reactive({
  project_id: '',
  project_head_id: '',
  priority: 'MEDIUM',
  required_by_date: '',
  purpose: '',
  items: [{ part_id: '', requested_quantity: 1, notes: '' }]
})

const issueForm = reactive({
  comments: '',
  items: []
})

const returnForm = reactive({
  indent_id: '',
  reason: '',
  items: []
})

const inspectForm = reactive({
  inspection_notes: '',
  items: []
})

// Filter Tabs Config
const filterTabs = computed(() => [
  { id: 'ALL', label: 'All Indents', icon: ClipboardList, count: indentsList.value.length },
  { id: 'PENDING_APPROVAL', label: 'Pending Approval', icon: Clock, count: stats.value.pending },
  { id: 'APPROVED', label: 'Ready to Issue', icon: PackageCheck, count: stats.value.approved },
  { id: 'ISSUED', label: 'Issued & Active', icon: CheckCircle2, count: stats.value.issued },
  { id: 'RETURNS', label: 'Material Returns', icon: RotateCcw, count: stats.value.returnsPending },
  { id: 'CLOSED', label: 'Closed Archive', icon: ClipboardList }
])

// Stats Calculation
const stats = computed(() => {
  const total = indentsList.value.length
  const pending = indentsList.value.filter(i => i.status === 'PENDING_APPROVAL').length
  const approved = indentsList.value.filter(i => ['APPROVED', 'PARTIALLY_ISSUED'].includes(i.status)).length
  const issued = indentsList.value.filter(i => i.status === 'ISSUED').length
  const returnsPending = returnsList.value.filter(r => r.status === 'PENDING_INSPECTION').length
  return { total, pending, approved, issued, returnsPending }
})

// Filtered Indents
const filteredIndents = computed(() => {
  let list = indentsList.value

  if (currentFilterTab.value !== 'ALL') {
    if (currentFilterTab.value === 'APPROVED') {
      list = list.filter(i => ['APPROVED', 'PARTIALLY_ISSUED'].includes(i.status))
    } else {
      list = list.filter(i => i.status === currentFilterTab.value)
    }
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(i =>
      i.indent_number?.toLowerCase().includes(q) ||
      i.project_id?.toLowerCase().includes(q) ||
      i.project_name?.toLowerCase().includes(q) ||
      i.requester_name?.toLowerCase().includes(q) ||
      i.purpose?.toLowerCase().includes(q)
    )
  }

  return list
})

const issuedIndents = computed(() => {
  return indentsList.value.filter(i => ['ISSUED', 'PARTIALLY_ISSUED', 'APPROVED'].includes(i.status))
})

// Helpers
const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleDateString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric'
  })
}

const formatStatus = (s) => (s || '').replace(/_/g, ' ')

const getPriorityClass = (priority) => {
  switch (priority) {
    case 'URGENT': return 'bg-red-950 text-red-400 border-red-800'
    case 'HIGH': return 'bg-amber-950 text-amber-400 border-amber-800'
    case 'MEDIUM': return 'bg-blue-950 text-blue-400 border-blue-800'
    default: return 'bg-slate-800 text-slate-400 border-slate-700'
  }
}

const getStatusClass = (status) => {
  switch (status) {
    case 'APPROVED': return 'bg-emerald-950/80 text-emerald-400 border-emerald-800'
    case 'ISSUED': return 'bg-blue-950/80 text-blue-400 border-blue-800'
    case 'PARTIALLY_ISSUED': return 'bg-teal-950/80 text-teal-400 border-teal-800'
    case 'PENDING_APPROVAL': return 'bg-amber-950/80 text-amber-400 border-amber-800'
    case 'REJECTED': return 'bg-red-950/80 text-red-400 border-red-800'
    case 'CLOSED': return 'bg-slate-900 text-slate-400 border-slate-800'
    default: return 'bg-slate-800 text-slate-300 border-slate-700'
  }
}

const getStatusDot = (status) => {
  switch (status) {
    case 'APPROVED':
    case 'ISSUED': return 'bg-emerald-400'
    case 'PARTIALLY_ISSUED': return 'bg-teal-400'
    case 'PENDING_APPROVAL': return 'bg-amber-400 animate-ping'
    case 'REJECTED': return 'bg-red-400'
    default: return 'bg-slate-400'
  }
}

const getTotalRequested = (indent) => {
  return indent.items?.reduce((sum, it) => sum + (it.requested_quantity || 0), 0) || 0
}

const getTotalIssued = (indent) => {
  return indent.items?.reduce((sum, it) => sum + (it.issued_quantity || 0), 0) || 0
}

// API Loaders
const fetchIndents = async () => {
  loadingIndents.value = true
  try {
    const res = await indentsApi.getAll()
    indentsList.value = res.data?.items || []
  } catch (e) {
    console.error('Failed to load indents', e)
  } finally {
    loadingIndents.value = false
  }
}

const fetchReturns = async () => {
  loadingReturns.value = true
  try {
    const res = await indentReturnsApi.getAll()
    returnsList.value = res.data?.items || []
  } catch (e) {
    console.error('Failed to load returns', e)
  } finally {
    loadingReturns.value = false
  }
}

const fetchPrerequisites = async () => {
  try {
    const [partsRes, prjRes, usersRes] = await Promise.all([
      partsApi.getAll().catch(() => itemsApi.getAll().catch(() => ({ data: [] }))),
      projectsApi.getAll().catch(() => ({ data: [] })),
      authApi.getAllUsers().catch(() => apiClient.get('/users').catch(() => ({ data: [] })))
    ])
    partsList.value = partsRes.data || []
    projectsList.value = prjRes.data || []
    usersList.value = usersRes.data || []
  } catch (e) {
    console.error('Prerequisites error', e)
  }
}

// Create Indent Handlers
const openCreateIndentModal = () => {
  newIndent.project_id = projectsList.value[0]?.project_id || ''
  newIndent.project_head_id = usersList.value[0]?._id || ''
  newIndent.priority = 'MEDIUM'
  newIndent.required_by_date = ''
  newIndent.purpose = ''
  newIndent.items = [{ part_id: partsList.value[0]?._id || '', requested_quantity: 10, notes: '' }]
  showCreateModal.value = true
}

const addIndentItemRow = () => {
  newIndent.items.push({ part_id: partsList.value[0]?._id || '', requested_quantity: 1, notes: '' })
}

const removeIndentItemRow = (idx) => {
  newIndent.items.splice(idx, 1)
}

const submitCreateIndent = async () => {
  try {
    await indentsApi.create({ ...newIndent, status: 'PENDING_APPROVAL' })
    toast.success('Indent raised and sent for Project Head approval!')
    showCreateModal.value = false
    fetchIndents()
  } catch (e) {
    toast.error(e.message || 'Failed to create indent')
  }
}

const saveAsDraft = async () => {
  try {
    await indentsApi.create({ ...newIndent, status: 'DRAFT' })
    toast.success('Indent saved as Draft')
    showCreateModal.value = false
    fetchIndents()
  } catch (e) {
    toast.error(e.message || 'Failed to save draft')
  }
}

const submitDraftIndent = async (indent) => {
  try {
    await indentsApi.submit(indent._id)
    toast.success(`Indent ${indent.indent_number} submitted for approval`)
    fetchIndents()
  } catch (e) {
    toast.error(e.message || 'Submission failed')
  }
}

// Approval Handlers
const openApprovalModal = (indent) => {
  selectedIndent.value = indent
  approvalComments.value = 'Approved for project requisition'
  showApprovalModal.value = true
}

const approveIndentAction = async () => {
  try {
    await indentsApi.approve(selectedIndent.value._id, { comments: approvalComments.value })
    toast.success(`Indent ${selectedIndent.value.indent_number} approved! Ready for store dispatch.`)
    showApprovalModal.value = false
    fetchIndents()
  } catch (e) {
    toast.error(e.message || 'Approval failed')
  }
}

const rejectIndentAction = async () => {
  if (!approvalComments.value.trim()) {
    toast.error('Please specify a rejection reason')
    return
  }
  try {
    await indentsApi.reject(selectedIndent.value._id, { reason: approvalComments.value })
    toast.success(`Indent ${selectedIndent.value.indent_number} rejected`)
    showApprovalModal.value = false
    fetchIndents()
  } catch (e) {
    toast.error(e.message || 'Rejection failed')
  }
}

// Issue Handlers
const openIssueModal = async (indent) => {
  selectedIndent.value = indent
  issueForm.comments = `Material dispatch for indent ${indent.indent_number}`
  const items = (indent.items || []).map(it => ({
    part_id: it.part_id,
    part_code: it.part_code,
    part_name: it.part_name,
    max_issue: (it.requested_quantity || 0) - (it.issued_quantity || 0),
    issued_quantity: (it.requested_quantity || 0) - (it.issued_quantity || 0),
    location_code: '',
    lot_number: '',
    inventoryLocations: [],
    loadingLots: true
  })).filter(it => it.max_issue > 0)

  issueForm.items = items
  showIssueModal.value = true

  // Fetch all stored places & inventory for each part
  await Promise.all(items.map(async (item) => {
    try {
      let invList = []
      try {
        const invRes = await inventoryApi.getByPart(item.part_id)
        invList = invRes.data || invRes || []
      } catch (err) {
        invList = []
      }

      if (!Array.isArray(invList) || invList.length === 0) {
        try {
          const lotsRes = await lotsApi.getAll({ part_id: item.part_id })
          const lots = lotsRes.data || lotsRes || []
          invList = lots.map(l => ({
            location_code: l.location_code || (l.locations && l.locations[0]) || 'STORE-A1',
            lot_number: l.lot_batch_no || l.lot_number || l._id || 'STANDARD',
            lot_batch_no: l.lot_batch_no || l.lot_number || l._id || 'STANDARD',
            available_quantity: l.available_quantity ?? l.quantity ?? 0,
            quantity: l.quantity ?? 0
          }))
        } catch (lErr) {
          invList = []
        }
      }

      item.inventoryLocations = Array.isArray(invList) ? invList : []
      if (item.inventoryLocations.length > 0) {
        const first = item.inventoryLocations[0]
        item.location_code = first.location_code || 'STORE-A1'
        item.lot_number = first.lot_number || first.lot_batch_no || 'STANDARD'
      } else {
        item.location_code = 'STORE-A1'
        item.lot_number = 'STANDARD'
      }
    } catch (err) {
      console.error('Failed to load storage locations for part', item.part_id, err)
      item.location_code = 'STORE-A1'
      item.lot_number = 'STANDARD'
    } finally {
      item.loadingLots = false
    }
  }))
}

const selectLocationLot = (item, inv) => {
  item.location_code = inv.location_code || ''
  item.lot_number = inv.lot_number || inv.lot_batch_no || 'STANDARD'
}

const onIssueLotChanged = (item) => {
  const selected = (item.inventoryLocations || []).find(
    l => (l.lot_number === item.lot_number || l.lot_batch_no === item.lot_number)
  )
  if (selected && selected.location_code) {
    item.location_code = selected.location_code
  }
}

const submitIssueStock = async () => {
  try {
    const payload = {
      comments: issueForm.comments,
      items: issueForm.items.map(it => ({
        part_id: it.part_id,
        location_code: it.location_code || undefined,
        lot_number: it.lot_number || undefined,
        issued_quantity: it.issued_quantity
      }))
    }
    await indentsApi.issue(selectedIndent.value._id, payload)
    toast.success('Stock deducted and material issued successfully!')
    showIssueModal.value = false
    fetchIndents()
  } catch (e) {
    toast.error(e.message || 'Material issue failed')
  }
}

// Return Handlers
const openCreateReturnModal = () => {
  returnForm.indent_id = issuedIndents.value[0]?._id || ''
  returnForm.reason = 'Surplus unused parts'
  onReturnIndentSelected()
  showReturnModal.value = true
}

const openReturnForIndent = (indent) => {
  returnForm.indent_id = indent._id
  returnForm.reason = 'Surplus unused parts'
  onReturnIndentSelected()
  showReturnModal.value = true
}

const onReturnIndentSelected = () => {
  const indent = indentsList.value.find(i => i._id === returnForm.indent_id)
  if (!indent) {
    returnForm.items = []
    return
  }
  returnForm.items = (indent.items || []).map(it => {
    const returnable = (it.issued_quantity || 0) - (it.returned_quantity || 0)
    return {
      part_id: it.part_id,
      part_code: it.part_code,
      max_returnable: returnable,
      returned_quantity: returnable > 0 ? returnable : 0,
      condition: 'GOOD'
    }
  }).filter(it => it.max_returnable > 0)
}

const submitCreateReturn = async () => {
  try {
    const validItems = returnForm.items.filter(it => it.returned_quantity > 0)
    if (validItems.length === 0) {
      toast.error('Please enter a return quantity > 0')
      return
    }
    await indentReturnsApi.create({
      indent_id: returnForm.indent_id,
      reason: returnForm.reason,
      items: validItems
    })
    toast.success('Material return request submitted to Store Incharge!')
    showReturnModal.value = false
    fetchReturns()
    fetchIndents()
  } catch (e) {
    toast.error(e.message || 'Return creation failed')
  }
}

// Inspect & Accept Return
const openInspectReturnModal = (ret) => {
  selectedReturn.value = ret
  inspectForm.inspection_notes = 'Parts inspected and verified intact'
  inspectForm.items = (ret.items || []).map(it => ({
    part_id: it.part_id,
    part_code: it.part_code,
    returned_quantity: it.returned_quantity,
    accepted_quantity: it.returned_quantity,
    condition: it.condition || 'GOOD',
    restock_location_code: 'E11-1A'
  }))
  showInspectReturnModal.value = true
}

const submitAcceptReturn = async () => {
  try {
    const payload = {
      status: 'ACCEPTED',
      inspection_notes: inspectForm.inspection_notes,
      items: inspectForm.items.map(it => ({
        part_id: it.part_id,
        accepted_quantity: it.accepted_quantity,
        condition: it.condition,
        restock_location_code: it.condition === 'GOOD' ? it.restock_location_code : undefined
      }))
    }
    await indentReturnsApi.accept(selectedReturn.value._id, payload)
    toast.success('Return accepted and inventory restocked!')
    showInspectReturnModal.value = false
    fetchReturns()
    fetchIndents()
  } catch (e) {
    toast.error(e.message || 'Failed to accept return')
  }
}

const viewIndentDetails = async (indent) => {
  try {
    const res = await indentsApi.getById(indent._id)
    selectedIndent.value = res.data
    showDetailsModal.value = true
  } catch (e) {
    toast.error('Failed to load indent details')
  }
}

onMounted(() => {
  fetchIndents()
  fetchReturns()
  fetchPrerequisites()
})
</script>
