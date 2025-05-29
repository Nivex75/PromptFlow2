import streamlit as st
import json
import os
from prompt_manager import PromptManager
from document_processor import DocumentProcessor
from gpt_handler import GPTHandler
from workflow_manager import WorkflowManager
from template_manager import TemplateManager
from source_manager import SourceDocumentManager
from project_manager import ProjectManager
from execution_manager import ExecutionManager
from help import show_help

# Configure the Streamlit page with wide layout and collapsed sidebar
st.set_page_config(
    page_title="PromptFlow",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load and apply custom CSS styles for the application
with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def create_loading_spinner(message):
    """Creates a custom loading spinner with animated progress bar"""
    spinner_container = st.empty()
    with spinner_container.container():
        st.markdown(
            f"""
            <div class="processing-overlay">
                <div class="stSpinner"></div>
                <p class="pulse-text">{message}</p>
                <div class="progress-container">
                    <div class="progress-bar"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    return spinner_container

def initialize_session_state():
    """Initialize all required session state variables if they don't exist"""
    # Document-related state
    if 'current_document' not in st.session_state:
        st.session_state.current_document = None
    if 'current_document_text' not in st.session_state:
        st.session_state.current_document_text = None
    if 'selected_source_document_id' not in st.session_state:
        st.session_state.selected_source_document_id = None
    if 'selected_template_id' not in st.session_state:
        st.session_state.selected_template_id = None

    # Core managers state
    if 'prompt_manager' not in st.session_state:
        st.session_state.prompt_manager = PromptManager()
    if 'workflow_manager' not in st.session_state:
        st.session_state.workflow_manager = WorkflowManager()
    if 'gpt_handler' not in st.session_state:
        st.session_state.gpt_handler = GPTHandler()
    if 'template_manager' not in st.session_state:
        st.session_state.template_manager = TemplateManager()
    if 'source_manager' not in st.session_state:
        st.session_state.source_manager = SourceDocumentManager()
    if 'project_manager' not in st.session_state:
        st.session_state.project_manager = ProjectManager()
    if 'execution_manager' not in st.session_state:
        st.session_state.execution_manager = ExecutionManager()

    # Project-related state
    if 'current_project_id' not in st.session_state:
        st.session_state.current_project_id = None

    # Initialize sample templates on first run
    if 'templates_initialized' not in st.session_state:
        st.session_state.template_manager.create_sample_templates()
        st.session_state.templates_initialized = True

    # Other state variables
    if 'selected_prompts' not in st.session_state:
        st.session_state.selected_prompts = []
    if 'last_results' not in st.session_state:
        st.session_state.last_results = {}
    if 'show_create_prompt' not in st.session_state:
        st.session_state.show_create_prompt = False
    if 'editing_system_prompt' not in st.session_state:
        st.session_state.editing_system_prompt = False
    if 'current_workflow' not in st.session_state:
        st.session_state.current_workflow = None
    if 'workflow_mode' not in st.session_state:
        st.session_state.workflow_mode = None
    if 'workflow_results' not in st.session_state:
        st.session_state.workflow_results = {}
    if 'test_results' not in st.session_state:
        st.session_state.test_results = {}

def show_project_context_bar():
    """Display the current project context bar"""
    if st.session_state.current_project_id:
        project = st.session_state.project_manager.get_project(st.session_state.current_project_id)
        if project:
            with st.container():
                col1, col2, col3 = st.columns([6, 2, 1])
                with col1:
                    st.info(f"🗂️ **Current Project:** {project['name']}")
                with col2:
                    # Quick project switcher
                    projects = st.session_state.project_manager.get_projects()
                    project_names = ["Switch Project..."] + [p['name'] for p in projects if p['id'] != st.session_state.current_project_id]
                    project_ids = [None] + [p['id'] for p in projects if p['id'] != st.session_state.current_project_id]

                    selected = st.selectbox(
                        "Quick Switch",
                        options=project_names,
                        key="project_switcher",
                        label_visibility="collapsed"
                    )

                    if selected != "Switch Project..." and selected:
                        idx = project_names.index(selected)
                        st.session_state.current_project_id = project_ids[idx]
                        st.rerun()

                with col3:
                    if st.button("✖️ Close", key="close_project"):
                        st.session_state.current_project_id = None
                        st.rerun()
            st.markdown("---")

def show_projects_tab():
    """Display the projects management interface"""
    st.header("📁 Projects")
    st.markdown("Organize your documents and workflows by project")

    # Create new project section
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Create New Project")
        with col2:
            if st.button("➕ Create New", type="primary", key="create_new_project_btn"):
                st.session_state.show_create_project_dialog = True

    # Create project dialog
    if st.session_state.get('show_create_project_dialog', False):
        with st.container():
            st.markdown("### New Project Details")
            project_name = st.text_input("Project Name", key="new_project_name_input")
            project_description = st.text_area(
                "Description (optional)", 
                key="new_project_desc_input",
                height=80
            )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Create", type="primary", key="confirm_create_project"):
                    if project_name:
                        try:
                            project = st.session_state.project_manager.create_project(
                                project_name, 
                                project_description
                            )
                            st.success(f"✅ Created project: {project['name']}")
                            # Automatically select the newly created project
                            st.session_state.current_project_id = project['id']
                            st.session_state.show_create_project_dialog = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating project: {str(e)}")
                    else:
                        st.error("Please enter a project name")
            with col2:
                if st.button("Cancel", key="cancel_create_project"):
                    st.session_state.show_create_project_dialog = False
                    st.rerun()

    # Display existing projects
    st.markdown("### 📚 Your Projects")

    projects = st.session_state.project_manager.get_projects()

    if not projects:
        st.info("No projects yet. Create your first project above!")
    else:
        # Show current project selection status
        if st.session_state.current_project_id:
            current_project = st.session_state.project_manager.get_project(st.session_state.current_project_id)
            if current_project:
                st.success(f"✅ Currently working in: **{current_project['name']}**")
        else:
            st.info("💡 Select a project to start working with documents and workflows")

        # Display projects in a grid
        for i in range(0, len(projects), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(projects):
                    project = projects[i + j]
                    with col:
                        with st.container():
                            # Update document count from source manager
                            doc_count = st.session_state.source_manager.get_project_document_count(project['id'])
                            workflow_count = len(st.session_state.workflow_manager.get_workflows(project['id']))
                            
                            # Highlight current project
                            is_current = project['id'] == st.session_state.current_project_id
                            border_style = "border: 3px solid #1A2543;" if is_current else "border: 1px solid #E0E4EC;"
                            bg_color = "background-color: #F0F8FF;" if is_current else "background-color: white;"
                            
                            st.markdown(f"""
                            <div style="{border_style} border-radius: 8px; 
                                        padding: 1rem; margin-bottom: 1rem; {bg_color}">
                                <h4 style="margin: 0 0 0.5rem 0;">{project['name']}</h4>
                                <p style="color: #666; font-size: 0.9em; margin: 0.5rem 0;">
                                    {project.get('description', 'No description')}
                                </p>
                                <p style="color: #999; font-size: 0.8em; margin: 0;">
                                    Created: {project['created_at'][:10]} | 
                                    Documents: {doc_count} | 
                                    Workflows: {workflow_count}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                button_type = "secondary" if is_current else "primary"
                                button_label = "✓ Current" if is_current else "📂 Open"
                                if st.button(button_label, key=f"open_{project['id']}", type=button_type, disabled=is_current):
                                    st.session_state.current_project_id = project['id']
                                    st.success(f"Opened project: {project['name']}")
                                    st.rerun()
                            with col_b:
                                if st.button("📊 Stats", key=f"stats_{project['id']}"):
                                    with st.expander("Project Statistics", expanded=True):
                                        st.write(f"**Documents:** {doc_count}")
                                        st.write(f"**Workflows:** {workflow_count}")
                                        recent_execs = st.session_state.execution_manager.get_recent_executions(
                                            limit=5, 
                                            project_id=project['id']
                                        )
                                        st.write(f"**Recent Executions:** {len(recent_execs)}")
                            with col_c:
                                if st.button("🗑️ Delete", key=f"delete_{project['id']}"):
                                    if project['id'] == st.session_state.current_project_id:
                                        st.error("Cannot delete the currently active project. Please close it first.")
                                    else:
                                        # Check if project has documents or workflows
                                        if doc_count > 0 or workflow_count > 0:
                                            st.warning(f"Project has {doc_count} documents and {workflow_count} workflows. Delete anyway?")
                                            if st.button("Yes, Delete", key=f"confirm_delete_{project['id']}"):
                                                if st.session_state.project_manager.delete_project(project['id']):
                                                    st.rerun()
                                        else:
                                            if st.session_state.project_manager.delete_project(project['id']):
                                                st.rerun()

def show_source_documents_tab():
    """Display the source documents management interface"""
    st.header("📄 Source Documents")

    # Check if we're in a project context
    if not st.session_state.current_project_id:
        st.warning("Please select a project first to manage documents")
        if st.button("Go to Projects"):
            st.rerun()
        return

    st.markdown("Upload and manage documents for this project")

    # Upload section
    with st.expander("➕ Upload New Document", expanded=False):
        uploaded_file = st.file_uploader(
            "Choose a Word or PDF document",
            type=['docx', 'pdf'],
            key="source_upload"
        )

        if uploaded_file:
            col1, col2 = st.columns([3, 1])
            with col1:
                doc_name = st.text_input(
                    "Document Name",
                    value=os.path.splitext(uploaded_file.name)[0],
                    key="source_name"
                )
                doc_description = st.text_area(
                    "Description (optional)",
                    key="source_desc",
                    height=80
                )

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📤 Upload", type="primary", key="upload_source"):
                    try:
                        spinner = create_loading_spinner("Uploading and processing document...")
                        doc_info = st.session_state.source_manager.upload_document(
                            uploaded_file, 
                            doc_name, 
                            doc_description,
                            project_id=st.session_state.current_project_id  # Add project context
                        )
                        spinner.empty()
                        st.success(f"✅ Document '{doc_name}' uploaded successfully!")
                        st.rerun()
                    except Exception as e:
                        spinner.empty()
                        st.error(f"❌ Error uploading document: {str(e)}")

    # Document library
    st.markdown("### 📚 Project Documents")

    # Search and filter
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("🔍 Search documents", key="search_source")

    # Get documents for current project
    if search_query:
        documents = st.session_state.source_manager.search_documents(
            search_query, 
            project_id=st.session_state.current_project_id
        )
    else:
        documents = st.session_state.source_manager.get_documents(
            project_id=st.session_state.current_project_id
        )

    if documents:
        # Display documents in a grid
        for i in range(0, len(documents), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(documents):
                    doc = documents[i + j]
                    with col:
                        with st.container():
                            st.markdown(f"""
                            <div style="border: 1px solid #E0E4EC; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                                <h4>{doc['name']}</h4>
                                <p style="color: #666; font-size: 0.9em;">{doc.get('description', 'No description')}</p>
                                <p style="color: #999; font-size: 0.8em;">
                                    Uploaded: {doc['uploaded_at'][:10]} | 
                                    Size: {doc['file_size'] // 1024}KB |
                                    Length: {doc['text_length']} chars
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                if st.button("👁️ Preview", key=f"preview_{doc['id']}"):
                                    st.session_state.preview_doc_id = doc['id']
                            with col_b:
                                if st.button("✅ Select", key=f"select_{doc['id']}", type="primary"):
                                    st.session_state.selected_source_document_id = doc['id']
                                    st.session_state.current_document = doc['name']
                                    st.session_state.current_document_text = st.session_state.source_manager.get_document_text(
                                        doc['id'],
                                        project_id=st.session_state.current_project_id
                                    )
                                    st.success(f"Selected '{doc['name']}' for analysis")
                            with col_c:
                                if st.button("🗑️ Delete", key=f"delete_{doc['id']}"):
                                    if st.session_state.source_manager.delete_document(
                                        doc['id'],
                                        project_id=st.session_state.current_project_id
                                    ):
                                        st.rerun()

        # Preview section
        if hasattr(st.session_state, 'preview_doc_id'):
            doc_text = st.session_state.source_manager.get_document_text(
                st.session_state.preview_doc_id,
                project_id=st.session_state.current_project_id
            )
            if doc_text:
                st.markdown("### Document Preview")
                st.text_area("", doc_text[:2000] + "...", height=300, disabled=True)
    else:
        st.info("📭 No documents in this project yet. Upload your first document above!")

def show_workflow_library_tab():
    """Display the global workflow library (read-only)"""
    st.header("📚 Workflow Library")
    st.markdown("Browse and copy global workflow templates")

    workflows = st.session_state.workflow_manager.get_workflows(project_id=None)

    if not workflows:
        st.info("No global workflows available yet.")
    else:
        for workflow in workflows:
            with st.expander(f"📋 {workflow['name']}", expanded=False):
                st.markdown(f"**Description:** {workflow.get('description', 'No description')}")
                st.markdown(f"**Status:** {workflow['status'].title()}")
                st.markdown(f"**Prompts:** {len(workflow.get('prompts', []))}")

                if st.session_state.current_project_id:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        new_name = st.text_input(
                            "New name (optional)",
                            value=f"{workflow['name']} (Copy)",
                            key=f"copy_name_{workflow['name']}"
                        )
                    with col2:
                        if st.button("📥 Copy to Project", key=f"copy_{workflow['name']}"):
                            if st.session_state.workflow_manager.copy_workflow_to_project(
                                workflow['name'],
                                st.session_state.current_project_id,
                                new_name
                            ):
                                st.success(f"Copied '{workflow['name']}' to current project")
                                st.rerun()
                else:
                    st.info("Select a project to copy this workflow")

def show_project_workflows_tab():
    """Display project-specific workflows"""
    st.header("⚙️ Project Workflows")

    if not st.session_state.current_project_id:
        st.warning("Please select a project first to manage workflows")
        return

    # Initialize workflow state
    if 'workflow_step' not in st.session_state:
        st.session_state.workflow_step = 'select'
    if 'selected_workflow_id' not in st.session_state:
        st.session_state.selected_workflow_id = None
    if 'workflow_source_doc' not in st.session_state:
        st.session_state.workflow_source_doc = None
    if 'workflow_template' not in st.session_state:
        st.session_state.workflow_template = None

    # Add import from library button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("📚 Import from Library", key="import_workflow_btn"):
            st.session_state.show_library_import = True

    # Show library import dialog
    if st.session_state.get('show_library_import', False):
        with st.container():
            st.markdown("### Import Workflow from Library")
            global_workflows = st.session_state.workflow_manager.get_workflows(project_id=None)

            if global_workflows:
                workflow_names = [w['name'] for w in global_workflows]
                selected_workflow = st.selectbox(
                    "Select workflow to import",
                    workflow_names,
                    key="import_workflow_select"
                )

                new_name = st.text_input(
                    "Name in project",
                    value=f"{selected_workflow} (Project Copy)",
                    key="import_workflow_name"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Import", type="primary", key="confirm_import"):
                        if st.session_state.workflow_manager.copy_workflow_to_project(
                            selected_workflow,
                            st.session_state.current_project_id,
                            new_name
                        ):
                            st.success(f"Imported '{selected_workflow}' to project")
                            st.session_state.show_library_import = False
                            st.rerun()
                with col2:
                    if st.button("Cancel", key="cancel_import"):
                        st.session_state.show_library_import = False
                        st.rerun()
            else:
                st.info("No workflows in library to import")

    # Step indicator
    steps = ['1. Select Workflow', '2. Configure', '3. Run']
    current_step = 0 if st.session_state.workflow_step == 'select' else (1 if st.session_state.workflow_step == 'configure' else 2)

    cols = st.columns(len(steps))
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i == current_step:
                st.info(f"**{step}**")
            elif i < current_step:
                st.success(f"✓ {step}")
            else:
                st.text(step)

    st.markdown("---")

    # Handle different steps
    if st.session_state.workflow_step == 'select':
        show_project_workflow_selection()
    elif st.session_state.workflow_step == 'configure':
        show_workflow_configuration()
    elif st.session_state.workflow_step == 'review':
        show_workflow_execution()

def show_project_workflow_selection():
    """Step 1: Select or create a project workflow"""

    # Create new workflow section
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader("Create New Workflow")
        with col2:
            if st.button("➕ Create New", type="primary", key="create_new_workflow_btn"):
                st.session_state.show_create_dialog = True

    # Create workflow dialog
    if st.session_state.get('show_create_dialog', False):
        with st.container():
            st.markdown("### New Workflow Details")
            new_name = st.text_input("Workflow Name", key="new_workflow_name_input")
            new_desc = st.text_area("Description (optional)", key="new_workflow_desc_input", height=80)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Create", type="primary", key="confirm_create"):
                    if new_name:
                        if st.session_state.workflow_manager.create_workflow(
                            new_name, 
                            new_desc,
                            project_id=st.session_state.current_project_id
                        ):
                            st.session_state.selected_workflow_id = new_name
                            st.session_state.workflow_step = 'configure'
                            st.session_state.show_create_dialog = False
                            st.rerun()
                        else:
                            st.error("A workflow with this name already exists in this project")
                    else:
                        st.error("Please enter a workflow name")
            with col2:
                if st.button("Cancel", key="cancel_create"):
                    st.session_state.show_create_dialog = False
                    st.rerun()

    # Existing workflows section
    st.markdown("---")
    st.subheader("📚 Project Workflows")

    workflows = st.session_state.workflow_manager.get_workflows(
        project_id=st.session_state.current_project_id
    )

    if workflows:
        for i in range(0, len(workflows), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(workflows):
                    workflow = workflows[i + j]
                    with col:
                        with st.container():
                            st.markdown(f"""
                            <div style="border: 2px solid #E0E4EC; border-radius: 10px; padding: 1.5rem; 
                                        margin-bottom: 1rem; background-color: #FAFBFC;">
                                <h4 style="margin: 0 0 0.5rem 0;">{workflow['name']}</h4>
                                <p style="color: #666; margin: 0.5rem 0;">{workflow.get('description', 'No description')}</p>
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 1rem;">
                                    <span style="color: #999; font-size: 0.9em;">
                                        Status: <strong>{workflow['status'].title()}</strong> | 
                                        Prompts: <strong>{len(workflow.get('prompts', []))}</strong>
                                    </span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                if st.button("📋 Select", key=f"select_wf_{workflow['name']}", type="primary"):
                                    st.session_state.selected_workflow_id = workflow['name']
                                    st.session_state.workflow_step = 'configure'
                                    st.rerun()
                            with col_b:
                                if st.button("✏️ Edit", key=f"quick_edit_{workflow['name']}"):
                                    st.session_state.workflow_mode = "edit"
                                    st.session_state.current_workflow = workflow['name']
                                    st.rerun()
                            with col_c:
                                if st.button("🗑️ Delete", key=f"delete_wf_{workflow['name']}"):
                                    if st.session_state.workflow_manager.delete_workflow(
                                        workflow['name'],
                                        project_id=st.session_state.current_project_id
                                    ):
                                        st.success(f"Deleted '{workflow['name']}'")
                                        st.rerun()
    else:
        st.info("No workflows in this project yet. Create a new one or import from library!")

def show_workflow_configuration():
    """Step 2: Configure workflow with source document and template"""

    workflow = st.session_state.workflow_manager.get_workflow(
        st.session_state.selected_workflow_id,
        project_id=st.session_state.current_project_id
    )
    if not workflow:
        st.error("Workflow not found")
        return

    # Header with back button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader(f"Configure: {workflow['name']}")
    with col2:
        if st.button("← Back", key="back_to_selection"):
            st.session_state.workflow_step = 'select'
            st.rerun()

    # Show workflow details
    with st.expander("ℹ️ Workflow Details", expanded=False):
        st.write(f"**Description:** {workflow.get('description', 'No description')}")
        st.write(f"**Status:** {workflow['status'].title()}")
        st.write(f"**Prompts:** {len(workflow.get('prompts', []))}")
        if workflow.get('prompts'):
            st.write("**Prompt Names:**")
            for prompt in workflow['prompts']:
                st.write(f"- {prompt['name']}")

    st.markdown("---")

    # Document selection
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📄 Select Source Document")

        source_docs = st.session_state.source_manager.get_documents(
            project_id=st.session_state.current_project_id
        )
        if source_docs:
            doc_options = ["Select a document..."] + [f"{doc['name']} ({doc['uploaded_at'][:10]})" for doc in source_docs]
            doc_values = [None] + [doc['id'] for doc in source_docs]

            selected_idx = 0
            if st.session_state.workflow_source_doc:
                try:
                    selected_idx = doc_values.index(st.session_state.workflow_source_doc)
                except ValueError:
                    pass

            selected = st.selectbox(
                "Choose document to analyze",
                options=doc_options,
                index=selected_idx,
                key="source_doc_selector"
            )

            if selected != "Select a document...":
                doc_id = doc_values[doc_options.index(selected)]
                st.session_state.workflow_source_doc = doc_id

                doc = st.session_state.source_manager.get_document(
                    doc_id,
                    project_id=st.session_state.current_project_id
                )
                if doc:
                    with st.container():
                        st.markdown(f"""
                        <div style="background-color: #F0F8FF; padding: 1rem; border-radius: 5px; margin-top: 0.5rem;">
                            <strong>Selected:</strong> {doc['name']}<br>
                            <small>Size: {doc['file_size'] // 1024}KB | 
                            Length: {doc['text_length']} chars</small>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning("No documents in this project. Please upload documents first.")

    with col2:
        st.markdown("### 📝 Select Template")

        templates = st.session_state.template_manager.get_templates()
        if templates:
            template_options = ["Select a template..."] + [f"{t['name']}" for t in templates]
            template_values = [None] + [t['id'] for t in templates]

            selected_idx = 0
            if workflow.get('template_id'):
                try:
                    selected_idx = template_values.index(workflow['template_id'])
                except ValueError:
                    pass
            elif st.session_state.workflow_template:
                try:
                    selected_idx = template_values.index(st.session_state.workflow_template)
                except ValueError:
                    pass

            selected = st.selectbox(
                "Choose output template",
                options=template_options,
                index=selected_idx,
                key="template_selector"
            )

            if selected != "Select a template...":
                template_id = template_values[template_options.index(selected)]
                st.session_state.workflow_template = template_id

                template = st.session_state.template_manager.get_template(template_id)
                if template:
                    markers = st.session_state.template_manager.get_template_markers(template_id)
                    with st.container():
                        st.markdown(f"""
                        <div style="background-color: #F0FFF0; padding: 1rem; border-radius: 5px; margin-top: 0.5rem;">
                            <strong>Selected:</strong> {template['name']}<br>
                            <small>Markers: {', '.join(markers[:3]) if markers else 'None'}
                            {'...' if len(markers) > 3 else ''}</small>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.warning("No templates available. Please upload templates in the Template Documents tab.")

    # Action buttons
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    ready = st.session_state.workflow_source_doc and st.session_state.workflow_template

    with col1:
        if st.button("✏️ Edit Workflow", key="edit_workflow_btn", 
                     help="Edit prompts and settings"):
            st.session_state.workflow_mode = "edit"
            st.session_state.current_workflow = workflow['name']
            st.rerun()

    with col2:
        if st.button("🔄 Test Prompts", key="test_workflow_btn", 
                     disabled=not st.session_state.workflow_source_doc,
                     help="Test and refine individual prompts"):
            if st.session_state.workflow_source_doc:
                st.session_state.current_document_text = st.session_state.source_manager.get_document_text(
                    st.session_state.workflow_source_doc,
                    project_id=st.session_state.current_project_id
                )
                st.session_state.workflow_mode = "test"
                st.session_state.current_workflow = workflow['name']
                st.rerun()

    with col3:
        if st.button("▶️ Run Workflow", key="run_workflow_btn", 
                     type="primary", 
                     disabled=not ready,
                     help="Process document and generate output"):
            if ready:
                st.session_state.workflow_step = 'review'
                st.rerun()

    if not ready:
        st.info("👆 Please select both a source document and a template to continue")

def show_workflow_execution():
    """Step 3: Review configuration and execute workflow"""

    workflow = st.session_state.workflow_manager.get_workflow(
        st.session_state.selected_workflow_id,
        project_id=st.session_state.current_project_id
    )
    if not workflow:
        st.error("Workflow not found")
        return

    # Header with back button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.subheader(f"Run: {workflow['name']}")
    with col2:
        if st.button("← Back", key="back_to_configure"):
            st.session_state.workflow_step = 'configure'
            st.rerun()

    # Show configuration summary
    st.markdown("### 📋 Configuration Summary")

    source_doc = st.session_state.source_manager.get_document(
        st.session_state.workflow_source_doc,
        project_id=st.session_state.current_project_id
    )
    template = st.session_state.template_manager.get_template(st.session_state.workflow_template)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div style="background-color: #F0F8FF; padding: 1rem; border-radius: 8px;">
            <h4 style="margin: 0 0 0.5rem 0;">📄 Source Document</h4>
            <strong>{source_doc['name'] if source_doc else 'Unknown'}</strong><br>
            <small>{source_doc['file_type'] if source_doc else ''} | 
            {source_doc['file_size'] // 1024 if source_doc else 0}KB</small>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background-color: #F0FFF0; padding: 1rem; border-radius: 8px;">
            <h4 style="margin: 0 0 0.5rem 0;">📝 Output Template</h4>
            <strong>{template['name'] if template else 'Unknown'}</strong><br>
            <small>{template['description'] if template and template.get('description') else 'No description'}</small>
        </div>
        """, unsafe_allow_html=True)

    # Run button
    st.markdown("---")

    if st.button("🚀 Execute Workflow", type="primary", use_container_width=True):
        spinner = create_loading_spinner("Processing workflow...")
        try:
            # Update the workflow's template if changed
            if template and workflow.get('template_id') != st.session_state.workflow_template:
                st.session_state.workflow_manager.update_workflow_template_id(
                    workflow['name'], 
                    st.session_state.workflow_template,
                    project_id=st.session_state.current_project_id
                )

            # Process workflow
            result = st.session_state.workflow_manager.process_workflow_with_template(
                workflow['name'],
                st.session_state.workflow_source_doc,
                st.session_state.template_manager,
                st.session_state.source_manager,
                st.session_state.gpt_handler,
                st.session_state.prompt_manager,
                project_id=st.session_state.current_project_id
            )

            spinner.empty()

            if "error" in result:
                st.error(result["error"])
                return

            # Record execution
            execution_id = st.session_state.execution_manager.record_execution(
                project_id=st.session_state.current_project_id,
                workflow_name=workflow['name'],
                document_id=st.session_state.workflow_source_doc,
                results=result['results'],
                template_content=result['content']
            )

            # Display results
            st.success("✅ Workflow completed successfully!")

            # Show individual prompt results
            with st.expander("📊 Individual Prompt Results", expanded=False):
                for marker, content in result['results'].items():
                    prompt_name = marker.replace('_OUTPUT', '').replace('_', ' ').title()
                    st.markdown(f"**{prompt_name}:**")
                    st.write(content)
                    st.markdown("---")

            # Show populated template
            st.markdown("### 📄 Generated Document")

            with st.container():
                st.markdown("""
                <div style="background-color: white; padding: 2rem; border-radius: 10px; 
                            border: 1px solid #E0E4EC; margin: 1rem 0;">
                """, unsafe_allow_html=True)

                if result['format'] == 'markdown':
                    st.markdown(result['content'])
                else:
                    st.markdown(result['content'], unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

            # Download button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                extension = ".md" if result['format'] == "markdown" else ".html"
                st.download_button(
                    label="📥 Download Generated Document",
                    data=result['content'],
                    file_name=f"{workflow['name']}_{source_doc['name']}_output{extension}",
                    mime="text/markdown" if extension == ".md" else "text/html",
                    use_container_width=True
                )

            # Option to run another
            st.markdown("---")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Run with Different Document", key="run_different"):
                    st.session_state.workflow_step = 'configure'
                    st.rerun()
            with col2:
                if st.button("🏠 Back to Workflows", key="back_to_start"):
                    st.session_state.workflow_step = 'select'
                    st.session_state.selected_workflow_id = None
                    st.session_state.workflow_source_doc = None
                    st.session_state.workflow_template = None
                    st.rerun()

        except Exception as e:
            spinner.empty()
            st.error(f"Error processing workflow: {str(e)}")
            st.exception(e)

def show_results_tab():
    """Display execution results for the current project"""
    st.header("📊 Results")

    if not st.session_state.current_project_id:
        st.warning("Please select a project to view results")
        return

    # Get recent executions
    executions = st.session_state.execution_manager.get_executions(
        project_id=st.session_state.current_project_id
    )

    if not executions:
        st.info("No workflow executions yet in this project")
        return

    # Display executions
    st.markdown("### Recent Executions")

    for execution in executions[:10]:  # Show last 10
        # Get document and workflow info
        doc = st.session_state.source_manager.get_document(
            execution['document_id'],
            project_id=st.session_state.current_project_id
        )

        with st.expander(
            f"📋 {execution['workflow_name']} - {doc['name'] if doc else 'Unknown'} "
            f"({execution['executed_at'][:19]})",
            expanded=False
        ):
            st.markdown(f"**Execution ID:** {execution['id']}")
            st.markdown(f"**Status:** {execution['status']}")

            if execution.get('template_content'):
                st.markdown("### Generated Document")
                st.markdown(execution['template_content'])

                # Download button
                st.download_button(
                    label="📥 Download",
                    data=execution['template_content'],
                    file_name=f"{execution['workflow_name']}_{execution['executed_at'][:10]}.md",
                    mime="text/markdown",
                    key=f"download_{execution['id']}"
                )

def show_workflow_testing(workflow_name):
    """Interface for testing and refining workflow prompts"""
    workflow = st.session_state.workflow_manager.get_workflow(
        workflow_name,
        project_id=st.session_state.current_project_id
    )
    if not workflow:
        st.error("Workflow not found")
        return

    st.header(f"Test & Refine: {workflow['name']}")

    # Back button
    if st.button("← Back to Workflows"):
        st.session_state.workflow_mode = None
        st.session_state.current_workflow = None
        st.rerun()

    # Test each prompt in the workflow
    for idx, prompt_data in enumerate(workflow['prompts']):
        with st.expander(f"📝 {prompt_data['name']}", expanded=True):
            st.subheader(prompt_data['name'])

            # Display current prompt
            st.markdown("#### Current Prompt")
            st.code(prompt_data['prompt'])

            # Edit interface
            st.markdown("#### Edit Prompt")
            edited_prompt = st.text_area(
                "Edit prompt text:", 
                prompt_data['prompt'],
                key=f"edit_{idx}",
                height=100
            )

            # Test buttons for original and edited versions
            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔄 Test Original", key=f"test_original_{idx}"):
                    spinner = create_loading_spinner("Testing original prompt...")
                    try:
                        result = st.session_state.gpt_handler.process_document(
                            st.session_state.current_document_text,
                            prompt_data['prompt'],
                            st.session_state.prompt_manager.get_system_prompt()
                        )
                        spinner.empty()
                        st.session_state.test_results[f"original_{prompt_data['name']}"] = result
                        st.rerun()
                    except Exception as e:
                        spinner.empty()
                        st.error(f"Error testing prompt: {str(e)}")

            with col2:
                if st.button("🔄 Test Changes", key=f"test_changes_{idx}"):
                    spinner = create_loading_spinner("Testing changes...")
                    try:
                        result = st.session_state.gpt_handler.process_document(
                            st.session_state.current_document_text,
                            edited_prompt,
                            st.session_state.prompt_manager.get_system_prompt()
                        )
                        spinner.empty()
                        st.session_state.test_results[f"edited_{prompt_data['name']}"] = result
                        st.rerun()
                    except Exception as e:
                        spinner.empty()
                        st.error(f"Error testing changes: {str(e)}")

            # Display test results comparison
            original_key = f"original_{prompt_data['name']}"
            edited_key = f"edited_{prompt_data['name']}"

            if original_key in st.session_state.test_results or edited_key in st.session_state.test_results:
                st.markdown("### Results")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("#### Original Result")
                    if original_key in st.session_state.test_results:
                        st.markdown(st.session_state.test_results[original_key])
                    else:
                        st.info("Not tested yet")

                with col2:
                    st.markdown("#### New Result")
                    if edited_key in st.session_state.test_results:
                        st.markdown(st.session_state.test_results[edited_key])
                    else:
                        st.info("Not tested yet")

                # Save/Discard buttons for edited version
                if edited_key in st.session_state.test_results:
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save Changes", key=f"save_{idx}", type="primary"):
                            updated_prompt = {
                                'name': prompt_data['name'],
                                'prompt': edited_prompt,
                                'type': prompt_data.get('type', 'custom')
                            }
                            if st.session_state.workflow_manager.update_workflow_prompt(
                                workflow_name, 
                                idx, 
                                updated_prompt,
                                project_id=st.session_state.current_project_id
                            ):
                                if original_key in st.session_state.test_results:
                                    del st.session_state.test_results[original_key]
                                if edited_key in st.session_state.test_results:
                                    del st.session_state.test_results[edited_key]
                                st.success("Changes saved!")
                                st.rerun()

                    with col2:
                        if st.button("❌ Discard Changes", key=f"discard_{idx}", type="secondary"):
                            if original_key in st.session_state.test_results:
                                del st.session_state.test_results[original_key]
                            if edited_key in st.session_state.test_results:
                                del st.session_state.test_results[edited_key]
                            st.rerun()

def show_workflow_editor(workflow_name):
    """Interface for editing workflow configuration"""
    workflow = st.session_state.workflow_manager.get_workflow(
        workflow_name,
        project_id=st.session_state.current_project_id
    )
    if not workflow:
        st.error("Workflow not found")
        return

    st.subheader(f"Editing: {workflow['name']}")

    # Back button
    if st.button("← Back to Workflows"):
        st.session_state.workflow_mode = None
        st.session_state.current_workflow = None
        st.rerun()

    # Template selection
    st.markdown("### 📝 Associated Template")
    templates = st.session_state.template_manager.get_templates()
    template_names = ["None"] + [t['name'] for t in templates]
    template_ids = [None] + [t['id'] for t in templates]

    current_template_idx = 0
    if workflow.get('template_id'):
        try:
            current_template_idx = template_ids.index(workflow['template_id'])
        except ValueError:
            pass

    selected_template_name = st.selectbox(
        "Select Template",
        template_names,
        index=current_template_idx,
        key="workflow_template_select"
    )

    if selected_template_name != "None":
        selected_idx = template_names.index(selected_template_name)
        selected_template_id = template_ids[selected_idx]

        if selected_template_id != workflow.get('template_id'):
            if st.button("Update Template", type="primary"):
                if st.session_state.workflow_manager.update_workflow_template_id(
                    workflow_name, 
                    selected_template_id,
                    project_id=st.session_state.current_project_id
                ):
                    st.success("Template updated!")
                    st.rerun()

    # Prompt management section
    st.markdown("### Add Prompts to Workflow")

    col1, col2 = st.columns(2)

    # Library prompts column
    with col1:
        st.markdown("#### Select from Library")
        library_prompts = st.session_state.prompt_manager.get_prompts()
        for prompt in library_prompts:
            if st.button(f"Add: {prompt['Name']}", key=f"add_lib_{prompt['Name']}"):
                prompt_data = {
                    "name": prompt['Name'],
                    "description": prompt['Description'],
                    "prompt": prompt['Prompt'],
                    "type": "library"
                }
                if st.session_state.workflow_manager.add_prompt_to_workflow(
                    workflow_name, 
                    prompt_data,
                    project_id=st.session_state.current_project_id
                ):
                    st.success(f"Added '{prompt['Name']}' to workflow")
                    st.rerun()

    # New prompt creation column
    with col2:
        st.markdown("#### Create New Prompt")
        new_prompt_name = st.text_input("Prompt Name", key="new_prompt_name")
        new_prompt_description = st.text_area("Description", key="new_prompt_description")
        new_prompt_text = st.text_area("Prompt", key="new_prompt_text", height=100)

        if st.button("Add to Workflow", type="primary", key="add_new_prompt"):
            if new_prompt_name and new_prompt_text:
                prompt_data = {
                    "name": new_prompt_name,
                    "description": new_prompt_description,
                    "prompt": new_prompt_text,
                    "type": "custom"
                }
                if st.session_state.workflow_manager.add_prompt_to_workflow(
                    workflow_name, 
                    prompt_data,
                    project_id=st.session_state.current_project_id
                ):
                    st.success(f"Added new prompt '{new_prompt_name}' to workflow")
                    st.rerun()
            else:
                st.error("Please provide both name and prompt text")

    # Display current workflow prompts
    st.markdown("---")
    st.markdown("### Current Workflow Prompts")

    if workflow['prompts']:
        for idx, prompt_data in enumerate(workflow['prompts']):
            with st.expander(f"{prompt_data['name']}", expanded=False):
                st.markdown("#### Current Prompt")
                st.markdown(f"```\n{prompt_data['prompt']}\n```")
    else:
        st.info("No prompts added to this workflow yet")

    # Complete workflow button
    st.markdown("---")
    if workflow['prompts']:
        if st.button("Complete Workflow", type="primary"):
            if st.session_state.workflow_manager.complete_workflow(
                workflow_name,
                project_id=st.session_state.current_project_id
            ):
                st.success("Workflow completed!")
                st.session_state.current_workflow = None
                st.session_state.workflow_mode = None
                st.rerun()

def show_template_documents_tab():
    """Display the template documents management interface (global)"""
    st.header("📝 Template Documents")
    st.markdown("Create and manage document templates that will be populated with workflow results")

    # Info box about markers
    with st.info("💡 **How to use templates**: Create templates with markers like `{RENT_OUTPUT}` or `{LANDLORD_OUTPUT}` that will be replaced with prompt results"):
        pass

    # Upload section
    with st.expander("➕ Upload New Template", expanded=False):
        uploaded_file = st.file_uploader(
            "Choose a template file",
            type=['docx', 'txt', 'md'],
            key="template_upload"
        )

        if uploaded_file:
            col1, col2 = st.columns([3, 1])
            with col1:
                template_name = st.text_input(
                    "Template Name",
                    value=os.path.splitext(uploaded_file.name)[0],
                    key="template_name"
                )
                template_description = st.text_area(
                    "Description (optional)",
                    key="template_desc",
                    height=80
                )

            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📤 Upload", type="primary", key="upload_template"):
                    try:
                        spinner = create_loading_spinner("Uploading template...")
                        template_info = st.session_state.template_manager.upload_template(
                            uploaded_file, template_name, template_description
                        )
                        spinner.empty()
                        st.success(f"✅ Template '{template_name}' uploaded successfully!")
                        st.rerun()
                    except Exception as e:
                        spinner.empty()
                        st.error(f"❌ Error uploading template: {str(e)}")

    # Template library
    st.markdown("### 📚 Template Library")

    templates = st.session_state.template_manager.get_templates()

    if templates:
        # Display templates in a grid
        for i in range(0, len(templates), 2):
            cols = st.columns(2)
            for j, col in enumerate(cols):
                if i + j < len(templates):
                    template = templates[i + j]
                    with col:
                        with st.container():
                            st.markdown(f"""
                            <div style="border: 1px solid #E0E4EC; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;">
                                <h4>{template['name']}</h4>
                                <p style="color: #666; font-size: 0.9em;">{template.get('description', 'No description')}</p>
                                <p style="color: #999; font-size: 0.8em;">
                                    Uploaded: {template['uploaded_at'][:10]} | 
                                    Type: {template['file_type']}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

                            # Get markers for this template
                            markers = st.session_state.template_manager.get_template_markers(template['id'])
                            if markers:
                                st.caption(f"📌 Markers: {', '.join(markers[:3])}{'...' if len(markers) > 3 else ''}")

                            col_a, col_b, col_c = st.columns(3)
                            with col_a:
                                if st.button("👁️ Preview", key=f"preview_template_{template['id']}"):
                                    st.session_state.preview_template_id = template['id']
                            with col_b:
                                if st.button("✅ Select", key=f"select_template_{template['id']}", type="primary"):
                                    st.session_state.selected_template_id = template['id']
                                    st.success(f"Selected '{template['name']}' template")
                            with col_c:
                                if st.button("🗑️ Delete", key=f"delete_template_{template['id']}"):
                                    if st.session_state.template_manager.delete_template(template['id']):
                                        st.rerun()

        # Preview section
        if hasattr(st.session_state, 'preview_template_id'):
            template_content = st.session_state.template_manager.read_template_content(st.session_state.preview_template_id)
            if template_content:
                st.markdown("### Template Preview")
                markers = st.session_state.template_manager.get_template_markers(st.session_state.preview_template_id)
                if markers:
                    st.info(f"**Found markers:** {', '.join(markers)}")
                st.text_area("", template_content, height=400, disabled=True)
    else:
        st.info("📭 No templates uploaded yet. Sample templates have been created for you!")

def main():
    """Main application entry point"""
    initialize_session_state()

    st.title("PromptFlow")

    # Show project context bar if a project is selected
    show_project_context_bar()

    # Determine which tabs to show based on project context
    if st.session_state.current_project_id:
        # Project-specific tabs
        tabs = ["Projects", "Documents", "Workflows", "Workflow Library", "Templates", "Results", "Help"]
        active_tab = st.tabs(tabs)

        with active_tab[0]:
            show_projects_tab()

        with active_tab[1]:
            show_source_documents_tab()

        with active_tab[2]:
            # Handle workflow modes
            if st.session_state.workflow_mode == "edit" and st.session_state.current_workflow:
                show_workflow_editor(st.session_state.current_workflow)
            elif st.session_state.workflow_mode == "test" and st.session_state.current_workflow:
                show_workflow_testing(st.session_state.current_workflow)
            else:
                show_project_workflows_tab()

        with active_tab[3]:
            show_workflow_library_tab()

        with active_tab[4]:
            show_template_documents_tab()

        with active_tab[5]:
            show_results_tab()

        with active_tab[6]:
            show_help()

    else:
        # No project selected - show limited tabs
        tabs = ["Projects", "Workflow Library", "Templates", "Help"]
        active_tab = st.tabs(tabs)

        with active_tab[0]:
            show_projects_tab()

        with active_tab[1]:
            show_workflow_library_tab()

        with active_tab[2]:
            show_template_documents_tab()

        with active_tab[3]:
            show_help()

if __name__ == "__main__":
    main()