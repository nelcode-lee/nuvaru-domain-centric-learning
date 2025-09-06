import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth tokens
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export interface ChatRequest {
  message: string
  user_id: number
  knowledge_base_id?: string
  context?: string
  session_id?: string
}

export interface ChatResponse {
  response: string
  sources: Array<{
    document_id: string
    title: string
    relevance_score: number
    excerpt: string
    metadata: any
  }>
  session_id: string
  timestamp: string
  metadata: {
    user_id: number
    knowledge_base_id?: string
    sources_count: number
    context_length: number
  }
}

export interface Document {
  id: string
  filename: string
  content_type: string
  size: number
  status: string
  metadata: any
  user_id: number
  chunks_count: number
}

export interface UploadResponse {
  id: string
  filename: string
  content_type: string
  size: number
  status: string
  metadata: any
  user_id: number
  chunks_count: number
}

export const apiService = {
  // Health check
  async healthCheck() {
    const response = await api.get('/health')
    return response.data
  },

  // Chat with AI
  async chatWithAI(request: ChatRequest): Promise<ChatResponse> {
    const formData = new FormData()
    formData.append('message', request.message)
    formData.append('user_id', request.user_id.toString())
    if (request.knowledge_base_id) {
      formData.append('knowledge_base_id', request.knowledge_base_id)
    }
    if (request.context) {
      formData.append('context', request.context)
    }
    if (request.session_id) {
      formData.append('session_id', request.session_id)
    }

    const response = await api.post('/learning/chat', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  // Document management
  async uploadDocument(formData: FormData): Promise<UploadResponse> {
    const response = await api.post('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async getDocuments(): Promise<Document[]> {
    const response = await api.get('/documents')
    return response.data
  },

  async getDocument(documentId: string): Promise<Document> {
    const response = await api.get(`/documents/${documentId}`)
    return response.data
  },

  async deleteDocument(documentId: string): Promise<void> {
    await api.delete(`/documents/${documentId}`)
  },

  async searchDocuments(query: string, knowledgeBaseId?: string): Promise<Document[]> {
    const params = new URLSearchParams()
    params.append('query', query)
    if (knowledgeBaseId) {
      params.append('knowledge_base_id', knowledgeBaseId)
    }
    
    const response = await api.get(`/documents/search?${params}`)
    return response.data
  },

  // Learning sessions
  async getLearningSessions(userId: number, limit = 50) {
    const response = await api.get(`/learning/sessions?user_id=${userId}&limit=${limit}`)
    return response.data
  },

  async submitFeedback(sessionId: string, responseId: string, rating: number, feedback: string, correctness: boolean, userId: number) {
    const response = await api.post('/learning/feedback', {
      session_id: sessionId,
      response_id: responseId,
      rating,
      feedback,
      correctness,
      user_id: userId,
    })
    return response.data
  },

  // Knowledge base stats
  async getKnowledgeBaseStats(userId: number, knowledgeBaseId?: string) {
    const params = new URLSearchParams()
    params.append('user_id', userId.toString())
    if (knowledgeBaseId) {
      params.append('knowledge_base_id', knowledgeBaseId)
    }
    
    const response = await api.get(`/learning/stats?${params}`)
    return response.data
  },

  // User management
  async login(email: string, password: string) {
    const response = await api.post('/auth/login', {
      email,
      password,
    })
    return response.data
  },

  async register(email: string, password: string, fullName: string) {
    const response = await api.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    })
    return response.data
  },

  async getCurrentUser() {
    const response = await api.get('/users/me')
    return response.data
  },
}

export default api


