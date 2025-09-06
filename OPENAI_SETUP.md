# OpenAI Configuration Guide

## Setup Instructions

### 1. Get OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key (it starts with `sk-`)

### 2. Set Environment Variable

#### Option A: Export in Terminal (Temporary)
```bash
export OPENAI_API_KEY="your-api-key-here"
```

#### Option B: Add to Shell Profile (Permanent)
Add this line to your `~/.zshrc` or `~/.bashrc`:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

#### Option C: Create .env File
Create a `.env` file in the project root:
```bash
OPENAI_API_KEY=your-api-key-here
```

### 3. Test Configuration
After setting up the API key, restart the backend and test the connection:

```bash
# Test OpenAI connection
curl http://localhost:8000/api/v1/learning/openai/test
```

### 4. Configure Model (Optional)
You can configure the OpenAI model and parameters:

```bash
# Configure model and parameters
curl -X POST "http://localhost:8000/api/v1/learning/openai/configure" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "max_tokens": 1500,
    "temperature": 0.7
  }'
```

## Available Models
- `gpt-3.5-turbo` (default, cost-effective)
- `gpt-4` (more capable, higher cost)
- `gpt-4-turbo` (latest, best performance)

## Privacy Note
For production use, consider switching to:
- **Ollama** (local, completely private)
- **Llama 3** (local, open source)
- **Other local LLMs** for data privacy

## Troubleshooting
- **401 Unauthorized**: Check your API key
- **429 Rate Limited**: You've hit rate limits, wait or upgrade plan
- **Connection Failed**: Check internet connection and API key validity

