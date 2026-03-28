<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTicketStore } from '../stores/ticketStore'
import { useNotificationStore } from '../stores/notificationStore'
import axios from 'axios'
import { API_URL } from '../config/api'

const route = useRoute()
const router = useRouter()
const ticketStore = useTicketStore()
const notificationStore = useNotificationStore()

const payments = ref([])
const loading = ref(false)
const editingPaymentId = ref(null)
const editForm = ref({})

const ticket = computed(() => ticketStore.currentTicket)

onMounted(async () => {
  loading.value = true
  await ticketStore.fetchTicket(route.params.id)
  await fetchPayments()
  loading.value = false
})

const fetchPayments = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/tickets/${route.params.id}/payments`)
    payments.value = response.data
  } catch (error) {
    console.error('Failed to fetch payments:', error)
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('en-IN', { 
    dateStyle: 'medium', 
    timeStyle: 'short'
  })
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-IN', { day: '2-digit', month: '2-digit', year: 'numeric' })
  } catch {
    return '-'
  }
}

const startEditPayment = (payment) => {
  editingPaymentId.value = payment.id
  // Extract date part (YYYY-MM-DD) from ISO datetime string
  const dateStr = payment.date ? payment.date.split('T')[0] : new Date().toISOString().split('T')[0]
  editForm.value = {
    interestPaid: payment.interestPaid,
    principalPaid: payment.principalPaid,
    monthsPaid: payment.monthsPaid,
    date: dateStr
  }
}

const cancelEdit = () => {
  editingPaymentId.value = null
  editForm.value = {}
}

const savePayment = async (paymentId) => {
  try {
    const updateData = {
      interestPaid: parseFloat(editForm.value.interestPaid) || 0,
      principalPaid: parseFloat(editForm.value.principalPaid) || 0,
      monthsPaid: parseFloat(editForm.value.monthsPaid) || 0,
      date: editForm.value.date
    }

    await axios.put(`${API_URL}/api/payments/${paymentId}`, updateData)
    
    notificationStore.addNotification('Payment updated successfully!', 'success', 3000)
    editingPaymentId.value = null
    editForm.value = {}
    
    // Refresh payments and ticket data
    await fetchPayments()
    await ticketStore.fetchTicket(route.params.id)
  } catch (error) {
    const errorMessage = error.response?.data?.error || error.message
    notificationStore.addNotification(`Failed to update payment: ${errorMessage}`, 'error', 3000)
  }
}

const deletePayment = async (paymentId) => {
  if (!confirm('Are you sure you want to delete this payment?')) {
    return
  }
  
  try {
    await axios.delete(`${API_URL}/api/payments/${paymentId}`)
    notificationStore.addNotification('Payment deleted successfully!', 'success', 3000)
    await fetchPayments()
    await ticketStore.fetchTicket(route.params.id)
  } catch (error) {
    const errorMessage = error.response?.data?.error || error.message
    notificationStore.addNotification(`Failed to delete payment: ${errorMessage}`, 'error', 3000)
  }
}

const canCloseTicket = computed(() => {
  return ticket.value && ticket.value.pendingPrincipal === 0
})

const closeTicket = async () => {
  if (!confirm('Close this ticket? This action cannot be undone.')) {
    return
  }
  
  try {
    await axios.put(`${API_URL}/api/tickets/${route.params.id}/close`)
    notificationStore.addNotification('Ticket closed successfully!', 'success', 3000)
    // Refresh both current ticket and all tickets in the store
    await ticketStore.fetchTicket(route.params.id)
    await ticketStore.fetchTickets()
    // Navigate back to dashboard after a brief delay
    setTimeout(() => {
      router.push('/')
    }, 1500)
  } catch (error) {
    const errorMessage = error.response?.data?.error || error.message
    notificationStore.addNotification(`Failed to close ticket: ${errorMessage}`, 'error', 3000)
  }
}
</script>

<template>
  <div class="space-y-6 px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">Payment History</h3>
          </div>
          <div class="flex gap-3">
            <button
              v-if="canCloseTicket && ticket && ticket.status === 'Active'"
              @click="closeTicket"
              class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700"
            >
              Close Ticket
            </button>
            <router-link 
              to="/" 
              class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              Back to Dashboard
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Ticket Summary -->
    <div class="bg-white shadow sm:rounded-lg" v-if="ticket">
      <div class="px-4 py-5 sm:p-6">
        <h4 class="text-md font-medium text-gray-900 mb-4">Loan Details</h4>
        <dl class="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2 md:grid-cols-3">
          <div>
            <dt class="text-sm font-medium text-gray-500">Customer Name</dt>
            <dd class="mt-1 text-sm font-bold text-gray-900">{{ ticket.customerName }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Item</dt>
            <dd class="mt-1 text-sm font-bold text-gray-900">{{ ticket.articleName }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Bill Number</dt>
            <dd class="mt-1 text-sm font-semibold text-gray-900">{{ ticket.billNumber || '-' }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Initial Principal</dt>
            <dd class="mt-1 text-sm text-gray-900">₹{{ ticket.principal?.toLocaleString() }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Pending Principal</dt>
            <dd class="mt-1 text-sm font-semibold text-gray-900">₹{{ ticket.pendingPrincipal?.toLocaleString() }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Interest Rate</dt>
            <dd class="mt-1 text-sm text-gray-900">{{ ticket.interestPercentage }}% per month</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Start Date</dt>
            <dd class="mt-1 text-sm text-gray-900">{{ formatDate(ticket.startDate) }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Total Interest Received</dt>
            <dd class="mt-1 text-sm font-semibold text-green-600">₹{{ ticket.totalInterestReceived?.toLocaleString() || 0 }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Status</dt>
            <dd class="mt-1">
              <span :class="[
                'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                ticket.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
              ]">
                {{ ticket.status }}
              </span>
            </dd>
          </div>
        </dl>
      </div>
    </div>

    <!-- Payment History Table -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6">
        <h4 class="text-md font-medium text-gray-900">Payment Transactions</h4>
        <p class="mt-1 text-sm text-gray-500">Complete history of all interest and principal payments</p>
      </div>
      <div class="border-t border-gray-200">
        <div v-if="loading" class="p-4 text-center text-gray-500">
          Loading...
        </div>
        <div v-else-if="payments.length === 0" class="p-8 text-center text-gray-500">
          <p>No payments recorded yet.</p>
          <router-link 
            :to="`/tickets/${route.params.id}/pay`"
            class="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Record First Payment
          </router-link>
        </div>
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Payment Date
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Months Paid
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Interest Paid
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Principal Paid
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Remaining Principal
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="payment in payments" :key="payment.id" :class="editingPaymentId === payment.id ? 'bg-blue-50' : 'hover:bg-gray-50'">
                <td v-if="editingPaymentId === payment.id" class="px-6 py-4 whitespace-nowrap text-sm">
                  <input 
                    type="date" 
                    v-model="editForm.date" 
                    class="border border-gray-300 rounded px-2 py-1 text-sm w-32"
                  />
                </td>
                <td v-else class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDate(payment.date) }}
                </td>
                <td v-if="editingPaymentId === payment.id" class="px-6 py-4 whitespace-nowrap text-sm">
                  <input 
                    type="number" 
                    v-model.number="editForm.monthsPaid" 
                    step="0.5"
                    min="0"
                    class="border border-gray-300 rounded px-2 py-1 text-sm w-20"
                  />
                </td>
                <td v-else class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ payment.monthsPaid || '-' }}
                </td>
                <td v-if="editingPaymentId === payment.id" class="px-6 py-4 whitespace-nowrap text-sm">
                  <input 
                    type="number" 
                    v-model.number="editForm.interestPaid" 
                    step="0.01"
                    min="0"
                    class="border border-gray-300 rounded px-2 py-1 text-sm w-24"
                  />
                </td>
                <td v-else class="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                  {{ payment.interestPaid > 0 ? `₹${payment.interestPaid.toLocaleString()}` : '-' }}
                </td>
                <td v-if="editingPaymentId === payment.id" class="px-6 py-4 whitespace-nowrap text-sm">
                  <input 
                    type="number" 
                    v-model.number="editForm.principalPaid" 
                    step="0.01"
                    min="0"
                    class="border border-gray-300 rounded px-2 py-1 text-sm w-24"
                  />
                </td>
                <td v-else class="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                  {{ payment.principalPaid > 0 ? `₹${payment.principalPaid.toLocaleString()}` : '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                  ₹{{ payment.remainingPrincipal?.toLocaleString() || 0 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <div v-if="editingPaymentId === payment.id" class="flex gap-2">
                    <button 
                      @click="savePayment(payment.id)"
                      class="text-green-600 hover:text-green-900 font-semibold"
                    >
                      Save
                    </button>
                    <button 
                      @click="cancelEdit"
                      class="text-gray-600 hover:text-gray-900"
                    >
                      Cancel
                    </button>
                  </div>
                  <div v-else class="flex gap-2">
                    <button 
                      @click="startEditPayment(payment)"
                      class="text-amber-600 hover:text-amber-900"
                    >
                      Edit
                    </button>
                    <button 
                      @click="deletePayment(payment.id)"
                      class="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
