# Mail-AI: Smart Email Response Generator

## Overview

Mail-AI is an intelligent email assistant that analyzes the emotional tone of received emails and generates appropriate, professional responses. The system integrates FastAPI for the backend, React Vite for the frontend, and leverages the Mistral 7B language model through Ollama for AI-powered email analysis and response generation.

## Key Features

- **Emotion Detection**: Automatically identifies the emotional tone in emails (joy, sadness, anger, neutral)
- **Contextual Responses**: Generates professional responses that acknowledge the sender's emotion
- **Real-time Streaming**: Delivers AI-generated responses token by token for a smoother user experience
- **Simple Interface**: Clean, intuitive UI for managing emails and viewing AI suggestions

## Technical Components

### Backend
- FastAPI framework for efficient API endpoints
- Langchain for orchestrating AI model interactions
- Ollama integration for local LLM inference
- Asynchronous email processing with aioimaplib

### Frontend
- React with Vite for a responsive single-page application
- Real-time response streaming
- Email management interface

### AI Engine
- Mistral 7B Instruct (quantized) model via Ollama
- Two-stage processing:
  1. Non-streaming emotion classification
  2. Streaming response generation

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Ollama installed with the mistral:7b-instruct-q4_K_M model

### Installation

#### Windows Setup

1. **Install Ollama and the required model**:
   ```powershell
   ollama pull mistral:7b-instruct-q4_K_M
   ```

2. **Setup the backend**:
   ```powershell
   cd "path\to\mailAi\backend"
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

3. **Setup the frontend**:
   ```powershell
   cd "path\to\mailAi\frontend"
   npm install
   npm run dev -- --port 8000
   ```

The backend API will be available at http://localhost:7000, and the frontend at http://localhost:8000.

## Response Generation Process

1. **Email Analysis**:
   - The content of the email is analyzed to identify the emotional tone
   - The system classifies the emotion as joy, sadness, anger, or neutral

2. **Response Formulation**:
   - The AI generates a response that acknowledges the sender's emotion
   - Addresses key concerns from the original email
   - Provides actionable solutions or next steps
   - Maintains professional, concise formatting

3. **User Review**:
   - The generated response is presented to the user for review
   - The user can edit, approve, or discard the suggestion before sending

## Configuration

The response generator can be customized by modifying parameters in response_generator.py:
- `max_tokens`: Controls the length of generated responses
- `temperature`: Adjusts creativity (lower = more focused)
- `num_thread` and `num_gpu`: Hardware utilization settings

## Limitations

- The system works best with English language emails
- Performance depends on your local hardware capabilities
- Response quality depends on the Mistral 7B model quality

## License

This project is licensed under the MIT License - see the LICENSE file for details.