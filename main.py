import streamlit as st
import json
import os
from prompt_manager import PromptManager
from document_processor import DocumentProcessor
from gpt_handler import GPTHandler
from workflow_manager import WorkflowManager
from help import show_help
from intro import show_introduction

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
    """Creates a custom loading spinner with animated progress bar
    
    Args:
        message (str): Message to display during loading
        
    Returns:
        container: Streamlit container object containing the spinner
    """
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
        
    # Core managers state
    if 'prompt_manager' not in st.session_state:
        st.session_state.prompt_manager = PromptManager()
    if 'workflow_manager' not in st.session_state:
        st.session_state.workflow_manager = WorkflowManager()
    if 'gpt_handler' not in st.session_state:
        st.session_state.gpt_handler = GPTHandler()
        
    # Prompt and workflow management state
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

def reset_prompt_editing():
    """Reset all prompt editing related session state variables"""
    st.session_state.editing_prompt = {}
    st.session_state.current_edits = {}
    st.session_state.test_results = {}

def show_workflow_tab():
    """Display and handle the workflow management interface"""
    st.header("Workflows")

    # Create new workflow button
    if st.button("➕ Create Workflow", type="primary"):
        st.session_state.current_workflow = "new"
        st.rerun()

    # New workflow creation interface
    if st.session_state.current_workflow == "new":
        name_col, button_col = st.columns([3, 1])
        with name_col:
            st.text_input("Workflow Name", placeholder="e.g., Collateral Warranty Review", key="new_workflow_name")

        st.text_area("Description (optional)", placeholder="Describe the purpose of this workflow", key="new_workflow_desc", label_visibility="visible")

        if st.session_state.get("new_workflow_name"):
            if st.button("Create", type="primary"):
                if st.session_state.workflow_manager.create_workflow(
                    st.session_state.new_workflow_name, 
                    st.session_state.get("new_workflow_desc", "")
                ):
                    st.success(f"Workflow '{st.session_state.new_workflow_name}' created!")
                    st.session_state.current_workflow = st.session_state.new_workflow_name
                    st.rerun()
                else:
                    st.error("A workflow with this name already exists")

    # Display existing workflows
    workflows = st.session_state.workflow_manager.get_workflows()

    if workflows:
        st.markdown("---")
        st.subheader("Available Workflows")

        for workflow in workflows:
            # Create a row for each workflow with action buttons
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])

            with col1:
                st.write(f"**{workflow['name']}**")
                if workflow['description']:
                    st.caption(workflow['description'])
                st.caption(f"Status: {workflow['status'].title()}")

            with col2:
                if st.button("✏️ Edit", key=f"edit_{workflow['name']}"):
                    st.session_state.workflow_mode = "edit"
                    st.session_state.current_workflow = workflow['name']
                    st.rerun()

            with col3:
                if st.button("🔄 Test", key=f"test_{workflow['name']}"):
                    if not st.session_state.current_document:
                        st.warning("Please upload a document first")
                    else:
                        st.session_state.workflow_mode = "test"
                        st.session_state.current_workflow = workflow['name']
                        st.rerun()

            with col4:
                if st.button("▶️ Run", key=f"run_{workflow['name']}"):
                    if not st.session_state.current_document:
                        st.warning("Please upload a document first")
                    else:
                        st.session_state.workflow_mode = "run"
                        st.session_state.current_workflow = workflow['name']
                        st.rerun()

    # Show appropriate interface based on mode
    if hasattr(st.session_state, 'workflow_mode') and st.session_state.current_workflow:
        if st.session_state.workflow_mode == "edit":
            show_workflow_editor(st.session_state.current_workflow)
        elif st.session_state.workflow_mode == "test":
            show_workflow_testing(st.session_state.current_workflow)
        elif st.session_state.workflow_mode == "run":
            show_workflow_results(st.session_state.current_workflow)

def show_workflow_testing(workflow_name):
    """Interface for testing and refining workflow prompts
    
    Args:
        workflow_name (str): Name of the workflow being tested
    """
    workflow = st.session_state.workflow_manager.get_workflow(workflow_name)
    if not workflow:
        st.error("Workflow not found")
        return

    st.header(f"Test & Refine: {workflow['name']}")

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
                                workflow_name, idx, updated_prompt
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
    """Interface for editing workflow configuration
    
    Args:
        workflow_name (str): Name of the workflow being edited
    """
    workflow = st.session_state.workflow_manager.get_workflow(workflow_name)
    if not workflow:
        st.error("Workflow not found")
        return

    st.subheader(f"Editing: {workflow['name']}")

    # Tabs for different sections
    edit_tab, template_tab = st.tabs(["📝 Prompts", "📄 Template"])

    with edit_tab:
        # Prompt selection/creation section
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
                    if st.session_state.workflow_manager.add_prompt_to_workflow(workflow_name, prompt_data):
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
                    if st.session_state.workflow_manager.add_prompt_to_workflow(workflow_name, prompt_data):
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

                    if st.button("Test Prompt", key=f"test_{idx}"):
                        if not st.session_state.current_document:
                            st.warning("Please upload a document first")
                        else:
                            spinner = create_loading_spinner("Testing prompt...")
                            try:
                                result = st.session_state.gpt_handler.process_document(
                                    st.session_state.current_document_text,
                                    prompt_data['prompt'],
                                    st.session_state.prompt_manager.get_system_prompt()
                                )
                                spinner.empty()
                                st.markdown("#### Result")
                                st.markdown(result)
                            except Exception as e:
                                spinner.empty()
                                st.error(f"Error testing prompt: {str(e)}")
        else:
            st.info("No prompts added to this workflow yet")

    # Template tab
    with template_tab:
        st.markdown("### Document Template")

        if not workflow['prompts']:
            st.warning("Add prompts to the workflow before creating a template")
        else:
            # Format selection
            output_format = st.selectbox(
                "Output Format",
                options=["markdown", "html"],
                index=0 if workflow.get("output_format", "markdown") == "markdown" else 1,
                key="template_format"
            )

            # Show available markers
            st.markdown("#### Available Markers")
            st.markdown("Use these markers in your template to insert prompt results:")
            for prompt in workflow['prompts']:
                st.code(f"{{{prompt['name']}_OUTPUT}}")
                st.caption(f"Insert the result from '{prompt['name']}'")

            # Template editor
            st.markdown("#### Edit Template")
            template_content = st.text_area(
                "Template Content",
                value=workflow.get("template", ""),
                height=300,
                help="Use the markers above to insert prompt results in your template",
                key="template_content"
            )

            if template_content:
                # Preview section
                st.markdown("#### Preview")
                preview_content = template_content
                for prompt in workflow['prompts']:
                    marker = f"{{{prompt['name']}_OUTPUT}}"
                    preview_content = preview_content.replace(
                        marker,
                        f"[Result from '{prompt['name']}' will appear here]"
                    )

                preview_container = st.expander("Show Preview", expanded=True)
                with preview_container:
                    if output_format == "markdown":
                        st.markdown(preview_content)
                    else:
                        st.markdown(preview_content, unsafe_allow_html=True)

                # Save template button
                if st.button("💾 Save Template", type="primary"):
                    if st.session_state.workflow_manager.update_workflow_template(
                        workflow_name,
                        template_content,
                        output_format
                    ):
                        st.success("Template saved successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to save template")

    # Complete workflow button
    st.markdown("---")
    if workflow['prompts']:
        if st.button("Complete Workflow", type="primary"):
            if st.session_state.workflow_manager.complete_workflow(workflow_name):
                st.success("Workflow completed!")
                st.session_state.current_workflow = None
                st.rerun()

def show_workflow_results(workflow_name):
    """Display results from running a workflow
    
    Args:
        workflow_name (str): Name of the workflow being run
    """
    workflow = st.session_state.workflow_manager.get_workflow(workflow_name)
    if not workflow:
        st.error("Workflow not found")
        return

    st.header(f"Results: {workflow['name']}")

    # Process all prompts in workflow
    results = {}
    total_prompts = len(workflow['prompts'])

    for idx, prompt_data in enumerate(workflow['prompts'], 1):
        spinner = create_loading_spinner(
            f"Processing {prompt_data['name']} ({idx}/{total_prompts})"
        )
        try:
            result = st.session_state.gpt_handler.process_document(
                st.session_state.current_document_text,
                prompt_data['prompt'],
                st.session_state.prompt_manager.get_system_prompt()
            )
            results[prompt_data['name']] = result
            spinner.empty()
        except Exception as e:
            spinner.empty()
            st.error(f"Error processing {prompt_data['name']}: {str(e)}")

    # Display individual results
    st.markdown("### Individual Prompt Results")
    for prompt_name, result in results.items():
        with st.expander(f"📄 {prompt_name}", expanded=False):
            st.write(result)

    # Generate template output if available
    if workflow.get("template"):
        st.markdown("---")
        st.markdown("### Generated Document")

        # Process template with results
        output_content = workflow["template"]
        for prompt_name, result in results.items():
            marker = f"{{{prompt_name}_OUTPUT}}"
            output_content = output_content.replace(marker, result)

        # Display processed template
        if workflow.get("output_format", "markdown") == "markdown":
            st.markdown(output_content)
        else:
            st.markdown(output_content, unsafe_allow_html=True)

        # Add download button
        extension = ".md" if workflow.get("output_format", "markdown") == "markdown" else ".html"
        st.download_button(
            label="📥 Download Document",
            data=output_content,
            file_name=f"{workflow['name']}_output{extension}",
            mime="text/markdown" if extension == ".md" else "text/html"
        )

def main():
    """Main application entry point"""
    initialize_session_state()

    show_introduction()
    st.markdown("---")  # Add separator between intro and main content

    # Main application tabs
    tabs = ["Document", "Prompt Library", "Workflows", "Help"]
    active_tab = st.tabs(tabs)

    # Document Tab
    with active_tab[0]:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.header("Upload a Word or PDF Document")
            uploaded_file = st.file_uploader("Upload a Word or PDF document", type=['docx', 'pdf'])

            if uploaded_file:
                try:
                    doc_processor = DocumentProcessor()
                    st.session_state.current_document = uploaded_file.name
                    st.session_state.current_document_text = doc_processor.extract_text(uploaded_file)
                    st.success(f"Document loaded successfully: {uploaded_file.name}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.session_state.current_document = None
                    st.session_state.current_document_text = None

        # Display document content if available
        if st.session_state.current_document and st.session_state.current_document_text:
            with col2:
                st.header("Document Content")
                st.text_area("Document Text", st.session_state.current_document_text, 
                               height=400, disabled=True, key="doc_view")
        elif uploaded_file:
            with col2:
                st.warning("Please ensure you've uploaded a valid Word document (.docx format)")

    # Prompt Library Tab
    with active_tab[1]:
        if not st.session_state.current_document:
            st.warning("Please upload a document first")
        else:
            if not st.session_state.show_create_prompt:
                # System prompt section
                st.header("System Prompt")
                current_system_prompt = st.session_state.prompt_manager.get_system_prompt()

                col1, col2 = st.columns([6, 1])
                with col2:
                    if st.button("✏️ Edit" if not st.session_state.editing_system_prompt else "Cancel"):
                        st.session_state.editing_system_prompt = not st.session_state.editing_system_prompt
                        st.rerun()

                # Display or edit system prompt
                if not st.session_state.editing_system_prompt:
                    st.code(current_system_prompt)
                else:
                    new_system_prompt = st.text_area(
                        "Edit system prompt:",
                        value=current_system_prompt,
                        height=100,
                        key="system_prompt"
                    )
                    if new_system_prompt != current_system_prompt:
                        if st.button("Save Changes", type="primary"):
                            if st.session_state.prompt_manager.update_system_prompt(new_system_prompt):
                                st.success("System prompt updated successfully!")
                                st.session_state.editing_system_prompt = False
                                st.rerun()
                            else:
                                st.error("Failed to update system prompt")

                # Available prompts section
                st.header("Available Prompts")

                if st.button("➕ Create New Prompt", type="primary", key="create_new_prompt_btn"):
                    st.session_state.show_create_prompt = True
                    st.rerun()

                # Display existing prompts
                prompts = st.session_state.prompt_manager.get_prompts()

                for prompt in prompts:
                    with st.expander(f"📝 {prompt['Name']}", expanded=True):
                        st.subheader(prompt['Name'])

                        # Current prompt display
                        st.markdown("#### Current Prompt")
                        st.code(prompt['Prompt'])

                        # Edit interface
                        st.markdown("#### Edit Prompt")
                        edited_prompt = st.text_area(
                            "Edit prompt text:", 
                            prompt['Prompt'],
                            key=f"prompt_{prompt['Name']}",
                            height=100
                        )

                        # Test buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔄 Test Original", key=f"test_original_{prompt['Name']}"):
                                spinner = create_loading_spinner("Testing original prompt...")
                                try:
                                    result = st.session_state.gpt_handler.process_document(
                                        st.session_state.current_document_text,
                                        prompt['Prompt'],
                                        st.session_state.prompt_manager.get_system_prompt()
                                    )
                                    spinner.empty()
                                    st.session_state.test_results[f"original_{prompt['Name']}"] = result
                                    st.rerun()
                                except Exception as e:
                                    spinner.empty()
                                    st.error(f"Error testing prompt: {str(e)}")

                        with col2:
                            if st.button("🔄 Test Edited Version", key=f"test_edited_{prompt['Name']}"):
                                spinner = create_loading_spinner("Testing edited version...")
                                try:
                                    result = st.session_state.gpt_handler.process_document(
                                        st.session_state.current_document_text,
                                        edited_prompt,
                                        st.session_state.prompt_manager.get_system_prompt()
                                    )
                                    spinner.empty()
                                    st.session_state.test_results[f"edited_{prompt['Name']}"] = result
                                    st.rerun()
                                except Exception as e:
                                    spinner.empty()
                                    st.error(f"Error testing edited version: {str(e)}")

                        # Display test results
                        original_key = f"original_{prompt['Name']}"
                        edited_key = f"edited_{prompt['Name']}"

                        if original_key in st.session_state.test_results or edited_key in st.session_state.test_results:
                            st.markdown("### Results Comparison")

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

                            # Save/Discard changes buttons
                            if edited_key in st.session_state.test_results:
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("💾 Save Changes", key=f"save_{prompt['Name']}", type="primary"):
                                        st.session_state.prompt_manager.update_prompt(
                                            prompt['Name'],
                                            prompt['Description'],
                                            edited_prompt
                                        )
                                        if original_key in st.session_state.test_results:
                                            del st.session_state.test_results[original_key]
                                        if edited_key in st.session_state.test_results:
                                            del st.session_state.test_results[edited_key]
                                        st.success("Changes saved!")
                                        st.rerun()

                                with col2:
                                    if st.button("❌ Discard Changes", key=f"discard_{prompt['Name']}", type="secondary"):
                                        if original_key in st.session_state.test_results:
                                            del st.session_state.test_results[original_key]
                                        if edited_key in st.session_state.test_results:
                                            del st.session_state.test_results[edited_key]
                                        st.rerun()

                        st.markdown("---")
                        if st.button("🗑️ Delete", key=f"delete_{prompt['Name']}", type="secondary"):
                            st.session_state.prompt_manager.delete_prompt(prompt['Name'])
                            st.rerun()

            else:
                # Create new prompt interface
                st.header("Create New Prompt")

                if st.button("← Back to Prompt Library"):
                    st.session_state.show_create_prompt = False
                    st.rerun()

                prompt_name = st.text_input("Name")
                prompt_description = st.text_area("Description", height=100)
                prompt_text = st.text_area("Prompt", height=200)

                if st.button("Save Prompt", type="primary"):
                    if prompt_name and prompt_text:
                        if st.session_state.prompt_manager.add_prompt(prompt_name, prompt_description, prompt_text):
                            st.success("Prompt saved!")
                            st.session_state.show_create_prompt = False
                            st.rerun()
                        else:
                            st.error("A prompt with this name already exists")
                    else:
                        st.error("Please provide both name and prompt text")

    # Workflows Tab
    with active_tab[2]:
        show_workflow_tab()

    # Help Tab
    with active_tab[3]:
        show_help()

if __name__ == "__main__":
    main()