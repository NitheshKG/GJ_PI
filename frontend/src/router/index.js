import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import NewTicket from '../views/NewTicket.vue'
import RecordPayment from '../views/RecordPayment.vue'
import PaymentHistory from '../views/PaymentHistory.vue'
import Reports from '../views/Reports.vue'
import Customers from '../views/Customers.vue'
import CustomerDetails from '../views/CustomerDetails.vue'

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: '/',
            name: 'dashboard',
            component: Dashboard
        },
        {
            path: '/tickets/new',
            name: 'new-ticket',
            component: NewTicket
        },
        {
            path: '/tickets/:id/pay',
            name: 'record-payment',
            component: RecordPayment
        },
        {
            path: '/tickets/:id/payments',
            name: 'payment-history',
            component: PaymentHistory
        },
        {
            path: '/reports',
            name: 'reports',
            component: Reports
        },
        {
            path: '/customers',
            name: 'customers',
            component: Customers
        },
        {
            path: '/customers/:id',
            name: 'customer-details',
            component: CustomerDetails
        }
    ]
})

export default router
