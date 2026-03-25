<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useTicketStore } from '../stores/ticketStore'
import { useNotificationStore } from '../stores/notificationStore'
import axios from 'axios'
import { API_URL } from '../config/api'

const ticketStore = useTicketStore()
const notificationStore = useNotificationStore()
const router = useRouter()
const route = useRoute()

const ticket = ref(null)
const loading = ref(true)

const ticketForm = ref({
  billNumber: '',
  articleName: '',
  itemType: 'Silver',
  grossWeight: '',
  netWeight: '',
  principal: '',
  interestPercentage: '',
  startDate: ''
})

const canEditPrincipal = computed(() => {
  if (!ticket.value) return false
  // Can only edit principal if no payments have been made (except initial interest)
  return ticket.value.interestReceivedMonths <= 1 && ticket.value.totalInterestReceived === 0
})

onMounted(async () => {
  try {
    await ticketStore.fetchTicket(route.params.id)
    ticket.value = ticketStore.currentTicket
    
    // Populate form with current ticket data
    if (ticket.value) {
      ticketForm.value = {
        billNumber: ticket.value.billNumber,
        articleName: ticket.value.articleName,
        itemType: ticket.value.itemType || 'Silver',
        grossWeight: ticket.value.grossWeight || '',
        netWeight: ticket.value.netWeight || '',
        principal: ticket.value.principal,
        interestPercentage: ticket.value.interestPercentage,
        startDate: ticket.value.startDate.split('T')[0] // Format to YYYY-MM-DD
      }
    }
  } catch (error) {
    notificationStore.addNotification('Failed to load ticket', 'error', 3000)
    console.error(error)
  } finally {
    loading.value = false
  }
})

const submitForm = async () => {
  try {
    // If principal is being edited and payments exist, warn user
    if (ticketForm.value.principal !== ticket.value.principal && !canEditPrincipal.value) {
      notificationStore.addNotification('Cannot edit principal after payments have been made', 'error', 3000)
      return
    }

    // Prepare update data
    const updateData = {
      billNumber: ticketForm.value.billNumber,
      articleName: ticketForm.value.articleName,
      itemType: ticketForm.value.itemType,
      grossWeight: parseFloat(ticketForm.value.grossWeight) || 0,
      netWeight: parseFloat(ticketForm.value.netWeight) || 0,
      principal: parseFloat(ticketForm.value.principal),
      interestPercentage: parseFloat(ticketForm.value.interestPercentage),
      startDate: ticketForm.value.startDate
    }

    await axios.put(`${API_URL}/api/tickets/${route.params.id}`, updateData)
    
    notificationStore.addNotification('Ticket updated successfully!', 'success', 3000)
    await ticketStore.fetchTickets()
    router.push('/')
  } catch (error) {
    const errorMessage = error.response?.data?.error || error.message
    notificationStore.addNotification(`Failed to update ticket: ${errorMessage}`, 'error', 3000)
  }
}

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="bg-white shadow sm:rounded-lg max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
    <div v-if="loading" class="px-4 py-5 sm:p-6 text-center">
      <p>Loading ticket details...</p>
    </div>
    
    <div v-else-if="ticket" class="px-4 py-5 sm:p-6">
      <div class="flex items-center justify-between mb-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900">Edit Ticket</h3>
        <button 
          @click="goBack"
          class="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
        >
          Back
        </button>
      </div>

      <div class="mb-4 p-4 bg-blue-50 rounded-md">
        <p class="text-sm text-blue-700">
          <strong>Customer:</strong> {{ ticket.customerName }} ({{ ticket.customerPhone }})
        </p>
      </div>

      <form @submit.prevent="submitForm" class="space-y-6">
        <!-- Ticket Details -->
        <div class="border-t border-gray-200 pt-6">
          <h4 class="text-md font-bold text-gray-900 mb-4">Ticket Details</h4>
          
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
            <div>
              <label for="billNumber" class="block text-sm font-medium text-gray-700">Bill Number *</label>
              <div class="mt-1">
                <input 
                  type="text" 
                  name="billNumber" 
                  id="billNumber" 
                  v-model="ticketForm.billNumber" 
                  required
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                />
              </div>
            </div>

            <div>
              <label for="articleName" class="block text-sm font-medium text-gray-700">Article Name *</label>
              <div class="mt-1">
                <input 
                  type="text" 
                  name="articleName" 
                  id="articleName" 
                  v-model="ticketForm.articleName" 
                  required
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                />
              </div>
            </div>

            <div>
              <label for="itemType" class="block text-sm font-medium text-gray-700">Item Type</label>
              <div class="mt-1">
                <select 
                  name="itemType" 
                  id="itemType" 
                  v-model="ticketForm.itemType"
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                >
                  <option value="Silver">Silver</option>
                  <option value="Gold">Gold</option>
                  <option value="Diamond">Diamond</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>

            <div>
              <label for="grossWeight" class="block text-sm font-medium text-gray-700">Gross Weight</label>
              <div class="mt-1">
                <input 
                  type="number" 
                  name="grossWeight" 
                  id="grossWeight" 
                  v-model="ticketForm.grossWeight" 
                  step="0.01"
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                />
              </div>
            </div>

            <div>
              <label for="netWeight" class="block text-sm font-medium text-gray-700">Net Weight</label>
              <div class="mt-1">
                <input 
                  type="number" 
                  name="netWeight" 
                  id="netWeight" 
                  v-model="ticketForm.netWeight" 
                  step="0.01"
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                />
              </div>
            </div>

            <div>
              <label for="startDate" class="block text-sm font-medium text-gray-700">Start Date *</label>
              <div class="mt-1">
                <input 
                  type="date" 
                  name="startDate" 
                  id="startDate" 
                  v-model="ticketForm.startDate" 
                  required
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Financial Details -->
        <div class="border-t border-gray-200 pt-6">
          <h4 class="text-md font-bold text-gray-900 mb-4">Financial Details</h4>
          
          <div class="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-2">
            <div>
              <label for="principal" class="block text-sm font-medium text-gray-700">
                Principal Amount *
                <span v-if="!canEditPrincipal" class="text-xs text-orange-600">(Read-only: Payments exist)</span>
              </label>
              <div class="mt-1">
                <input 
                  type="number" 
                  name="principal" 
                  id="principal" 
                  v-model="ticketForm.principal" 
                  :disabled="!canEditPrincipal"
                  step="0.01"
                  required
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border disabled:bg-gray-100 disabled:cursor-not-allowed"
                />
              </div>
            </div>

            <div>
              <label for="interestPercentage" class="block text-sm font-medium text-gray-700">Interest Rate (%) *</label>
              <div class="mt-1">
                <input 
                  type="number" 
                  name="interestPercentage" 
                  id="interestPercentage" 
                  v-model="ticketForm.interestPercentage" 
                  step="0.01"
                  required
                  class="shadow-sm focus:ring-indigo-500 focus:border-indigo-500 block w-full sm:text-sm border-gray-300 rounded-md p-2 border"
                />
              </div>
              <p class="mt-1 text-xs text-gray-500">Monthly interest percentage</p>
            </div>
          </div>
        </div>

        <!-- Summary Info -->
        <div class="border-t border-gray-200 pt-6 bg-gray-50 p-4 rounded-md">
          <h4 class="text-sm font-bold text-gray-900 mb-3">Current Status</h4>
          <dl class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt class="text-gray-500">Status</dt>
              <dd class="font-semibold text-gray-900">{{ ticket.status }}</dd>
            </div>
            <div>
              <dt class="text-gray-500">Pending Principal</dt>
              <dd class="font-semibold text-gray-900">₹{{ ticket.pendingPrincipal?.toLocaleString() }}</dd>
            </div>
            <div>
              <dt class="text-gray-500">Total Interest Received</dt>
              <dd class="font-semibold text-green-600">₹{{ ticket.totalInterestReceived?.toLocaleString() || 0 }}</dd>
            </div>
            <div>
              <dt class="text-gray-500">Payments Made</dt>
              <dd class="font-semibold text-gray-900">{{ ticket.interestReceivedMonths }} months</dd>
            </div>
          </dl>
        </div>

        <!-- Form Actions -->
        <div class="border-t border-gray-200 pt-6 flex gap-3">
          <button 
            type="submit" 
            class="inline-flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
          >
            Update Ticket
          </button>
          <button 
            type="button" 
            @click="goBack"
            class="inline-flex justify-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>

    <div v-else class="px-4 py-5 sm:p-6 text-center text-red-600">
      <p>Ticket not found</p>
      <button 
        @click="goBack"
        class="mt-4 inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
      >
        Back to Dashboard
      </button>
    </div>
  </div>
</template>
