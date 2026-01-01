<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const customer = ref(null)
const tickets = ref([])
const loading = ref(false)
const showEditModal = ref(false)
const editForm = ref({
  name: '',
  phone: '',
  address: '',
  state: '',
  city: '',
  pincode: '',
  idProofType: '',
  idProofOtherName: '',
  idProofNumber: ''
})

const indianStates = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", 
  "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", 
  "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", 
  "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", 
  "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", 
  "Dadra and Nagar Haveli and Daman and Diu", "Lakshadweep", "Delhi", "Puducherry", 
  "Ladakh", "Jammu and Kashmir"
]

onMounted(async () => {
  await fetchCustomer()
  await fetchTickets()
})

const fetchCustomer = async () => {
  loading.value = true
  try {
    const response = await axios.get(`http://localhost:5000/api/customers/${route.params.id}`)
    customer.value = response.data
  } catch (error) {
    console.error('Failed to fetch customer:', error)
  }
  loading.value = false
}

const fetchTickets = async () => {
  try {
    const response = await axios.get(`http://localhost:5000/api/customers/${route.params.id}/tickets`)
    tickets.value = response.data
  } catch (error) {
    console.error('Failed to fetch tickets:', error)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString()
}

const recordPayment = (ticketId) => {
  router.push(`/tickets/${ticketId}/pay`)
}

const viewPayments = (ticketId) => {
  router.push(`/tickets/${ticketId}/payments`)
}

const openEditModal = () => {
  editForm.value = { ...customer.value }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
}

const updateCustomer = async () => {
  try {
    await axios.put(`http://localhost:5000/api/customers/${route.params.id}`, editForm.value)
    showEditModal.value = false
    await fetchCustomer() // Refresh details
    // Ideally we should also add a notification here but we don't have the store imported
  } catch (error) {
    console.error('Failed to update customer:', error)
    alert('Failed to update customer. Please try again.')
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Header -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg leading-6 font-medium text-gray-900">Customer Details</h3>
          </div>
          <router-link
            to="/customers"
            class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Back to Customers
          </router-link>
        </div>
      </div>
    </div>

    <!-- Customer Information -->
    <div v-if="customer" class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="flex items-center justify-between mb-4">
          <h4 class="text-md font-medium text-gray-900">Personal Information</h4>
          <button @click="openEditModal" class="text-gray-400 hover:text-indigo-600 transition-colors duration-200">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
            </svg>
          </button>
        </div>
        <dl class="grid grid-cols-1 gap-x-4 gap-y-4 sm:grid-cols-2 md:grid-cols-3">
          <div>
            <dt class="text-sm font-medium text-gray-500">Name</dt>
            <dd class="mt-1 text-sm font-bold text-gray-900">{{ customer.name }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Phone</dt>
            <dd class="mt-1 text-sm text-gray-900">{{ customer.phone }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Address</dt>
            <dd class="mt-1 text-sm text-gray-900">{{ customer.address || '-' }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">City</dt>
            <dd class="mt-1 text-sm text-gray-900">{{ customer.city || '-' }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">State</dt>
            <dd class="mt-1 text-sm text-gray-900">{{ customer.state || '-' }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">Pincode</dt>
            <dd class="mt-1 text-sm text-gray-900">{{ customer.pincode || '-' }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">ID Proof Type</dt>
            <dd class="mt-1 text-sm text-gray-900">{{ customer.idProofType || '-' }}</dd>
          </div>
          <div v-if="customer.idProofType === 'Others'">
            <dt class="text-sm font-medium text-gray-500">Other ID Proof Name</dt>
            <dd class="mt-1 text-sm text-gray-900">{{ customer.idProofOtherName || '-' }}</dd>
          </div>
          <div>
            <dt class="text-sm font-medium text-gray-500">ID Proof Number</dt>
            <dd class="mt-1 text-sm text-gray-900">{{ customer.idProofNumber || '-' }}</dd>
          </div>
        </dl>
      </div>
    </div>

    <!-- Customer Tickets -->
    <div class="bg-white shadow sm:rounded-lg">
      <div class="px-4 py-5 sm:px-6 border-b border-gray-200">
        <h4 class="text-md font-medium text-gray-900">Tickets</h4>
        <p class="mt-1 text-sm text-gray-500">All tickets for this customer</p>
      </div>
      <div v-if="tickets.length === 0" class="p-8 text-center text-gray-500">
        <p>No tickets found for this customer</p>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Article</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Principal</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pending</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Interest %</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Start Date</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="ticket in tickets" :key="ticket.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                {{ ticket.articleName }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <span :class="ticket.itemType === 'Gold' ? 'text-yellow-600 font-bold' : 'text-gray-600'">
                  {{ ticket.itemType || 'Silver' }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                ₹{{ ticket.principal?.toLocaleString() }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                ₹{{ ticket.pendingPrincipal?.toLocaleString() }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ ticket.interestPercentage }}%
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDate(ticket.startDate) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                  ticket.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                ]">
                  {{ ticket.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-3">
                <button
                  @click="recordPayment(ticket.id)"
                  class="text-green-600 hover:text-green-900 font-semibold"
                >
                  Record Payment
                </button>
                <span class="text-gray-300">|</span>
                <button
                  @click="viewPayments(ticket.id)"
                  class="text-blue-600 hover:text-blue-900"
                >
                  View Payments
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <!-- Edit Customer Modal -->
    <div v-if="showEditModal" class="fixed z-10 inset-0 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="closeEditModal"></div>

        <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

        <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4" id="modal-title">
              Edit Customer Details
            </h3>
            <form @submit.prevent="updateCustomer" class="space-y-4">
              <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Name</label>
                  <input type="text" v-model="editForm.name" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Phone</label>
                  <input type="tel" v-model="editForm.phone" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                </div>
                <div class="sm:col-span-2">
                  <label class="block text-sm font-medium text-gray-700">Address</label>
                  <input type="text" v-model="editForm.address" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">State</label>
                  <select v-model="editForm.state" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                    <option v-for="state in indianStates" :key="state" :value="state">{{ state }}</option>
                  </select>
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">City</label>
                  <input type="text" v-model="editForm.city" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">Pincode</label>
                  <input type="text" v-model="editForm.pincode" required pattern="[0-9]{6}" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">ID Proof Type</label>
                  <select v-model="editForm.idProofType" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                    <option>Aadhar</option>
                    <option>Licence</option>
                    <option>Others</option>
                  </select>
                </div>
                <div v-if="editForm.idProofType === 'Others'">
                  <label class="block text-sm font-medium text-gray-700">Other Proof Name</label>
                  <input type="text" v-model="editForm.idProofOtherName" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                </div>
                <div>
                  <label class="block text-sm font-medium text-gray-700">ID Proof Number</label>
                  <input type="text" v-model="editForm.idProofNumber" required class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                </div>
              </div>
              <div class="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
                <button type="submit" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:col-start-2 sm:text-sm">
                  Save Changes
                </button>
                <button type="button" @click="closeEditModal" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:col-start-1 sm:text-sm">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
