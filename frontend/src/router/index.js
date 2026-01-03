import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/authStore'
import Dashboard from '../views/Dashboard.vue'
import NewTicket from '../views/NewTicket.vue'
import RecordPayment from '../views/RecordPayment.vue'
import PaymentHistory from '../views/PaymentHistory.vue'
import Reports from '../views/Reports.vue'
import Customers from '../views/Customers.vue'
import CustomerDetails from '../views/CustomerDetails.vue'
import Alerts from '../views/Alerts.vue'
import Login from '../views/Login.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: Login,
            meta: { requiresAuth: false }
        },
        {
            path: '/',
            name: 'dashboard',
            component: Dashboard,
            meta: { requiresAuth: true }
        },
        {
            path: '/tickets/new',
            name: 'new-ticket',
            component: NewTicket,
            meta: { requiresAuth: true }
        },
        {
            path: '/tickets/:id/pay',
            name: 'record-payment',
            component: RecordPayment,
            meta: { requiresAuth: true }
        },
        {
            path: '/tickets/:id/payments',
            name: 'payment-history',
            component: PaymentHistory,
            meta: { requiresAuth: true }
        },
        {
            path: '/reports',
            name: 'reports',
            component: Reports,
            meta: { requiresAuth: true }
        },
        {
            path: '/customers',
            name: 'customers',
            component: Customers,
            meta: { requiresAuth: true }
        },
        {
            path: '/customers/:id',
            name: 'customer-details',
            component: CustomerDetails,
            meta: { requiresAuth: true }
        },
        {
            path: '/alerts',
            name: 'alerts',
            component: Alerts,
            meta: { requiresAuth: true }
        }
    ]
})

// Route guard for authentication
router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()
    const requiresAuth = to.meta.requiresAuth !== false
    
    // Check if we have a stored token
    if (authStore.token && !authStore.user) {
        // Verify token on app load
        const isValid = await authStore.verifyToken()
        if (!isValid) {
            authStore.setToken(null)
        }
    }
    
    if (requiresAuth && !authStore.isAuthenticated) {
        // Redirect to login if trying to access protected route
        next('/login')
    } else if (to.path === '/login' && authStore.isAuthenticated) {
        // Redirect to dashboard if trying to access login while authenticated
        next('/')
    } else {
        next()
    }
})

export default router
