import streamlit as st
import os
import tempfile
import json
from typing import Optional
from pathlib import Path
import asyncio

# API and instructor imports
import instructor
from google import genai
import anthropic
from openai import AsyncOpenAI

# Project imports
from resumer import ResumeTailorPipeline
from resumer.utils.latex_ops import json_to_latex_pdf

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Resume Tailor AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { padding-top: 1rem; }
    .stTabs [data-baseweb="tab-list"] button { font-size: 1.1em; }
    </style>
    """, unsafe_allow_html=True)

# ============================================
# MODEL CONFIGURATIONS
# ============================================

MODELS = {
    "Gemini": [
        "gemini-3-flash-preview",
        "gemini-3-pro-image-preview",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite"
    ],
    "Claude": [
        "claude-sonnet-4-5",
        "claude-haiku-4-5",
        "claude-opus-4-5",
    ],
    "OpenAI": [
        "gpt-5-mini",
        "gpt-5-nano",
        "gpt-4o-mini",
        "gpt-4o",
    ]
}

# ============================================
# SESSION STATE INITIALIZATION
# ============================================

def init_session_state():
    defaults = {
        "authenticated": False,
        "api_provider": None,
        "selected_model": None,
        "api_key": None,
        "resume_file": None,
        "resume_path": None,
        "resume_bytes": None,
        "job_url": None,
        "job_text": None,
        "pipeline": None,
        "tailored_resume_path": None,
        "tailored_resume_pdf": None,
        "tailored_resume_tex": None,
        "tailored_resume_json": None,
        "processing_log": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# ============================================
# API CLIENT INITIALIZATION
# ============================================

def get_gemini_instructor_client(api_key: str):
    """Initialize Instructor-patched Gemini client"""
    native_client = genai.Client(api_key=api_key)
    aclient = instructor.from_genai(
        native_client,
        mode=instructor.Mode.GENAI_TOOLS,
        use_async=True
    )
    return aclient

def get_claude_instructor_client(api_key: str):
    """Initialize Instructor-patched Claude client"""
    native_client = anthropic.Anthropic(api_key=api_key)
    aclient = instructor.from_anthropic(
        native_client,
        mode=instructor.Mode.TOOLS,
    )
    return aclient

def get_openai_instructor_client(api_key: str):
    """Initialize Instructor-patched OpenAI client"""
    native_client = AsyncOpenAI(api_key=api_key)
    aclient = instructor.from_openai(
        native_client,
        mode=instructor.Mode.TOOLS,
    )
    return aclient

# ============================================
# UTILITY FUNCTIONS
# ============================================

def log_message(message: str):
    """Add message to processing log"""
    st.session_state.processing_log.append(message)

def save_uploaded_file(uploaded_file) -> str:
    """Save uploaded file to temporary location and store bytes"""
    # Read the file bytes first
    file_bytes = uploaded_file.getvalue()
    st.session_state.resume_bytes = file_bytes
    
    # Save to temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        return tmp.name

async def run_pipeline(
    aclient,
    model_name: str,
    resume_path: str,
    job_url: Optional[str] = None,
    job_text: Optional[str] = None,
    progress_callback=None
) -> Optional[tuple]:
    """Run the ResumeTailorPipeline asynchronously"""
    try:
        if progress_callback:
            progress_callback("📖 Initializing pipeline...")
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline = ResumeTailorPipeline(
                aclient=aclient,
                model_name=model_name,
                resume_path=resume_path,
                output_dir=tmpdir,
                log_callback=progress_callback
            )
            
            # Store pipeline in session state
            st.session_state.pipeline = pipeline
            
            # Generate tailored resume asynchronously
            result = await pipeline.generate_tailored_resume(
                job_url=job_url,
                job_site_content=job_text
            )
            
            # Result is now a tuple: (pdf_path, tex_path)
            if isinstance(result, tuple):
                tailored_pdf_path, tailored_tex_path = result
            else:
                tailored_pdf_path = result
                tailored_tex_path = None
            
            if progress_callback:
                progress_callback("💾 Reading generated files...")
            
            # Read the PDF and store in session state
            if tailored_pdf_path and os.path.exists(tailored_pdf_path):
                with open(tailored_pdf_path, "rb") as f:
                    st.session_state.tailored_resume_pdf = f.read()
            
            # Read the TEX file and store in session state
            if tailored_tex_path and os.path.exists(tailored_tex_path):
                with open(tailored_tex_path, "r", encoding="utf-8") as f:
                    st.session_state.tailored_resume_tex = f.read()
            
            # Also store the JSON details
            st.session_state.tailored_resume_json = pipeline.resume_details
            
            if progress_callback:
                progress_callback("✅ Cleanup and finalization...")
            
            pipeline.close_cache()
            return (tailored_pdf_path, tailored_tex_path)
            
    except Exception as e:
        if progress_callback:
            progress_callback(f"❌ Error: {str(e)}")
        st.error(f"Pipeline Error: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

# ============================================
# MAIN APP UI
# ============================================

def main():
    # Header
    col1, col2 = st.columns([0.7, 0.3])
    with col1:
        st.title("📄 ResFit: Resume Tailor AI")
        st.markdown("*Tailor your resume for any job using AI - **Preserving your Links!***")
        st.info("💡 **Why ResFit?** Unlike other tools, this app preserves all hyperlinks in your resume (Portfolio, LinkedIn, GitHub, etc.) while tailoring the content.")
    
    # ========== SIDEBAR: AUTHENTICATION ==========
    with st.sidebar:
        st.header("🔐 Authentication")
        
        # Step 1: Select Provider
        api_provider = st.radio(
            "Step 1: Select API Provider",
            ["Gemini", "Claude", "OpenAI"],
            key="provider_select"
        )
        st.session_state.api_provider = api_provider
        
        # Step 2: Select Model based on provider
        available_models = MODELS[api_provider]
        selected_model = st.selectbox(
            "Step 2: Select Model",
            available_models,
            key=f"model_select_{api_provider}",
            index=0
        )
        st.session_state.selected_model = selected_model
        
        # Display model info
        model_info = {
            "Gemini": {
                "gemini-3-flash-preview": "⚡ Fastest, latest (recommended)",
                "gemini-3-pro-image-preview": "🖼️ Vision capabilities, advanced",
                "gemini-2.5-pro": "💪 Most capable but slower",
                "gemini-2.5-flash": "⚡ Fast & capable",
                "gemini-2.5-flash-lite": "💨 Fastest, most affordable",
            },
            "Claude": {
                "claude-sonnet-4-5": "⚡ Latest Sonnet (recommended)",
                "claude-haiku-4-5": "💨 Fastest, most affordable",
                "claude-opus-4-5": "💪 Most capable but slower",
            },
            "OpenAI": {
                "gpt-5-mini": "⚡ Latest & fastest (recommended)",
                "gpt-5-nano": "💨 Most affordable",
                "gpt-4o-mini": "💪 Good balance",
                "gpt-4o": "🦾 Most capable",
            }
        }
        
        if selected_model in model_info.get(api_provider, {}):
            st.caption(f"ℹ️ {model_info[api_provider][selected_model]}")
        
        st.divider()
        
        # Step 3: Enter API Key
        api_key = st.text_input(
            "Step 3: Enter API Key",
            type="password",
            key="api_key_input",
            help=f"Your {api_provider} API key will not be stored"
        )
        
        st.divider()
        
        # Authenticate button
        if st.button("🔓 Authenticate", use_container_width=True, type="primary"):
            if api_key:
                try:
                    if api_provider == "Gemini":
                        aclient = get_gemini_instructor_client(api_key)
                    elif api_provider == "Claude":
                        aclient = get_claude_instructor_client(api_key)
                    else:  # OpenAI
                        aclient = get_openai_instructor_client(api_key)
                    
                    st.session_state.authenticated = True
                    st.session_state.api_key = api_key
                    st.session_state.aclient = aclient
                    st.success(f"✅ Authenticated!\n\n**Provider:** {api_provider}\n**Model:** {selected_model}")
                except Exception as e:
                    st.error(f"❌ Authentication failed: {str(e)}")
            else:
                st.error("Please enter an API key")
        
        st.divider()
        
        # Display current auth status
        if st.session_state.authenticated:
            st.info(f"""
            ✅ **Authenticated**
            
            **Provider:** {st.session_state.api_provider}
            **Model:** {st.session_state.selected_model}
            """)
            
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.api_key = None
                st.session_state.api_provider = None
                st.session_state.selected_model = None
                st.session_state.aclient = None
                st.rerun()
    
    # ========== MAIN CONTENT ==========
    if not st.session_state.authenticated:
        st.warning("⚠️ Please authenticate with an API provider in the sidebar to continue")
        st.info("""
        **How to get an API key:**
        
        🔵 **Gemini**: Free API key at [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
        
        🔴 **Claude**: API key at [https://console.anthropic.com/](https://console.anthropic.com/)
        
        🟢 **OpenAI**: API key at [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
        """)
        return
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["📤 Upload", "⚙️ Process", "📊 Results"])
    
    # ========== TAB 1: UPLOAD ==========
    with tab1:
        st.header("Upload Your Materials")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📄 Resume PDF")
            resume_file = st.file_uploader(
                "Select your resume (PDF only)",
                type=["pdf"],
                key="resume_uploader"
            )
            
            if resume_file:
                # Save to temporary location
                resume_path = save_uploaded_file(resume_file)
                st.session_state.resume_file = resume_file
                st.session_state.resume_path = resume_path
                st.success(f"✅ Uploaded: {resume_file.name}")
                st.info(f"📊 Size: {resume_file.size / 1024:.1f} KB")
        
        with col2:
            st.subheader("🎯 Job Description")
            
            job_source = st.radio(
                "Provide job description via:",
                ["📎 URL", "📝 Text"],
                horizontal=False,
                key="job_source_select"
            )
            
            if job_source == "📎 URL":
                job_url = st.text_input(
                    "Paste job posting URL:",
                    placeholder="https://careers.example.com/job/123",
                    key="job_url_input"
                )
                if job_url:
                    st.session_state.job_url = job_url
                    st.session_state.job_text = None
                    st.success("✅ URL saved")
                
            else:  # Text
                job_text = st.text_area(
                    "Paste job description text:",
                    placeholder="Paste the complete job description here...",
                    height=200,
                    key="job_text_input"
                )
                if job_text:
                    st.session_state.job_text = job_text
                    st.session_state.job_url = None
                    st.success("✅ Job description saved")
        
        st.divider()
        
        # Summary
        st.subheader("📋 Upload Summary")
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            if st.session_state.resume_path:
                st.metric("Resume", "✅ Ready")
            else:
                st.metric("Resume", "⏳ Waiting")
        
        with summary_col2:
            if st.session_state.job_url or st.session_state.job_text:
                st.metric("Job Description", "✅ Ready")
            else:
                st.metric("Job Description", "⏳ Waiting")
    
    # ========== TAB 2: PROCESS ==========
    with tab2:
        st.header("Process Your Resume")
        
        # Validation
        if not st.session_state.resume_path:
            st.error("❌ Please upload a resume in the Upload tab")
            return
        
        if not st.session_state.job_url and not st.session_state.job_text:
            st.error("❌ Please provide a job description in the Upload tab")
            return
        
        st.info(f"""
        **Processing Configuration:**
        - **Provider:** {st.session_state.api_provider}
        - **Model:** {st.session_state.selected_model}
        
        **This process will:**
        1. Extract your resume structure asynchronously
        2. Extract job requirements asynchronously
        3. Tailor your resume to match the job
        4. Generate a PDF with the tailored version
        """)
        
        st.divider()
        
        # Start processing button
        if st.button("🚀 Generate Tailored Resume", use_container_width=True, type="primary", key="btn_start"):
            # Clear processing log
            st.session_state.processing_log = []
            
            # Create a single placeholder for live log display
            log_placeholder = st.empty()
            
            def update_progress(message: str):
                """Callback to update progress"""
                # Add message to log
                st.session_state.processing_log.append(message)
                
                # Keep only the latest x logs
                max_logs = 5
                if len(st.session_state.processing_log) > max_logs:
                    latest_logs = st.session_state.processing_log[-max_logs:]
                else:
                    latest_logs = st.session_state.processing_log
                
                # Update the placeholder with latest logs (no duplicates)
                with log_placeholder.container():
                    st.subheader(f"📝 Live Processing Log (Latest {max_logs})")
                    for log in latest_logs:
                        st.write(log)
            
            try:
                update_progress("🔐 Initializing async event loop...")
                
                # Create and run async pipeline
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                update_progress("⏳ Starting resume processing...")
                
                result = loop.run_until_complete(
                    run_pipeline(
                        aclient=st.session_state.aclient,
                        model_name=st.session_state.selected_model,
                        resume_path=st.session_state.resume_path,
                        job_url=st.session_state.job_url,
                        job_text=st.session_state.job_text,
                        progress_callback=update_progress
                    )
                )
                
                loop.close()
                
                if result:
                    st.session_state.tailored_resume_path = result
                    st.divider()
                    st.success("✅ Resume tailored successfully!")
                    st.balloons()
                else:
                    st.divider()
                    st.error("❌ Failed to generate tailored resume")
                    
            except Exception as e:
                st.divider()
                st.error(f"❌ Error: {str(e)}")
        
        # Display full processing log history (after processing)
        if st.session_state.processing_log:
            st.divider()
            st.subheader("📋 Full Processing Log")
            with st.expander("View all logs", expanded=False):
                for log in st.session_state.processing_log:
                    st.write(log)
    
    # ========== TAB 3: RESULTS ==========
    with tab3:
        st.header("Results")
        
        if not st.session_state.tailored_resume_path:
            st.info("👈 Complete the processing in the Process tab to see results here")
            return
        
        st.success("✅ Your tailored resume is ready!")
        
        # Download options
        st.subheader("📥 Download Your Resumes")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Original Resume")
            if st.session_state.resume_bytes:
                st.download_button(
                    label="📥 Download Original PDF",
                    data=st.session_state.resume_bytes,
                    file_name="original_resume.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        
        with col2:
            st.markdown("#### Tailored Resume (PDF)")
            if "tailored_resume_pdf" in st.session_state:
                st.download_button(
                    label="📥 Download Tailored PDF",
                    data=st.session_state.tailored_resume_pdf,
                    file_name="tailored_resume.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary"
                )
        
        with col3:
            st.markdown("#### Tailored Resume (LaTeX)")
            if "tailored_resume_tex" in st.session_state and st.session_state.tailored_resume_tex:
                st.download_button(
                    label="📥 Download LaTeX (.tex)",
                    data=st.session_state.tailored_resume_tex.encode('utf-8'),
                    file_name="tailored_resume.tex",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                st.info("LaTeX file not available")
        
        st.divider()
        
        # PDF Preview Section using iframe
        st.subheader("📄 PDF Preview")
        
        preview_col1, preview_col2 = st.columns(2)
        
        with preview_col1:
            with st.expander("👁️ View Original Resume PDF", expanded=True):
                if st.session_state.resume_bytes:
                    import base64
                    pdf_b64 = base64.b64encode(st.session_state.resume_bytes).decode()
                    pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_b64}" width="100%" height="600" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                else:
                    st.info("No original resume available")
        
        with preview_col2:
            with st.expander("✨ View Tailored Resume PDF", expanded=True):
                if "tailored_resume_pdf" in st.session_state:
                    import base64
                    pdf_b64 = base64.b64encode(st.session_state.tailored_resume_pdf).decode()
                    pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_b64}" width="100%" height="600" type="application/pdf"></iframe>'
                    st.markdown(pdf_display, unsafe_allow_html=True)
                else:
                    st.info("No tailored resume available")
        
        st.divider()
        
        # LaTeX Source Code Viewer
        st.subheader("📝 LaTeX Source Code")
        if "tailored_resume_tex" in st.session_state and st.session_state.tailored_resume_tex:
            with st.expander("👁️ View LaTeX Source Code", expanded=False):
                st.code(st.session_state.tailored_resume_tex, language="latex")
        else:
            st.info("No LaTeX source available")
        
        st.divider()
        
        # Data comparison
        st.subheader("📊 Resume Data Comparison")
        
        if st.session_state.pipeline:
            result_col1, result_col2 = st.columns(2)
            
            with result_col1:
                with st.expander("📖 Original Resume Data", expanded=False):
                    if st.session_state.pipeline.resume_info:
                        st.json(st.session_state.pipeline.resume_info.model_dump())
                    else:
                        st.info("No data available")
            
            with result_col2:
                with st.expander("✨ Tailored Resume Data", expanded=False):
                    if "tailored_resume_json" in st.session_state:
                        st.json(st.session_state.tailored_resume_json)
                    else:
                        st.info("No data available")
        
        st.divider()
        
        # Job info display
        st.subheader("🎯 Job Requirements (Extracted)")
        if st.session_state.pipeline and st.session_state.pipeline.job_info:
            with st.expander("View job info", expanded=False):
                if hasattr(st.session_state.pipeline.job_info, 'model_dump'):
                    st.json(st.session_state.pipeline.job_info.model_dump())
                else:
                    st.json(st.session_state.pipeline.job_info)

if __name__ == "__main__":
    main()