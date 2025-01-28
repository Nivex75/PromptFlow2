# PromptFlow - Document Analysis System Prototype

A  Python-based document analysis system that leverages GPT-4 for structured legal document processing. This prototype demonstrates a service-oriented architecture for processing legal documents through customizable prompts that build into workflows with template-based output generation.

## Core Features

- Document Processing: Upload and analyze Word documents
- Prompt Library: Create, test, and manage reusable prompts
- Workflow Management: Build custom  workflows by asembling and adapting prompts
- GPT-4 Integration
- Template System: Convert workflow outputs into formatted documents

## System Architecture

### Service Components

1. **DocumentProcessor** (`document_processor.py`)
   - Handles DOCX parsing using python-docx
   - Preserves document structure including tables
   - Maintains extracted text in memory for workflow processing

2. **PromptManager** (`prompt_manager.py`)
   - Manages prompt library and versioning
   - JSON-based storage (`prompts.json`)
   - Supports system and analysis prompts
   - CRUD operations for prompt management

3. **WorkflowManager** (`workflow_manager.py`)
   - Orchestrates multi-prompt document analysis
   - JSON-based workflow storage (`workflows.json`)
   - Template-based output generation
   - Workflow state management

4. **GPTHandler** (`gpt_handler.py`)
   - Manages OpenAI API interactions
   - Processes prompts sequentially
   - Maintains context between prompts
   - Handles response aggregation

### Template System

- Document template functionality for formatted outputs
- Supports markdown and HTML formats
- Live preview with actual outputs
- Template editing during review
- Marker system using {PROMPT_NAME_OUTPUT} format
- Needs to adap to allow download in .docx

## Data Flow
```
Document Upload → Document Processor → Text Extraction
                                   ↓
                             Memory Storage
                                   ↓
Workflow Execution → Prompt Processing → GPT Analysis
                                   ↓
                         Template Processing
                                   ↓
                       Formatted Output Generation
```

## Data Storage Implementation

### Prompts (`prompts.json`)
```json
{
    "system_prompt": string,
    "prompts": [
        {
            "Name": string,
            "Description": string,
            "Prompt": string
        }
    ]
}
```

### Workflows (`workflows.json`)
```json
{
    "name": string,
    "description": string,
    "created_at": ISO8601,
    "status": "draft" | "completed",
    "prompts": Array<PromptConfig>,
    "template": string | null,
    "output_format": "markdown" | "html"
}
```

## Technical Dependencies

- streamlit==1.30.0: UI framework
- python-docx==1.0.0: Document processing
- openai==1.0.0: GPT-4 integration
- JSON: Data persistence

## Current Technical Limitations

1. **Processing**
   - Single-threaded document processing
   - In-memory document state
   - No persistent document cache

2. **Storage**
   - JSON-based persistence
   - Limited concurrent access
   - No document persistence

3. **Scalability**
   - Limited concurrent workflow support
   - Memory constraints for large documents
   - No distributed processing

## Implementation Notes

- Built using Streamlit for rapid prototyping
- Event-driven architecture for UI updates
- Template-based output generation
- Error boundary implementation
- State isolation between components

## Extension Points

1. **Document Processing**
   - PDF support integration
   - Document chunking implementation
   - Enhanced formatting preservation

2. **Storage Layer**
   - Database integration
   - Document persistence
   - Concurrent access support

3. **Processing Engine**
   - Distributed processing
   - Batch document support
   - Enhanced caching

4. **Template System**
   - Enhanced formatting options
   - Custom styling support
   - Multiple output formats
