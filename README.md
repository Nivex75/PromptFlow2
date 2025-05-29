# PromptFlow - AI-Powered Document Analysis Platform

## 🎯 Overview

PromptFlow is a sophisticated document analysis system that leverages GPT-4 to process legal documents through customizable workflows. The platform features a **project-based architecture** that provides clear workspace isolation and powerful batch processing capabilities.

## ✨ Key Enhancements

### 1. Project-Centric UI
- **Clear Project Context**: When you're working in a project, the entire UI is focused on that project
- **Visual Distinction**: Project workspace has a distinctive header showing you're "inside" the project
- **Isolated Workspaces**: Each project contains its own documents, workflows, and results
- **Easy Navigation**: Simple project switching and clear exit options

### 2. Batch Processing Power
- **One-Click Processing**: "Run Workflows and Generate Results" button appears when ready
- **Smart Detection**: Button only shows when project has both documents and workflows
- **Progress Tracking**: Real-time progress bar with detailed status updates
- **Error Handling**: Comprehensive error reporting for failed operations
- **Bulk Results**: Generate multiple reports across all document-workflow combinations

## 🏗️ Architecture

### Project Structure
```
Project
├── Documents (Source files for analysis)
├── Workflows (Analysis sequences)
├── Results (Generated outputs)
└── Templates (Shared across projects)
```

### Key Components

1. **Project Manager** (`project_manager.py`)
   - Creates and manages project workspaces
   - Tracks project metadata and statistics
   - Handles project isolation

2. **Document Processor** (`document_processor.py`)
   - Supports Word (.docx) and PDF formats
   - Robust text extraction with fallbacks
   - Project-aware document storage

3. **Workflow Manager** (`workflow_manager.py`)
   - Project-specific workflow creation
   - Global workflow library
   - Import/export capabilities

4. **Batch Processor** (in `main.py`)
   - Processes all documents × all workflows
   - Progress tracking and status updates
   - Automatic template matching
   - Comprehensive error handling

5. **Template System** (`template_manager.py`)
   - Marker-based content replacement
   - Global template library
   - Format preservation

## 🚀 Getting Started

### 1. Create a Project
```python
# From the main screen
1. Enter project name
2. Add optional description
3. Click "Create Project"
```

### 2. Enter Project Workspace
```python
# Click "Open" on any project card
# You'll see the project header with:
- Project name and description
- Exit button
- Project-specific tabs
```

### 3. Upload Documents
```python
# In Documents tab
1. Click "Upload New Document"
2. Select Word or PDF files
3. Name and describe each document
```

### 4. Create Workflows
```python
# In Workflows tab
1. Click "Create New Workflow"
2. Add prompts from library or create custom
3. Assign output template
4. Test individual prompts
```

### 5. Batch Process
```python
# When ready (documents + workflows exist)
1. Look for "Run Workflows and Generate Results" button
2. Click to start batch processing
3. Monitor progress bar
4. Check Results tab for outputs
```

## 💡 Features

### Project Management
- Create unlimited projects
- Visual project cards with statistics
- Quick project switching
- Project deletion with safety checks

### Document Handling
- Multi-format support (DOCX, PDF)
- Text extraction with error handling
- Preview capabilities
- Search functionality
- Project-isolated storage

### Workflow Design
- Visual workflow builder
- Prompt library integration
- Custom prompt creation
- Template assignment
- Individual prompt testing

### Batch Processing
- Automatic detection of readiness
- All documents × all workflows processing
- Real-time progress tracking
- Error aggregation and reporting
- Result organization by execution

### Results Management
- Chronological result listing
- Document preview and download
- Execution metadata tracking
- Result deletion options

## 🔧 Technical Implementation

### Session State Management
```python
# Project context maintained throughout session
st.session_state.current_project_id
st.session_state.workflow_mode
st.session_state.test_results
```

### Batch Processing Algorithm
```python
for document in project_documents:
    for workflow in project_workflows:
        # Process workflow against document
        # Record results
        # Update progress
        # Handle errors
```

### UI State Flow
```
Main Screen → Project Selection → Project Workspace
                ↓                        ↓
         Create New Project    [Documents|Workflows|Results|Templates]
                                         ↓
                                 Batch Process Button
                                         ↓
                                  Progress & Results
```

## 📊 Performance Optimizations

- **Lazy Loading**: Documents loaded only when needed
- **Progress Streaming**: Real-time updates during batch processing
- **Error Recovery**: Continue processing despite individual failures
- **Smart Caching**: Template and prompt results cached during session

## 🎨 UI/UX Enhancements

### Visual Design
- Gradient animations for headers
- Smooth transitions and hover effects
- Clear visual hierarchy
- Consistent color scheme
- Responsive card layouts

### User Feedback
- Progress bars with percentages
- Status messages during operations
- Success celebrations (balloons!)
- Clear error messages
- Contextual help text

### Navigation
- Breadcrumb-style project context
- Clear exit points
- Tab-based organization
- Quick action buttons
- Keyboard shortcuts support

## 🚦 Error Handling

### Batch Processing Errors
- Individual failure tracking
- Aggregate error reporting
- Continue-on-error capability
- Detailed error messages

### Document Processing Errors
- Format validation
- Extraction fallbacks
- Size limit checking
- Encoding detection

## 🔒 Data Isolation

- Projects are completely isolated
- No cross-project data access
- Separate storage paths
- Independent workflow contexts

## 📈 Future Enhancements

1. **Parallel Processing**: Multi-threaded batch operations
2. **Selective Batch**: Choose specific document-workflow pairs
3. **Progress Persistence**: Resume interrupted batches
4. **Export Options**: Bulk export of results
5. **Project Templates**: Pre-configured project setups
6. **Collaboration**: Multi-user project access
7. **Version Control**: Track workflow and template changes
8. **Analytics**: Processing statistics and insights

## 🤝 Contributing

The codebase is organized for easy extension:
- Add new document formats in `document_processor.py`
- Create workflow templates in `workflow_manager.py`
- Enhance UI components in `main.py`
- Add styling in `style.css`

## 📝 License

This project is provided as-is for demonstration and educational purposes.