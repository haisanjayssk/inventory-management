import { ref } from 'vue'
import { useToastStore } from '@/stores/toast'
import locationsApi from '@/api/locations'

export function useNfc() {
  const isScanning = ref(false)
  const isSupported = ref('NDEFReader' in window)
  const lastScannedTag = ref(null)
  const resolvedLocation = ref(null)
  const error = ref(null)
  const toast = useToastStore()

  // Start hardware Web NFC scanning (for Android Chrome / Mobile)
  const startScan = async (onLocationResolved) => {
    error.value = null
    resolvedLocation.value = null

    if (!('NDEFReader' in window)) {
      error.value = 'Web NFC API is not supported on this browser/platform. Please use Camera Barcode/QR or Manual code input.'
      return false
    }

    try {
      const ndef = new window.NDEFReader()
      await ndef.scan()
      isScanning.value = true
      toast.info('NFC Scanner active. Tap an NFC tag to scan...')

      ndef.onreading = async (event) => {
        const serialNumber = event.serialNumber
        let tagPayload = serialNumber

        // Parse records if available
        for (const record of event.message.records) {
          if (record.recordType === 'text') {
            const textDecoder = new TextDecoder(record.encoding || 'utf-8')
            tagPayload = textDecoder.decode(record.data)
            break
          } else if (record.recordType === 'url') {
            const textDecoder = new TextDecoder()
            tagPayload = textDecoder.decode(record.data)
            break
          }
        }

        lastScannedTag.value = tagPayload
        await resolveTag(tagPayload, onLocationResolved)
      }

      ndef.onreadingerror = () => {
        error.value = 'Failed to read NFC tag. Please hold the tag steady and try again.'
        toast.warning(error.value)
      }

      return true
    } catch (err) {
      isScanning.value = false
      error.value = err.message || 'Could not start NFC scanning'
      toast.error(error.value)
      return false
    }
  }

  // Resolve an NFC tag payload (e.g. inventory://location/E11-1A or E11-1A) with backend
  const resolveTag = async (tagPayload, callback) => {
    try {
      const response = await locationsApi.getByNfc(tagPayload)
      if (response.success && response.data) {
        resolvedLocation.value = response.data
        toast.success(`Location resolved: ${response.data.location_code}`)
        if (callback) callback(response.data)
        return response.data
      }
    } catch (err) {
      // If tag match fails, try resolving as direct location code
      try {
        const cleanCode = tagPayload.replace('inventory://location/', '').trim()
        const codeRes = await locationsApi.getByCode(cleanCode)
        if (codeRes.success && codeRes.data) {
          resolvedLocation.value = codeRes.data
          toast.success(`Location resolved: ${codeRes.data.location_code}`)
          if (callback) callback(codeRes.data)
          return codeRes.data
        }
      } catch (innerErr) {
        error.value = `Unrecognized location identifier: ${tagPayload}`
      }
    }
    return null
  }

  return {
    isScanning,
    isSupported,
    lastScannedTag,
    resolvedLocation,
    error,
    startScan,
    resolveTag
  }
}
