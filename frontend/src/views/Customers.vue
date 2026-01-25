<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { API_URL } from '../config/api'

const router = useRouter()
const customers = ref([])
const loading = ref(false)
const searchQuery = ref('')

onMounted(async () => {
  await fetchCustomers()
})

const fetchCustomers = async () => {
  loading.value = true
  try {
    const response = await axios.get(`${API_URL}/api/customers`)
    customers.value = response.data
  } catch (error) {
    console.error('Failed to fetch customers:', error)
  }
  loading.value = false
}

const filteredCustomers = computed(() => {
  if (!searchQuery.value) {
    return customers.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return customers.value.filter(customer => 
    customer.name.toLowerCase().includes(query) ||
    customer.phone.toLowerCase().includes(query)
  )
})

const viewCustomer = (customerId) => {
  router.push(`/customers/${customerId}`)
}

const goToNewTicket = () => {
  router.push('/tickets/new')
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6 flex flex-col sm:flex-row justify-between items-start sm:items-center">
        <div class="mb-4 sm:mb-0">
          <h3 class="text-lg leading-6 font-medium text-gray-900">Customers</h3>
          <p class="mt-1 max-w-2xl text-sm text-gray-500">Manage all customer records</p>
        </div>
      </div>
    </div>

    <!-- Search Bar -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-4 sm:px-6">
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search customers by name or phone..."
            class="block w-full pl-10 pr-3 py-2 sm:py-3 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm transition-all duration-200"
          >
        </div>
        <p v-if="searchQuery" class="mt-2 text-sm text-gray-500">
          Found {{ filteredCustomers.length }} customer{{ filteredCustomers.length !== 1 ? 's' : '' }}
        </p>
      </div>
    </div>

    <!-- Customers List -->
    <div class="bg-white shadow sm:rounded-lg">
      <div v-if="loading" class="p-4 text-center text-gray-500">
        Loading customers...
      </div>
      <div v-else-if="customers.length === 0" class="p-8 text-center text-gray-500">
        <p>No customers found</p>
      </div>
      <div v-else>
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Phone</th>
                <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Active Tickets</th>
                <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total Tickets</th>
                <th class="px-4 sm:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Outstanding</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="customer in filteredCustomers" :key="customer.id" class="hover:bg-gray-50">
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm font-medium">
                  <router-link 
                    :to="`/customers/${customer.id}`"
                    class="text-indigo-600 hover:text-indigo-900 hover:underline font-semibold"
                  >
                    {{ customer.name }}
                  </router-link>
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ customer.phone }}
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ customer.activeTickets || 0 }}
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ customer.totalTickets || 0 }}
                </td>
                <td class="px-4 sm:px-6 py-4 whitespace-nowrap text-sm font-semibold text-orange-600">
                  ₹{{ customer.totalOutstanding?.toLocaleString() || 0 }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>
