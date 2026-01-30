# 🏮 Code Lantern - Project Architecture Analyzer

> **Illuminate your codebase.** Upload any project and instantly visualize its architecture, dependencies, and code quality with AI-powered insights.

[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)](https://tailwindcss.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

## ✨ Features

- **🚀 Instant Analysis** - Upload a ZIP or connect a GitHub repository.
- **🏗️ Interactive Architecture Maps** - Visual tree diagrams of your file structure.
- **🔗 Dependency Graphs** - Track file and function-level dependencies visually with Cytoscape.js.
- **🤖 Multi-LLM AI Insights** - Powered by **Groq** (Llama 3), **Gemini**, and **Cohere** with automatic fallback.
- **📊 Complexity Heatmaps** - Identify technical debt and complex hotspots with AST-based cyclomatic complexity.
- **🔒 Privacy-First** - All code analysis happens locally; your code never leaves your machine (unless you opt-in to AI insights).
- **⚡ Rate Limiting & Caching** - Smart resource management to keep costs low (or free).
- **🧹 Auto-Cleanup** - Old projects are automatically removed after 1 hour.
- **🎨 Premium UI** - Glassmorphism design, smooth animations, and responsive layout.

## 🌐 Supported Languages

Code Lantern uses **Tree-sitter** for accurate AST-based code analysis, supporting:

- 🐍 **Python** (`.py`)
- 📜 **JavaScript** (`.js`, `.jsx`)
- 💙 **TypeScript** (`.ts`, `.tsx`)
- ☕ **Java** (`.java`)
- ⚙️ **C++** (`.cpp`, `.cc`, `.cxx`, `.h`, `.hpp`)
- 🦀 **Rust** (`.rs`)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Tjindl/code-lantern.git
cd code-lantern

# Create backend .env file
cp backend/.env.example backend/.env
# Add your API keys (GROQ_API_KEY, GEMINI_API_KEY, etc.) to backend/.env

# Start with Docker Compose
docker-compose up --build

# Access the application
# Frontend: http://localhost (Port 80)
# Backend API: http://localhost:8002
```

### Option 2: Manual Setup

#### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/Tjindl/code-lantern.git
cd code-lantern/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add API keys (GROQ_API_KEY, GEMINI_API_KEY, etc.) to .env

# Start the server
python main.py
```

#### 2. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Visit **http://localhost:5173** to start analyzing!

## 🔧 Configuration

Create a `.env` file in the `backend/` directory:

```env
# Primary Provider (Ultrafast)
GROQ_API_KEY=your_groq_key

# Fallback Provider 1 (Reliable)
GEMINI_API_KEY=your_gemini_key

# Fallback Provider 2 (Backup)
COHERE_API_KEY=your_cohere_key

# GitHub Integration (Optional)
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_REDIRECT_URI=http://localhost:8000/api/github/callback
```

> **Note:** You can run Code Lantern without AI providers - all architecture analysis works locally. AI is only used for optional function insights.

## 🏗️ Architecture

### Backend
- **FastAPI**: High-performance async API framework.
- **Tree-sitter Analysis Engine**: Industry-standard AST parsing (same technology used by GitHub) for 6 languages.
- **Multi-LLM Provider**: Robust abstraction layer handling automatic failovers between AI providers (Groq → Gemini → Cohere).
- **Rate Limiter**: In-memory tracking to prevent abuse and manage API quotas.
- **Gunicorn + Uvicorn**: Production-ready ASGI server with async workers.

### Frontend
- **React 18 + Vite**: Blazing fast development and optimized production builds.
- **Cytoscape.js**: Powerful graph visualization for dependency mapping.
- **Tailwind CSS**: Modern, utility-first styling for premium UI.
- **React Router**: Client-side routing for seamless navigation.

### DevOps
- **Docker**: Multi-stage builds for optimized containers.
- **Nginx**: Production-grade static file serving.
- **Docker Compose**: Easy orchestration of frontend and backend services.

## 🔒 Privacy & Security

- **Local Analysis**: All code parsing happens on your server using Tree-sitter AST parsers.
- **No Database**: Your code is never stored in a database.
- **Auto-Cleanup**: Uploaded projects are automatically deleted after 1 hour.
- **Opt-in AI**: AI insights are triggered per-function only when you click. You control what gets analyzed.
- **No Tracking**: No user analytics or telemetry.

## 📚 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 18, Vite, Tailwind CSS, Cytoscape.js |
| **Backend** | FastAPI, Python 3.11+, Pydantic |
| **Analysis** | Tree-sitter (Python, JS, TS, Java, C++, Rust) |
| **AI** | Groq, Google Gemini, Cohere |
| **Server** | Gunicorn, Uvicorn (ASGI) |
| **Deployment** | Docker, Docker Compose, Nginx |

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for developers who love clean code.**
