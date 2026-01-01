<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useTicketStore } from '../stores/ticketStore'
import { useNotificationStore } from '../stores/notificationStore'
import { useRoute, useRouter } from 'vue-router'

const ticketStore = useTicketStore()
const notificationStore = useNotificationStore()
const route = useRoute()
const router = useRouter()

const form = ref({
  interestPaid: 0,
  principalPaid: 0,
  monthsPaid: 1
})

onMounted(async () => {
  await ticketStore.fetchTicket(route.params.id)
  // Auto-calculate interest on mount
  if (ticket.value) {
    calculateInterest()
  }
})

const ticket = computed(() => ticketStore.currentTicket)

// Calculate Interest Pending Months
const interestPendingMonths = computed(() => {
  if (!ticket.value) return 0
  const totalElapsed = ticket.value.interestPendingMonths || 0
  const received = ticket.value.interestReceivedMonths || 0
  return Math.max(0, totalElapsed - received)
})

// Check if principal payment is allowed
const canPayPrincipal = computed(() => {
  // Allow if no interest is pending OR if the user is paying enough months to cover pending interest
  const pendingAfterPayment = Math.max(0, interestPendingMonths.value - (form.value.monthsPaid || 0))
  return pendingAfterPayment === 0
})

// Auto-calculate interest based on pending principal, interest percentage, and months
const calculateInterest = () => {
  if (ticket.value && (form.value.monthsPaid || form.value.monthsPaid === 0)) {
    const principal = ticket.value.pendingPrincipal || 0
    const rate = ticket.value.interestPercentage || 0
    const months = form.value.monthsPaid || 0
    
    // Formula: (Principal × Rate × Months) / 100
    // Example: Principal=20000, Rate=2%, Months=4 => (20000 × 2 × 4) / 100 = 1600
    const calculatedInterest = (principal * rate * months) / 100
    form.value.interestPaid = parseFloat(calculatedInterest.toFixed(2))
  }
}

// Watch for changes in monthsPaid to auto-update interest
watch(() => form.value.monthsPaid, () => {
  calculateInterest()
})

const submitPayment = async () => {
  // Validate that at least one payment type is provided
  if (form.value.interestPaid <= 0 && form.value.principalPaid <= 0) {
    notificationStore.addNotification('Please enter either interest amount or principal amount (or both)', 'warning', 3000)
    return
  }
  
  try {
    await ticketStore.addPayment(route.params.id, form.value)
    // Redirect immediately and show notification on dashboard
    router.push('/')
    notificationStore.addNotification('Payment recorded successfully!', 'success', 3000)
  } catch (e) {
    notificationStore.addNotification(`Failed to record payment: ${e.message}`, 'error', 3000)
  }
}

</script>

<template>
  <div class="bg-white shadow sm:rounded-lg max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
    <div v-if="ticket" class="px-4 py-5 sm:p-6">
      <h3 class="text-lg leading-6 font-medium text-gray-900">Record Payment</h3>
      <div class="mt-2 max-w-xl text-sm text-gray-500">
        <p>Recording payment for <strong>{{ ticket.name }}</strong> ({{ ticket.articleName }})</p>
        <p>Current Pending Principal: <strong>₹{{ ticket.pendingPrincipal?.toLocaleString() }}</strong></p>
        <p>Interest Rate: <strong>{{ ticket.interestPercentage }}% per month</strong></p>
        <p class="mt-2" :class="interestPendingMonths > 0 ? 'text-orange-600 font-semibold' : 'text-green-600 font-semibold'">
          Interest Pending Months: <strong>{{ interestPendingMonths }} months</strong>
        </p>
      </div>

      <form @submit.prevent="submitPayment" class="mt-5 space-y-6">
        <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
          <div>
            <label for="monthsPaid" class="block text-sm font-medium text-gray-700">Months Paid</label>
            <div class="mt-1">
              <input type="number" name="monthsPaid" id="monthsPaid" v-model="form.monthsPaid" min="0" class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none">
            </div>
            <p class="mt-1 text-xs text-gray-500">Leave as 0 if only paying principal</p>
          </div>

          <div>
            <label for="interestPaid" class="block text-sm font-medium text-gray-700">Interest Amount</label>
            <div class="mt-1">
              <input type="number" name="interestPaid" id="interestPaid" v-model="form.interestPaid" min="0" step="0.01" class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none">
            </div>
            <p class="mt-1 text-xs text-gray-500">Auto-calculated based on months paid</p>
          </div>

          <div>
            <label for="principalPaid" class="block text-sm font-medium" :class="!canPayPrincipal ? 'text-gray-400' : 'text-gray-700'">
              Principal Paid
            </label>
            <div class="mt-1">
              <input 
                type="number" 
                name="principalPaid" 
                id="principalPaid" 
                v-model="form.principalPaid" 
                min="0" 
                step="0.01" 
                :disabled="!canPayPrincipal"
                :class="[
                  'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none',
                  !canPayPrincipal ? 'bg-gray-100 cursor-not-allowed text-gray-400' : ''
                ]"
              >
            </div>
            <p class="mt-1 text-xs text-gray-500">This will reduce the pending principal</p>
          </div>
        </div>

        <div class="flex justify-end space-x-4">
          <router-link to="/" class="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            Cancel
          </router-link>
          <button type="submit" :disabled="ticketStore.loading" class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
            {{ ticketStore.loading ? 'Processing...' : 'Record Payment' }}
          </button>
        </div>
      </form>
    </div>
    <div v-else class="text-center p-10">
      Loading ticket details...
    </div>
  </div>
</template>
