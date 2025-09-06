# OpenCosts 🚀

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)

> A comprehensive tool for discovering and comparing AI model costs across OpenRouter providers

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Development](#development)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Support](#support)

## Overview

**What**: OpenCosts is a full-stack application that automatically discovers AI models from OpenRouter based on configurable search terms, fetches detailed provider information including pricing and context limits, and presents the data through an intuitive web interface.

**Why**: With hundreds of AI models available across multiple providers, comparing costs and capabilities is time-consuming and error-prone. OpenCosts automates this process, providing real-time pricing data and provider comparisons in one place.

**Key Features**:
- 🔍 **Smart Model Discovery**: Finds models using configurable search terms
- 💰 **Real-time Pricing**: Fetches current pricing from OpenRouter API
- 🏢 **Provider Comparison**: Compare context lengths, input/output token costs across providers
- 🌐 **Modern Web Interface**: React TypeScript frontend with responsive design
- 🐳 **Container-Ready**: Full Docker containerization for easy deployment
- 📊 **Data Export**: CSV export functionality for further analysis
- ⚡ **Fast API**: RESTful API with automatic documentation

## Architecture

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend│    │   FastAPI       │    │   OpenRouter    │
│   (Port 5173)   │◄──►│   Backend       │◄──►│   API           │
│                 │    │   (Port 8000)   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │   Data Storage  │
│   (CSV Export)  │    │   (Input/Output)│
└─────────────────┘    └─────────────────┘
```

### Tech Stack

**Backend**:
- Python 3.12+ with FastAPI
- Requests for HTTP client
- Concurrent processing with ThreadPoolExecutor
- UV package manager

**Frontend**:
- React 18+ with TypeScript
- Vite build tool
- Mantine UI components
- Modern CSS with responsive design

**Infrastructure**:
- Docker & Docker Compose
- Multi-stage container builds
- Volume mounting for data persistence

### Key Components

- **API Service**: FastAPI backend providing RESTful endpoints for model data
- **Scraper Service**: Standalone Python service for fetching OpenRouter data
- **Frontend Application**: React TypeScript SPA for data visualization
- **Data Layer**: File-based storage with CSV export capabilities

### Data Flow

1. **Configuration**: Search terms loaded from `data/input/models_strings.txt`
2. **Discovery**: Backend queries OpenRouter API for matching models
3. **Enrichment**: Fetches provider details, pricing, and context limits
4. **Storage**: Data saved as CSV in `frontend/public/` for web access
5. **Presentation**: React frontend displays organized, searchable results

## Prerequisites

- **Docker**: Version 20.10+ and Docker Compose
- **System**: macOS, Linux, or Windows with WSL2
- **Memory**: 2GB+ available RAM
- **Network**: Internet connection for OpenRouter API access

## Quick Start

Get OpenCosts running in under 2 minutes using the provided Makefile:

```bash
# Clone the repository
git clone https://github.com/rjalexa/opencosts.git
cd opencosts

# Ensure Docker is installed and running
# The Makefile will attempt to start Docker if it's not running

# Start the application
make run

# Access the application
open http://localhost:5173
```

The `make run` command performs the following steps:
- Ensures Docker is running (and attempts to start it if needed)
- Generates fresh data using the scraper service
- Builds and starts the backend and frontend services
- Opens the web application in your default browser

**Stopping the Application**:
```bash
make stop
```

## Installation & Setup

### Development Setup

1. **Clone and Configure**:
   ```bash
   git clone https://github.com/rjalexa/opencosts.git
   cd opencosts
   
   ```

2. **Customize Search Terms** (Optional):
   ```bash
   # Edit the model search terms
   nano data/input/models_strings.txt
   ```

3. **Build and Start Services**:
   ```bash
   # Recommended: Use the automated setup script
   ./scripts/run.sh
   
   # Alternative: Manual Docker Compose approach
   cd docker
   docker compose up -d --build
   ```

4. **Verify Installation**:
   ```bash
   # Check service status
   docker compose ps
   
   # View logs
   docker compose logs -f
   ```

### Production Setup

For production deployment:

```bash
# Use production compose file (when available)
docker compose -f docker-compose.prod.yml up -d --build

# Or configure environment variables for production
export API_BASE_URL=https://your-domain.com
export FRONTEND_PORT=80
```

## Usage

### Web Interface

1. **Access Application**: Navigate to `http://localhost:5173`
2. **Browse Models**: View models organized by author/provider
3. **Compare Providers**: Expand model cards to see provider comparison tables
4. **Export Data**: Download CSV files for external analysis

### API Endpoints

- **Health Check**: `GET /health`
- **Refresh Data**: `POST /refresh-data`
- **Download CSV**: `GET /csv`
- **Get Models JSON**: `GET /models`

### Configuration Options

**Environment Variables** (`.env`):
```bash
# API Configuration
API_PORT=8000
FRONTEND_PORT=5173

# OpenRouter Settings
OPENROUTER_BASE_URL=https://openrouter.ai
REQUEST_TIMEOUT=30

# Docker Settings
COMPOSE_PROJECT_NAME=opencosts
```

**Search Terms** (`data/input/models_strings.txt`):
```
Gemini 2.5
Sonnet 4
Opus 4
Kimi K2
Deepseek R1
Qwen3
```

### CLI Commands

```bash
# Refresh model data manually
docker compose exec scraper python src/main.py

# Access backend API directly
curl http://localhost:8000/models

# View real-time logs
docker compose logs -f backend
```

## Development

### Project Structure

```
opencosts/
├── src/                          # Backend Python source code
│   ├── main.py                   # Core scraping logic
│   └── api.py                    # FastAPI web service
├── frontend/                     # React TypeScript frontend
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/             # API client
│   │   └── types/                # TypeScript definitions
│   └── public/                   # Static assets & CSV output
├── docker/                       # Container configuration
│   ├── docker-compose.yml        # Service orchestration
│   ├── Dockerfile.backend        # Python container
│   └── Dockerfile.frontend       # React container
├── data/                         # Runtime data
│   ├── input/                    # Configuration files
│   └── output/                   # Generated reports
└── scripts/                      # Automation scripts
```

### Development Workflow

1. **Make Changes**: Edit source code in `src/` or `frontend/src/`
2. **Rebuild Service**: 
   ```bash
   docker compose down backend
   docker compose up -d backend --build
   ```
3. **Test Changes**: Verify functionality through web interface
4. **Run Quality Checks**:
   ```bash
   # Python formatting and linting
   docker compose exec backend ruff format .
   docker compose exec backend ruff check --fix .
   
   # Frontend linting
   docker compose exec frontend pnpm lint --fix
   ```

### Available Scripts/Commands

```bash
# Quick Start (Recommended)
./scripts/run.sh                  # Complete setup: data generation + build + start

# Development
docker compose up -d --build      # Start all services
docker compose down               # Stop all services
docker compose logs -f SERVICE    # View service logs

# Backend Development
docker compose exec backend python src/main.py    # Run scraper
docker compose exec backend python src/api.py     # Run API server

# Frontend Development
docker compose exec frontend pnpm dev            # Development server
docker compose exec frontend pnpm build          # Production build
docker compose exec frontend pnpm lint           # Code linting

# Data Management
docker compose exec scraper python src/main.py   # Refresh model data
docker compose run --rm scraper                  # One-time data generation
```

## API Reference

### Base URL
- Development: `http://localhost:8000`
- Production: Configure via environment variables

### Endpoints

#### Health Check
```http
GET /health
```
Returns service health status.

#### Refresh Model Data
```http
POST /refresh-data
```
Fetches latest model data from OpenRouter API.

**Response**:
```json
{
  "message": "Data refreshed successfully",
  "models_found": 25,
  "provider_rows": 150,
  "output_file": "frontend/public/openrouter_models_providers.csv"
}
```

#### Get Models (JSON)
```http
GET /models
```
Returns structured model data organized by author.

**Response**:
```json
[
  {
    "name": "Anthropic",
    "models": [
      {
        "name": "Claude 3.5 Sonnet",
        "url": "https://openrouter.ai/anthropic/claude-3.5-sonnet",
        "id": "anthropic/claude-3.5-sonnet",
        "providers": [
          {
            "Provider": "Anthropic",
            "Context length": "200000",
            "Price/input token": "0.000003",
            "Price/output token": "0.000015"
          }
        ]
      }
    ]
  }
]
```

#### Download CSV
```http
GET /csv
```
Downloads the complete dataset as CSV file.

### Authentication
Currently no authentication required. For production use, consider implementing API keys.

### Rate Limiting
No rate limiting implemented. OpenRouter API limits apply to upstream requests.

## Testing

### Running Tests

```bash
# Backend tests (when implemented)
docker compose exec backend python -m pytest tests/

# Frontend tests (when implemented)
docker compose exec frontend pnpm test

# Integration tests
docker compose exec backend python src/main.py  # Verify scraper works
curl http://localhost:8000/health                # Verify API works
```

### Test Structure

```
tests/
├── unit/
│   ├── backend/          # Python unit tests
│   └── frontend/         # React component tests
├── integration/          # API integration tests
└── e2e/                 # End-to-end browser tests
```

### Manual Testing

1. **Data Refresh**: Use `/refresh-data` endpoint
2. **Web Interface**: Navigate through all UI components
3. **CSV Export**: Download and verify CSV format
4. **Error Handling**: Test with invalid search terms

## Deployment

### Docker Deployment

**Development**:
```bash
cd docker
docker compose up -d --build
```

**Production** (recommended):
```bash
# Create production environment file
.prod

# Deploy with production settings
docker compose -f docker-compose.prod.yml up -d --build
```

### Environment Variables

**Complete list for production**:
```bash
# Application
API_PORT=8000
FRONTEND_PORT=5173
APP_ENV=production

# OpenRouter API
OPENROUTER_BASE_URL=https://openrouter.ai
REQUEST_TIMEOUT=30
MAX_WORKERS=8

# Docker
COMPOSE_PROJECT_NAME=opencosts

# Security (for production)
CORS_ORIGINS=https://yourdomain.com
API_KEY=your-secret-key  # If implementing auth
```

### Scaling Considerations

- **Horizontal Scaling**: Run multiple backend instances behind load balancer
- **Caching**: Implement Redis for API response caching
- **Database**: Consider PostgreSQL for persistent storage at scale
- **CDN**: Serve static assets via CDN for global performance

### Monitoring and Logging

```bash
# View application logs
docker compose logs -f

# Monitor resource usage
docker stats

# Health monitoring
curl http://localhost:8000/health
```

## Contributing

We welcome contributions! OpenCosts is an MIT licensed project that thrives on community collaboration.

### How to Contribute

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Make Changes**: Follow our coding standards
4. **Test Thoroughly**: Ensure all tests pass
5. **Submit Pull Request**: Describe your changes clearly

### Development Guidelines

- **Code Style**: Use Ruff for Python, ESLint for TypeScript
- **Commits**: Use conventional commit messages
- **Documentation**: Update README for new features
- **Testing**: Add tests for new functionality

### Types of Contributions Welcome

- 🐛 **Bug Fixes**: Report and fix issues
- ✨ **New Features**: Enhance functionality
- 📚 **Documentation**: Improve guides and examples
- 🎨 **UI/UX**: Design improvements
- 🔧 **DevOps**: Build and deployment enhancements
- 🌐 **Translations**: Internationalization support

### Code of Conduct

Please be respectful and inclusive. We're building a welcoming community for developers of all backgrounds and experience levels.

## Troubleshooting

### Common Issues

**Services won't start**:
```bash
# Check Docker status
docker --version
docker compose --version

# Verify ports are available
lsof -i :8000
lsof -i :5173

# Rebuild containers
docker compose down
docker compose up -d --build
```

**No model data appearing**:
```bash
# Check if data directory exists
ls -la data/input/

# Verify search terms file
cat data/input/models_strings.txt

# Use the run script to regenerate data
./scripts/run.sh

# Or manually refresh data
docker compose exec backend python src/main.py
```

**Frontend not loading**:
```bash
# Check frontend build
docker compose logs frontend

# Verify backend connectivity
curl http://localhost:8000/health

# Rebuild frontend
docker compose down frontend
docker compose up -d frontend --build
```

**API errors**:
```bash
# Check backend logs
docker compose logs backend

# Test OpenRouter connectivity
curl https://openrouter.ai/api/v1/models

# Verify environment variables
docker compose exec backend env | grep -E "(API|OPENROUTER)"
```

### Debug Mode

Enable verbose logging:
```bash
# Set debug environment
echo "LOG_LEVEL=debug" >> .env

# Restart services
docker compose down && docker compose up -d
```

### FAQ

**Q: How often should I refresh the data?**
A: Model pricing changes infrequently. Daily or weekly refreshes are typically sufficient.

**Q: Can I add custom search terms?**
A: Yes, edit `data/input/models_strings.txt` and restart the scraper service.

**Q: Is there a rate limit on the OpenRouter API?**
A: OpenRouter has undocumented rate limits. The application uses reasonable delays and concurrent request limiting.

**Q: Can I run this without Docker?**
A: While possible, Docker is strongly recommended for consistent environments and easy deployment.

## Performance

### Benchmarks

- **Model Discovery**: ~2-5 seconds for 6 search terms
- **Provider Fetching**: ~10-30 seconds depending on model count
- **Frontend Load**: <2 seconds initial page load
- **Memory Usage**: ~200MB total (all containers)

### Optimization Tips

- **Concurrent Requests**: Adjust `MAX_WORKERS` environment variable
- **Caching**: Implement Redis for repeated API calls
- **CDN**: Use CDN for static assets in production
- **Database**: Consider PostgreSQL for large datasets

## Security

### Security Considerations

- **API Keys**: Store sensitive keys in environment variables
- **CORS**: Configure specific origins for production
- **Input Validation**: All user inputs are validated
- **Container Security**: Containers run as non-root users

### Reporting Vulnerabilities

Please report security issues privately to the maintainers before public disclosure.

### Best Practices for Deployment

- Use HTTPS in production
- Implement API authentication for sensitive deployments
- Regular security updates for base images
- Monitor logs for suspicious activity

## Roadmap

### Planned Features

- 🔐 **Authentication**: User accounts and API keys
- 📊 **Advanced Analytics**: Historical pricing trends
- 🔔 **Notifications**: Price change alerts
- 🌍 **Multi-Provider**: Support for additional AI providers
- 📱 **Mobile App**: React Native mobile application
- 🤖 **AI Integration**: Smart model recommendations

### Known Limitations

- **Provider Coverage**: Limited to OpenRouter ecosystem
- **Real-time Data**: Manual refresh required for latest pricing
- **Latency Metrics**: Not available via current OpenRouter API
- **Historical Data**: No built-in trend analysis

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### MIT License Summary

- ✅ **Commercial Use**: Use in commercial projects
- ✅ **Modification**: Modify and distribute
- ✅ **Distribution**: Share with others
- ✅ **Private Use**: Use privately
- ❗ **Liability**: No warranty provided
- ❗ **Attribution**: Include original license

## Support

### Getting Help

- 📖 **Documentation**: Check this README and inline code comments
- 🐛 **Issues**: [GitHub Issues](https://github.com/rjalexa/opencosts/issues) for bugs and feature requests
- 💬 **Discussions**: [GitHub Discussions](https://github.com/rjalexa/opencosts/discussions) for questions and ideas
- 📧 **Email**: Contact maintainers for private inquiries

### Community

- **Contributors Welcome**: We actively encourage pull requests and collaboration
- **Beginner Friendly**: Good first issues are labeled for new contributors
- **Responsive Maintainers**: Issues and PRs reviewed regularly

### Commercial Support

For enterprise deployments or custom development, please contact the maintainers to discuss commercial support options.

---

**Built with ❤️ by the OpenCosts community**

*Star ⭐ this repository if you find it useful!*
