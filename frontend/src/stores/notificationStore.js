import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
    const notifications = ref([])
    let notificationId = 0

    const addNotification = (message, type = 'success', duration = 3000) => {
        const id = notificationId++
        notifications.value.push({ id, message, type })

        // Auto-remove after duration
        setTimeout(() => {
            removeNotification(id)
        }, duration)

        return id
    }

    const removeNotification = (id) => {
        const index = notifications.value.findIndex(n => n.id === id)
        if (index > -1) {
            notifications.value.splice(index, 1)
        }
    }

    return {
        notifications,
        addNotification,
        removeNotification
    }
})
