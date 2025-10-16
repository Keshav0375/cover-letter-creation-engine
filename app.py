import streamlit as st
import json
from pathlib import Path
import time
from main import generate_cover_letter
from pdf import create_pdf
import traceback

# Page configuration
st.set_page_config(
    page_title="AI Cover Letter Generator",
    page_icon="📄",
    layout="centered"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stTextArea textarea {
        font-size: 14px;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">📄 AI Cover Letter Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Generate professional, personalized cover letters in seconds</div>',
            unsafe_allow_html=True)

# Initialize session state
if 'cover_letter' not in st.session_state:
    st.session_state.cover_letter = None
if 'pdf_bytes' not in st.session_state:
    st.session_state.pdf_bytes = None


# Load hardcoded resume
@st.cache_data
def load_resume():
    """Load the resume from example_resume.json"""
    try:
        resume_path = Path("example_resume.json")
        if not resume_path.exists():
            st.error("❌ Resume file 'example_resume.json' not found in the project directory!")
            st.stop()

        with open(resume_path, 'r', encoding='utf-8') as f:
            resume_data = json.load(f)
        return resume_data
    except Exception as e:
        st.error(f"❌ Error loading resume: {str(e)}")
        st.stop()


# Load resume data
resume_data = load_resume()

# Display candidate info (optional)
with st.expander("ℹ️ View Resume Summary"):
    st.markdown(f"""
    **Candidate:** {resume_data.get('name', 'N/A')}  
    **Email:** {resume_data.get('contacts', {}).get('email', 'N/A')}  
    **Location:** {resume_data.get('contacts', {}).get('location', 'N/A')}

    Resume is loaded and ready to generate cover letters!
    """)

st.markdown("---")

# Job Description Input
st.markdown("### 💼 Job Description")
job_description = st.text_area(
    "Paste the complete job description here",
    height=300,
    placeholder="Paste the full job description including role overview, responsibilities, requirements, and company information...",
    help="Include as much detail as possible for a better cover letter"
)

# Generate button
if job_description and len(job_description.strip()) >= 50:
    if st.button("🚀 Generate Cover Letter PDF", type="primary", use_container_width=True):
        try:
            with st.spinner("🤖 AI is crafting your personalized cover letter... This may take 10-20 seconds."):
                # Generate cover letter
                cover_letter = generate_cover_letter(resume_data, job_description.strip())
                st.session_state.cover_letter = cover_letter

            with st.spinner("📄 Creating PDF..."):
                # Generate PDF
                pdf_bytes = create_pdf(cover_letter)
                st.session_state.pdf_bytes = pdf_bytes
                time.sleep(0.3)  # Brief pause for UX

            st.success("✅ Cover letter generated successfully!")

        except ValueError as ve:
            st.error(f"❌ Validation Error: {str(ve)}")
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            with st.expander("🔍 Error Details"):
                st.code(traceback.format_exc())
else:
    if not job_description:
        st.info("👆 Paste a job description above to get started!")
    elif len(job_description.strip()) < 50:
        st.warning("⚠️ Job description seems too short. Please provide more details (minimum 50 characters).")

# Display results
if st.session_state.cover_letter:
    st.markdown("---")
    st.markdown("### 📝 Your Cover Letter")

    # Display cover letter in a nice box
    st.markdown(f"""
    <div style="background-color: white; padding: 2rem; border-radius: 10px; 
                border: 1px solid #ddd; line-height: 1.8; white-space: pre-wrap;">
    {st.session_state.cover_letter}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Download button (centered)
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.session_state.pdf_bytes:
            st.download_button(
                label="⬇️ Download PDF",
                data=st.session_state.pdf_bytes,
                file_name="cover_letter.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    # Option to generate new cover letter
    if st.button("🔄 Generate New Cover Letter", use_container_width=True):
        st.session_state.cover_letter = None
        st.session_state.pdf_bytes = None
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>🤖 Powered by AWS Bedrock Claude Sonnet 3.5 | Built with Streamlit</p>
        <p>💡 Using resume: example_resume.json</p>
    </div>
""", unsafe_allow_html=True)