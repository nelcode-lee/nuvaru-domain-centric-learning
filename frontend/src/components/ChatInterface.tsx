import { useState, useRef, useEffect } from 'react'
import { PaperAirplaneIcon, DocumentTextIcon } from '@heroicons/react/24/outline'
import { useMutation } from 'react-query'
import toast from 'react-hot-toast'
import { apiService } from '../services/api'

interface Message {
  id: string
  type: 'user' | 'ai'
  content: string
  timestamp: Date
  sources?: Array<{
    document_id: string
    title: string
    relevance_score: number
    excerpt: string
  }>
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const chatMutation = useMutation(
    async (message: string) => {
      const response = await apiService.chatWithAI({
        message,
        user_id: 1, // In production, get from auth context
        knowledge_base_id: 'default'
      })
      return response
    },
    {
      onSuccess: (data) => {
        const aiMessage: Message = {
          id: Date.now().toString(),
          type: 'ai',
          content: data.response,
          timestamp: new Date(),
          sources: data.sources
        }
        setMessages(prev => [...prev, aiMessage])
        setIsLoading(false)
      },
      onError: (error: any) => {
        toast.error('Failed to get AI response. Please try again.')
        setIsLoading(false)
      }
    }
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    chatMutation.mutate(input.trim())
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="flex flex-col h-[600px] bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-8">
            <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Start a conversation
            </h3>
            <p className="text-sm">
              Ask questions about your uploaded documents to get AI-powered answers.
            </p>
            <div className="mt-6 space-y-2">
              <p className="text-sm font-medium text-gray-700">Try asking:</p>
              <div className="space-y-1">
                <button
                  onClick={() => setInput("What are the main topics in my documents?")}
                  className="block text-sm text-blue-600 hover:text-blue-800"
                >
                  "What are the main topics in my documents?"
                </button>
                <button
                  onClick={() => setInput("Summarize the key points from my knowledge base")}
                  className="block text-sm text-blue-600 hover:text-blue-800"
                >
                  "Summarize the key points from my knowledge base"
                </button>
                <button
                  onClick={() => setInput("Find information about specific topics")}
                  className="block text-sm text-blue-600 hover:text-blue-800"
                >
                  "Find information about specific topics"
                </button>
              </div>
            </div>
          </div>
        )}
        
        {messages.map((message) => (
          <div key={message.id} className={`message-bubble ${message.type === 'user' ? 'message-user' : 'message-ai'}`}>
            <div className="whitespace-pre-wrap">{message.content}</div>
            
            {message.sources && message.sources.length > 0 && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Sources:</h4>
                <div className="space-y-2">
                  {message.sources.map((source, index) => (
                    <div key={index} className="text-xs bg-gray-50 p-2 rounded">
                      <div className="font-medium">{source.title}</div>
                      <div className="text-gray-600 mt-1">{source.excerpt}</div>
                      <div className="text-gray-500 mt-1">
                        Relevance: {(source.relevance_score * 100).toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            <div className="text-xs text-gray-500 mt-2">
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message-bubble message-ai">
            <div className="flex items-center space-x-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span>AI is thinking...</span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input Area */}
      <div className="border-t border-gray-200 p-4">
        <form onSubmit={handleSubmit} className="flex space-x-4">
          <div className="flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask a question about your documents..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={2}
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PaperAirplaneIcon className="h-4 w-4" />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  )
}


