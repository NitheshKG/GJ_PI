<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTicketStore } from '../stores/ticketStore'
import { useNotificationStore } from '../stores/notificationStore'
import axios from 'axios'
import { API_URL } from '../config/api'

const ticketStore = useTicketStore()
const notificationStore = useNotificationStore()
const router = useRouter()

const customers = ref([])
const filteredCustomers = ref([])
const customerSearchQuery = ref('')
const showNewCustomerForm = ref(false)
const selectedCustomerId = ref('')
const isDropdownOpen = ref(false)
const dropdownRef = ref(null)

const indianStates = [
  "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", 
  "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", 
  "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", 
  "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", 
  "Uttarakhand", "West Bengal", "Andaman and Nicobar Islands", "Chandigarh", 
  "Dadra and Nagar Haveli and Daman and Diu", "Lakshadweep", "Delhi", "Puducherry", 
  "Ladakh", "Jammu and Kashmir"
]

const customerForm = ref({
  name: '',
  phone: '',
  address: '',
  state: '',
  city: '',
  pincode: '',
  idProofType: 'Aadhar',
  idProofOtherName: '',
  idProofNumber: ''
})

const ticketForm = ref({
  billNumber: '',
  articleName: '',
  itemType: 'Silver',
  grossWeight: '',
  netWeight: '',
  principal: '',
  interestPercentage: '',
  startDate: new Date().toISOString().split('T')[0]
})

onMounted(async () => {
  await fetchCustomers()
  // Add event listener to close dropdown when clicking outside
  document.addEventListener('click', handleClickOutside)
})

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isDropdownOpen.value = false
  }
}

const fetchCustomers = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/customers`)
    customers.value = response.data
    filteredCustomers.value = response.data
  } catch (error) {
    console.error('Failed to fetch customers:', error)
  }
}

const filterCustomers = () => {
  const query = customerSearchQuery.value.toLowerCase().trim()
  if (!query) {
    filteredCustomers.value = customers.value
  } else {
    filteredCustomers.value = customers.value.filter(customer => 
      customer.name.toLowerCase().includes(query) || 
      customer.phone.includes(query)
    )
  }
}

const selectCustomer = (customerId) => {
  selectedCustomerId.value = customerId
  isDropdownOpen.value = false
  customerSearchQuery.value = ''
  filterCustomers()
}

const submitForm = async () => {
  try {
    let customerId = selectedCustomerId.value

    if (!customerId && !showNewCustomerForm.value) {
      notificationStore.addNotification('Please select or create a customer', 'error', 3000)
      return
    }

    // IMPORTANT: If creating a new customer, validate the bill number FIRST
    // This prevents orphan customers when ticket creation fails
    if (showNewCustomerForm.value && ticketForm.value.billNumber) {
      try {
        // Check if bill number already exists by attempting to get tickets with this bill number
        const checkResponse = await axios.get(`${API_URL}/api/tickets`)
        const existingTicket = checkResponse.data.find(t => t.billNumber === ticketForm.value.billNumber)
        if (existingTicket) {
          notificationStore.addNotification('Ticket with this bill number already exists', 'error', 3000)
          return
        }
      } catch (error) {
        console.error('Error checking bill number:', error)
      }
    }

    // Prepare ticket data
    const ticketData = {
      ...ticketForm.value,
      customerId: customerId || 'temp' // Use temp value if creating new customer
    }

    // Create new customer only AFTER validating bill number
    if (showNewCustomerForm.value) {
      try {
        const customerResponse = await axios.post(`${API_URL}/api/customers`, customerForm.value)
        customerId = customerResponse.data.id
        ticketData.customerId = customerId
      } catch (customerError) {
        const errorMessage = customerError.response?.data?.error || customerError.message
        notificationStore.addNotification(`Failed to create customer: ${errorMessage}`, 'error', 3000)
        return // Stop here - don't create ticket if customer creation failed
      }
    }

    // Create ticket
    await axios.post(`${API_URL}/api/tickets`, ticketData)
    router.push('/')
    notificationStore.addNotification('Ticket created successfully!', 'success', 3000)
  } catch (e) {
    const errorMessage = e.response?.data?.error || e.message
    notificationStore.addNotification(`Failed to create ticket: ${errorMessage}`, 'error', 3000)
  }
}
</script>

<template>
  <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header with Gradient -->
    <div class="bg-gradient-to-r from-indigo-600 to-blue-600 rounded-t-2xl px-6 py-6 shadow-lg">
      <h2 class="text-2xl font-bold text-white">Create New Ticket</h2>
      <p class="text-indigo-100 mt-1">Add customer information and ticket details</p>
    </div>

    <div class="bg-white shadow-xl rounded-b-2xl">
      <form @submit.prevent="submitForm" class="p-6 space-y-6">
        <!-- Customer Selection with Card Buttons -->
        <div>
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <svg class="w-6 h-6 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
            </svg>
            Customer Information
          </h3>

          <!-- Card-based Selection Buttons -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
            <!-- Select Existing Customer Button -->
            <button
              type="button"
              @click="showNewCustomerForm = false"
              :class="[
                'relative p-4 rounded-xl border-2 transition-all duration-300 transform hover:scale-105',
                !showNewCustomerForm 
                  ? 'border-indigo-600 bg-gradient-to-br from-indigo-50 to-blue-50 shadow-lg' 
                  : 'border-gray-200 bg-white hover:border-indigo-300 hover:shadow-md'
              ]"
            >
              <div class="flex items-start">
                <div :class="[
                  'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300',
                  !showNewCustomerForm ? 'bg-indigo-600' : 'bg-gray-100'
                ]">
                  <svg class="w-5 h-5" :class="!showNewCustomerForm ? 'text-white' : 'text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                  </svg>
                </div>
                <div class="ml-3 text-left flex-1">
                  <h4 :class="['font-semibold text-base', !showNewCustomerForm ? 'text-indigo-900' : 'text-gray-900']">
                    Select Existing Customer
                  </h4>
                  <p :class="['text-sm mt-1', !showNewCustomerForm ? 'text-indigo-700' : 'text-gray-500']">
                    Choose from your customer database
                  </p>
                </div>
              </div>
            </button>

            <!-- Create New Customer Button -->
            <button
              type="button"
              @click="showNewCustomerForm = true"
              :class="[
                'relative p-4 rounded-xl border-2 transition-all duration-300 transform hover:scale-105',
                showNewCustomerForm 
                  ? 'border-indigo-600 bg-gradient-to-br from-indigo-50 to-blue-50 shadow-lg' 
                  : 'border-gray-200 bg-white hover:border-indigo-300 hover:shadow-md'
              ]"
            >
              <div class="flex items-start">
                <div :class="[
                  'flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300',
                  showNewCustomerForm ? 'bg-indigo-600' : 'bg-gray-100'
                ]">
                  <svg class="w-5 h-5" :class="showNewCustomerForm ? 'text-white' : 'text-gray-500'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
                  </svg>
                </div>
                <div class="ml-3 text-left flex-1">
                  <h4 :class="['font-semibold text-base', showNewCustomerForm ? 'text-indigo-900' : 'text-gray-900']">
                    Create New Customer
                  </h4>
                  <p :class="['text-sm mt-1', showNewCustomerForm ? 'text-indigo-700' : 'text-gray-500']">
                    Add a new customer to the system
                  </p>
                </div>
              </div>
            </button>
          </div>

          <!-- Customer Forms with Smooth Transitions -->
          <div class="mt-4">
            <!-- Existing Customer Selection with Search -->
            <transition name="fade-slide">
              <div v-if="!showNewCustomerForm" class="bg-gray-50 rounded-xl p-4 border border-gray-200">
                <label class="block text-sm font-semibold text-gray-700 mb-2">Select Customer</label>
                <div class="relative" ref="dropdownRef">
                  <div class="flex items-center">
                    <input
                      type="text"
                      v-model="customerSearchQuery"
                      @input="filterCustomers"
                      @focus="isDropdownOpen = true"
                      @click="isDropdownOpen = true"
                      :placeholder="selectedCustomerId ? 'Search customers...' : '-- Choose a customer --'"
                      class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200"
                    >
                    <svg v-if="!isDropdownOpen" class="absolute right-3 w-4 h-4 text-gray-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
                    </svg>
                    <svg v-else class="absolute right-3 w-4 h-4 text-indigo-600 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7 7 7"></path>
                    </svg>
                  </div>
                  
                  <!-- Dropdown Menu -->
                  <div
                    v-if="isDropdownOpen"
                    class="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-64 overflow-y-auto"
                  >
                    <div v-if="filteredCustomers.length === 0" class="p-4 text-center text-gray-500 text-sm">
                      {{ customerSearchQuery ? 'No customers found' : 'No customers available' }}
                    </div>
                    <div v-else class="py-1">
                      <button
                        v-for="customer in filteredCustomers"
                        :key="customer.id"
                        type="button"
                        @click="selectCustomer(customer.id)"
                        class="w-full text-left px-4 py-2 hover:bg-indigo-100 transition-colors duration-150 focus:outline-none focus:bg-indigo-100"
                      >
                        <div class="font-medium text-gray-900">{{ customer.name }}</div>
                        <div class="text-sm text-gray-500">{{ customer.phone }}</div>
                      </button>
                    </div>
                  </div>

                  <!-- Show selected customer -->
                  <div v-if="selectedCustomerId && !isDropdownOpen" class="mt-2 p-2 bg-indigo-50 border border-indigo-200 rounded-lg">
                    <p class="text-sm text-indigo-900 font-medium">
                      Selected: {{ customers.find(c => c.id === selectedCustomerId)?.name }} ({{ customers.find(c => c.id === selectedCustomerId)?.phone }})
                    </p>
                  </div>
                </div>
              </div>
            </transition>

            <!-- New Customer Form -->
            <transition name="fade-slide">
              <div v-if="showNewCustomerForm" class="bg-gradient-to-br from-gray-50 to-indigo-50 rounded-xl p-4 border border-indigo-200">
                <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-1">
                      Name <span class="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      v-model="customerForm.name"
                      required
                      placeholder="Enter full name"
                      class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-1">
                      Phone <span class="text-red-500">*</span>
                    </label>
                    <input
                      type="tel"
                      v-model="customerForm.phone"
                      required
                      placeholder="Enter phone number"
                      class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200"
                    >
                  </div>
                  <div class="sm:col-span-2">
                    <label class="block text-sm font-semibold text-gray-700 mb-1">
                      Address <span class="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      v-model="customerForm.address"
                      required
                      placeholder="Enter address"
                      class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-1">
                      State <span class="text-red-500">*</span>
                    </label>
                    <select
                      v-model="customerForm.state"
                      required
                      class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200"
                    >
                      <option value="">Select State</option>
                      <option v-for="state in indianStates" :key="state" :value="state">{{ state }}</option>
                    </select>
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-1">
                      City <span class="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      v-model="customerForm.city"
                      required
                      placeholder="Enter city"
                      class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-1">
                      Pincode <span class="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      v-model="customerForm.pincode"
                      required
                      pattern="[0-9]{6}"
                      placeholder="Enter 6-digit pincode"
                      class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-1">
                      ID Proof Type <span class="text-red-500">*</span>
                    </label>
                    <select
                      v-model="customerForm.idProofType"
                      required
                      class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200"
                    >
                      <option>Aadhar</option>
                      <option>Licence</option>
                      <option>Others</option>
                    </select>
                  </div>
                  <div v-if="customerForm.idProofType === 'Others'">
                    <label class="block text-sm font-semibold text-gray-700 mb-1">
                      Other Proof Name <span class="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      v-model="customerForm.idProofOtherName"
                      required
                      placeholder="Specify proof type"
                      class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200"
                    >
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-1">
                      ID Proof Number <span class="text-red-500">*</span>
                    </label>
                    <input
                      type="text"
                      v-model="customerForm.idProofNumber"
                      required
                      placeholder="Enter ID number"
                      class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200"
                    >
                  </div>
                </div>
              </div>
            </transition>
          </div>
        </div>

        <!-- Ticket Details Section -->
        <div class="border-t border-gray-200 pt-6">
          <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <svg class="w-6 h-6 mr-2 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            Ticket Details
          </h3>

          <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div class="lg:col-span-3">
              <label class="block text-sm font-semibold text-gray-700 mb-2">Item Type</label>
              <div class="flex items-center space-x-6 bg-gray-50 p-3 rounded-lg border border-gray-200 w-fit">
                <label class="inline-flex items-center cursor-pointer">
                  <input type="radio" v-model="ticketForm.itemType" value="Silver" class="form-radio h-5 w-5 text-indigo-600 focus:ring-indigo-500 border-gray-300 transition duration-150 ease-in-out">
                  <span class="ml-2 text-gray-700 font-medium">Silver</span>
                </label>
                <label class="inline-flex items-center cursor-pointer">
                  <input type="radio" v-model="ticketForm.itemType" value="Gold" class="form-radio h-5 w-5 text-yellow-500 focus:ring-yellow-500 border-gray-300 transition duration-150 ease-in-out">
                  <span class="ml-2 text-gray-900 font-medium">Gold</span>
                </label>
              </div>
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Bill Number <span class="text-red-500">*</span>
              </label>
              <input
                type="number"
                v-model="ticketForm.billNumber"
                required
                placeholder="Enter bill number"
                class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              >
            </div>
            <div class="lg:col-span-2">
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Article Name <span class="text-red-500">*</span>
              </label>
              <input
                type="text"
                v-model="ticketForm.articleName"
                required
                placeholder="e.g., Gold Chain, Diamond Ring"
                class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200"
              >
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Start Date <span class="text-red-500">*</span></label>
              <input
                type="date"
                v-model="ticketForm.startDate"
                required
                class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200"
              >
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Gross Weight (gms)</label>
              <input
                type="number"
                v-model="ticketForm.grossWeight"
                step="0.001"
                placeholder="0.000"
                class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              >
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">Net Weight (gms)</label>
              <input
                type="number"
                v-model="ticketForm.netWeight"
                step="0.001"
                placeholder="0.000"
                class="block w-full rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
              >
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Principal Amount <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <span class="absolute left-3 top-2.5 text-gray-500">₹</span>
                <input
                  type="number"
                  v-model="ticketForm.principal"
                  required
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  class="block w-full pl-8 rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                >
              </div>
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-1">
                Interest Rate <span class="text-red-500">*</span>
              </label>
              <div class="relative">
                <input
                  type="number"
                  v-model="ticketForm.interestPercentage"
                  required
                  min="0"
                  step="0.01"
                  placeholder="0.00"
                  class="block w-full pr-8 rounded-lg border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500 sm:text-sm p-2 border transition-all duration-200 [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                >
                <span class="absolute right-3 top-2.5 text-gray-500">%</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end space-x-4 pt-4 border-t border-gray-200">
          <router-link
            to="/"
            class="px-4 py-2 border-2 border-gray-300 rounded-lg text-sm font-semibold text-gray-700 hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 transform hover:scale-105"
          >
            Cancel
          </router-link>
          <button
            type="submit"
            class="px-6 py-2 bg-gradient-to-r from-indigo-600 to-blue-600 rounded-lg text-sm font-semibold text-white shadow-lg hover:from-indigo-700 hover:to-blue-700 transition-all duration-200 transform hover:scale-105 hover:shadow-xl"
          >
            Create Ticket
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
