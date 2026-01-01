import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = 'http://localhost:5000/api'

export const useTicketStore = defineStore('ticket', {
    state: () => ({
        tickets: [],
        currentTicket: null,
        loading: false,
        error: null
    }),
    actions: {
        async fetchTickets() {
            this.loading = true
            try {
                const response = await axios.get(`${API_URL}/tickets`)
                this.tickets = response.data
            } catch (err) {
                this.error = err.message
            } finally {
                this.loading = false
            }
        },
        async createTicket(ticketData) {
            this.loading = true
            try {
                await axios.post(`${API_URL}/tickets`, ticketData)
                await this.fetchTickets()
            } catch (err) {
                this.error = err.message
                throw err
            } finally {
                this.loading = false
            }
        },
        async fetchTicket(id) {
            this.loading = true
            try {
                const response = await axios.get(`${API_URL}/tickets/${id}`)
                this.currentTicket = response.data
            } catch (err) {
                this.error = err.message
            } finally {
                this.loading = false
            }
        },
        async addPayment(ticketId, paymentData) {
            this.loading = true
            try {
                await axios.post(`${API_URL}/tickets/${ticketId}/payments`, paymentData)
                await this.fetchTicket(ticketId) // Refresh ticket data
            } catch (err) {
                this.error = err.message
                throw err
            } finally {
                this.loading = false
            }
        }
    }
})
