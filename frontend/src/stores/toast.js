import { defineStore } from 'pinia'

export const useToastStore = defineStore('toast', {
  state: () => ({
    toasts: []
  }),
  actions: {
    add(message, type = 'info', duration = 4000) {
      const id = Date.now() + Math.random().toString(36).substring(2, 5)
      this.toasts.push({ id, message, type })

      if (duration > 0) {
        setTimeout(() => {
          this.remove(id)
        }, duration)
      }
    },
    success(msg, duration = 3500) {
      this.add(msg, 'success', duration)
    },
    error(msg, duration = 5000) {
      this.add(msg, 'error', duration)
    },
    warning(msg, duration = 4000) {
      this.add(msg, 'warning', duration)
    },
    info(msg, duration = 3500) {
      this.add(msg, 'info', duration)
    },
    remove(id) {
      this.toasts = this.toasts.filter(t => t.id !== id)
    }
  }
})
