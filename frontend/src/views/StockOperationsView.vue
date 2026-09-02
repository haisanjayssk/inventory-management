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
      <div class="border-b border-slate-800 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <Download class="w-5 h-5 text-emerald-400" />
            Material & Battery Cell Receiving
          </h2>
          <p class="text-xs text-slate-400">Receive supplier batches or intake serial-tracked lithium battery cells</p>
        </div>

        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="openNfcScanner('receive_dest')"
            class="px-3 py-1.5 bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-700/60 text-emerald-300 text-xs font-bold rounded-lg flex items-center gap-1.5 transition"
          >
            <Radio class="w-3.5 h-3.5 animate-pulse text-emerald-400" />
            <span>Scan NFC</span>
          </button>
          <button
            type="button"
            @click="openBarcodeScanner('receive_dest')"
            class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-bold rounded-lg flex items-center gap-1.5 transition"
          >
            <QrCode class="w-3.5 h-3.5 text-slate-400" />
            <span>Scan QR</span>
          </button>
          <span class="text-xs font-mono text-emerald-400 bg-emerald-950 px-2.5 py-1.5 rounded-lg border border-emerald-800/50">
            TYPE: {{ selectedPart?.tracking_type || 'SELECT PART' }}
          </span>
        </div>
      </div>

      <!-- Live Location Inventory Info Box & Quick Restock Selector -->
      <div v-if="receiveForm.location_code" class="p-4 rounded-xl bg-slate-950/90 border transition-all"
        :class="receiveBinInventoryList.length > 0 ? 'border-emerald-500/40 bg-gradient-to-r from-emerald-950/20 to-slate-950' : 'border-slate-800'">
        
        <div class="flex items-center justify-between mb-2.5">
          <div class="flex items-center gap-2">
            <div class="w-2.5 h-2.5 rounded-full" :class="receiveBinInventoryList.length > 0 ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'"></div>
            <span class="text-xs font-mono font-extrabold text-white uppercase tracking-wider">
              Bin Location: <span class="text-emerald-400 font-bold font-mono">{{ receiveForm.location_code }}</span>
            </span>
            <span v-if="loadingReceiveStock" class="text-[11px] text-slate-400 animate-pulse">Loading bin contents...</span>
          </div>

          <span v-if="receiveBinInventoryList.length > 0" class="text-[11px] font-semibold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/60">
            {{ receiveBinInventoryList.length }} Part{{ receiveBinInventoryList.length > 1 ? 's' : '' }} Stored Here
          </span>
          <span v-else-if="!loadingReceiveStock" class="text-[11px] font-semibold text-slate-300 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
            Empty Bin &bull; Ready for Storage
          </span>
        </div>

        <!-- Quick 1-Click Part Selection Cards -->
        <div v-if="receiveBinInventoryList.length > 0" class="space-y-1.5">
          <p class="text-[11px] text-slate-400 font-semibold">Click a part below to restock / receive into this bin:</p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <button
              v-for="item in receiveBinInventoryList"
              :key="item._id"
              type="button"
              @click="selectReceiveBinItem(item)"
              class="text-left p-2.5 rounded-lg border transition-all flex items-center justify-between"
              :class="receiveForm.part_id === item.part_id
                ? 'bg-emerald-950/80 border-emerald-500 ring-1 ring-emerald-500/50 shadow-md text-white'
                : 'bg-slate-900/80 border-slate-800 hover:border-slate-700 text-slate-300'"
            >
              <div class="min-w-0 pr-2">
                <div class="text-xs font-bold font-mono flex items-center gap-1.5 truncate">
                  <span class="text-emerald-400 font-mono">[{{ item.part_code || item.part_id }}]</span>
                  <span class="truncate">{{ item.part_name || 'Part' }}</span>
                </div>
                <div class="text-[10px] text-slate-400 font-mono mt-0.5">
                  Current In-Stock: <span class="text-slate-200 font-bold font-mono">{{ item.quantity?.toLocaleString() }} {{ item.unit_of_measure || 'PCS' }}</span>
                </div>
              </div>
              <div class="text-right flex-shrink-0">
                <span class="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded text-[10px] font-bold">
                  Restock
                </span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <form @submit.prevent="submitReceive" class="space-y-5">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- 1. Destination Location via NFC / QR Scan -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              1. Destination Location (NFC / QR Bin) <span class="text-rose-400">*</span>
            </label>
            <div class="flex gap-2">
              <input
                v-model="receiveForm.location_code"
                type="text"
                required
                @change="handleReceiveLocationAutoFill(receiveForm.location_code)"
                @blur="handleReceiveLocationAutoFill(receiveForm.location_code)"
                placeholder="e.g. E11-1A"
                class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-emerald-500 font-mono font-bold"
              />
              <button
                type="button"
                @click="openNfcScanner('receive_dest')"
                class="px-3 py-2 bg-emerald-950 hover:bg-emerald-900 border border-emerald-700 text-emerald-300 text-xs font-bold rounded-xl flex items-center gap-1 transition"
                title="Scan NFC Tag"
              >
                <Radio class="w-3.5 h-3.5 animate-pulse text-emerald-400" />
                <span>NFC</span>
              </button>
              <button
                type="button"
                @click="openBarcodeScanner('receive_dest')"
                class="px-3 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-bold rounded-xl flex items-center gap-1 transition"
                title="Scan QR / Barcode"
              >
                <QrCode class="w-3.5 h-3.5 text-slate-400" />
                <span>QR</span>
              </button>
            </div>
            <p v-if="resolvedDestLocation" class="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
              <CheckCircle2 class="w-3.5 h-3.5" />
              Resolved: {{ resolvedDestLocation.warehouse_code }} | Bay {{ resolvedDestLocation.bay_number }} | Rack {{ resolvedDestLocation.rack_number }} | Sec {{ resolvedDestLocation.section_code }}
            </p>
          </div>

          <!-- 2. Part to Receive -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              2. Material / Part to Receive <span class="text-rose-400">*</span>
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

          <!-- 3. Lot / Batch Number -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              3. Lot / Batch Number <span class="text-rose-400">*</span>
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
                class="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 rounded-xl border border-slate-700 transition"
                title="Auto Generate Lot Code"
              >
                Auto
              </button>
            </div>
          </div>

          <!-- 4. Reference / PO -->
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

          <!-- 5. Quantity to Receive (if Bulk) -->
          <div v-if="selectedPart?.tracking_type !== 'SERIAL'" class="md:col-span-2">
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider">
                5. Quantity to Receive (PCS) <span class="text-rose-400">*</span>
              </label>
              <span v-if="selectedReceiveBinItem" class="text-xs font-mono font-semibold text-emerald-400">
                Current in Bin: <span class="font-bold underline">{{ selectedReceiveBinItem.quantity?.toLocaleString() }}</span> {{ selectedReceiveBinItem.unit_of_measure || 'PCS' }}
              </span>
            </div>
            <input
              ref="receiveQtyInputRef"
              v-model.number="receiveForm.quantity"
              type="number"
              min="1"
              required
              placeholder="Enter quantity to receive..."
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-base text-white focus:outline-none focus:border-emerald-500 font-mono font-bold"
            />
            <p class="text-[11px] text-slate-400 mt-1">
              Press <kbd class="px-1.5 py-0.5 text-[10px] bg-slate-800 text-emerald-400 rounded border border-slate-700 font-mono">Enter ↵</kbd> to confirm receive.
            </p>
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

        <!-- Submit Button -->
        <div class="pt-4 border-t border-slate-800 flex items-center justify-between">
          <span class="text-xs text-slate-400 hidden sm:inline">
            Atomic receipt with automatic inventory recording and audit logging.
          </span>
          <button
            type="submit"
            :disabled="submitting || !receiveForm.part_id || !receiveForm.lot_batch_no || !receiveForm.location_code || (!receiveForm.quantity && selectedPart?.tracking_type !== 'SERIAL')"
            class="px-6 py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-extrabold text-sm rounded-xl shadow-lg shadow-emerald-950 flex items-center gap-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <CheckCircle2 class="w-5 h-5" />
            <span>{{ submitting ? 'Processing Receive...' : 'Confirm & Execute Receive' }}</span>
          </button>
        </div>
      </form>
    </div>

    <!-- TAB 2: ISSUE MATERIAL -->
    <div v-if="activeTab === 'issue'" class="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div class="border-b border-slate-800 pb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h2 class="text-base font-bold text-white flex items-center gap-2">
            <Upload class="w-5 h-5 text-amber-400" />
            Material Issue for Production / Work Orders
          </h2>
          <p class="text-xs text-slate-400">Deduct material from verified warehouse location with negative-stock prevention</p>
        </div>

        <div class="flex items-center gap-2">
          <button
            type="button"
            @click="openNfcScanner('issue_src')"
            class="px-3 py-1.5 bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-700/60 text-emerald-300 text-xs font-bold rounded-lg flex items-center gap-1.5 transition"
          >
            <Radio class="w-3.5 h-3.5 animate-pulse text-emerald-400" />
            <span>Scan NFC</span>
          </button>
          <button
            type="button"
            @click="openBarcodeScanner('issue_src')"
            class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-bold rounded-lg flex items-center gap-1.5 transition"
          >
            <QrCode class="w-3.5 h-3.5 text-slate-400" />
            <span>Scan QR</span>
          </button>
        </div>
      </div>

      <!-- Live Location Inventory Info Box & Quick Part Selector -->
      <div v-if="issueForm.location_code" class="p-4 rounded-xl bg-slate-950/90 border transition-all"
        :class="binInventoryList.length > 0 ? 'border-amber-500/40 bg-gradient-to-r from-amber-950/20 to-slate-950' : 'border-slate-800'">
        
        <div class="flex items-center justify-between mb-2.5">
          <div class="flex items-center gap-2">
            <div class="w-2.5 h-2.5 rounded-full" :class="binInventoryList.length > 0 ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'"></div>
            <span class="text-xs font-mono font-extrabold text-white uppercase tracking-wider">
              Bin Location: <span class="text-amber-400 font-bold font-mono">{{ issueForm.location_code }}</span>
            </span>
            <span v-if="loadingLocationStock" class="text-[11px] text-slate-400 animate-pulse">Loading bin contents...</span>
          </div>

          <span v-if="binInventoryList.length > 0" class="text-[11px] font-semibold text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded border border-emerald-800/60">
            {{ binInventoryList.length }} Part{{ binInventoryList.length > 1 ? 's' : '' }} Stored Here
          </span>
          <span v-else-if="!loadingLocationStock" class="text-[11px] font-semibold text-rose-400 bg-rose-950/60 px-2 py-0.5 rounded border border-rose-800/40">
            No Bulk Parts Stored in this Bin
          </span>
        </div>

        <!-- Quick 1-Click Part Selection Cards -->
        <div v-if="binInventoryList.length > 0" class="space-y-1.5">
          <p class="text-[11px] text-slate-400 font-semibold">Click a part below to issue from this bin:</p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            <button
              v-for="item in binInventoryList"
              :key="item._id"
              type="button"
              @click="selectBinItem(item)"
              class="text-left p-2.5 rounded-lg border transition-all flex items-center justify-between"
              :class="issueForm.part_id === item.part_id && issueForm.lot_id === item.lot_id
                ? 'bg-amber-950/80 border-amber-500 ring-1 ring-amber-500/50 shadow-md text-white'
                : 'bg-slate-900/80 border-slate-800 hover:border-slate-700 text-slate-300'"
            >
              <div class="min-w-0 pr-2">
                <div class="text-xs font-bold font-mono flex items-center gap-1.5 truncate">
                  <span class="text-amber-400 font-mono">[{{ item.part_code || item.part_id }}]</span>
                  <span class="truncate">{{ item.part_name || 'Part' }}</span>
                </div>
                <div class="text-[10px] text-slate-400 font-mono mt-0.5">
                  Lot: <span class="text-slate-300 font-medium">{{ item.lot_batch_no || item.lot_id }}</span>
                </div>
              </div>
              <div class="text-right flex-shrink-0">
                <span class="text-xs font-bold font-mono text-emerald-400">
                  {{ item.available_quantity?.toLocaleString() }}
                </span>
                <span class="text-[10px] text-slate-400 ml-1">{{ item.unit_of_measure || 'PCS' }}</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <form @submit.prevent="submitIssue" class="space-y-5">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
          <!-- Source NFC / QR Location -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              1. Source Location (NFC / QR Bin) <span class="text-rose-400">*</span>
            </label>
            <div class="flex gap-2">
              <input
                v-model="issueForm.location_code"
                type="text"
                required
                @change="loadLocationInventory(issueForm.location_code)"
                @blur="loadLocationInventory(issueForm.location_code)"
                placeholder="e.g. E11-1A"
                class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono font-bold focus:outline-none focus:border-amber-500"
              />
              <button
                type="button"
                @click="openNfcScanner('issue_src')"
                class="px-3.5 py-2 bg-emerald-950 hover:bg-emerald-900 border border-emerald-700 text-emerald-300 text-xs font-bold rounded-xl flex items-center gap-1.5 transition"
                title="Scan NFC Tag"
              >
                <Radio class="w-4 h-4 animate-pulse text-emerald-400" />
                <span>NFC</span>
              </button>
              <button
                type="button"
                @click="openBarcodeScanner('issue_src')"
                class="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 text-xs font-bold rounded-xl flex items-center gap-1.5 transition"
                title="Scan QR / Barcode"
              >
                <QrCode class="w-4 h-4 text-slate-400" />
                <span>QR</span>
              </button>
            </div>
          </div>

          <!-- Part -->
          <div>
            <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider mb-1.5">
              2. Part to Issue <span class="text-rose-400">*</span>
            </label>
            <select
              v-model="issueForm.part_id"
              required
              @change="loadLotsForIssue"
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono focus:outline-none focus:border-amber-500"
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
              3. Lot / Batch <span class="text-rose-400">*</span>
            </label>
            <select
              v-model="issueForm.lot_id"
              required
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono focus:outline-none focus:border-amber-500"
            >
              <option value="" disabled>-- Select Lot --</option>
              <option v-for="lot in partLots" :key="lot._id" :value="lot._id">
                Lot: {{ lot.lot_batch_no }} (Received: {{ lot.received_date || 'N/A' }})
              </option>
            </select>
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
              class="w-full bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-sm text-white font-mono focus:outline-none focus:border-amber-500"
            />
          </div>

          <!-- Quantity to Issue -->
          <div class="md:col-span-2">
            <div class="flex items-center justify-between mb-1.5">
              <label class="block text-xs font-bold text-slate-300 uppercase tracking-wider">
                5. Quantity to Issue <span class="text-rose-400">*</span>
              </label>
              <span v-if="selectedBinItem" class="text-xs font-mono font-semibold text-emerald-400">
                Available Stock: <span class="font-bold underline">{{ selectedBinItem.available_quantity?.toLocaleString() }}</span> {{ selectedBinItem.unit_of_measure || 'PCS' }}
              </span>
            </div>
            <div class="flex gap-3">
              <input
                ref="quantityInputRef"
                v-model.number="issueForm.quantity"
                type="number"
                min="1"
                :max="selectedBinItem?.available_quantity || undefined"
                required
                placeholder="Enter quantity..."
                class="flex-1 bg-slate-950 border border-slate-700 rounded-xl px-3.5 py-2.5 text-base text-white font-mono font-bold focus:outline-none focus:border-amber-500"
              />
              <button
                v-if="selectedBinItem"
                type="button"
                @click="issueForm.quantity = selectedBinItem.available_quantity"
                class="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-300 rounded-xl border border-slate-700 transition"
                title="Fill Maximum Available"
              >
                Max ({{ selectedBinItem.available_quantity }})
              </button>
            </div>
            <p class="text-[11px] text-slate-400 mt-1">
              Press <kbd class="px-1.5 py-0.5 text-[10px] bg-slate-800 text-amber-400 rounded border border-slate-700 font-mono">Enter ↵</kbd> to issue immediately.
            </p>
          </div>
        </div>

        <div class="pt-4 border-t border-slate-800 flex items-center justify-between">
          <span class="text-xs text-slate-400 hidden sm:inline">
            Atomic deduction with negative-stock prevention.
          </span>
          <button
            type="submit"
            :disabled="submitting || !issueForm.part_id || !issueForm.lot_id || !issueForm.location_code || !issueForm.quantity"
            class="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-sm rounded-xl shadow-lg shadow-amber-950 flex items-center gap-2 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <CheckCircle2 class="w-5 h-5" />
            <span>{{ submitting ? 'Processing Issue...' : 'Confirm & Issue Stock' }}</span>
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import partsApi from '@/api/parts'
import lotsApi from '@/api/lots'
import inventoryApi from '@/api/inventory'
import locationsApi from '@/api/locations'
import stockApi from '@/api/stock'
import cellsApi from '@/api/cells'
import { useToastStore } from '@/stores/toast'
import NfcReaderModal from '@/components/NfcReaderModal.vue'
import BarcodeScannerModal from '@/components/BarcodeScannerModal.vue'
import {
  Download, Upload, ArrowLeftRight, Lock, Unlock, Radio,
  QrCode, CheckCircle2, BatteryCharging
} from 'lucide-vue-next'

const route = useRoute()
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

// Location Inventory & Fast Picker state
const receiveQtyInputRef = ref(null)
const quantityInputRef = ref(null)
const binInventoryList = ref([])
const selectedBinItem = ref(null)
const loadingLocationStock = ref(false)

const receiveBinInventoryList = ref([])
const selectedReceiveBinItem = ref(null)
const loadingReceiveStock = ref(false)

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
const barcodeTargetField = ref(null)
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

const openBarcodeScanner = (target = null) => {
  barcodeTargetField.value = target
  showBarcodeModal.value = true
}

// Automatically resolve and load all parts stored in the given bin location for Issue
const loadLocationInventory = async (locationCode) => {
  if (!locationCode || !locationCode.trim()) {
    binInventoryList.value = []
    selectedBinItem.value = null
    return
  }

  const cleanCode = locationCode.replace('inventory://location/', '').trim()
  loadingLocationStock.value = true

  try {
    const locRes = await locationsApi.getByCode(cleanCode)
    const loc = locRes.data || locRes

    if (loc && loc._id) {
      // Get enriched inventory items for this location
      let items = []
      if (loc.inventory && loc.inventory.length > 0) {
        items = loc.inventory
      } else {
        const invRes = await inventoryApi.getByLocation(loc._id)
        items = invRes.data || []
      }

      // Filter to items with positive available stock
      const availableItems = items.filter(i => (i.available_quantity || i.quantity || 0) > 0)
      binInventoryList.value = availableItems

      if (availableItems.length > 0) {
        // Pre-select the first part in this bin
        await selectBinItem(availableItems[0])
      } else {
        selectedBinItem.value = null
      }
    } else {
      binInventoryList.value = []
      selectedBinItem.value = null
    }
  } catch (err) {
    binInventoryList.value = []
    selectedBinItem.value = null
  } finally {
    loadingLocationStock.value = false
  }
}

// Automatically pre-fill Receive form when a destination location is scanned
const handleReceiveLocationAutoFill = async (locCode) => {
  if (!locCode || !locCode.trim()) {
    receiveBinInventoryList.value = []
    selectedReceiveBinItem.value = null
    return
  }
  const cleanCode = locCode.replace('inventory://location/', '').trim()
  receiveForm.value.location_code = cleanCode
  loadingReceiveStock.value = true

  try {
    const locRes = await locationsApi.getByCode(cleanCode)
    const loc = locRes.data || locRes

    if (loc && loc._id) {
      resolvedDestLocation.value = loc

      let items = []
      if (loc.inventory && loc.inventory.length > 0) {
        items = loc.inventory
      } else {
        const invRes = await inventoryApi.getByLocation(loc._id)
        items = invRes.data || []
      }

      const validItems = items.filter(i => (i.quantity || 0) > 0 || (i.available_quantity || 0) > 0)
      receiveBinInventoryList.value = validItems

      // If this bin already stores inventory items, pre-select that part
      if (validItems.length > 0) {
        selectReceiveBinItem(validItems[0])
      } else {
        selectedReceiveBinItem.value = null
        if (!receiveForm.value.part_id && partsList.value.length > 0) {
          receiveForm.value.part_id = partsList.value[0]._id
        }
        autoGenerateLot()

        if (!receiveForm.value.reference_id) {
          const todayStr = new Date().toISOString().slice(0, 10).replace(/-/g, '')
          receiveForm.value.reference_id = `PO-${todayStr}-01`
        }

        nextTick(() => {
          if (receiveQtyInputRef.value) {
            receiveQtyInputRef.value.focus()
            receiveQtyInputRef.value.select()
          }
        })
      }
    } else {
      receiveBinInventoryList.value = []
      selectedReceiveBinItem.value = null
    }
  } catch (e) {
    receiveBinInventoryList.value = []
    selectedReceiveBinItem.value = null
  } finally {
    loadingReceiveStock.value = false
  }
}

// 1-Click select a part stored in this bin to restock
const selectReceiveBinItem = (item) => {
  if (!item) return
  selectedReceiveBinItem.value = item
  receiveForm.value.part_id = item.part_id
  autoGenerateLot()

  if (!receiveForm.value.reference_id) {
    const todayStr = new Date().toISOString().slice(0, 10).replace(/-/g, '')
    receiveForm.value.reference_id = `PO-${todayStr}-01`
  }

  nextTick(() => {
    if (receiveQtyInputRef.value) {
      receiveQtyInputRef.value.focus()
      receiveQtyInputRef.value.select()
    }
  })
}

// 1-Click select a part/lot stored in this bin
const selectBinItem = async (item) => {
  if (!item) return
  selectedBinItem.value = item
  issueForm.value.part_id = item.part_id
  await loadLotsForIssue()
  issueForm.value.lot_id = item.lot_id

  if (!issueForm.value.reference_id) {
    const todayStr = new Date().toISOString().slice(0, 10).replace(/-/g, '')
    issueForm.value.reference_id = `WO-ISSUE-${todayStr}`
  }

  // Pre-fill quantity if not already set
  if (!issueForm.value.quantity || issueForm.value.quantity <= 0) {
    issueForm.value.quantity = Math.min(100, item.available_quantity || 1)
  }

  // Focus the quantity input for immediate typing and Enter key submission
  nextTick(() => {
    if (quantityInputRef.value) {
      quantityInputRef.value.focus()
      quantityInputRef.value.select()
    }
  })
}

const handleLocationResolved = async (loc) => {
  if (nfcTargetField.value === 'receive_dest') {
    receiveForm.value.location_code = loc.location_code
    resolvedDestLocation.value = loc
    await handleReceiveLocationAutoFill(loc.location_code)
  } else if (nfcTargetField.value === 'issue_src') {
    issueForm.value.location_code = loc.location_code
    await loadLocationInventory(loc.location_code)
  } else if (nfcTargetField.value === 'trans_src') {
    transferForm.value.from_location_code = loc.location_code
  } else if (nfcTargetField.value === 'trans_dest') {
    transferForm.value.to_location_code = loc.location_code
  } else if (nfcTargetField.value === 'cell_trans_dest') {
    cellTransferForm.value.to_location_code = loc.location_code
  } else {
    // General quick resolver from top button
    if (activeTab.value === 'receive') {
      receiveForm.value.location_code = loc.location_code
      await handleReceiveLocationAutoFill(loc.location_code)
    } else {
      issueForm.value.location_code = loc.location_code
      activeTab.value = 'issue'
      await loadLocationInventory(loc.location_code)
    }
  }
}

const handleBarcodeScanned = async (code) => {
  const cleanCode = (code || '').trim()
  if (!cleanCode) return

  if (barcodeTargetField.value === 'receive_dest') {
    const locCode = cleanCode.replace('inventory://location/', '').trim()
    receiveForm.value.location_code = locCode
    await handleReceiveLocationAutoFill(locCode)
    return
  }

  if (barcodeTargetField.value === 'issue_src') {
    const locCode = cleanCode.replace('inventory://location/', '').trim()
    issueForm.value.location_code = locCode
    await loadLocationInventory(locCode)
    return
  }

  if (cleanCode.startsWith('CELL-')) {
    cellTransferForm.value.cell_serial_no = cleanCode
    return
  }

  // Fallback: check if it's a location code
  try {
    const locTag = cleanCode.replace('inventory://location/', '').trim()
    const locRes = await locationsApi.getByCode(locTag)
    if (locRes && (locRes.data || locRes._id)) {
      const loc = locRes.data || locRes
      if (activeTab.value === 'receive') {
        receiveForm.value.location_code = loc.location_code
        await handleReceiveLocationAutoFill(loc.location_code)
      } else {
        issueForm.value.location_code = loc.location_code
        activeTab.value = 'issue'
        await loadLocationInventory(loc.location_code)
      }
      return
    }
  } catch (e) {}

  toast.info(`Scanned Code: ${cleanCode}`)
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
    toast.success(res.message || 'Material received successfully')
    await loadData()
    if (receiveForm.value.location_code) {
      await handleReceiveLocationAutoFill(receiveForm.value.location_code)
    }
  } finally {
    submitting.value = false
  }
}

const submitIssue = async () => {
  submitting.value = true
  try {
    const res = await stockApi.issue(issueForm.value)
    toast.success(res.message || 'Material issued successfully')
    await loadData()
    if (issueForm.value.location_code) {
      await loadLocationInventory(issueForm.value.location_code)
    }
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

// Sync route parameters (e.g. /stock-operations?tab=receive&location=E11-1A or tab=issue)
const syncFromRoute = async () => {
  if (route.query.tab) {
    activeTab.value = route.query.tab
  }
  if (route.query.location) {
    const loc = route.query.location
    if (partsList.value.length === 0) {
      await loadData()
    }
    if (activeTab.value === 'receive') {
      await handleReceiveLocationAutoFill(loc)
    } else {
      issueForm.value.location_code = loc
      await loadLocationInventory(loc)
    }
  }
}

watch(() => route.query, () => {
  syncFromRoute()
}, { immediate: true })

onMounted(() => {
  loadData()
})
</script>
