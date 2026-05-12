import React, { createContext, useContext, useReducer, useEffect } from 'react'
import { isAuthenticated, login, logout, getUserInfo } from '../services/auth'

// Action types
export const AUTH_ACTIONS = {
  LOGIN_START: 'LOGIN_START',
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  LOAD_USER: 'LOAD_USER'
}

// Initial state
const initialState = {
  user: null,
  isLoading: false,
  isAuthenticated: false,
  error: null
}

// Reducer function
function authReducer(state, action) {
  switch (action.type) {
    case AUTH_ACTIONS.LOGIN_START:
      return {
        ...state,
        isLoading: true,
        error: null
      }
    
    case AUTH_ACTIONS.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload,
        isAuthenticated: true,
        isLoading: false,
        error: null
      }
    
    case AUTH_ACTIONS.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: action.payload
      }
    
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null
      }
    
    case AUTH_ACTIONS.LOAD_USER:
      return {
        ...state,
        user: action.payload,
        isAuthenticated: !!action.payload,
        isLoading: false
      }
    
    default:
      return state
  }
}

// Create context
const AuthContext = createContext()

// AuthProvider component
export function AuthProvider({ children }) {
  const [state, dispatch] = useReducer(authReducer, initialState)

  // Load user on mount
  useEffect(() => {
    if (isAuthenticated()) {
      const user = getUserInfo()
      dispatch({ type: AUTH_ACTIONS.LOAD_USER, payload: user })
    }
  }, [])

  // Login function
  const loginUser = async (credentials) => {
    dispatch({ type: AUTH_ACTIONS.LOGIN_START })
    
    try {
      const response = await login(credentials)
      
      if (response.success) {
        const user = getUserInfo()
        dispatch({ type: AUTH_ACTIONS.LOGIN_SUCCESS, payload: user })
        return { success: true }
      } else {
        dispatch({ type: AUTH_ACTIONS.LOGIN_FAILURE, payload: response.error })
        return { success: false, error: response.error }
      }
    } catch (error) {
      dispatch({ type: AUTH_ACTIONS.LOGIN_FAILURE, payload: 'Login failed' })
      return { success: false, error: 'Login failed' }
    }
  }

  // Logout function
  const logoutUser = () => {
    logout()
    dispatch({ type: AUTH_ACTIONS.LOGOUT })
  }

  const value = {
    ...state,
    loginUser,
    logoutUser
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Custom hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export default AuthContext
