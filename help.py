import streamlit as st

def show_help():
    st.title("📚 PromptFlow Help Guide")

    # Overview
    st.header("Overview")
    st.markdown("""
    PromptFlow is a sophisticated document analysis application that leverages GPT-4 to streamline intelligent document 
    processing and prompt management. The application is organized around **Projects**, which contain your documents, 
    workflows, and results all in one place.
    """)

    # Key Features
    with st.expander("🎯 Key Features", expanded=True):
        st.markdown("""
        - **Project-Based Organization**: Keep your work organized in dedicated project spaces
        - **Document Processing**: Upload and analyze Word and PDF documents
        - **Workflow Management**: Build custom analysis workflows with reusable prompts
        - **Template System**: Create formatted output documents with dynamic content
        - **Batch Processing**: Run multiple workflows across multiple documents with one click
        - **GPT-4 Integration**: Powerful AI-driven document analysis
        """)

    # Getting Started
    with st.expander("🚀 Getting Started", expanded=True):
        st.markdown("""
        ### 1. Create a Project
        - From the main screen, enter a project name and description
        - Click "✨ Create Project" to create your workspace
        - Each project is completely isolated from others

        ### 2. Enter Your Project
        - Click "📂 Open" on any project card to enter that project
        - Once inside, you'll see tabs specific to that project:
          - **Documents**: Upload and manage source documents
          - **Workflows**: Create and edit analysis workflows
          - **Results**: View all generated outputs
          - **Templates**: Browse available output templates

        ### 3. Upload Documents
        - In the Documents tab, click "➕ Upload New Document"
        - Select Word (.docx) or PDF files
        - Give each document a meaningful name and description

        ### 4. Create Workflows
        - In the Workflows tab, click "➕ Create New Workflow"
        - Add prompts from the library or create custom ones
        - Associate a template for formatted output

        ### 5. Run Analysis
        - When you have documents and workflows ready, a special button appears:
          **"⚡ Run Workflows and Generate Results"**
        - This processes all workflows against all documents automatically
        - View results in the Results tab
        """)

    # Project Workflow
    with st.expander("📁 Understanding Projects", expanded=True):
        st.markdown("""
        ### What is a Project?
        A project is a dedicated workspace that contains:
        - **Documents**: The source files you want to analyze
        - **Workflows**: The analysis processes you've configured
        - **Results**: All outputs generated from running workflows
        - **Templates**: Output format templates (shared globally)

        ### Project Benefits
        - **Isolation**: Each project's data is separate
        - **Organization**: Group related documents and workflows
        - **Efficiency**: Batch process entire projects at once
        - **Clarity**: Clear visual indication of which project you're in

        ### Project Navigation
        - The project header shows you're inside a project workspace
        - Use "← Exit Project" to return to project selection
        - All tabs and actions apply only to the current project
        """)

    # Batch Processing
    with st.expander("⚡ Batch Processing", expanded=True):
        st.markdown("""
        ### The Power Button
        When your project has both documents and workflows, a special button appears:
        **"⚡ Run Workflows and Generate Results"**

        ### What It Does
        1. Takes each document in your project
        2. Runs every workflow against each document
        3. Generates results using the assigned templates
        4. Saves all outputs to the Results tab
        5. Shows progress with a real-time progress bar

        ### When to Use It
        - Processing multiple contracts with the same analysis
        - Running comprehensive document reviews
        - Generating reports for multiple files at once
        - Updating all analyses after workflow changes

        ### Tips
        - Ensure each workflow has a template assigned
        - Check that template markers match workflow prompts
        - Monitor the progress bar and error messages
        - Review results in the Results tab after completion
        """)

    # Working with Workflows
    with st.expander("🔄 Working with Workflows", expanded=True):
        st.markdown("""
        ### Creating Workflows
        1. Inside a project, go to the Workflows tab
        2. Click "➕ Create New Workflow"
        3. Add prompts in sequence
        4. Assign an output template
        5. Test with sample documents

        ### Workflow Components
        - **Prompts**: Individual analysis tasks
        - **Sequence**: Order matters - each prompt builds on previous results
        - **Template**: Defines how results are formatted
        - **Status**: Draft or Completed

        ### Testing Workflows
        - Use the "✏️ Edit" button to modify prompts
        - Test individual prompts before running full workflow
        - Compare original vs edited prompt results
        - Save successful changes

        ### Running Individual Workflows
        - Click "▶️ Run" on any workflow
        - Select a document and template
        - Execute to see immediate results
        - Download generated documents
        """)

    # Templates and Markers
    with st.expander("📝 Templates and Output", expanded=True):
        st.markdown("""
        ### Understanding Templates
        Templates are document formats that get filled with workflow results.

        ### Marker System
        - Templates contain markers like `{PROMPT_NAME_OUTPUT}`
        - Markers are automatically replaced with prompt results
        - Example: `{RENT_OUTPUT}` → actual rent amount from analysis

        ### Creating Effective Templates
        1. Use clear, descriptive marker names
        2. Match markers exactly to prompt names
        3. Format: `{PROMPT NAME_OUTPUT}` (spaces become underscores)
        4. Test with sample data first

        ### Template Types
        - **Letter Templates**: For client communications
        - **Report Templates**: For detailed analysis
        - **Summary Templates**: For executive overviews
        """)

    # Best Practices
    with st.expander("✨ Best Practices", expanded=True):
        st.markdown("""
        ### Project Organization
        - Create separate projects for different clients or matters
        - Use descriptive project names and descriptions
        - Keep related documents together
        - Archive completed projects

        ### Document Management
        - Use consistent naming conventions
        - Add descriptions to help identify documents
        - Upload clean, text-searchable files
        - Preview documents before processing

        ### Workflow Design
        - Start simple and add complexity gradually
        - Test each prompt individually first
        - Use library prompts when possible
        - Document custom prompt purposes

        ### Efficient Processing
        - Batch process when analyzing multiple documents
        - Check template assignments before running
        - Monitor progress and handle errors promptly
        - Review results systematically
        """)

    # Troubleshooting
    with st.expander("🔧 Troubleshooting", expanded=True):
        st.markdown("""
        ### Common Issues and Solutions

        **"Run Workflows" Button Not Appearing**
        - Ensure project has at least one document
        - Ensure project has at least one workflow
        - Refresh the page if needed

        **Batch Processing Errors**
        - Check that all workflows have templates assigned
        - Verify template markers match prompt names
        - Ensure documents are properly uploaded
        - Check API key validity

        **Missing Results**
        - Confirm workflows completed successfully
        - Check the Results tab in the correct project
        - Verify template markers were properly replaced

        **Performance Issues**
        - Process documents in smaller batches
        - Simplify complex prompts
        - Check document file sizes
        - Monitor API usage limits
        """)

    # Tips and Tricks
    with st.expander("💡 Tips and Tricks", expanded=True):
        st.markdown("""
        ### Power User Tips

        **Quick Workflow Creation**
        - Import workflows from the global library
        - Customize imported workflows for specific needs
        - Save successful prompt combinations

        **Template Optimization**
        - Create template variations for different audiences
        - Use conditional text based on results
        - Include formatting for professional output

        **Batch Processing Strategy**
        - Group similar documents in projects
        - Run test batches first
        - Review errors before full processing
        - Export results for further analysis

        **Collaboration**
        - Document workflow purposes clearly
        - Use consistent naming conventions
        - Share successful templates
        - Export results in standard formats
        """)

def main():
    show_help()

if __name__ == "__main__":
    main()