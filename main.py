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

def show_project_selection():
    """Display the project selection and management interface"""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 0;">
        <h1 style="font-size: 3rem; margin-bottom: 1rem;">🎯 PromptFlow</h1>
        <p style="font-size: 1.3rem; color: #666; margin-bottom: 3rem;">
            Streamline your document analysis with AI-powered workflows
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Create new project section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown("""
            <div style="background-color: #f0f8ff; padding: 2rem; border-radius: 15px; 
                        border: 2px solid #1A2543; margin-bottom: 2rem;">
                <h3 style="text-align: center; margin-bottom: 1.5rem;">🚀 Create New Project</h3>
            </div>
            """, unsafe_allow_html=True)

            project_name = st.text_input("Project Name", placeholder="Enter a unique project name")
            project_description = st.text_area(
                "Description (optional)", 
                placeholder="Describe the purpose of this project",
                height=80
            )

            if st.button("✨ Create Project", type="primary", use_container_width=True):
                if project_name:
                    try:
                        project = st.session_state.project_manager.create_project(
                            project_name, 
                            project_description
                        )
                        st.success(f"✅ Created project: {project['name']}")
                        st.session_state.current_project_id = project['id']
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating project: {str(e)}")
                else:
                    st.error("Please enter a project name")

    # Display existing projects
    st.markdown("---")
    st.markdown("### 📂 Your Projects")

    projects = st.session_state.project_manager.get_projects()

    if not projects:
        st.info("No projects yet. Create your first project above!")
    else:
        # Create a grid of project cards
        cols = st.columns(3)
        for i, project in enumerate(projects):
            with cols[i % 3]:
                # Update document and workflow counts
                doc_count = st.session_state.source_manager.get_project_document_count(project['id'])
                workflow_count = len(st.session_state.workflow_manager.get_workflows(project['id']))

                # Create project card
                st.markdown(f"""
                <div style="background-color: white; border: 2px solid #E0E4EC; 
                            border-radius: 15px; padding: 1.5rem; margin-bottom: 1rem;
                            transition: all 0.3s ease; cursor: pointer;"
                     onmouseover="this.style.borderColor='#1A2543'; this.style.transform='translateY(-2px)'; 
                                  this.style.boxShadow='0 8px 16px rgba(0,0,0,0.1)';"
                     onmouseout="this.style.borderColor='#E0E4EC'; this.style.transform='translateY(0)'; 
                                 this.style.boxShadow='none';">
                    <h4 style="margin: 0 0 0.5rem 0; color: #1A2543;">{project['name']}</h4>
                    <p style="color: #666; font-size: 0.9em; margin: 0.5rem 0; min-height: 3rem;">
                        {project.get('description', 'No description')}
                    </p>
                    <div style="display: flex; justify-content: space-between; margin: 1rem 0;">
                        <span style="color: #08B0A0; font-size: 0.85em;">
                            📄 {doc_count} docs
                        </span>
                        <span style="color: #00A7C5; font-size: 0.85em;">
                            ⚙️ {workflow_count} workflows
                        </span>
                    </div>
                    <hr style="margin: 0.5rem 0; border: none; border-top: 1px solid #E0E4EC;">
                    <p style="color: #999; font-size: 0.75em; margin: 0.5rem 0 0 0;">
                        Created: {project['created_at'][:10]}
                    </p>
                </div>
                """, unsafe_allow_html=True)

                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("📂 Open", key=f"open_{project['id']}", type="primary", use_container_width=True):
                        st.session_state.current_project_id = project['id']
                        st.rerun()
                with col_b:
                    if st.button("🗑️ Delete", key=f"delete_{project['id']}", use_container_width=True):
                        if doc_count > 0 or workflow_count > 0:
                            st.warning(f"Project has {doc_count} documents and {workflow_count} workflows. Delete anyway?")
                            if st.button("Yes, Delete", key=f"confirm_delete_{project['id']}"):
                                if st.session_state.project_manager.delete_project(project['id']):
                                    st.rerun()
                        else:
                            if st.session_state.project_manager.delete_project(project['id']):
                                st.rerun()

def show_project_workspace():
    """Display the project workspace with all project-specific features"""
    project = st.session_state.project_manager.get_project(st.session_state.current_project_id)
    if not project:
        st.error("Project not found")
        st.session_state.current_project_id = None
        st.rerun()
        return

    # Project header with enhanced styling
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #1A2543 0%, #08B0A0 100%); 
                color: white; padding: 2rem; border-radius: 15px; margin-bottom: 2rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="margin: 0; color: white;">📁 {project['name']}</h1>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{project.get('description', 'No description')}</p>
            </div>
            <button onclick="window.location.reload();" 
                    style="background: rgba(255,255,255,0.2); border: 2px solid white; 
                           color: white; padding: 0.5rem 1.5rem; border-radius: 10px; 
                           cursor: pointer; font-weight: bold; transition: all 0.3s ease;"
                    onmouseover="this.style.background='rgba(255,255,255,0.3)'"
                    onmouseout="this.style.background='rgba(255,255,255,0.2)'">
                ← Exit Project
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Add the "Run Workflows and Generate Results" button if conditions are met
    doc_count = st.session_state.source_manager.get_project_document_count(project['id'])
    workflows = st.session_state.workflow_manager.get_workflows(project['id'])
    workflow_count = len(workflows)

    if doc_count > 0 and workflow_count > 0:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #E2345D 0%, #50A036 100%); 
                    padding: 1.5rem; border-radius: 15px; margin-bottom: 2rem;
                    box-shadow: 0 4px 12px rgba(226, 52, 93, 0.3);">
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            <h3 style="color: white; text-align: center; margin-bottom: 1rem;">
                🚀 Ready to Process!
            </h3>
            <p style="color: white; text-align: center; margin-bottom: 1rem; opacity: 0.9;">
                You have {doc_count} document{'s' if doc_count > 1 else ''} and 
                {workflow_count} workflow{'s' if workflow_count > 1 else ''} ready
            </p>
            """.format(doc_count=doc_count, workflow_count=workflow_count), unsafe_allow_html=True)

            if st.button("⚡ Run Workflows and Generate Results", 
                        type="primary", 
                        use_container_width=True,
                        key="batch_process"):
                batch_process_workflows(project['id'])

        st.markdown("</div>", unsafe_allow_html=True)

    # Project tabs - only show project-specific content
    tabs = st.tabs(["📄 Documents", "⚙️ Workflows", "📊 Results", "📋 Templates"])

    with tabs[0]:  # Documents
        show_project_documents_tab(project['id'])

    with tabs[1]:  # Workflows
        show_project_workflows_tab_content(project['id'])

    with tabs[2]:  # Results
        show_project_results_tab(project['id'])

    with tabs[3]:  # Templates
        show_project_templates_tab(project['id'])

    # Exit button at the bottom
    st.markdown("---")
    if st.button("← Back to Projects", key="exit_project_bottom"):
        st.session_state.current_project_id = None
        st.session_state.workflow_step = 'select'
        st.session_state.selected_workflow_id = None
        st.session_state.workflow_source_doc = None
        st.session_state.workflow_template = None
        st.rerun()

def batch_process_workflows(project_id):
    """Process all workflows against all documents in a project"""
    spinner = create_loading_spinner("Processing all workflows...")

    try:
        documents = st.session_state.source_manager.get_documents(project_id)
        workflows = st.session_state.workflow_manager.get_workflows(project_id)
        templates = st.session_state.template_manager.get_templates()

        if not documents or not workflows:
            spinner.empty()
            st.error("No documents or workflows to process")
            return

        results_generated = 0
        errors = []

        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        total_operations = len(documents) * len(workflows)
        current_operation = 0

        for doc in documents:
            for workflow in workflows:
                current_operation += 1
                progress = current_operation / total_operations
                progress_bar.progress(progress)
                status_text.text(f"Processing: {doc['name']} with {workflow['name']} ({current_operation}/{total_operations})")

                # Check if workflow has a template
                if not workflow.get('template_id'):
                    # Try to find a matching template
                    matching_template = None
                    for template in templates:
                        markers = st.session_state.template_manager.get_template_markers(template['id'])
                        # Check if template markers match workflow prompts
                        workflow_markers = [f"{p['name'].upper().replace(' ', '_')}_OUTPUT" 
                                          for p in workflow.get('prompts', [])]
                        if any(marker in workflow_markers for marker in markers):
                            matching_template = template['id']
                            break

                    if matching_template:
                        workflow['template_id'] = matching_template
                        st.session_state.workflow_manager.update_workflow_template_id(
                            workflow['name'], matching_template, project_id
                        )

                if workflow.get('template_id'):
                    try:
                        # Process the workflow
                        result = st.session_state.workflow_manager.process_workflow_with_template(
                            workflow['name'],
                            doc['id'],
                            st.session_state.template_manager,
                            st.session_state.source_manager,
                            st.session_state.gpt_handler,
                            st.session_state.prompt_manager,
                            project_id=project_id
                        )

                        if "error" not in result:
                            # Record execution
                            st.session_state.execution_manager.record_execution(
                                project_id=project_id,
                                workflow_name=workflow['name'],
                                document_id=doc['id'],
                                results=result['results'],
                                template_content=result['content']
                            )
                            results_generated += 1
                        else:
                            errors.append(f"{workflow['name']} on {doc['name']}: {result['error']}")
                    except Exception as e:
                        errors.append(f"{workflow['name']} on {doc['name']}: {str(e)}")
                else:
                    errors.append(f"{workflow['name']}: No template assigned")

        spinner.empty()
        progress_bar.empty()
        status_text.empty()

        # Show results summary
        if results_generated > 0:
            st.success(f"✅ Successfully generated {results_generated} results!")

        if errors:
            with st.expander("⚠️ Errors encountered", expanded=True):
                for error in errors:
                    st.error(error)

        # Refresh to show new results
        if results_generated > 0:
            st.balloons()
            st.rerun()

    except Exception as e:
        spinner.empty()
        st.error(f"Batch processing failed: {str(e)}")

def show_project_documents_tab(project_id):
    """Display documents management for a specific project"""
    st.header("📄 Project Documents")
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
                            project_id=project_id
                        )
                        spinner.empty()
                        st.success(f"✅ Document '{doc_name}' uploaded successfully!")
                        st.rerun()
                    except Exception as e:
                        spinner.empty()
                        st.error(f"❌ Error uploading document: {str(e)}")

    # Document library
    st.markdown("### 📚 Documents in this Project")

    # Search and filter
    search_query = st.text_input("🔍 Search documents", key="search_source")

    # Get documents for current project
    if search_query:
        documents = st.session_state.source_manager.search_documents(
            search_query, 
            project_id=project_id
        )
    else:
        documents = st.session_state.source_manager.get_documents(
            project_id=project_id
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
                            <div style="border: 1px solid #E0E4EC; border-radius: 8px; 
                                        padding: 1rem; margin-bottom: 1rem; background-color: white;">
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
                                        project_id=project_id
                                    )
                                    st.success(f"Selected '{doc['name']}' for analysis")
                            with col_c:
                                if st.button("🗑️ Delete", key=f"delete_{doc['id']}"):
                                    if st.session_state.source_manager.delete_document(
                                        doc['id'],
                                        project_id=project_id
                                    ):
                                        st.rerun()

        # Preview section
        if hasattr(st.session_state, 'preview_doc_id'):
            doc_text = st.session_state.source_manager.get_document_text(
                st.session_state.preview_doc_id,
                project_id=project_id
            )
            if doc_text:
                st.markdown("### Document Preview")
                st.text_area("", doc_text[:2000] + "...", height=300, disabled=True)
    else:
        st.info("📭 No documents in this project yet. Upload your first document above!")

def show_project_workflows_tab_content(project_id):
    """Display workflows management for a specific project"""
    st.header("⚙️ Project Workflows")

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
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("➕ Create New Workflow", key="create_workflow_btn", type="primary"):
            st.session_state.show_create_dialog = True
    with col2:
        if st.button("📚 Import from Library", key="import_workflow_btn"):
            st.session_state.show_library_import = True

    # Show create workflow dialog
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
                            project_id=project_id
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
                            project_id,
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

    # Handle workflow modes
    if st.session_state.workflow_mode == "edit" and st.session_state.current_workflow:
        show_workflow_editor(st.session_state.current_workflow, project_id)
    elif st.session_state.workflow_mode == "test" and st.session_state.current_workflow:
        show_workflow_testing(st.session_state.current_workflow, project_id)
    else:
        # Show existing workflows
        st.markdown("---")
        st.subheader("📚 Workflows in this Project")

        workflows = st.session_state.workflow_manager.get_workflows(project_id=project_id)

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
                                            margin-bottom: 1rem; background-color: white;">
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
                                    if st.button("▶️ Run", key=f"run_wf_{workflow['name']}", type="primary"):
                                        st.session_state.selected_workflow_id = workflow['name']
                                        st.session_state.workflow_step = 'configure'
                                        show_workflow_runner(workflow['name'], project_id)
                                with col_b:
                                    if st.button("✏️ Edit", key=f"edit_{workflow['name']}"):
                                        st.session_state.workflow_mode = "edit"
                                        st.session_state.current_workflow = workflow['name']
                                        st.rerun()
                                with col_c:
                                    if st.button("🗑️ Delete", key=f"delete_wf_{workflow['name']}"):
                                        if st.session_state.workflow_manager.delete_workflow(
                                            workflow['name'],
                                            project_id=project_id
                                        ):
                                            st.success(f"Deleted '{workflow['name']}'")
                                            st.rerun()
        else:
            st.info("No workflows in this project yet. Create a new one or import from library!")

def show_workflow_runner(workflow_name, project_id):
    """Inline workflow runner within the workflows tab"""
    workflow = st.session_state.workflow_manager.get_workflow(workflow_name, project_id=project_id)
    if not workflow:
        st.error("Workflow not found")
        return

    st.markdown("---")
    st.markdown(f"### 🚀 Run Workflow: {workflow['name']}")

    # Document selection
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📄 Select Document")
        source_docs = st.session_state.source_manager.get_documents(project_id=project_id)

        if source_docs:
            doc_options = ["Select a document..."] + [f"{doc['name']}" for doc in source_docs]
            doc_values = [None] + [doc['id'] for doc in source_docs]

            selected = st.selectbox(
                "Choose document to analyze",
                options=doc_options,
                key=f"doc_select_{workflow_name}"
            )

            if selected != "Select a document...":
                doc_id = doc_values[doc_options.index(selected)]
                st.session_state.workflow_source_doc = doc_id
        else:
            st.warning("No documents in this project")

    with col2:
        st.markdown("#### 📝 Select Template")
        templates = st.session_state.template_manager.get_templates()

        if templates:
            template_options = ["Select a template..."] + [f"{t['name']}" for t in templates]
            template_values = [None] + [t['id'] for t in templates]

            # Pre-select if workflow has a template
            selected_idx = 0
            if workflow.get('template_id'):
                try:
                    selected_idx = template_values.index(workflow['template_id'])
                except ValueError:
                    pass

            selected = st.selectbox(
                "Choose output template",
                options=template_options,
                index=selected_idx,
                key=f"template_select_{workflow_name}"
            )

            if selected != "Select a template...":
                template_id = template_values[template_options.index(selected)]
                st.session_state.workflow_template = template_id
        else:
            st.warning("No templates available")

    # Run button
    if st.session_state.get('workflow_source_doc') and st.session_state.get('workflow_template'):
        if st.button("⚡ Execute Workflow", type="primary", use_container_width=True):
            spinner = create_loading_spinner("Processing workflow...")
            try:
                # Update workflow template if changed
                if workflow.get('template_id') != st.session_state.workflow_template:
                    st.session_state.workflow_manager.update_workflow_template_id(
                        workflow_name, 
                        st.session_state.workflow_template,
                        project_id=project_id
                    )

                # Process workflow
                result = st.session_state.workflow_manager.process_workflow_with_template(
                    workflow_name,
                    st.session_state.workflow_source_doc,
                    st.session_state.template_manager,
                    st.session_state.source_manager,
                    st.session_state.gpt_handler,
                    st.session_state.prompt_manager,
                    project_id=project_id
                )

                spinner.empty()

                if "error" in result:
                    st.error(result["error"])
                    return

                # Record execution
                st.session_state.execution_manager.record_execution(
                    project_id=project_id,
                    workflow_name=workflow['name'],
                    document_id=st.session_state.workflow_source_doc,
                    results=result['results'],
                    template_content=result['content']
                )

                st.success("✅ Workflow completed successfully!")

                # Show preview
                with st.expander("📄 View Generated Document", expanded=True):
                    st.markdown(result['content'])

                    # Download button
                    extension = ".md" if result['format'] == "markdown" else ".html"
                    st.download_button(
                        label="📥 Download",
                        data=result['content'],
                        file_name=f"{workflow['name']}_output{extension}",
                        mime="text/markdown" if extension == ".md" else "text/html"
                    )

            except Exception as e:
                spinner.empty()
                st.error(f"Error processing workflow: {str(e)}")
    else:
        st.info("👆 Please select both a document and a template to run the workflow")

def show_project_results_tab(project_id):
    """Display execution results for a specific project"""
    st.header("📊 Project Results")

    # Get executions for this project
    executions = st.session_state.execution_manager.get_executions(project_id=project_id)

    if not executions:
        st.info("No workflow executions yet in this project. Run some workflows to see results here!")
        return

    # Summary statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Executions", len(executions))
    with col2:
        unique_workflows = len(set(e['workflow_name'] for e in executions))
        st.metric("Workflows Used", unique_workflows)
    with col3:
        unique_docs = len(set(e['document_id'] for e in executions))
        st.metric("Documents Processed", unique_docs)

    st.markdown("---")

    # Display recent executions
    st.markdown("### Recent Executions")

    for execution in executions[:20]:  # Show last 20
        # Get document info
        doc = st.session_state.source_manager.get_document(
            execution['document_id'],
            project_id=project_id
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

                # Delete button
                if st.button("🗑️ Delete Result", key=f"delete_result_{execution['id']}"):
                    if st.session_state.execution_manager.delete_execution(execution['id']):
                        st.rerun()

def show_project_templates_tab(project_id):
    """Display template management within a project context"""
    st.header("📋 Project Templates")
    st.markdown("View and select templates for your workflows")

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
                            <div style="border: 1px solid #E0E4EC; border-radius: 8px; 
                                        padding: 1rem; margin-bottom: 1rem; background-color: white;">
                                <h4>{template['name']}</h4>
                                <p style="color: #666; font-size: 0.9em;">{template.get('description', 'No description')}</p>
                                <p style="color: #999; font-size: 0.8em;">
                                    Type: {template['file_type']}
                                </p>
                            </div>
                            """, unsafe_allow_html=True)

                            # Get markers for this template
                            markers = st.session_state.template_manager.get_template_markers(template['id'])
                            if markers:
                                st.caption(f"📌 Markers: {', '.join(markers[:3])}{'...' if len(markers) > 3 else ''}")

                            if st.button("👁️ Preview", key=f"preview_proj_template_{template['id']}"):
                                template_content = st.session_state.template_manager.read_template_content(template['id'])
                                if template_content:
                                    st.markdown("### Template Preview")
                                    st.text_area("", template_content, height=400, disabled=True, key=f"preview_content_{template['id']}")
    else:
        st.info("📭 No templates available. Upload templates in the global Templates section.")

def show_workflow_editor(workflow_name, project_id):
    """Interface for editing workflow configuration"""
    workflow = st.session_state.workflow_manager.get_workflow(workflow_name, project_id=project_id)
    if not workflow:
        st.error("Workflow not found")
        return

    st.subheader(f"✏️ Editing: {workflow['name']}")

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
                    project_id=project_id
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
                    project_id=project_id
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
                    project_id=project_id
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
                project_id=project_id
            ):
                st.success("Workflow completed!")
                st.session_state.current_workflow = None
                st.session_state.workflow_mode = None
                st.rerun()

def show_workflow_testing(workflow_name, project_id):
    """Interface for testing and refining workflow prompts"""
    workflow = st.session_state.workflow_manager.get_workflow(workflow_name, project_id=project_id)
    if not workflow:
        st.error("Workflow not found")
        return

    st.header(f"Test & Refine: {workflow['name']}")

    # Back button
    if st.button("← Back to Workflows"):
        st.session_state.workflow_mode = None
        st.session_state.current_workflow = None
        st.rerun()

    # Check if we have a document to test with
    if not st.session_state.current_document_text:
        st.warning("Please select a document first to test prompts")
        return

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

            # Test buttons
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

            # Display test results
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

                # Save/Discard buttons
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
                                project_id=project_id
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

def main():
    """Main application entry point"""
    initialize_session_state()

    # Show different UI based on whether a project is selected
    if st.session_state.current_project_id:
        show_project_workspace()
    else:
        show_project_selection()

if __name__ == "__main__":
    main()