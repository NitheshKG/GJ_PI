<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTicketStore } from '../stores/ticketStore'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const ticketStore = useTicketStore()

const payments = ref([])
const loading = ref(false)

const ticket = computed(() => ticketStore.currentTicket)

onMounted(async () => {
  loading.value = true
  await ticketStore.fetchTicket(route.params.id)
  await fetchPayments()
  loading.value = false
})

const fetchPayments = async () => {
  try {
    const response = await axios.get(`http://localhost:5000/api/tickets/${route.params.id}/payments`)
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
  return new Date(dateString).toLocaleDateString('en-IN', { dateStyle: 'medium' })
}
</script>

<template>
  <div class="space-y-6 px-4 sm:px-6 lg:px-8">
    <!-- Header -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">Payment History</h3>
          </div>
          <router-link 
            to="/" 
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Back to Dashboard
          </router-link>
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
            <dd class="mt-1 text-sm font-bold text-gray-900">{{ ticket.name }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Item</dt>
            <dd class="mt-1 text-sm font-bold text-gray-900">{{ ticket.articleName }}</dd>
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
                  Interest Received At
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Principal Paid
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Principal Received At
                </th>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Remaining Principal
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="payment in payments" :key="payment.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDateTime(payment.date) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ payment.monthsPaid || '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                  {{ payment.interestPaid > 0 ? `₹${payment.interestPaid.toLocaleString()}` : '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDateTime(payment.interestReceivedAt) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                  {{ payment.principalPaid > 0 ? `₹${payment.principalPaid.toLocaleString()}` : '-' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDateTime(payment.principalReceivedAt) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                  ₹{{ payment.remainingPrincipal?.toLocaleString() || 0 }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
