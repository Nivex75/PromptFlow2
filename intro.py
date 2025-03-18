import streamlit as st

def show_introduction():
    st.markdown("""
    # PromptFlow

    PromptFlow helps legal professionals analyze documents systematically by creating reusable analysis workflows.

    ## Core Concept

    Instead of analyzing a document with a single prompt, PromptFlow lets you:
    1. Break down analysis into specific tasks
    2. Chain multiple prompts together
    3. Generate structured output documents

    ## How It Works

    1. **Upload Your Document** 📄
       - Upload any legal document (.docx format)
       - The text will be extracted automatically

    2. **Build Your Analysis Workflow** ⚙️
       - Create a workflow with multiple prompts
       - Each prompt focuses on a specific aspect
       - Example chain:
         1. First prompt extracts party details
         2. Second prompt identifies key dates
         3. Third prompt analyzes obligations
         4. Fourth prompt assesses risks
       - Test and refine each prompt individually
       - Results from earlier prompts inform later ones

    3. **Create Output Templates** 📋
       - Design document templates that combine all results
       - Use markers to insert prompt outputs:
         - Format: `{PROMPT_NAME_OUTPUT}`
         - Example: `{Extract Parties_OUTPUT}` inserts the party details
       - Templates can be in Markdown or HTML format
       - Download the final document when complete

    ## Example Workflow: Lease Agreement Analysis

    Here's how a lease analysis workflow works:

    1. **Individual Prompts**:
       ```
       Prompt 1: "Landlord Details"
       {Extract party information about the landlord}

       Prompt 2: "Key Dates"
       {Find lease start, end, and critical dates}

       Prompt 3: "Payment Terms"
       {Extract rent amounts and payment schedules}
       ```

    2. **Template Using Results**:
       ```markdown
       # Lease Analysis Report

       ## Landlord Information
       {Landlord Details_OUTPUT}

       ## Key Dates
       {Key Dates_OUTPUT}

       ## Payment Structure
       {Payment Terms_OUTPUT}
       ```

    ## Getting Started

    1. Go to the 'Document' tab → Upload your document
    2. Visit 'Workflows' tab → Create a new workflow
    3. Add prompts and test each one
    4. Create a template using the prompt markers
    5. Run the complete workflow to generate your document
    """)

if __name__ == "__main__":
    show_introduction()