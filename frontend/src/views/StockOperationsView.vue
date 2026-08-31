<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl font-black text-white tracking-tight">Stock Operations Center</h1>
        <p class="text-xs text-slate-400 mt-0.5">Execute atomic material receipt, transfers, issues, and cell movements</p>
      </div>

      <!-- Quick Scan Triggers -->
      <div class="flex items-center gap-2">
        <button
          @click="openNfcScanner(null)"
          class="flex items-center gap-1.5 px-3.5 py-1.5 bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-700/60 text-emerald-300 text-xs font-bold rounded-lg transition"
        >
          <Radio class="w-4 h-4 animate-pulse text-emerald-400" />
          <span>Quick NFC Location Resolver</span>
        </button>
      </div>
    </div>

    <!-- Operations Tabs Bar -->
    <div class="bg-slate-900/90 border border-slate-800 rounded-2xl p-1.5 flex flex-wrap gap-1 shadow-lg">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        @click="activeTab = tab.id"
        class="flex-1 min-w-[120px] flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl text-xs font-bold transition-all"
        :class="activeTab === tab.id ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-950' : 'text-slate-400 hover:text-white hover:bg-slate-800/60'"
      >
        <component :is="tab.icon" class="w-4 h-4" />
        <span>{{ tab.label }}</span>
      </button>
    </div>

    <!-- TAB 1: RECEIVE MATERIAL & CELLS -->
    <div v-if="activeTab === 'receive'" class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div class="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <Download class="w-5 h-5 text-emerald-400" />
            Material & Battery Cell Receiving
          </h2>
          <p class="text-xs text-slate-400">Receive supplier batches or intake serial-tracked lithium battery cells</p>
        </div>

        <span class="text-xs font-mono text-emerald-400 bg-emerald-950 px-2.5 py-1 rounded border border-emerald-800/50">
          TYPE: {{ selectedPart?.tracking_type || 'SELECT PART' }}
        </span>
      </div>

      <form @submit.prevent="submitReceive" class="space-y-6">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- Select Part -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              1. Material / Part <span class="text-rose-400">*</span>
            </label>
            <select
              v-model="receiveForm.part_id"
              required
              @change="onPartSelected"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 font-mono"
            >
              <option value="" disabled>-- Select Part from Catalog --</option>
              <option v-for="part in partsList" :key="part._id" :value="part._id">
                [{{ part.part_code }}] {{ part.part_name }} ({{ part.tracking_type }})
              </option>
            </select>
          </div>

          <!-- Lot Selection / Creation -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              2. Lot / Batch Number <span class="text-rose-400">*</span>
            </label>
            <div class="flex gap-2">
              <input
                v-model="receiveForm.lot_batch_no"
                type="text"
                required
                placeholder="e.g. YG20260831 or CELLLOT-001"
                class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 font-mono"
              />
              <button
                type="button"
                @click="autoGenerateLot"
                class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 rounded-xl border border-slate-700"
                title="Auto Generate Lot Code"
              >
                Auto
              </button>
            </div>
          </div>

          <!-- Destination Location via NFC Scan -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              3. Destination Warehouse Location (NFC Tag) <span class="text-rose-400">*</span>
            </label>
            <div class="flex gap-2">
              <input
                v-model="receiveForm.location_code"
                type="text"
                required
                placeholder="e.g. E11-1A"
                class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 font-mono font-bold"
              />
              <button
                type="button"
                @click="openNfcScanner('receive_dest')"
                class="px-3.5 py-2 bg-emerald-950 hover:bg-emerald-900 border border-emerald-700 text-emerald-300 text-xs font-bold rounded-xl flex items-center gap-1.5"
              >
                <Radio class="w-4 h-4 animate-pulse text-emerald-400" />
                <span>Scan NFC</span>
              </button>
            </div>
            <p v-if="resolvedDestLocation" class="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
              <CheckCircle2 class="w-3.5 h-3.5" />
              Resolved: {{ resolvedDestLocation.warehouse_code }} | Bay {{ resolvedDestLocation.bay_number }} | Rack {{ resolvedDestLocation.rack_number }} | Sec {{ resolvedDestLocation.section_code }}
            </p>
          </div>

          <!-- Reference ID (PO / GRN) -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              4. PO / Invoice Reference
            </label>
            <input
              v-model="receiveForm.reference_id"
              type="text"
              placeholder="e.g. PO-2026-10045"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 font-mono"
            />
          </div>
        </div>

        <!-- SPECIAL SECTION: IF PART IS SERIAL TRACKED (BATTERY CELLS) -->
        <div v-if="selectedPart?.tracking_type === 'SERIAL'" class="p-5 rounded-2xl bg-slate-950/80 border border-emerald-500/30 space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="text-sm font-bold text-emerald-400 flex items-center gap-2">
              <BatteryCharging class="w-4 h-4" />
              Battery Cell Serial Number Ingestion
            </h3>
            <div class="flex gap-1 text-xs">
              <button
                type="button"
                @click="cellMode = 'range'"
                class="px-3 py-1 rounded-lg font-semibold"
                :class="cellMode === 'range' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400'"
              >
                Range Generator
              </button>
              <button
                type="button"
                @click="cellMode = 'csv'"
                class="px-3 py-1 rounded-lg font-semibold"
                :class="cellMode === 'csv' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400'"
              >
                CSV Upload / Paste
              </button>
            </div>
          </div>

          <!-- Mode 1: Range Generator -->
          <div v-if="cellMode === 'range'" class="grid grid-cols-1 sm:grid-cols-4 gap-3">
            <div>
              <label class="block text-[11px] font-semibold text-slate-400 mb-1">Prefix</label>
              <input
                v-model="receiveForm.serial_range_prefix"
                type="text"
                placeholder="CELL-2026-"
                class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-white"
              />
            </div>
            <div>
              <label class="block text-[11px] font-semibold text-slate-400 mb-1">Start #</label>
              <input
                v-model.number="receiveForm.serial_range_start"
                type="number"
                min="1"
                placeholder="1"
                class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-white"
              />
            </div>
            <div>
              <label class="block text-[11px] font-semibold text-slate-400 mb-1">End #</label>
              <input
                v-model.number="receiveForm.serial_range_end"
                type="number"
                min="1"
                placeholder="1000"
                class="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-xs font-mono text-white"
              />
            </div>
            <div>
              <label class="block text-[11px] font-semibold text-slate-400 mb-1">Calculated Total</label>
              <div class="px-3 py-2 bg-slate-900 rounded-lg border border-slate-700 text-emerald-400 font-mono font-bold text-xs">
                {{ calculatedCellCount }} CELLS
              </div>
            </div>
          </div>

          <!-- Mode 2: CSV / Paste -->
          <div v-if="cellMode === 'csv'" class="space-y-2">
            <textarea
              v-model="csvSerialInput"
              rows="4"
              placeholder="Paste comma or newline separated serials (e.g. CELL-2026-000001, CELL-2026-000002...)"
              class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-xs font-mono text-white focus:outline-none focus:border-emerald-500"
            ></textarea>
            <p class="text-[11px] text-slate-400">Parsed Serials: <span class="text-emerald-400 font-mono font-bold">{{ parsedCsvSerials.length }}</span></p>
          </div>
        </div>

        <!-- IF PART IS QUANTITY TRACKED -->
        <div v-else>
          <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
            Quantity to Receive (PCS) <span class="text-rose-400">*</span>
          </label>
          <input
            v-model.number="receiveForm.quantity"
            type="number"
            min="1"
            required
            placeholder="e.g. 10000"
            class="w-full sm:w-1/2 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 font-mono font-bold text-base"
          />
        </div>

        <!-- Submit Button -->
        <div class="pt-4 border-t border-slate-800 flex justify-end">
          <button
            type="submit"
            :disabled="submitting"
            class="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-sm rounded-xl shadow-lg shadow-emerald-950 flex items-center gap-2 transition disabled:opacity-50"
          >
            <CheckCircle2 class="w-5 h-5" />
            <span>Confirm & Execute Receive</span>
          </button>
        </div>
      </form>
    </div>

    <!-- TAB 2: ISSUE MATERIAL -->
    <div v-if="activeTab === 'issue'" class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div class="border-b border-slate-800 pb-4">
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          <Upload class="w-5 h-5 text-amber-400" />
          Material Issue for Production / Work Orders
        </h2>
        <p class="text-xs text-slate-400">Deduct material from verified warehouse location with negative-stock prevention</p>
      </div>

      <form @submit.prevent="submitIssue" class="space-y-5">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- Part -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              1. Part <span class="text-rose-400">*</span>
            </label>
            <select
              v-model="issueForm.part_id"
              required
              @change="loadLotsForIssue"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono"
            >
              <option value="" disabled>-- Select Part --</option>
              <option v-for="part in quantityPartsList" :key="part._id" :value="part._id">
                [{{ part.part_code }}] {{ part.part_name }}
              </option>
            </select>
          </div>

          <!-- Lot -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              2. Lot / Batch <span class="text-rose-400">*</span>
            </label>
            <select
              v-model="issueForm.lot_id"
              required
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono"
            >
              <option value="" disabled>-- Select Lot --</option>
              <option v-for="lot in partLots" :key="lot._id" :value="lot._id">
                Lot: {{ lot.lot_batch_no }} (Received: {{ lot.received_date || 'N/A' }})
              </option>
            </select>
          </div>

          <!-- Source NFC Location -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              3. Source Location (NFC Tag) <span class="text-rose-400">*</span>
            </label>
            <div class="flex gap-2">
              <input
                v-model="issueForm.location_code"
                type="text"
                required
                placeholder="e.g. E11-1A"
                class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono font-bold"
              />
              <button
                type="button"
                @click="openNfcScanner('issue_src')"
                class="px-3.5 py-2 bg-amber-950 hover:bg-amber-900 border border-amber-700 text-amber-300 text-xs font-bold rounded-xl flex items-center gap-1.5"
              >
                <Radio class="w-4 h-4 animate-pulse text-amber-400" />
                <span>Scan NFC</span>
              </button>
            </div>
          </div>

          <!-- Work Order / Reference -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              4. Work Order / Production Reference <span class="text-rose-400">*</span>
            </label>
            <input
              v-model="issueForm.reference_id"
              type="text"
              required
              placeholder="e.g. WO-2026-BATTPACK-01"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono"
            />
          </div>

          <!-- Quantity -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              5. Quantity to Issue <span class="text-rose-400">*</span>
            </label>
            <input
              v-model.number="issueForm.quantity"
              type="number"
              min="1"
              required
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono font-bold"
            />
          </div>
        </div>

        <div class="pt-4 border-t border-slate-800 flex justify-end">
          <button
            type="submit"
            :disabled="submitting"
            class="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-sm rounded-xl shadow-lg shadow-amber-950 flex items-center gap-2 transition"
          >
            <CheckCircle2 class="w-5 h-5" />
            <span>Confirm & Issue Stock</span>
          </button>
        </div>
      </form>
    </div>

    <!-- TAB 3: TRANSFER (QUANTITY & INDIVIDUAL CELL) -->
    <div v-if="activeTab === 'transfer'" class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div class="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <ArrowLeftRight class="w-5 h-5 text-blue-400" />
            Inter-Location Transfer
          </h2>
          <p class="text-xs text-slate-400">Transfer bulk components or individual battery cells between warehouse bins</p>
        </div>

        <div class="flex gap-1 text-xs">
          <button
            type="button"
            @click="transferMode = 'quantity'"
            class="px-3 py-1.5 rounded-lg font-bold transition"
            :class="transferMode === 'quantity' ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400'"
          >
            Bulk Parts Transfer
          </button>
          <button
            type="button"
            @click="transferMode = 'cell'"
            class="px-3 py-1.5 rounded-lg font-bold transition"
            :class="transferMode === 'cell' ? 'bg-emerald-600 text-white' : 'bg-slate-800 text-slate-400'"
          >
            Individual Cell Transfer
          </button>
        </div>
      </div>

      <!-- Mode A: Bulk Parts Transfer -->
      <form v-if="transferMode === 'quantity'" @submit.prevent="submitQuantityTransfer" class="space-y-5">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- Part -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              1. Part <span class="text-rose-400">*</span>
            </label>
            <select
              v-model="transferForm.part_id"
              required
              @change="loadLotsForTransfer"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono"
            >
              <option value="" disabled>-- Select Part --</option>
              <option v-for="part in quantityPartsList" :key="part._id" :value="part._id">
                [{{ part.part_code }}] {{ part.part_name }}
              </option>
            </select>
          </div>

          <!-- Lot -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              2. Lot <span class="text-rose-400">*</span>
            </label>
            <select
              v-model="transferForm.lot_id"
              required
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono"
            >
              <option value="" disabled>-- Select Lot --</option>
              <option v-for="lot in partLots" :key="lot._id" :value="lot._id">
                Lot: {{ lot.lot_batch_no }}
              </option>
            </select>
          </div>

          <!-- Source NFC -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              3. Source Location NFC <span class="text-rose-400">*</span>
            </label>
            <div class="flex gap-2">
              <input
                v-model="transferForm.from_location_code"
                type="text"
                required
                placeholder="e.g. E11-1A"
                class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono font-bold"
              />
              <button
                type="button"
                @click="openNfcScanner('trans_src')"
                class="px-3.5 py-2 bg-blue-950 hover:bg-blue-900 border border-blue-700 text-blue-300 text-xs font-bold rounded-xl flex items-center gap-1.5"
              >
                <Radio class="w-4 h-4 animate-pulse text-blue-400" />
                <span>Scan Source NFC</span>
              </button>
            </div>
          </div>

          <!-- Destination NFC -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              4. Destination Location NFC <span class="text-rose-400">*</span>
            </label>
            <div class="flex gap-2">
              <input
                v-model="transferForm.to_location_code"
                type="text"
                required
                placeholder="e.g. E11-2A"
                class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono font-bold"
              />
              <button
                type="button"
                @click="openNfcScanner('trans_dest')"
                class="px-3.5 py-2 bg-emerald-950 hover:bg-emerald-900 border border-emerald-700 text-emerald-300 text-xs font-bold rounded-xl flex items-center gap-1.5"
              >
                <Radio class="w-4 h-4 animate-pulse text-emerald-400" />
                <span>Scan Dest NFC</span>
              </button>
            </div>
          </div>

          <!-- Quantity -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              5. Quantity to Transfer <span class="text-rose-400">*</span>
            </label>
            <input
              v-model.number="transferForm.quantity"
              type="number"
              min="1"
              required
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono font-bold"
            />
          </div>
        </div>

        <div class="pt-4 border-t border-slate-800 flex justify-end">
          <button
            type="submit"
            :disabled="submitting"
            class="px-6 py-3 bg-blue-500 hover:bg-blue-400 text-slate-950 font-extrabold text-sm rounded-xl shadow-lg shadow-blue-950 flex items-center gap-2 transition"
          >
            <CheckCircle2 class="w-5 h-5" />
            <span>Confirm Transfer</span>
          </button>
        </div>
      </form>

      <!-- Mode B: Individual Battery Cell Transfer -->
      <form v-else @submit.prevent="submitCellTransfer" class="space-y-5">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- Cell Serial Number with Barcode Scanner -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              1. Cell Serial Number <span class="text-rose-400">*</span>
            </label>
            <div class="flex gap-2">
              <input
                v-model="cellTransferForm.cell_serial_no"
                type="text"
                required
                placeholder="e.g. CELL-2026-000001"
                class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono font-bold"
              />
              <button
                type="button"
                @click="openBarcodeScanner"
                class="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-bold rounded-xl flex items-center gap-1.5"
              >
                <QrCode class="w-4 h-4 text-emerald-400" />
                <span>Scan Serial</span>
              </button>
            </div>
          </div>

          <!-- Destination Location NFC -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              2. Destination Location NFC <span class="text-rose-400">*</span>
            </label>
            <div class="flex gap-2">
              <input
                v-model="cellTransferForm.to_location_code"
                type="text"
                required
                placeholder="e.g. E11-2B"
                class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono font-bold"
              />
              <button
                type="button"
                @click="openNfcScanner('cell_trans_dest')"
                class="px-3.5 py-2 bg-emerald-950 hover:bg-emerald-900 border border-emerald-700 text-emerald-300 text-xs font-bold rounded-xl flex items-center gap-1.5"
              >
                <Radio class="w-4 h-4 animate-pulse text-emerald-400" />
                <span>Scan Dest NFC</span>
              </button>
            </div>
          </div>
        </div>

        <div class="pt-4 border-t border-slate-800 flex justify-end">
          <button
            type="submit"
            :disabled="submitting"
            class="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-sm rounded-xl shadow-lg shadow-emerald-950 flex items-center gap-2 transition"
          >
            <CheckCircle2 class="w-5 h-5" />
            <span>Confirm Cell Transfer</span>
          </button>
        </div>
      </form>
    </div>

    <!-- TAB 4: RESERVE STOCK -->
    <div v-if="activeTab === 'reserve'" class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div class="border-b border-slate-800 pb-4">
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          <Lock class="w-5 h-5 text-purple-400" />
          Stock Reservation (Work Order Allocation)
        </h2>
        <p class="text-xs text-slate-400">Lock available quantities to prevent double allocation during production planning</p>
      </div>

      <form @submit.prevent="submitReserve" class="space-y-5">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              Select Inventory Item <span class="text-rose-400">*</span>
            </label>
            <select
              v-model="reserveForm.inventory_id"
              required
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono"
            >
              <option value="" disabled>-- Select Stock Item --</option>
              <option v-for="inv in inventoryList" :key="inv._id" :value="inv._id">
                [{{ inv.part_code }}] Loc: {{ inv.location_code }} | Avail: {{ inv.available_quantity }} PCS
              </option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              Work Order Reference <span class="text-rose-400">*</span>
            </label>
            <input
              v-model="reserveForm.reserved_for"
              type="text"
              required
              placeholder="e.g. WO-2026-PACK-88"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono"
            />
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              Quantity to Reserve <span class="text-rose-400">*</span>
            </label>
            <input
              v-model.number="reserveForm.quantity"
              type="number"
              min="1"
              required
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono font-bold"
            />
          </div>
        </div>

        <div class="pt-4 border-t border-slate-800 flex justify-end">
          <button
            type="submit"
            :disabled="submitting"
            class="px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white font-extrabold text-sm rounded-xl shadow-lg shadow-purple-950 flex items-center gap-2 transition"
          >
            <Lock class="w-5 h-5" />
            <span>Confirm Stock Reservation</span>
          </button>
        </div>
      </form>
    </div>

    <!-- TAB 5: RELEASE RESERVED STOCK -->
    <div v-if="activeTab === 'release'" class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div class="border-b border-slate-800 pb-4">
        <h2 class="text-base font-bold text-white flex items-center gap-2">
          <Unlock class="w-5 h-5 text-emerald-400" />
          Release Reserved Stock
        </h2>
        <p class="text-xs text-slate-400">Unlock previously reserved stock back to general available inventory</p>
      </div>

      <form @submit.prevent="submitRelease" class="space-y-5">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              Select Reserved Item <span class="text-rose-400">*</span>
            </label>
            <select
              v-model="releaseForm.inventory_id"
              required
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono"
            >
              <option value="" disabled>-- Select Item with Reserved Stock --</option>
              <option v-for="inv in reservedInventoryList" :key="inv._id" :value="inv._id">
                [{{ inv.part_code }}] Loc: {{ inv.location_code }} | Reserved: {{ inv.reserved_quantity }} ({{ inv.reserved_for || 'N/A' }})
              </option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              Quantity to Release <span class="text-rose-400">*</span>
            </label>
            <input
              v-model.number="releaseForm.quantity"
              type="number"
              min="1"
              required
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono font-bold"
            />
          </div>
        </div>

        <div class="pt-4 border-t border-slate-800 flex justify-end">
          <button
            type="submit"
            :disabled="submitting"
            class="px-6 py-3 bg-emerald-600 hover:bg-emerald-500 text-white font-extrabold text-sm rounded-xl shadow-lg shadow-emerald-950 flex items-center gap-2 transition"
          >
            <Unlock class="w-5 h-5" />
            <span>Confirm Stock Release</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Modals -->
    <NfcReaderModal v-model="showNfcModal" @locationResolved="handleLocationResolved" />
    <BarcodeScannerModal v-model="showBarcodeModal" @scan="handleBarcodeScanned" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import partsApi from '@/api/parts'
import lotsApi from '@/api/lots'
import inventoryApi from '@/api/inventory'
import stockApi from '@/api/stock'
import cellsApi from '@/api/cells'
import { useToastStore } from '@/stores/toast'
import NfcReaderModal from '@/components/NfcReaderModal.vue'
import BarcodeScannerModal from '@/components/BarcodeScannerModal.vue'
import {
  Download, Upload, ArrowLeftRight, Lock, Unlock, Radio,
  QrCode, CheckCircle2, BatteryCharging
} from 'lucide-vue-next'

const toast = useToastStore()
const activeTab = ref('receive')
const submitting = ref(false)

const tabs = [
  { id: 'receive', label: 'Receive Material', icon: Download },
  { id: 'issue', label: 'Issue Stock', icon: Upload },
  { id: 'transfer', label: 'Transfer', icon: ArrowLeftRight },
  { id: 'reserve', label: 'Reserve', icon: Lock },
  { id: 'release', label: 'Release', icon: Unlock },
]

const partsList = ref([])
const partLots = ref([])
const inventoryList = ref([])
const cellMode = ref('range')
const transferMode = ref('quantity')
const csvSerialInput = ref('')

// Forms
const receiveForm = ref({
  part_id: '',
  lot_batch_no: '',
  location_code: '',
  quantity: 1000,
  reference_id: '',
  serial_range_prefix: 'CELL-2026-',
  serial_range_start: 1,
  serial_range_end: 100
})

const issueForm = ref({
  part_id: '',
  lot_id: '',
  location_code: '',
  quantity: 100,
  reference_id: ''
})

const transferForm = ref({
  part_id: '',
  lot_id: '',
  from_location_code: '',
  to_location_code: '',
  quantity: 100
})

const cellTransferForm = ref({
  cell_serial_no: '',
  to_location_code: ''
})

const reserveForm = ref({
  inventory_id: '',
  reserved_for: '',
  quantity: 100
})

const releaseForm = ref({
  inventory_id: '',
  quantity: 100
})

// Modals
const showNfcModal = ref(false)
const showBarcodeModal = ref(false)
const nfcTargetField = ref(null)
const resolvedDestLocation = ref(null)

const selectedPart = computed(() => {
  return partsList.value.find(p => p._id === receiveForm.value.part_id)
})

const quantityPartsList = computed(() => {
  return partsList.value.filter(p => p.tracking_type === 'QUANTITY')
})

const calculatedCellCount = computed(() => {
  const start = receiveForm.value.serial_range_start || 0
  const end = receiveForm.value.serial_range_end || 0
  return end >= start ? (end - start + 1) : 0
})

const parsedCsvSerials = computed(() => {
  if (!csvSerialInput.value) return []
  return csvSerialInput.value
    .split(/[\n,]+/)
    .map(s => s.trim())
    .filter(s => s.length > 0)
})

const reservedInventoryList = computed(() => {
  return inventoryList.value.filter(i => (i.reserved_quantity || 0) > 0)
})

const loadData = async () => {
  const [pRes, invRes] = await Promise.all([
    partsApi.getAll(),
    inventoryApi.getAll({ limit: 200 })
  ])
  partsList.value = pRes.data || []
  inventoryList.value = invRes.data?.items || []
}

const onPartSelected = () => {
  autoGenerateLot()
}

const autoGenerateLot = () => {
  const now = new Date()
  const dateStr = now.toISOString().slice(0, 10).replace(/-/g, '')
  if (selectedPart.value?.tracking_type === 'SERIAL') {
    receiveForm.value.lot_batch_no = `CELLLOT-${dateStr}`
  } else {
    receiveForm.value.lot_batch_no = `LOT-${dateStr}`
  }
}

const loadLotsForIssue = async () => {
  if (issueForm.value.part_id) {
    const res = await lotsApi.getAll({ part_id: issueForm.value.part_id })
    partLots.value = res.data || []
  }
}

const loadLotsForTransfer = async () => {
  if (transferForm.value.part_id) {
    const res = await lotsApi.getAll({ part_id: transferForm.value.part_id })
    partLots.value = res.data || []
  }
}

const openNfcScanner = (target) => {
  nfcTargetField.value = target
  showNfcModal.value = true
}

const openBarcodeScanner = () => {
  showBarcodeModal.value = true
}

const handleLocationResolved = (loc) => {
  if (nfcTargetField.value === 'receive_dest') {
    receiveForm.value.location_code = loc.location_code
    resolvedDestLocation.value = loc
  } else if (nfcTargetField.value === 'issue_src') {
    issueForm.value.location_code = loc.location_code
  } else if (nfcTargetField.value === 'trans_src') {
    transferForm.value.from_location_code = loc.location_code
  } else if (nfcTargetField.value === 'trans_dest') {
    transferForm.value.to_location_code = loc.location_code
  } else if (nfcTargetField.value === 'cell_trans_dest') {
    cellTransferForm.value.to_location_code = loc.location_code
  } else {
    toast.success(`Scanned: ${loc.location_code}`)
  }
}

const handleBarcodeScanned = (code) => {
  cellTransferForm.value.cell_serial_no = code
}

// Submissions
const submitReceive = async () => {
  submitting.value = true
  try {
    const payload = {
      part_id: receiveForm.value.part_id,
      lot_batch_no: receiveForm.value.lot_batch_no,
      location_code: receiveForm.value.location_code,
      reference_id: receiveForm.value.reference_id
    }

    if (selectedPart.value?.tracking_type === 'SERIAL') {
      if (cellMode.value === 'range') {
        payload.serial_range_prefix = receiveForm.value.serial_range_prefix
        payload.serial_range_start = receiveForm.value.serial_range_start
        payload.serial_range_end = receiveForm.value.serial_range_end
        payload.quantity = calculatedCellCount.value
      } else {
        payload.cell_serials = parsedCsvSerials.value
        payload.quantity = parsedCsvSerials.value.length
      }
    } else {
      payload.quantity = receiveForm.value.quantity
    }

    const res = await stockApi.receive(payload)
    toast.success(res.message || 'Receive successful')
    await loadData()
  } finally {
    submitting.value = false
  }
}

const submitIssue = async () => {
  submitting.value = true
  try {
    const res = await stockApi.issue(issueForm.value)
    toast.success(res.message || 'Issue successful')
    await loadData()
  } finally {
    submitting.value = false
  }
}

const submitQuantityTransfer = async () => {
  submitting.value = true
  try {
    const res = await stockApi.transfer(transferForm.value)
    toast.success(res.message || 'Transfer successful')
    await loadData()
  } finally {
    submitting.value = false
  }
}

const submitCellTransfer = async () => {
  submitting.value = true
  try {
    const res = await cellsApi.transfer(cellTransferForm.value)
    toast.success(res.message || 'Cell transfer successful')
    cellTransferForm.value.cell_serial_no = ''
    await loadData()
  } finally {
    submitting.value = false
  }
}

const submitReserve = async () => {
  submitting.value = true
  try {
    const res = await stockApi.reserve(reserveForm.value)
    toast.success(res.message || 'Stock reserved successfully')
    await loadData()
  } finally {
    submitting.value = false
  }
}

const submitRelease = async () => {
  submitting.value = true
  try {
    const res = await stockApi.release(releaseForm.value)
    toast.success(res.message || 'Stock released successfully')
    await loadData()
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>
