<script setup>
import { useNotificationStore } from '../stores/notificationStore'

const notificationStore = useNotificationStore()

const getTypeClass = (type) => {
  const classes = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    warning: 'bg-yellow-500',
    info: 'bg-blue-500'
  }
  return classes[type] || classes.info
}
</script>

<template>
  <div class="fixed top-4 right-4 z-50 space-y-2">
    <transition-group name="slide-fade">
      <div
        v-for="notification in notificationStore.notifications"
        :key="notification.id"
        :class="[
          'px-6 py-4 rounded-lg shadow-lg text-white flex items-center space-x-3 min-w-[300px] max-w-md',
          getTypeClass(notification.type)
        ]"
      >
        <div class="flex-1">
          {{ notification.message }}
        </div>
        <button
          @click="notificationStore.removeNotification(notification.id)"
          class="text-white hover:text-gray-200 focus:outline-none"
        >
          <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </transition-group>
  </div>
</template>

<style scoped>
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.3s ease-in;
}

.slide-fade-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}
</style>
