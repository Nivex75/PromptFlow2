import streamlit as st

def show_introduction():
    st.markdown("""
    # 🎯 Welcome to PromptFlow

    PromptFlow is a powerful document analysis tool designed for legal professionals who need to extract specific information from documents efficiently and consistently.

    ## 🏗️ Project-Based Organization

    PromptFlow organizes your work into **Projects** - dedicated workspaces that keep your documents, workflows, and results together:

    ### What's a Project?
    - **📁 A Container**: Each project holds related documents and workflows
    - **🔒 Isolated**: Projects are separate from each other
    - **🎯 Focused**: Work on one matter or client at a time
    - **⚡ Efficient**: Process entire projects with one click

    ## 📋 Core Workflow

    ### 1. Create a Project
    Start by creating a project for your matter or client. Give it a meaningful name and description.

    ### 2. Inside Your Project
    Once you open a project, you'll see four main areas:
    - **📄 Documents**: Upload contracts, leases, or other legal documents
    - **⚙️ Workflows**: Build analysis sequences with AI prompts
    - **📊 Results**: View all generated outputs
    - **📋 Templates**: Browse output format templates

    ### 3. The Magic Button ⚡
    When your project has both documents and workflows ready, a special button appears:
    **"Run Workflows and Generate Results"**

    This powerful feature:
    - Processes every document with every workflow
    - Generates formatted outputs automatically
    - Shows real-time progress
    - Handles errors gracefully

    ## 🔄 How Workflows Work

    Workflows are sequences of prompts that analyze your documents:

    1. **Prompt Chains**
       ```
       Prompt 1: "Extract all parties"
       → Identifies: Landlord LLC, Tenant Corp

       Prompt 2: "Find obligations for {parties}"
       → Uses parties from Prompt 1

       Prompt 3: "Assess risks"
       → Analyzes obligations from Prompt 2
       ```

    2. **Template Integration**
       - Templates contain markers like `{EXTRACT_PARTIES_OUTPUT}`
       - Workflow results automatically fill these markers
       - Get professionally formatted documents

    3. **Batch Processing**
       - Run one workflow on many documents
       - Run many workflows on one document  
       - Or run everything at once!

    ## 💡 Real-World Example

    **Project**: "Q1 2024 Lease Reviews"

    **Documents**: 
    - 10 commercial lease agreements
    - Various landlords and terms

    **Workflows**:
    1. "Key Terms Extraction" - Gets rent, term, parties
    2. "Risk Assessment" - Identifies problematic clauses
    3. "Executive Summary" - Creates 1-page overview

    **One Click Results**:
    - 30 formatted reports (3 per lease)
    - Consistent analysis across all documents
    - Hours of work completed in minutes

    ## 🚀 Getting Started

    1. **Create Your First Project**
       - Click "Create Project" on the main screen
       - Enter a name like "Smith Corp Lease Review"

    2. **Upload Documents**
       - Enter your project
       - Go to Documents tab
       - Upload Word or PDF files

    3. **Set Up Workflows**
       - Go to Workflows tab
       - Create new or import from library
       - Add prompts and assign templates

    4. **Generate Results**
       - Click the magic button when ready
       - Watch the progress bar
       - Download your reports

    ## 🎯 Why Projects?

    - **Organization**: Keep related work together
    - **Efficiency**: Batch process with one click
    - **Clarity**: Always know which project you're in
    - **Scalability**: Handle multiple matters simultaneously
    - **Isolation**: Each project's data stays separate

    ## 💪 Pro Tips

    1. **Start Small**: Test with one document first
    2. **Build Libraries**: Save successful workflows
    3. **Template First**: Design output before prompts
    4. **Batch Smart**: Group similar documents
    5. **Iterate Often**: Refine prompts based on results

    Ready to transform how you analyze documents? Create your first project and experience the power of PromptFlow!
    """)

if __name__ == "__main__":
    show_introduction()