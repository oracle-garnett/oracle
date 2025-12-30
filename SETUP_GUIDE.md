# Oracle Setup Guide

Welcome to the setup guide for **Oracle**, your advanced local AI assistant. Follow these steps to bring Oracle to life on your laptop.

## Prerequisites

1.  **Python 3.10+**: Ensure Python is installed and added to your PATH.
2.  **Git**: Required to clone the repository.
3.  **Ollama (Optional but Recommended)**: For running local LLMs like Llama 3 or Mistral. Download at [ollama.com](https://ollama.com).
4.  **FFmpeg**: Required for Whisper (speech-to-text) to process audio.

## Installation

Run the following command in your **PowerShell** (as Administrator) to clone and set up Oracle:

```powershell
git clone https://github.com/YOUR_USERNAME/oracle.git; cd oracle; ./scripts/start_oracle.ps1
```

*(Note: Replace `YOUR_USERNAME` with the actual GitHub username once the repository is pushed.)*

## Configuration

### 1. Memory Persistence (Cloud Database)
Oracle uses a cloud database for long-term memory. To set this up:
- Create a free account on [Supabase](https://supabase.com) or [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
- Obtain your connection string.
- Update the `memory/memory_manager.py` file with your credentials or set them as environment variables.

### 2. AI Models
- **Local LLM**: Install Ollama and run `ollama run llama3`. Oracle will automatically attempt to connect to the local Ollama server.
- **Voice (Whisper)**: The first time you use voice commands, Oracle will download the Whisper model (approx. 150MB for the 'base' model).

## Administrative Safeguards

- **Admin PIN**: The default PIN is `1234`. You can change this in `safeguards/admin_override.py`.
- **Override**: If Oracle behaves unexpectedly, use the "Admin Override" feature in the UI or type `OVERRIDE` in the console to pause all operations.

## Troubleshooting

- **UI not appearing**: Ensure `customtkinter` is installed (`pip install customtkinter`).
- **Voice not working**: Check if FFmpeg is installed and accessible in your system's PATH.
- **Self-Healing**: If Oracle encounters an error, check `logs/oracle_actions.log` to see the self-repair attempts.
