<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <!-- Header with Gradient -->
    <div class="bg-gradient-to-r from-red-600 to-orange-600 rounded-t-2xl px-6 py-6 shadow-lg">
      <h2 class="text-2xl font-bold text-white">Alerts</h2>
      <p class="text-red-100 mt-1">Customers with 12+ months pending interests</p>
    </div>

    <div class="bg-white shadow-xl rounded-b-2xl p-6">
      <!-- Setup Status Banner -->
      <div v-if="!servicesConfigured" class="mb-6 bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-start gap-3">
        <svg class="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a.75.75 0 000 1.5h.253a.25.25 0 01.244.304l-.459 2.066A1.75 1.75 0 0010.747 15H11a.75.75 0 000-1.5h-.253a.25.25 0 01-.244-.304l.459-2.066A1.75 1.75 0 009.253 9H9z" clip-rule="evenodd" />
        </svg>
        <div class="flex-1">
          <h3 class="text-sm font-medium text-blue-900">Message Services Not Configured</h3>
          <p class="text-sm text-blue-700 mt-1">To send actual messages, you need to configure at least one free service (Fast2SMS, Twilio WhatsApp, or Email).</p>
          <p class="text-sm text-blue-700 mt-2">
            <a href="https://www.fast2sms.com/" target="_blank" class="underline font-medium hover:text-blue-900">Fast2SMS (Free SMS)</a> • 
            <a href="https://www.twilio.com/console/sms/whatsapp/learn" target="_blank" class="underline font-medium hover:text-blue-900">Twilio WhatsApp (Free)</a> • 
            <a href="/FREE_ALERTS_SETUP.md" class="underline font-medium hover:text-blue-900">Setup Guide</a>
          </p>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-gradient-to-br from-red-50 to-orange-50 rounded-lg p-4 border border-red-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-red-600">Overdue Customers</p>
              <p class="text-3xl font-bold text-red-900 mt-1">{{ alertCount }}</p>
            </div>
            <svg class="w-12 h-12 text-red-300" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M13.477 14.89A6 6 0 0 1 5.11 6.623a6 6 0 0 1 8.367 8.267ZM9 13a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>

        <div class="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-4 border border-blue-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-blue-600">Total Pending Tickets</p>
              <p class="text-3xl font-bold text-blue-900 mt-1">{{ totalPendingTickets }}</p>
            </div>
            <svg class="w-12 h-12 text-blue-300" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M5 2a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v12a1 1 0 1 1 0 2h-2.5a1 1 0 0 0-1 1v2a1 1 0 1 1-2 0v-2a1 1 0 0 0-1-1H5a1 1 0 1 1 0-2V2Z" clip-rule="evenodd" />
            </svg>
          </div>
        </div>

        <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-4 border border-green-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm font-medium text-green-600">Messages Sent</p>
              <p class="text-3xl font-bold text-green-900 mt-1">{{ messagesSentCount }}</p>
            </div>
            <svg class="w-12 h-12 text-green-300" fill="currentColor" viewBox="0 0 20 20">
              <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0 0 16 4H4a2 2 0 0 0-1.997 1.884Z" />
              <path d="m18 8.118-8 4-8-4V14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8.118Z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <div class="border-b border-gray-200 mb-6 flex items-center justify-between">
        <div class="flex space-x-8">
          <button
            @click="switchTab('customers')"
            :class="[
              'px-4 py-2 font-medium border-b-2 transition-colors duration-200',
              activeTab === 'customers'
                ? 'text-red-600 border-red-600'
                : 'text-gray-600 border-transparent hover:text-gray-900 hover:border-gray-300'
            ]"
          >
            Overdue Customers ({{ alertCount }})
          </button>
          <button
            @click="switchTab('history')"
            :class="[
              'px-4 py-2 font-medium border-b-2 transition-colors duration-200',
              activeTab === 'history'
                ? 'text-red-600 border-red-600'
                : 'text-gray-600 border-transparent hover:text-gray-900 hover:border-gray-300'
            ]"
          >
            Message History
          </button>
        </div>
        <button
          @click="refreshData"
          :disabled="loading || loadingHistory"
          class="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg class="w-4 h-4" :class="{ 'animate-spin': loading || loadingHistory }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>

      <!-- Customers Tab -->
      <div v-if="activeTab === 'customers'">
        <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
          <p class="text-gray-600 mt-4">Loading alert data...</p>
        </div>

        <div v-else-if="alertCustomers.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900">No overdue customers</h3>
          <p class="text-gray-600 mt-2">All customers are current with their interest payments!</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="customer in alertCustomers"
            :key="customer.customerId"
            class="border border-red-200 rounded-lg overflow-hidden hover:shadow-lg transition-shadow duration-200"
          >
            <div class="bg-gradient-to-r from-red-50 to-orange-50 px-6 py-4 border-b border-red-200">
              <div class="flex items-start justify-between">
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-gray-900">{{ customer.customerName }}</h3>
                  <p class="text-sm text-gray-600 mt-1">
                    <span class="inline-block mr-4">
                      <svg class="inline-block w-4 h-4 text-gray-400 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.637.756a6.001 6.001 0 007.753 7.753l.756-1.637a1 1 0 011.06-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2.2A13.995 13.995 0 012 3Z" />
                      </svg>
                      {{ customer.customerPhone }}
                    </span>
                  </p>
                </div>
                <div class="text-right">
                  <span class="inline-block px-3 py-1 bg-red-100 text-red-800 text-sm font-medium rounded-full">
                    {{ customer.ticketCount }} {{ customer.ticketCount === 1 ? 'ticket' : 'tickets' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Tickets List -->
            <div class="px-6 py-4 space-y-3">
              <div v-for="ticket in customer.tickets" :key="ticket.id" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                <div class="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p class="text-gray-600">Article</p>
                    <p class="font-medium text-gray-900">{{ ticket.articleName }}</p>
                  </div>
                  <div>
                    <p class="text-gray-600">Pending Interest</p>
                    <p class="font-medium text-red-600">{{ ticket.monthsPending }} months</p>
                  </div>
                  <div>
                    <p class="text-gray-600">Principal</p>
                    <p class="font-medium text-gray-900">₹{{ parseFloat(ticket.principal).toFixed(2) }}</p>
                  </div>
                  <div>
                    <p class="text-gray-600">Pending Principal</p>
                    <p class="font-medium text-gray-900">₹{{ parseFloat(ticket.pendingPrincipal).toFixed(2) }}</p>
                  </div>
                  <div>
                    <p class="text-gray-600">Interest Rate</p>
                    <p class="font-medium text-gray-900">{{ ticket.interestPercentage }}%</p>
                  </div>
                  <div>
                    <p class="text-gray-600">Start Date</p>
                    <p class="font-medium text-gray-900">{{ formatDate(ticket.startDate) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <p class="text-sm text-gray-600">Send reminder to customer</p>
              <div class="flex gap-2">
                <button
                  @click="openMessageDialog(customer)"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200 flex items-center gap-2 text-sm font-medium"
                >
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0 0 16 4H4a2 2 0 0 0-1.997 1.884Z" />
                    <path d="m18 8.118-8 4-8-4V14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8.118Z" />
                  </svg>
                  Send Message
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Message History Tab -->
      <div v-if="activeTab === 'history'">
        <div v-if="loadingHistory" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
          <p class="text-gray-600 mt-4">Loading message history...</p>
        </div>

        <div v-else-if="messageHistory.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h3 class="mt-4 text-lg font-medium text-gray-900">No messages sent yet</h3>
          <p class="text-gray-600 mt-2">Messages sent to customers will appear here</p>
        </div>

        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="bg-gray-50 border-b border-gray-200">
              <tr>
                <th class="px-6 py-3 text-left font-semibold text-gray-900">Customer</th>
                <th class="px-6 py-3 text-left font-semibold text-gray-900">Phone</th>
                <th class="px-6 py-3 text-left font-semibold text-gray-900">Method</th>
                <th class="px-6 py-3 text-left font-semibold text-gray-900">Message</th>
                <th class="px-6 py-3 text-left font-semibold text-gray-900">Sent At</th>
                <th class="px-6 py-3 text-left font-semibold text-gray-900">Status</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200">
              <tr v-for="msg in messageHistory" :key="msg.id" class="hover:bg-gray-50 transition-colors duration-200">
                <td class="px-6 py-4 font-medium text-gray-900">{{ msg.customerName }}</td>
                <td class="px-6 py-4 text-gray-600">{{ msg.phoneNumber }}</td>
                <td class="px-6 py-4">
                  <span class="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded">
                    {{ msg.method.toUpperCase() }}
                  </span>
                </td>
                <td class="px-6 py-4 text-gray-600">
                  <p class="truncate max-w-xs">{{ msg.message }}</p>
                </td>
                <td class="px-6 py-4 text-gray-600">{{ formatDateTime(msg.timestamp) }}</td>
                <td class="px-6 py-4">
                  <span class="inline-block px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded">
                    {{ msg.status.charAt(0).toUpperCase() + msg.status.slice(1) }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Message Dialog -->
    <div
      v-if="showMessageDialog"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click="showMessageDialog = false"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4" @click.stop>
        <div class="bg-gradient-to-r from-red-600 to-orange-600 px-6 py-4">
          <h3 class="text-lg font-bold text-white">Send Alert Message</h3>
          <p class="text-red-100 text-sm mt-1">to {{ selectedCustomer?.customerName }}</p>
        </div>

        <div class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Message Type</label>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  type="radio"
                  v-model="messageType"
                  value="default"
                  class="h-4 w-4 text-red-600"
                >
                <span class="ml-2 text-gray-700">Use default message</span>
              </label>
              <label class="flex items-center">
                <input
                  type="radio"
                  v-model="messageType"
                  value="custom"
                  class="h-4 w-4 text-red-600"
                >
                <span class="ml-2 text-gray-700">Write custom message</span>
              </label>
            </div>
          </div>

          <div v-if="messageType === 'default'" class="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <p class="text-sm text-gray-700">
              Dear {{ selectedCustomer?.customerName }}, this is a reminder that you have pending interest payments for 12+ months. Please arrange to pay at your earliest convenience. Contact us for more details.
            </p>
          </div>

          <div v-else>
            <label class="block text-sm font-medium text-gray-700 mb-2">Custom Message</label>
            <textarea
              v-model="customMessage"
              rows="4"
              placeholder="Enter your message..."
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            ></textarea>
            <p class="text-xs text-gray-500 mt-1">{{ customMessage.length }}/160 characters</p>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Send Via</label>
            <select v-model="sendMethod" class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent">
              <option value="sms">SMS</option>
              <option value="whatsapp">WhatsApp</option>
            </select>
          </div>
        </div>

        <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex justify-end gap-3">
          <button
            @click="showMessageDialog = false"
            class="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors duration-200"
          >
            Cancel
          </button>
          <button
            @click="sendMessage"
            :disabled="sendingMessage"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center gap-2"
          >
            <svg v-if="sendingMessage" class="animate-spin h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ sendingMessage ? 'Sending...' : 'Send Message' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useNotificationStore } from '../stores/notificationStore'
import { API_URL } from '../config/api'

const notificationStore = useNotificationStore()

const activeTab = ref('customers')
const loading = ref(true)
const loadingHistory = ref(false)
const alertCustomers = ref([])
const messageHistory = ref([])
const showMessageDialog = ref(false)
const selectedCustomer = ref(null)
const messageType = ref('default')
const customMessage = ref('')
const sendMethod = ref('sms')
const sendingMessage = ref(false)
const setupStatus = ref({})

const alertCount = computed(() => alertCustomers.value.length)
const totalPendingTickets = computed(() => {
  return alertCustomers.value.reduce((sum, customer) => sum + customer.tickets.length, 0)
})
const messagesSentCount = computed(() => messageHistory.value.length)
const servicesConfigured = computed(() => {
  const services = setupStatus.value.services || {}
  return services.sms?.configured || services.whatsapp?.configured || services.email?.configured
})

const fetchSetupStatus = async () => {
  try {
    const response = await axios.get(`${API_URL}/api/alerts/setup-status`)
    setupStatus.value = response.data
  } catch (error) {
    console.error('Failed to fetch setup status:', error)
  }
}

const fetchAlerts = async () => {
  try {
    loading.value = true
    const response = await axios.get(`${API_URL}/api/alerts/overdue-interests`)
    alertCustomers.value = response.data.customers || []
  } catch (error) {
    console.error('Failed to fetch alerts:', error)
    notificationStore.addNotification('Failed to load alert data', 'error', 3000)
  } finally {
    loading.value = false
  }
}

const fetchMessageHistory = async () => {
  try {
    loadingHistory.value = true
    const response = await axios.get(`${API_URL}/api/alerts/message-history`)
    messageHistory.value = response.data.messages || []
  } catch (error) {
    console.error('Failed to fetch message history:', error)
    notificationStore.addNotification('Failed to load message history', 'error', 3000)
  } finally {
    loadingHistory.value = false
  }
}

const openMessageDialog = (customer) => {
  selectedCustomer.value = customer
  messageType.value = 'default'
  customMessage.value = ''
  sendMethod.value = 'sms'
  showMessageDialog.value = true
}

const switchTab = async (tab) => {
  activeTab.value = tab
  if (tab === 'customers') {
    await fetchAlerts()
  } else if (tab === 'history') {
    await fetchMessageHistory()
  }
}

const refreshData = async () => {
  if (activeTab.value === 'customers') {
    await fetchAlerts()
  } else if (activeTab.value === 'history') {
    await fetchMessageHistory()
  }
}

const sendMessage = async () => {
  if (!selectedCustomer.value) return

  const message = messageType.value === 'default'
    ? `Dear ${selectedCustomer.value.customerName}, this is a reminder that you have pending interest payments for 12+ months. Please arrange to pay at your earliest convenience. Contact us for more details.`
    : customMessage.value

  if (!message.trim()) {
    notificationStore.addNotification('Message cannot be empty', 'error', 3000)
    return
  }

  try {
    sendingMessage.value = true
    const response = await axios.post(`${API_URL}/api/alerts/send-message/${selectedCustomer.value.customerId}`, {
      message,
      method: sendMethod.value
    })

    notificationStore.addNotification('Message sent successfully!', 'success', 3000)
    showMessageDialog.value = false
    await Promise.all([
      fetchAlerts(),
      fetchMessageHistory()
    ])
  } catch (error) {
    console.error('Failed to send message:', error)
    notificationStore.addNotification('Failed to send message', 'error', 3000)
  } finally {
    sendingMessage.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric' })
  } catch {
    return dateString
  }
}

const formatDateTime = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-IN', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
  } catch {
    return dateString
  }
}

onMounted(async () => {
  await Promise.all([
    fetchAlerts(),
    fetchMessageHistory(),
    fetchSetupStatus()
  ])
})
</script>

<style scoped>
/* Add any additional styles here */
</style>
