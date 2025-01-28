import streamlit as st

def show_help():
    st.title("📚 PromptFlow Help Guide")
    
    # Overview
    st.header("Overview")
    st.markdown("""
    PromptFlow is a sophisticated document analysis application that leverages GPT-4 to streamline intelligent document 
    processing and prompt management. This tool helps you analyze legal documents efficiently by creating and managing 
    reusable prompts and workflows.
    """)

    # Key Features
    with st.expander("🎯 Key Features", expanded=True):
        st.markdown("""
        - **Document Processing**: Upload and analyze Word documents
        - **Prompt Library**: Create, test, and manage reusable prompts
        - **Workflow Management**: Build custom analysis workflows
        - **GPT-4 Integration**: Powerful AI-driven document analysis
        """)

    # Getting Started
    with st.expander("🚀 Getting Started", expanded=True):
        st.markdown("""
        ### 1. Upload a Document
        - Click on the 'Document' tab
        - Use the file uploader to select a Word document (.docx)
        - The document content will be displayed for review

        ### 2. Using the Prompt Library
        - Navigate to the 'Prompt Library' tab
        - Create new prompts or use existing ones
        - Test prompts with your document
        - Compare results and refine prompts

        ### 3. Creating Workflows
        - Go to the 'Workflows' tab
        - Click '➕ Create Workflow'
        - Add prompts from library or create new ones
        - Test and refine your workflow
        """)

    # Working with Prompts
    with st.expander("📝 Working with Prompts", expanded=True):
        st.markdown("""
        ### Creating a New Prompt
        1. Go to 'Prompt Library'
        2. Click '➕ Create New Prompt'
        3. Fill in:
           - Name: A unique identifier
           - Description: Purpose of the prompt
           - Prompt Text: The actual prompt

        ### Testing Prompts
        1. Select an existing prompt
        2. Click '🔄 Test Original' to test current version
        3. Edit the prompt if needed
        4. Click '🔄 Test Edited Version' to test changes
        5. Compare results side by side
        6. Save or discard changes

        ### Tips for Writing Prompts
        - Be specific and clear in your instructions
        - Break down complex tasks into smaller prompts
        - Use consistent formatting for similar types of analysis
        """)

    # Working with Workflows
    with st.expander("🔄 Working with Workflows", expanded=True):
        st.markdown("""
        ### Creating a Workflow
        1. Go to 'Workflows' tab
        2. Click '➕ Create Workflow'
        3. Name your workflow
        4. Add description (optional)

        ### Managing Workflow Prompts
        - Add prompts from library
        - Create new custom prompts
        - Arrange prompts in desired order
        - Test individual prompts
        - Edit and refine as needed

        ### Testing & Running Workflows
        Three modes available:
        1. **Edit Mode**: Modify workflow structure and prompts
        2. **Test Mode**: Test and refine individual prompts
        3. **Run Mode**: Execute full workflow and view results
        """)

    # Best Practices
    with st.expander("✨ Best Practices", expanded=True):
        st.markdown("""
        ### Document Preparation
        - Use clean, well-formatted Word documents
        - Ensure documents are text-searchable
        - Keep file sizes reasonable

        ### Prompt Management
        - Use descriptive names for prompts
        - Test prompts with various document types
        - Document prompt purposes and use cases
        - Regular review and refinement of prompts

        ### Workflow Efficiency
        - Start with simpler workflows
        - Test workflows with sample documents
        - Regularly backup important prompts
        - Monitor and optimize processing time
        """)

    # Troubleshooting
    with st.expander("🔧 Troubleshooting", expanded=True):
        st.markdown("""
        ### Common Issues and Solutions

        **Document Won't Upload**
        - Verify file is in .docx format
        - Check file size
        - Ensure document isn't corrupt

        **Prompt Testing Issues**
        - Verify document is loaded
        - Check prompt syntax
        - Ensure API key is valid
        - Try with shorter document sections first

        **Workflow Problems**
        - Test individual prompts first
        - Verify workflow configuration
        - Check for prompt dependencies
        - Monitor system resources
        """)

def main():
    show_help()

if __name__ == "__main__":
    main()
