<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import ToastNotification from './components/ToastNotification.vue'
import { useAuthStore } from './stores/authStore'
import { ref } from 'vue'

const router = useRouter()
const authStore = useAuthStore()
const showUserMenu = ref(false)

const handleLogout = async () => {
  await authStore.logout()
  showUserMenu.value = false
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen bg-gray-100">
    <nav class="bg-white shadow-sm">
      <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <h1 class="text-xl font-bold text-gray-800">Gunaa Jewells</h1>
            </div>
            <div v-if="authStore.isAuthenticated" class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <RouterLink to="/" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Dashboard
              </RouterLink>
              <RouterLink to="/customers" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Customers
              </RouterLink>
              <RouterLink to="/alerts" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Alerts
              </RouterLink>
              <RouterLink to="/reports" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Reports
              </RouterLink>
            </div>
          </div>
          
          <!-- User Menu -->
          <div v-if="authStore.isAuthenticated" class="flex items-center">
            <div class="relative">
              <button
                @click="showUserMenu = !showUserMenu"
                class="flex items-center text-gray-500 hover:text-gray-700 focus:outline-none"
              >
                <div class="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-medium">
                  {{ authStore.user?.name?.charAt(0).toUpperCase() || 'U' }}
                </div>
              </button>
              
              <!-- Dropdown Menu -->
              <div
                v-if="showUserMenu"
                @click.outside="showUserMenu = false"
                class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg z-50"
              >
                <div class="px-4 py-3 border-b border-gray-200">
                  <p class="text-sm font-medium text-gray-900">{{ authStore.user?.name }}</p>
                  <p class="text-xs text-gray-500">{{ authStore.user?.email }}</p>
                </div>
                <button
                  @click="handleLogout"
                  class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <main class="py-10">
      <div class="max-w-full mx-auto px-4 sm:px-6 lg:px-8">
        <RouterView />
      </div>
    </main>
    
    <!-- Toast Notifications -->
    <ToastNotification />
  </div>
</template>
