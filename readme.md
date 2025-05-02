Here's a comprehensive `README.md` file documenting your setup and run scripts:

```markdown
# MailAI Project

A React + FastAPI application for AI-powered email management.

## Prerequisites

- Python 3.9+
- Node.js 16+
- npm 8+
- Ollama installed and running
- mistral:7b-instruct-q4_K_M model available in Ollama

## Installation

### First-Time Setup

Run the appropriate setup script for your OS:

#### Windows
```batch
setup.bat
```

#### Linux/macOS
```bash
chmod +x setup.sh
./setup.sh
```

This will:
1. Download required AI model
2. Set up Python virtual environment
3. Install backend dependencies
4. Install frontend dependencies

## Running the Application

Use the run scripts to start both backend and frontend servers:

### Windows
```batch
run.bat
```

### Linux/macOS
```bash
chmod +x run.sh
./run.sh
```

The application will:
- Start backend server on port 7000
- Start frontend development server on port 8000
- Automatically open browser to http://localhost:8000 after 5 seconds

## Access Points

- **Frontend**: http://localhost:8000
- **Backend API**: http://localhost:7000
- **API Documentation**: http://localhost:7000/docs

## Script Details

### Setup Scripts (`setup.*`)
- Installs Python dependencies in virtual environment
- Installs Node.js dependencies
- Configures required AI model

### Run Scripts (`run.*`)
- Starts FastAPI backend server
- Starts React frontend development server
- Opens browser automatically
- Runs servers in parallel

## Configuration

### Environment Variables
Create `.env` files for customization:
- `backend/.env` for API settings
- `frontend/.env` for UI settings

Example frontend config:
```ini
VITE_COMPANY_NAME="Your Brand Name"
VITE_LOGO_PATH="/logo.png"
```

## Notes

1. First run might take longer due to AI model download
2. Servers must remain running for application to work
3. Scripts assume they're run from project root directory
4. Windows scripts require PowerShell or Command Prompt
5. For production use, consider:
   - Proper process management (PM2, systemd)
   - Environment-specific builds
   - Security hardening

## Troubleshooting

Common issues:
- Model not found: Run `ollama pull mistral:7b-instruct-q4_K_M` manually
- Port conflicts: Adjust ports in `main.py` and `vite.config.js`
- Missing dependencies: Delete `node_modules` and `venv` then rerun setup

## Security Considerations

❗ Never commit:
- `.env` files
- `venv/` directory
- `node_modules/`
- Local storage data

---

**Maintained by**  
Druidot Consulting (I) OPC Private Limited ®  
[datamiracle.com](https://datamiracle.com)
```

This README includes:
1. Clear setup/run instructions
2. Environment requirements
3. Access URLs
4. Script functionality details
5. Configuration guidance
6. Troubleshooting tips
7. Security notes
8. Company branding

The documentation uses standard markdown formatting and follows common README conventions while incorporating your specific project requirements and branding.