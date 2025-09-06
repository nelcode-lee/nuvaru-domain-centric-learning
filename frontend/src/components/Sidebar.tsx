import { 
  ChatBubbleLeftRightIcon, 
  DocumentTextIcon, 
  CloudArrowUpIcon,
  Cog6ToothIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'

interface SidebarProps {
  activeTab: 'chat' | 'documents' | 'upload' | 'settings' | 'analytics'
  onTabChange: (tab: 'chat' | 'documents' | 'upload' | 'settings' | 'analytics') => void
}

const navigation = [
  { 
    id: 'chat', 
    name: 'AI Chat', 
    icon: ChatBubbleLeftRightIcon,
    description: 'Ask questions about your documents'
  },
  { 
    id: 'documents', 
    name: 'Knowledge Base', 
    icon: DocumentTextIcon,
    description: 'Manage uploaded documents'
  },
  { 
    id: 'upload', 
    name: 'Upload', 
    icon: CloudArrowUpIcon,
    description: 'Add new documents'
  },
  { 
    id: 'analytics', 
    name: 'Analytics', 
    icon: ChartBarIcon,
    description: 'Usage and performance metrics'
  },
  { 
    id: 'settings', 
    name: 'Settings', 
    icon: Cog6ToothIcon,
    description: 'System configuration'
  },
]

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  return (
    <div className="w-64 bg-white shadow-sm border-r border-gray-200 min-h-screen">
      <nav className="mt-8 px-4">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const isActive = activeTab === item.id
            return (
              <li key={item.id}>
                <button
                  onClick={() => onTabChange(item.id as any)}
                  className={`w-full flex items-center px-3 py-3 text-left rounded-lg transition-colors duration-200 ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 border border-blue-200'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <item.icon 
                    className={`mr-3 h-5 w-5 ${
                      isActive ? 'text-blue-500' : 'text-gray-400'
                    }`} 
                  />
                  <div className="flex-1">
                    <div className="font-medium">{item.name}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      {item.description}
                    </div>
                  </div>
                </button>
              </li>
            )
          })}
        </ul>
      </nav>
      
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500">
          <div className="font-medium">Nuvaru Platform</div>
          <div>Version 1.0.0</div>
          <div className="mt-1">
            <span className="inline-flex items-center">
              <div className="w-2 h-2 bg-green-400 rounded-full mr-2"></div>
              RAG System Active
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}


