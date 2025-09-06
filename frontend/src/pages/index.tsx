import { useState, useRef, useEffect } from 'react'
import Head from 'next/head'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'chat' | 'documents' | 'upload'>('chat')
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<Array<{id: string, type: 'user' | 'ai', content: string, timestamp: Date}>>([])
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async () => {
    if (!message.trim() || isTyping) return

    const userMessage = {
      id: Date.now().toString(),
      type: 'user' as const,
      content: message.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setMessage('')
    setIsTyping(true)

    // Simulate AI response with typing animation
    setTimeout(() => {
      const responses = [
        `I understand you're asking about "${message}". The RAG system is analyzing your documents to provide the most relevant information.`,
        `Great question! Based on your query, I found several relevant documents in the knowledge base that can help answer this.`,
        `That's an interesting question about "${message}". Let me search through the uploaded documents for the most accurate information.`,
        `I've processed your question and found relevant information in the knowledge base. Here's what I discovered about "${message}".`,
        `Excellent question! The RAG system has identified several key documents that contain information related to "${message}".`
      ]
      const randomResponse = responses[Math.floor(Math.random() * responses.length)]
      
      const aiMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai' as const,
        content: randomResponse,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, aiMessage])
      setIsTyping(false)
    }, 2000)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <>
      <Head>
        <title>Nuvaru - Domain-Centric Learning Platform</title>
        <meta name="description" content="Private AI platform for enterprise domain-specific learning" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
        {/* Header */}
        <header className="bg-white/90 backdrop-blur-md shadow-lg border-b border-white/20 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center">
                    <span className="text-white font-bold text-lg">N</span>
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                      Nuvaru
                    </h1>
                    <p className="text-sm text-gray-600 font-medium">Domain-Centric Learning Platform</p>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2 px-3 py-1.5 bg-green-100 rounded-full">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm font-medium text-green-700">System Online</span>
                </div>
                <div className="hidden md:flex items-center space-x-2 text-sm text-gray-600">
                  <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded-md font-medium">Private AI</span>
                  <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded-md font-medium">Air-Gapped Ready</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        <div className="flex">
          {/* Sidebar */}
          <div className="w-72 bg-white/80 backdrop-blur-md shadow-xl border-r border-white/20 min-h-screen">
            <nav className="mt-8 px-6">
              <ul className="space-y-3">
                {[
                  { id: 'chat', name: 'AI Chat', icon: '💬', description: 'Ask questions about documents', color: 'from-blue-500 to-cyan-500' },
                  { id: 'documents', name: 'Knowledge Base', icon: '📚', description: 'Manage uploaded documents', color: 'from-emerald-500 to-teal-500' },
                  { id: 'upload', name: 'Upload', icon: '📤', description: 'Add new documents', color: 'from-purple-500 to-pink-500' }
                ].map((item) => (
                  <li key={item.id}>
                    <button
                      onClick={() => setActiveTab(item.id as any)}
                      className={`w-full group relative overflow-hidden rounded-2xl transition-all duration-300 ${
                        activeTab === item.id
                          ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-lg shadow-blue-500/25 transform scale-105'
                          : 'bg-white/50 hover:bg-white/80 text-gray-700 hover:text-gray-900 hover:shadow-lg hover:scale-105'
                      }`}
                    >
                      <div className="flex items-center px-4 py-4">
                        <div className={`text-2xl mr-4 transition-transform duration-300 ${
                          activeTab === item.id ? 'scale-110' : 'group-hover:scale-110'
                        }`}>
                          {item.icon}
                        </div>
                        <div className="text-left">
                          <div className="font-semibold text-lg">{item.name}</div>
                          <div className={`text-sm ${
                            activeTab === item.id ? 'text-blue-100' : 'text-gray-500'
                          }`}>
                            {item.description}
                          </div>
                        </div>
                      </div>
                      {activeTab === item.id && (
                        <div className="absolute inset-0 bg-gradient-to-r from-white/10 to-transparent"></div>
                      )}
                    </button>
                  </li>
                ))}
              </ul>
            </nav>

            {/* Sidebar Footer */}
            <div className="absolute bottom-0 left-0 right-0 p-6 border-t border-white/20">
              <div className="text-center">
                <div className="text-xs text-gray-500 mb-2">Nuvaru Platform</div>
                <div className="text-sm font-semibold text-gray-700">Version 1.0.0</div>
                <div className="mt-2 flex items-center justify-center space-x-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-xs text-gray-600">RAG System Active</span>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <main className="flex-1 p-8">
            {activeTab === 'chat' && (
              <div className="max-w-5xl mx-auto">
                <div className="mb-8">
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-800 bg-clip-text text-transparent mb-4">
                    AI Knowledge Assistant
                  </h1>
                  <p className="text-lg text-gray-600 leading-relaxed">
                    Ask questions about your uploaded documents and get AI-powered answers with source attribution.
                  </p>
                </div>
                
                {/* Chat Interface */}
                <div className="bg-white/90 backdrop-blur-md rounded-3xl shadow-2xl border border-white/20 overflow-hidden">
                  {/* Messages */}
                  <div className="h-96 overflow-y-auto p-6 space-y-6">
                    {messages.length === 0 && (
                      <div className="text-center py-12">
                        <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
                          <span className="text-3xl">🤖</span>
                        </div>
                        <h3 className="text-2xl font-bold text-gray-800 mb-3">Start a conversation</h3>
                        <p className="text-gray-600 mb-6">Ask questions about your documents to get AI-powered answers.</p>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                          {[
                            "What are the main topics in my documents?",
                            "Summarize the key findings",
                            "Find information about specific topics",
                            "What insights can you provide?"
                          ].map((suggestion, index) => (
                            <button
                              key={index}
                              onClick={() => setMessage(suggestion)}
                              className="p-3 text-left bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 rounded-xl border border-blue-200 hover:border-blue-300 transition-all duration-200 text-sm font-medium text-gray-700 hover:text-gray-900"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {messages.map((msg, index) => (
                      <div key={msg.id} className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
                        <div className={`max-w-3xl rounded-2xl px-6 py-4 shadow-lg ${
                          msg.type === 'user' 
                            ? 'bg-gradient-to-r from-blue-500 to-indigo-500 text-white' 
                            : 'bg-gradient-to-r from-gray-100 to-gray-50 text-gray-800 border border-gray-200'
                        }`}>
                          <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                          <div className={`text-xs mt-2 ${
                            msg.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                          }`}>
                            {formatTime(msg.timestamp)}
                          </div>
                        </div>
                      </div>
                    ))}
                    
                    {isTyping && (
                      <div className="flex justify-start animate-fadeIn">
                        <div className="bg-gradient-to-r from-gray-100 to-gray-50 text-gray-800 border border-gray-200 rounded-2xl px-6 py-4 shadow-lg">
                          <div className="flex items-center space-x-2">
                            <div className="flex space-x-1">
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                            </div>
                            <span className="text-sm text-gray-600">AI is thinking...</span>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    <div ref={messagesEndRef} />
                  </div>
                  
                  {/* Input */}
                  <div className="border-t border-gray-200/50 p-6 bg-gradient-to-r from-gray-50/50 to-blue-50/50">
                    <div className="flex space-x-4">
                      <div className="flex-1 relative">
                        <textarea
                          value={message}
                          onChange={(e) => setMessage(e.target.value)}
                          onKeyPress={handleKeyPress}
                          placeholder="Ask a question about your documents..."
                          className="w-full px-4 py-3 pr-12 bg-white/80 backdrop-blur-sm border border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all duration-200 placeholder-gray-500"
                          rows={2}
                          disabled={isTyping}
                        />
                        <div className="absolute right-3 top-3 text-gray-400">
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                          </svg>
                        </div>
                      </div>
                      <button
                        onClick={handleSendMessage}
                        disabled={!message.trim() || isTyping}
                        className="bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 disabled:from-gray-300 disabled:to-gray-400 text-white font-semibold py-3 px-6 rounded-2xl transition-all duration-200 transform hover:scale-105 disabled:scale-100 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
                      >
                        <div className="flex items-center space-x-2">
                          <span>Send</span>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                          </svg>
                        </div>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'documents' && (
              <div className="max-w-7xl mx-auto">
                <div className="mb-8">
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-emerald-700 to-teal-700 bg-clip-text text-transparent mb-4">
                    Knowledge Base
                  </h1>
                  <p className="text-lg text-gray-600 leading-relaxed">
                    Manage your uploaded documents and view their processing status.
                  </p>
                </div>
                
                <div className="bg-white/90 backdrop-blur-md rounded-3xl shadow-2xl border border-white/20 p-8">
                  <div className="text-center py-16">
                    <div className="w-24 h-24 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-full flex items-center justify-center mx-auto mb-6">
                      <span className="text-4xl">📚</span>
                    </div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-3">No documents uploaded</h3>
                    <p className="text-gray-600 mb-8 max-w-md mx-auto">
                      Upload some documents to get started with your knowledge base and enable AI-powered conversations.
                    </p>
                    <button
                      onClick={() => setActiveTab('upload')}
                      className="bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white font-semibold py-3 px-8 rounded-2xl transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
                    >
                      Upload Documents
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'upload' && (
              <div className="max-w-5xl mx-auto">
                <div className="mb-8">
                  <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-purple-700 to-pink-700 bg-clip-text text-transparent mb-4">
                    Upload Documents
                  </h1>
                  <p className="text-lg text-gray-600 leading-relaxed">
                    Upload documents to build your knowledge base. Supported formats: TXT, MD, JSON.
                  </p>
                </div>
                
                <div className="bg-white/90 backdrop-blur-md rounded-3xl shadow-2xl border border-white/20 p-8">
                  <div className="text-center py-16">
                    <div className="w-24 h-24 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6">
                      <span className="text-4xl">📤</span>
                    </div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-3">Drag and drop files here</h3>
                    <p className="text-gray-600 mb-8 max-w-md mx-auto">
                      Or click to select files from your computer. Documents will be automatically processed and added to your knowledge base.
                    </p>
                    <div className="max-w-md mx-auto">
                      <input 
                        type="file" 
                        multiple 
                        accept=".txt,.md,.json" 
                        className="w-full p-4 border-2 border-dashed border-purple-300 rounded-2xl hover:border-purple-400 transition-colors duration-200 cursor-pointer"
                      />
                      <p className="text-sm text-gray-500 mt-4">
                        Supported formats: TXT, MD, JSON (Max 10MB per file)
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </>
  )
}