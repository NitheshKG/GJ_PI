<script setup>
import { onMounted, ref, computed } from 'vue'
import { useTicketStore } from '../stores/ticketStore'
import { useNotificationStore } from '../stores/notificationStore'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { API_URL } from '../config/api'
import ConfirmDialog from '../components/ConfirmDialog.vue'

const ticketStore = useTicketStore()
const notificationStore = useNotificationStore()
const router = useRouter()

const showConfirmDialog = ref(false)
const selectedTicketId = ref(null)
const selectedTicketName = ref('')

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(10)

// Sorting
const sortBy = ref('startDate')
const sortOrder = ref('desc')

onMounted(() => {
  ticketStore.fetchTickets()
})

// Sorting computed property
const sortedTickets = computed(() => {
  const tickets = [...ticketStore.tickets]
  
  tickets.sort((a, b) => {
    let aValue = a[sortBy.value]
    let bValue = b[sortBy.value]
    
    // Handle nested or special properties
    if (sortBy.value === 'pendingMonths') {
      aValue = calculatePendingMonths(a)
      bValue = calculatePendingMonths(b)
    }
    
    // Handle null/undefined values
    if (aValue == null && bValue == null) return 0
    if (aValue == null) return sortOrder.value === 'asc' ? 1 : -1
    if (bValue == null) return sortOrder.value === 'asc' ? -1 : 1
    
    // Sort dates
    if (sortBy.value === 'startDate' || sortBy.value === 'closeDate') {
      aValue = new Date(aValue).getTime()
      bValue = new Date(bValue).getTime()
    }
    
    // Compare values
    if (aValue < bValue) return sortOrder.value === 'asc' ? -1 : 1
    if (aValue > bValue) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })
  
  return tickets
})

// Pagination computed properties
const totalPages = computed(() => {
  return Math.ceil(sortedTickets.value.length / itemsPerPage.value)
})

const paginatedTickets = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return sortedTickets.value.slice(start, end)
})

const visiblePageNumbers = computed(() => {
  const pages = []
  const total = totalPages.value
  const current = currentPage.value
  
  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 3) {
      for (let i = 1; i <= 5; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    } else if (current >= total - 2) {
      pages.push(1)
      pages.push('...')
      for (let i = total - 4; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      pages.push('...')
      for (let i = current - 1; i <= current + 1; i++) pages.push(i)
      pages.push('...')
      pages.push(total)
    }
  }
  
  return pages
})

const navigateToPay = (id) => {
  router.push(`/tickets/${id}/pay`)
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString()
}

const calculatePendingMonths = (ticket) => {
  // Interest Pending Months = (current month - start month) - interest received months
  const totalElapsedMonths = ticket.interestPendingMonths || 0
  const receivedMonths = ticket.interestReceivedMonths || 0
  return Math.max(0, totalElapsedMonths - receivedMonths)
}

const canCloseTicket = (ticket) => {
  return calculatePendingMonths(ticket) === 0 && ticket.pendingPrincipal === 0
}

const openCloseDialog = (ticket) => {
  selectedTicketId.value = ticket.id
  selectedTicketName.value = ticket.name
  showConfirmDialog.value = true
}

const closeTicket = async () => {
  try {
    await axios.put(`${API_URL}/api/tickets/${selectedTicketId.value}/close`)
    notificationStore.addNotification('Ticket closed successfully!', 'success', 3000)
    await ticketStore.fetchTickets()
  } catch (error) {
    notificationStore.addNotification('Failed to close ticket', 'error', 3000)
  }
}

const goToPage = (page) => {
  if (page > 0 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const toggleSort = (column) => {
  if (sortBy.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortOrder.value = 'asc'
  }
  currentPage.value = 1
}

const getSortIcon = (column) => {
  if (sortBy.value !== column) return '⇅'
  return sortOrder.value === 'asc' ? '↑' : '↓'
}
</script>

<template>
  <div class="bg-white shadow overflow-hidden sm:rounded-lg">
    <div class="px-4 py-5 sm:px-6 flex flex-col sm:flex-row justify-between items-start sm:items-center">
      <div class="mb-4 sm:mb-0">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Active Tickets</h3>
        <p class="mt-1 max-w-2xl text-sm text-gray-500">List of all current loans and their status.</p>
      </div>
      <router-link 
        to="/tickets/new" 
        class="inline-flex items-center gap-2 px-4 sm:px-6 py-2 sm:py-3 bg-gradient-to-r from-indigo-600 to-blue-600 rounded-lg text-sm font-semibold text-white shadow-lg hover:from-indigo-700 hover:to-blue-700 transition-all duration-200 transform hover:scale-105 hover:shadow-xl"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
        </svg>
        New Ticket
      </router-link>
    </div>

    <div class="border-t border-gray-200">
      <div v-if="ticketStore.loading" class="p-4 text-center text-gray-500">
        Loading...
      </div>
      <div v-else-if="ticketStore.tickets.length === 0" class="p-4 text-center text-gray-500">
        No tickets found.
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none" @click="toggleSort('name')">
                  <div class="flex items-center justify-between gap-2">
                    Name
                    <span class="text-gray-400">{{ getSortIcon('name') }}</span>
                  </div>
                </th>
                <th scope="col" class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none" @click="toggleSort('billNumber')">
                  <div class="flex items-center justify-between gap-2">
                    Bill Number
                    <span class="text-gray-400">{{ getSortIcon('billNumber') }}</span>
                  </div>
                </th>
                <th scope="col" class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none" @click="toggleSort('articleName')">
                  <div class="flex items-center justify-between gap-2">
                    Item
                    <span class="text-gray-400">{{ getSortIcon('articleName') }}</span>
                  </div>
                </th>
                <th scope="col" class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none" @click="toggleSort('principal')">
                  <div class="flex items-center justify-between gap-2">
                    Initial Principal
                    <span class="text-gray-400">{{ getSortIcon('principal') }}</span>
                  </div>
                </th>
                <th scope="col" class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none" @click="toggleSort('pendingPrincipal')">
                  <div class="flex items-center justify-between gap-2">
                    Pending Principal
                    <span class="text-gray-400">{{ getSortIcon('pendingPrincipal') }}</span>
                  </div>
                </th>
                <th scope="col" class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none" @click="toggleSort('interestPercentage')">
                  <div class="flex items-center justify-between gap-2">
                    Interest %
                    <span class="text-gray-400">{{ getSortIcon('interestPercentage') }}</span>
                  </div>
                </th>
                <th scope="col" class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none" @click="toggleSort('startDate')">
                  <div class="flex items-center justify-between gap-2">
                    Start Date
                    <span class="text-gray-400">{{ getSortIcon('startDate') }}</span>
                  </div>
                </th>
                <th scope="col" class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none" @click="toggleSort('pendingMonths')">
                  <div class="flex items-center justify-between gap-2">
                    Interest Pending Months
                    <span class="text-gray-400">{{ getSortIcon('pendingMonths') }}</span>
                  </div>
                </th>
                <th scope="col" class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none" @click="toggleSort('totalInterestReceived')">
                  <div class="flex items-center justify-between gap-2">
                    Interest Received
                    <span class="text-gray-400">{{ getSortIcon('totalInterestReceived') }}</span>
                  </div>
                </th>
                <th scope="col" class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none" @click="toggleSort('status')">
                  <div class="flex items-center justify-between gap-2">
                    Status
                    <span class="text-gray-400">{{ getSortIcon('status') }}</span>
                  </div>
                </th>
                <th scope="col" class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100 select-none" @click="toggleSort('closeDate')">
                  <div class="flex items-center justify-between gap-2">
                    Close Date
                    <span class="text-gray-400">{{ getSortIcon('closeDate') }}</span>
                  </div>
                </th>
                <th scope="col" class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="ticket in paginatedTickets" :key="ticket.id" class="hover:bg-gray-50">
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <router-link 
                    :to="`/customers/${ticket.customerId}`"
                    class="text-indigo-600 hover:text-indigo-900 hover:underline font-semibold"
                  >
                    {{ ticket.name }}
                  </router-link>
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                  {{ ticket.billNumber || '-' }}
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ ticket.articleName }}
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ₹{{ ticket.principal?.toLocaleString() || 0 }}
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                  ₹{{ ticket.pendingPrincipal?.toLocaleString() || 0 }}
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ ticket.interestPercentage }}%
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(ticket.startDate) }}
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm font-medium text-orange-600">
                  {{ calculatePendingMonths(ticket) }} months
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-green-600 font-medium">
                  ₹{{ ticket.totalInterestReceived?.toLocaleString() || 0 }}
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap">
                  <span :class="[
                    'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                    ticket.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  ]">
                    {{ ticket.status }}
                  </span>
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(ticket.closeDate) }}
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm font-medium space-x-3">
                  <router-link 
                    :to="`/tickets/${ticket.id}/payments`"
                    class="text-blue-600 hover:text-blue-900"
                  >
                    View Payments
                  </router-link>
                  <button 
                    v-if="ticket.status === 'Active'"
                    @click="navigateToPay(ticket.id)" 
                    class="text-indigo-600 hover:text-indigo-900"
                  >
                    Record Payment
                  </button>
                  <button 
                    v-if="canCloseTicket(ticket) && ticket.status === 'Active'"
                    @click="openCloseDialog(ticket)" 
                    class="text-red-600 hover:text-red-900 font-semibold"
                  >
                    Close Ticket
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Pagination Controls -->
      <div v-if="totalPages > 1" class="bg-white px-4 py-3 flex flex-col sm:flex-row items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
            :class="[
              'relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md',
              currentPage === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-gray-50'
            ]"
          >
            Previous
          </button>
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            :class="[
              'ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md',
              currentPage === totalPages ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-700 hover:bg-gray-50'
            ]"
          >
            Next
          </button>
        </div>
        <div class="hidden sm:flex sm:w-full sm:items-center sm:justify-between gap-8">
          <div class="flex items-center space-x-4">
            <div>
              <p class="text-sm text-gray-700">
                Showing
                <span class="font-medium">{{ (currentPage - 1) * itemsPerPage + 1 }}</span>
                to
                <span class="font-medium">{{ Math.min(currentPage * itemsPerPage, sortedTickets.length) }}</span>
                of
                <span class="font-medium">{{ sortedTickets.length }}</span>
                tickets
              </p>
            </div>
            <div class="border-l border-gray-300 pl-4">
              <label for="items-per-page" class="block text-sm font-medium text-gray-700 mb-1">
                Tickets per page:
              </label>
              <select
                id="items-per-page"
                v-model.number="itemsPerPage"
                @change="currentPage = 1"
                class="block w-20 px-3 py-1 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 text-sm"
              >
                <option :value="10">10</option>
                <option :value="50">50</option>
                <option :value="100">100</option>
              </select>
            </div>
          </div>
          <div class="flex-shrink-0">
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <!-- Previous Button -->
              <button
                @click="goToPage(currentPage - 1)"
                :disabled="currentPage === 1"
                :class="[
                  'relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 text-sm font-medium',
                  currentPage === 1 ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-500 hover:bg-gray-50'
                ]"
              >
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </button>
              
              <!-- Page Numbers -->
              <template v-for="page in visiblePageNumbers" :key="page">
                <button
                  v-if="page !== '...'"
                  @click="goToPage(page)"
                  :class="[
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                    currentPage === page
                      ? 'z-10 bg-indigo-600 border-indigo-600 text-white'
                      : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                  ]"
                >
                  {{ page }}
                </button>
                <span
                  v-else
                  class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700"
                >
                  ...
                </span>
              </template>
              
              <!-- Next Button -->
              <button
                @click="goToPage(currentPage + 1)"
                :disabled="currentPage === totalPages"
                :class="[
                  'relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 text-sm font-medium',
                  currentPage === totalPages ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-white text-gray-500 hover:bg-gray-50'
                ]"
              >
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>
  </div>
  
  <!-- Confirmation Dialog -->
  <ConfirmDialog
    v-model:show="showConfirmDialog"
    title="Close Ticket"
    :message="`Are you sure you want to close the ticket for ${selectedTicketName}? This action cannot be undone.`"
    confirmText="Yes, Close Ticket"
    cancelText="Cancel"
    @confirm="closeTicket"
  />
</template>
