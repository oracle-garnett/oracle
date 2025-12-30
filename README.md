# Oracle: Advanced Local AI Assistant

Oracle is a sophisticated, modular AI assistant designed to live locally on a laptop while maintaining persistent memory via cloud integration. It features a floating, collapsible UI, self-healing capabilities, and robust administrative safeguards.

## Project Structure

The project is organized into several key modules to ensure maintainability and scalability:

| Directory | Purpose |
| :--- | :--- |
| `core/` | Contains the central logic, task execution engine, and self-healing mechanisms. |
| `ui/` | Handles the floating, collapsible user interface. |
| `memory/` | Manages local and cloud-based memory persistence with encryption. |
| `safeguards/` | Implements administrative overrides, resource monitoring, and action logging. |
| `models/` | Interface for integrating various AI models (the "brain"). |
| `logs/` | Stores operational logs for transparency and debugging. |
| `scripts/` | Contains utility scripts, including the PowerShell startup script. |

## Core Principles

1. **Autonomy with Control**: Oracle is designed to complete tasks and fix its own code, but always remains under the absolute authority of the user via administrative overrides.
2. **Persistence**: Memory is stored securely in the cloud, allowing Oracle to "remember" interactions across sessions.
3. **Accessibility**: A floating UI ensures Oracle is always available, regardless of the active application.
4. **Transparency**: Every action and thought is logged for user review.
