import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

project_name = "ai-ticket-system"

# List of all files and folders to create based on the modular architecture
list_of_files = [
    # Backend files
    "backend/app/api/__init__.py",
    "backend/app/api/v1/__init__.py",
    "backend/app/api/v1/routes/__init__.py",
    "backend/app/api/v1/routes/tickets.py",
    "backend/app/api/v1/routes/users.py",
    "backend/app/api/v1/routes/webhooks.py",
    "backend/app/api/v1/dependencies.py",
    "backend/app/core/__init__.py",
    "backend/app/core/config.py",
    "backend/app/core/security.py",
    "backend/app/core/logging.py",
    "backend/app/db/__init__.py",
    "backend/app/db/database.py",
    "backend/app/db/models/__init__.py",
    "backend/app/db/models/ticket_model.py",
    "backend/app/db/models/user_model.py",
    "backend/app/schemas/__init__.py",
    "backend/app/schemas/ticket_schema.py",
    "backend/app/schemas/user_schema.py",
    "backend/app/services/__init__.py",
    "backend/app/services/ticket_service.py",
    "backend/app/services/email_service.py",
    "backend/app/ai/__init__.py",
    "backend/app/ai/engine.py",
    "backend/app/ai/llm_client.py",
    "backend/app/ai/prompts/__init__.py",
    "backend/app/ai/prompts/triage_prompt.py",
    "backend/app/ai/prompts/draft_reply_prompt.py",
    "backend/app/ai/agents/__init__.py",
    "backend/app/ai/agents/resolution_agent.py",
    "backend/app/ai/rag/__init__.py",
    "backend/app/ai/rag/embedder.py",
    "backend/app/ai/rag/vector_db.py",
    "backend/tests/__init__.py",
    "backend/requirements.txt",
    "backend/setup.py",
    "backend/main.py",
    
    # Frontend files
    "frontend/src/app/(customer)/dashboard/page.tsx",
    "frontend/src/app/(agent)/workspace/page.tsx",
    "frontend/src/app/layout.tsx",
    "frontend/src/app/page.tsx",
    "frontend/src/components/ui/Button.tsx",
    "frontend/src/components/tickets/TicketList.tsx",
    "frontend/src/components/tickets/TicketDetail.tsx",
    "frontend/src/components/ai/AiDraftViewer.tsx",
    "frontend/src/lib/api_client.ts",
    "frontend/src/hooks/useTickets.ts",
    "frontend/src/store/ticketStore.ts",
    "frontend/src/types/index.ts",
    "frontend/package.json",
    "frontend/tailwind.config.ts",
    "frontend/tsconfig.json",
    
    # Root level configuration files
    "docker-compose.yml",
    ".gitignore",
    "README.md"
]

def create_project_structure():
    logging.info(f"Initializing project structure for: {project_name}")
    
    for filepath in list_of_files:
        # Convert to Path object for cross-platform compatibility
        filepath = Path(filepath)
        
        # Split into directory path and file name
        filedir, filename = os.path.split(filepath)

        # Create directory if it doesn't exist
        if filedir != "":
            os.makedirs(filedir, exist_ok=True)
            logging.info(f"Creating directory: {filedir} for the file {filename}")

        # Create empty file if it doesn't exist or is empty
        if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
            with open(filepath, 'w') as f:
                # Add basic content to some key files to make them valid
                if filename.endswith('.py') and filename != '__init__.py':
                    f.write("# TODO: Implement module logic\n")
                elif filename == 'requirements.txt':
                    f.write("fastapi\nuvicorn\npydantic\nsqlalchemy\n")
                elif filename == 'package.json':
                    f.write("{\n  \"name\": \"frontend\",\n  \"version\": \"0.1.0\"\n}\n")
                else:
                    pass
            logging.info(f"Creating file: {filepath}")
        else:
            logging.info(f"File already exists: {filename}")

if __name__ == '__main__':
    create_project_structure()
    logging.info("Project structure generation complete!")
