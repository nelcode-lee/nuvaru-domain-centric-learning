# 🎨 Frontend Setup Guide

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ installed
- Backend server running (http://localhost:8000)

### Start the Frontend
```bash
# Start the frontend development server
./start_frontend.sh
```

The frontend will be available at: **http://localhost:3000**

## 🏗️ Frontend Architecture

### Technology Stack
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Query
- **UI Components**: Headless UI + Heroicons
- **File Upload**: React Dropzone
- **HTTP Client**: Axios

### Project Structure
```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── Header.tsx      # Navigation header
│   │   ├── Sidebar.tsx     # Main navigation
│   │   ├── ChatInterface.tsx # AI chat interface
│   │   ├── DocumentUpload.tsx # File upload component
│   │   └── DocumentList.tsx # Document management
│   ├── pages/              # Next.js pages
│   │   ├── _app.tsx        # App wrapper
│   │   └── index.tsx       # Main dashboard
│   ├── services/           # API services
│   │   └── api.ts          # API client
│   └── styles/             # Global styles
│       └── globals.css     # Tailwind CSS
├── package.json            # Dependencies
├── next.config.js          # Next.js configuration
├── tailwind.config.js      # Tailwind configuration
└── tsconfig.json           # TypeScript configuration
```

## 🎯 Key Features

### 1. **AI Chat Interface**
- Real-time conversation with RAG system
- Source attribution for responses
- Message history and timestamps
- Loading states and error handling

### 2. **Document Management**
- Drag-and-drop file upload
- Support for TXT, MD, JSON files
- Document list with search and filtering
- File metadata and processing status

### 3. **Knowledge Base**
- Document search and retrieval
- Processing status tracking
- Chunk count and file information
- Delete and view operations

### 4. **Responsive Design**
- Mobile-friendly interface
- Clean, modern UI with Tailwind CSS
- Accessible components
- Professional enterprise look

## 🔧 Development

### Available Scripts
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linting
npm run lint

# Type checking
npm run type-check
```

### Environment Variables
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### API Integration
The frontend connects to the FastAPI backend through:
- **Base URL**: `http://localhost:8000/api/v1`
- **Authentication**: JWT tokens (when implemented)
- **Error Handling**: Axios interceptors
- **Type Safety**: TypeScript interfaces

## 🎨 UI Components

### Main Layout
- **Header**: Logo, status indicators, system info
- **Sidebar**: Navigation between features
- **Main Content**: Feature-specific interfaces

### Chat Interface
- **Message Bubbles**: User and AI messages
- **Source Attribution**: Document sources with relevance scores
- **Input Area**: Text input with send button
- **Loading States**: Spinner and status indicators

### Document Upload
- **Drag & Drop Zone**: File upload area
- **File List**: Uploaded files with metadata
- **Progress Indicators**: Upload status and processing
- **File Validation**: Type and size checking

### Document Management
- **Search Bar**: Find documents by name or type
- **Document Cards**: File information and actions
- **Status Badges**: Processing status indicators
- **Action Buttons**: View, delete, download

## 🚀 Deployment

### Development
```bash
# Start both backend and frontend
./start_dev.sh      # Backend
./start_frontend.sh  # Frontend
```

### Production
```bash
# Build and deploy
npm run build
npm start
```

### Docker
```bash
# Build frontend image
docker build -t nuvaru-frontend .

# Run with docker-compose
docker-compose up frontend
```

## 🔗 API Endpoints Used

### Chat & Learning
- `POST /learning/chat` - Chat with AI
- `GET /learning/sessions` - Get learning sessions
- `POST /learning/feedback` - Submit feedback
- `GET /learning/stats` - Knowledge base statistics

### Document Management
- `POST /documents/upload` - Upload documents
- `GET /documents` - List documents
- `GET /documents/{id}` - Get specific document
- `DELETE /documents/{id}` - Delete document
- `GET /documents/search` - Search documents

### System
- `GET /health` - Health check
- `GET /docs` - API documentation

## 🎯 User Experience

### Workflow
1. **Upload Documents**: Drag and drop files to build knowledge base
2. **Chat with AI**: Ask questions about uploaded content
3. **View Sources**: See which documents informed the AI response
4. **Manage Knowledge**: Search, filter, and organize documents

### Key Benefits
- **Intuitive Interface**: Easy to use for non-technical users
- **Real-time Feedback**: Immediate responses and status updates
- **Source Transparency**: Clear attribution for AI responses
- **Professional Design**: Enterprise-ready appearance

## 🛠️ Customization

### Styling
- Modify `tailwind.config.js` for theme changes
- Update `globals.css` for custom styles
- Use Tailwind utility classes for rapid styling

### Components
- Add new components in `src/components/`
- Extend existing components for new features
- Use TypeScript for type safety

### API Integration
- Update `api.ts` for new endpoints
- Add TypeScript interfaces for new data types
- Implement error handling for new features

## 🎉 Ready to Use!

The frontend is now ready and provides a complete user interface for the Nuvaru RAG system. Users can:

✅ **Upload documents** and build their knowledge base
✅ **Chat with AI** using natural language queries
✅ **View source attribution** for all AI responses
✅ **Manage documents** with search and filtering
✅ **Monitor system status** and performance

**Start the frontend with `./start_frontend.sh` and access it at http://localhost:3000!**


