<script setup>
import { RouterLink, RouterView } from 'vue-router'
import ToastNotification from './components/ToastNotification.vue'
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
            <div class="hidden sm:ml-6 sm:flex sm:space-x-8">
              <RouterLink to="/" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Dashboard
              </RouterLink>
              <RouterLink to="/customers" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Customers
              </RouterLink>
              <RouterLink to="/reports" class="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium">
                Reports
              </RouterLink>
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
