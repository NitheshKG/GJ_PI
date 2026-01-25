import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { API_URL } from '../config/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('authToken') || null)
  const loading = ref(false)
  const error = ref(null)

  const isAuthenticated = computed(() => !!token.value)

  const setToken = (newToken) => {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('authToken', newToken)
    } else {
      localStorage.removeItem('authToken')
    }
  }

  const login = async (username, password) => {
    loading.value = true
    error.value = null
    try {
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        username,
        password
      })
      
      setToken(response.data.token)
      user.value = response.data.user
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Login failed'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    loading.value = true
    try {
      if (token.value) {
        await axios.post(`${API_URL}/api/auth/logout`, {
          token: token.value
        })
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      setToken(null)
      user.value = null
      loading.value = false
    }
  }

  const verifyToken = async () => {
    if (!token.value) return false
    
    try {
      const response = await axios.post(`${API_URL}/api/auth/verify-token`, {
        token: token.value
      })
      
      user.value = response.data.user
      return true
    } catch (err) {
      setToken(null)
      user.value = null
      return false
    }
  }

  const changePassword = async (oldPassword, newPassword) => {
    loading.value = true
    error.value = null
    try {
      const response = await axios.post(`${API_URL}/api/auth/change-password`, {
        token: token.value,
        oldPassword,
        newPassword
      })
      
      return response.data
    } catch (err) {
      error.value = err.response?.data?.error || 'Password change failed'
      throw error.value
    } finally {
      loading.value = false
    }
  }

  return {
    user,
    token,
    loading,
    error,
    isAuthenticated,
    login,
    logout,
    verifyToken,
    changePassword,
    setToken
  }
})
