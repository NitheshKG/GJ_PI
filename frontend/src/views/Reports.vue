<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const loading = ref(false)
const filterType = ref('month') // 'month', 'range', 'all'
const selectedMonth = ref('')
const startMonth = ref('')
const endMonth = ref('')
const monthlyReport = ref(null)
const outstandingLoans = ref(null)
const allTickets = ref([])
const allPayments = ref([])

// Set current month as default
onMounted(async () => {
  const now = new Date()
  selectedMonth.value = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
  startMonth.value = `${now.getFullYear()}-01`
  endMonth.value = selectedMonth.value
  
  await Promise.all([
    fetchAllPayments(),
    fetchOutstandingLoans(),
    fetchAllTickets()
  ])
  fetchMonthlyReport()
})

const fetchAllPayments = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/payments')
    allPayments.value = response.data || []
  } catch (error) {
    console.error('Failed to fetch all payments:', error)
    allPayments.value = []
  }
}

const fetchMonthlyReport = async () => {
  loading.value = true
  try {
    let filteredPayments = []
    let filteredTickets = []
    let start, end
    
    if (filterType.value === 'all') {
      // All time - use all payments and tickets
      filteredPayments = allPayments.value
      filteredTickets = allTickets.value
    } else if (filterType.value === 'month') {
      // Single month
      const monthStart = new Date(selectedMonth.value + '-01')
      const monthEnd = new Date(monthStart)
      monthEnd.setMonth(monthEnd.getMonth() + 1)
      start = monthStart
      end = monthEnd
      
      filteredPayments = allPayments.value.filter(p => {
        const paymentDate = new Date(p.date)
        return paymentDate >= start && paymentDate < end
      })
      
      filteredTickets = allTickets.value.filter(t => {
        const ticketDate = new Date(t.startDate)
        return ticketDate >= start && ticketDate < end
      })
    } else if (filterType.value === 'range') {
      // Date range
      start = new Date(startMonth.value + '-01')
      end = new Date(endMonth.value + '-01')
      end.setMonth(end.getMonth() + 1) // Include the end month
      
      filteredPayments = allPayments.value.filter(p => {
        const paymentDate = new Date(p.date)
        return paymentDate >= start && paymentDate < end
      })
      
      filteredTickets = allTickets.value.filter(t => {
        const ticketDate = new Date(t.startDate)
        return ticketDate >= start && ticketDate < end
      })
    }
    
    // Calculate aggregated data from payments
    const totalInterest = filteredPayments.reduce((sum, p) => sum + (p.interestPaid || 0), 0)
    const totalPrincipalReceived = filteredPayments.reduce((sum, p) => sum + (p.principalPaid || 0), 0)
    
    // Create combined transactions list (investments + payments)
    const transactions = []
    
    // Add ticket investments as transactions
    filteredTickets.forEach(ticket => {
      transactions.push({
        id: `investment-${ticket.id}`,
        date: ticket.startDate,
        customerName: ticket.name,
        type: 'Invested',
        interestPaid: 0,
        principalPaid: ticket.principal,
        isPrincipalInvestment: true
      })
    })
    
    // Add payments as transactions
    filteredPayments.forEach(payment => {
      transactions.push({
        ...payment,
        type: 'Received',
        isPrincipalInvestment: false
      })
    })
    
    monthlyReport.value = {
      month: filterType.value === 'all' ? 'All Time' : filterType.value === 'month' ? selectedMonth.value : `${startMonth.value} to ${endMonth.value}`,
      totalInterest,
      totalPrincipal: totalPrincipalReceived,
      paymentCount: filteredPayments.length,
      payments: transactions.sort((a, b) => new Date(b.date) - new Date(a.date))
    }
  } catch (error) {
    console.error('Failed to fetch monthly report:', error)
  }
  loading.value = false
}

const fetchOutstandingLoans = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/reports/outstanding-loans')
    outstandingLoans.value = response.data
  } catch (error) {
    console.error('Failed to fetch outstanding loans:', error)
  }
}

const fetchAllTickets = async () => {
  try {
    const response = await axios.get('http://localhost:5000/api/tickets')
    allTickets.value = response.data
  } catch (error) {
    console.error('Failed to fetch tickets:', error)
  }
}

const totalPrincipalInvested = computed(() => {
  // Always show all-time data regardless of filter
  return allTickets.value.reduce((sum, ticket) => sum + (ticket.principal || 0), 0)
})

const totalInterestEarned = computed(() => {
  // Always show all-time data regardless of filter
  // Sum all interest paid from payments collection for accurate total
  return allPayments.value.reduce((sum, payment) => sum + (payment.interestPaid || 0), 0)
})

const activeTicketsCount = computed(() => {
  // Always show all-time data regardless of filter
  return allTickets.value.filter(t => t.status === 'Active').length
})

const closedTicketsCount = computed(() => {
  // Always show all-time data regardless of filter
  return allTickets.value.filter(t => t.status === 'Closed').length
})

// Filtered principal invested based on selected month/range (for Payment Report section)
const filteredPrincipalInvested = computed(() => {
  let tickets = allTickets.value
  
  if (filterType.value === 'month') {
    const monthStart = new Date(selectedMonth.value + '-01')
    const monthEnd = new Date(monthStart)
    monthEnd.setMonth(monthEnd.getMonth() + 1)
    
    tickets = tickets.filter(t => {
      const startDate = new Date(t.startDate)
      return startDate >= monthStart && startDate < monthEnd
    })
  } else if (filterType.value === 'range') {
    const start = new Date(startMonth.value + '-01')
    const end = new Date(endMonth.value + '-01')
    end.setMonth(end.getMonth() + 1)
    
    tickets = tickets.filter(t => {
      const startDate = new Date(t.startDate)
      return startDate >= start && startDate < end
    })
  }
  // 'all' type shows all tickets
  
  return tickets.reduce((sum, ticket) => sum + (ticket.principal || 0), 0)
})

const handleFilterChange = () => {
  fetchMonthlyReport()
}

const formatCurrency = (amount) => {
  return `₹${amount?.toLocaleString() || 0}`
}

const exportPaymentReport = async () => {
  try {
    let url = 'http://localhost:5000/api/reports/export/payment-report?'
    
    const params = new URLSearchParams()
    params.append('filterType', filterType.value)
    
    if (filterType.value === 'month') {
      params.append('month', selectedMonth.value)
    } else if (filterType.value === 'range') {
      params.append('startMonth', startMonth.value)
      params.append('endMonth', endMonth.value)
    }
    
    url += params.toString()
    
    // Open in new window to trigger download
    window.open(url, '_blank')
  } catch (error) {
    console.error('Failed to export payment report:', error)
    alert('Failed to export payment report')
  }
}

const exportOutstandingLoans = async () => {
  try {
    const url = 'http://localhost:5000/api/reports/export/outstanding-loans'
    // Open in new window to trigger download
    window.open(url, '_blank')
  } catch (error) {
    console.error('Failed to export outstanding loans:', error)
    alert('Failed to export outstanding loans')
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Page Header -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Financial Summary & Reports</h3>
        <p class="mt-1 max-w-2xl text-sm text-gray-500">Overview of your pawn business financials</p>
      </div>
    </div>

    <!-- Overall Summary Cards -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <!-- Total Principal Invested -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Principal Invested</dt>
                <dd class="text-lg font-semibold text-gray-900">{{ formatCurrency(totalPrincipalInvested) }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Total Interest Earned -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 14l6-6m-5.5.5h.01m4.99 5h.01M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16l3.5-2 3.5 2 3.5-2 3.5 2z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Interest Earned (All Time)</dt>
                <dd class="text-lg font-semibold text-green-600">{{ formatCurrency(totalInterestEarned) }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Tickets -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Active Tickets</dt>
                <dd class="text-lg font-semibold text-indigo-600">{{ activeTicketsCount }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- Outstanding Amount -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Outstanding Principal</dt>
                <dd class="text-lg font-semibold text-orange-600">{{ formatCurrency(outstandingLoans?.totalOutstanding) }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Monthly Report Section -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
        <div class="flex items-start justify-between">
          <div>
            <h4 class="text-md font-medium text-gray-900">Payment Report</h4>
            <p class="mt-1 text-sm text-gray-500">Filter payments by time period</p>
          </div>
          <div class="flex flex-col items-end space-y-3">
            <!-- Export Button -->
            <button
              @click="exportPaymentReport"
              class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export to CSV
            </button>
            
            <!-- Filter Type Selection -->
            <div class="flex items-center space-x-4">
              <label class="inline-flex items-center">
                <input
                  type="radio"
                  v-model="filterType"
                  value="month"
                  @change="handleFilterChange"
                  class="form-radio h-4 w-4 text-indigo-600"
                >
                <span class="ml-2 text-sm text-gray-700">Single Month</span>
              </label>
              <label class="inline-flex items-center">
                <input
                  type="radio"
                  v-model="filterType"
                  value="range"
                  @change="handleFilterChange"
                  class="form-radio h-4 w-4 text-indigo-600"
                >
                <span class="ml-2 text-sm text-gray-700">Date Range</span>
              </label>
              <label class="inline-flex items-center">
                <input
                  type="radio"
                  v-model="filterType"
                  value="all"
                  @change="handleFilterChange"
                  class="form-radio h-4 w-4 text-indigo-600"
                >
                <span class="ml-2 text-sm text-gray-700">All Time</span>
              </label>
            </div>
            
            <!-- Single Month Input -->
            <div v-if="filterType === 'month'" class="flex items-center space-x-2">
              <label for="month-select" class="text-sm font-medium text-gray-700">Month:</label>
              <input
                id="month-select"
                type="month"
                v-model="selectedMonth"
                @change="handleFilterChange"
                class="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
              >
            </div>
            
            <!-- Date Range Inputs -->
            <div v-if="filterType === 'range'" class="flex items-center space-x-2">
              <label class="text-sm font-medium text-gray-700">From:</label>
              <input
                type="month"
                v-model="startMonth"
                @change="handleFilterChange"
                class="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
              >
              <label class="text-sm font-medium text-gray-700">To:</label>
              <input
                type="month"
                v-model="endMonth"
                @change="handleFilterChange"
                class="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm px-3 py-2 border"
              >
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="p-8 text-center text-gray-500">
        Loading report...
      </div>

      <div v-else-if="monthlyReport" class="p-6">
        <!-- Monthly Summary Cards -->
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-6">
          <div class="bg-indigo-50 rounded-lg p-4">
            <dt class="text-sm font-medium text-indigo-800">Principal Invested</dt>
            <dd class="mt-1 text-2xl font-semibold text-indigo-900">{{ formatCurrency(filteredPrincipalInvested) }}</dd>
          </div>
          <div class="bg-green-50 rounded-lg p-4">
            <dt class="text-sm font-medium text-green-800">Total Interest Received</dt>
            <dd class="mt-1 text-2xl font-semibold text-green-900">{{ formatCurrency(monthlyReport.totalInterest) }}</dd>
          </div>
          <div class="bg-blue-50 rounded-lg p-4">
            <dt class="text-sm font-medium text-blue-800">Total Principal Received</dt>
            <dd class="mt-1 text-2xl font-semibold text-blue-900">{{ formatCurrency(monthlyReport.totalPrincipal) }}</dd>
          </div>
          <div class="bg-purple-50 rounded-lg p-4">
            <dt class="text-sm font-medium text-purple-800">Number of Payments</dt>
            <dd class="mt-1 text-2xl font-semibold text-purple-900">{{ monthlyReport.paymentCount }}</dd>
          </div>
        </div>

        <!-- Payment Details Table -->
        <div v-if="monthlyReport.payments && monthlyReport.payments.length > 0">
          <h5 class="text-sm font-medium text-gray-900 mb-3">Transaction Details</h5>
          <div class="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
            <table class="min-w-full divide-y divide-gray-300">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-2 sm:px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th class="px-2 sm:px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                  <th class="px-2 sm:px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th class="px-2 sm:px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Interest</th>
                  <th class="px-2 sm:px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Principal</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="payment in monthlyReport.payments" :key="payment.id">
                  <td class="whitespace-nowrap px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm text-gray-900">
                    {{ new Date(payment.date).toLocaleDateString() }}
                  </td>
                  <td class="whitespace-nowrap px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm text-gray-900">{{ payment.customerName }}</td>
                  <td class="whitespace-nowrap px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm">
                    <span :class="payment.type === 'Invested' ? 'text-orange-600 font-medium' : 'text-green-600 font-medium'">
                      {{ payment.type }}
                    </span>
                  </td>
                  <td class="whitespace-nowrap px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm font-medium text-green-600">
                    {{ formatCurrency(payment.interestPaid) }}
                  </td>
                  <td class="whitespace-nowrap px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm font-medium" :class="payment.type === 'Invested' ? 'text-orange-600' : 'text-blue-600'">
                    {{ formatCurrency(payment.principalPaid) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          No payments recorded for this month
        </div>
      </div>
    </div>

    <!-- Outstanding Loans Section -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
        <div class="flex items-start justify-between">
          <div>
            <h4 class="text-md font-medium text-gray-900">Outstanding Loans</h4>
            <p class="mt-1 text-sm text-gray-500">All tickets with pending principal amounts</p>
          </div>
          <button
            @click="exportOutstandingLoans"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-orange-600 hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
          >
            <svg class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export to CSV
          </button>
        </div>
      </div>

      <div v-if="outstandingLoans" class="p-6">
        <!-- Summary Cards -->
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 mb-6">
          <div class="bg-orange-50 rounded-lg p-4">
            <dt class="text-sm font-medium text-orange-800">Total Outstanding Amount</dt>
            <dd class="mt-1 text-2xl font-semibold text-orange-900">{{ formatCurrency(outstandingLoans.totalOutstanding) }}</dd>
          </div>
          <div class="bg-blue-50 rounded-lg p-4">
            <dt class="text-sm font-medium text-blue-800">Number of Outstanding Tickets</dt>
            <dd class="mt-1 text-2xl font-semibold text-blue-900">{{ outstandingLoans.ticketCount }}</dd>
          </div>
        </div>

        <!-- Outstanding Loans Table -->
        <div v-if="outstandingLoans.tickets && outstandingLoans.tickets.length > 0">
          <h5 class="text-sm font-medium text-gray-900 mb-3">Outstanding Tickets Details</h5>
          <div class="overflow-x-auto shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
            <table class="min-w-full divide-y divide-gray-300">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-2 sm:px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Bill Number</th>
                  <th class="px-2 sm:px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Customer</th>
                  <th class="px-2 sm:px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Article</th>
                  <th class="px-2 sm:px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Original Principal</th>
                  <th class="px-2 sm:px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pending Principal</th>
                  <th class="px-2 sm:px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Interest Rate</th>
                  <th class="px-2 sm:px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase">Start Date</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="ticket in outstandingLoans.tickets" :key="ticket.id">
                  <td class="whitespace-nowrap px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm font-semibold text-gray-900">{{ ticket.billNumber || '-' }}</td>
                  <td class="whitespace-nowrap px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm text-gray-900">{{ ticket.name }}</td>
                  <td class="whitespace-nowrap px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm text-gray-900">{{ ticket.articleName }}</td>
                  <td class="whitespace-nowrap px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm font-medium text-gray-900">
                    {{ formatCurrency(ticket.principal) }}
                  </td>
                  <td class="whitespace-nowrap px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm font-medium text-orange-600">
                    {{ formatCurrency(ticket.pendingPrincipal) }}
                  </td>
                  <td class="whitespace-nowrap px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm text-gray-900">
                    {{ ticket.interestPercentage }}%
                  </td>
                  <td class="whitespace-nowrap px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm text-gray-900">
                    {{ new Date(ticket.startDate).toLocaleDateString() }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-else class="text-center py-8 text-gray-500">
          No outstanding loans
        </div>
      </div>
    </div>
  </div>
</template>
