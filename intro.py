import streamlit as st

def show_introduction():
    st.markdown("""
    # Welcome to PromptFlow 👋
    
    PromptFlow is a powerful tool designed to streamline your legal document analysis using advanced AI technology. Think of it as your intelligent legal assistant that helps you analyze documents systematically and efficiently.
    
    ## How It Works 🔄
    
    1. **Upload Your Document** 📄
       - Start by uploading any legal document (contracts, agreements, leases, etc.)
       - The document will be processed and ready for analysis
    
    2. **Build Your Analysis Workflow** ⚙️
       - Create a new workflow or use existing templates
       - Add prompts from the library or create custom ones
       - Each prompt focuses on extracting specific information (e.g., key terms, obligations, parties)
    
    3. **Test and Refine** 🔍
       - Test individual prompts to see results immediately
       - Compare different versions of prompts
       - Iterate and refine until you get the desired output
    
    4. **Generate Complete Analysis** 📊
       - Run your entire workflow
       - Get structured results
       - Download formatted reports
    
    ## Example Workflow: Lease Agreement Analysis
    
    Here's a practical example:
    1. Upload a lease agreement
    2. Add prompts to extract:
       - Landlord and tenant details
       - Key dates and terms
       - Rent and payment terms
       - Special conditions
    3. Test each prompt and refine
    4. Generate a complete analysis report
    
    ## Benefits 🌟
    
    - **Save Time**: Automate repetitive document review tasks
    - **Ensure Consistency**: Use standardized prompts across similar documents
    - **Improve Accuracy**: Refine prompts based on actual results
    - **Flexible Analysis**: Customize workflows for different document types
    
    ## Ready to Start? 🚀
    
    1. Go to the 'Document' tab to upload your first document
    2. Visit the 'Prompt Library' to explore available prompts
    3. Create a workflow in the 'Workflows' tab
    
    Need help? Check out our detailed guide in the 'Help' tab!
    """)

if __name__ == "__main__":
    show_introduction()
