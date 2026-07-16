"""
Candidate Profile Change Tracker - Manual Input Form Version
Users can manually enter resume details instead of uploading files.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import backend modules
from backend.database import Database
from backend.models import Resume, Comparison
from backend.ai_service import AIService
from backend.comparator import Comparator

# Page configuration
st.set_page_config(
    page_title="Candidate Profile Change Tracker",
    page_icon="",
    layout="wide"
)

# Initialize database
db = Database()

# Initialize services
@st.cache_resource
def init_ai_service():
    use_ai = st.session_state.get('use_ai', False)
    api_key = st.session_state.get('gemini_api_key', os.getenv('GEMINI_API_KEY', ''))
    return AIService(use_ai=use_ai, gemini_api_key=api_key)

@st.cache_resource
def init_comparator():
    ai_service = init_ai_service()
    return Comparator(ai_service=ai_service)

# Sidebar
with st.sidebar:
    st.title("Settings")
    
    st.subheader("AI Configuration")
    
    use_ai = st.toggle(
        "Enable AI Classification",
        value=st.session_state.get('use_ai', False),
        help="Use Google Gemini AI for enhanced parsing and classification"
    )
    st.session_state.use_ai = use_ai
    
    if use_ai:
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            value=st.session_state.get('gemini_api_key', ''),
            help="Get your API key from Google AI Studio"
        )
        st.session_state.gemini_api_key = api_key
        
        ai_service = init_ai_service()
        status = ai_service.get_status()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("AI Success", f"{status['ai_success_count']}")
            st.metric("Token Usage", f"{status['token_used']:,}")
        with col2:
            st.metric("Fallbacks", f"{status['fallback_count']}")
            st.metric("Success Rate", f"{status['success_rate']:.1f}%")
        
        if status['ai_enabled']:
            st.success("AI is active")
        else:
            st.error("AI is not available - using rule-based fallback")
    
    st.divider()
    
    st.subheader("Statistics")
    candidates = db.get_all_candidates()
    st.metric("Total Candidates", len(candidates))
    
    comparisons = db.get_all_comparisons()
    st.metric("Total Comparisons", len(comparisons))
    
    st.divider()
    
    # Quick example button
    if st.button("Load Example Data", use_container_width=True):
        st.session_state.show_example = True
        st.rerun()

# Main content
st.title("Candidate Profile Change Tracker")
st.markdown("Enter resume details manually to track profile changes")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "Manual Input",
    "Comparison Results",
    "History",
    "Analytics"
])

# Tab 1: Manual Input Form
with tab1:
    st.subheader("Enter Resume Details")
    
    # Create two columns for Previous and Updated resumes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Previous Resume")
        
        # Candidate ID
        prev_candidate_id = st.text_input(
            "Candidate ID",
            value="candidate_1" if st.session_state.get('show_example', False) else "",
            key="prev_candidate_id",
            placeholder="e.g., candidate_1"
        )
        
        # Job Title
        prev_job_title = st.text_input(
            "Job Title",
            value="Python Developer" if st.session_state.get('show_example', False) else "",
            key="prev_job_title",
            placeholder="e.g., Python Developer"
        )
        
        # Skills
        prev_skills = st.text_input(
            "Skills (comma-separated)",
            value="Python, Django, PostgreSQL" if st.session_state.get('show_example', False) else "",
            key="prev_skills",
            placeholder="e.g., Python, Django, PostgreSQL"
        )
        
        # Employer
        prev_employer = st.text_input(
            "Employer",
            value="ABC Technologies" if st.session_state.get('show_example', False) else "",
            key="prev_employer",
            placeholder="e.g., ABC Technologies"
        )
        
        # Experience
        prev_experience = st.number_input(
            "Experience (years)",
            min_value=0.0,
            max_value=50.0,
            value=2.0 if st.session_state.get('show_example', False) else 0.0,
            step=0.5,
            key="prev_experience"
        )
        
        # Location
        prev_location = st.text_input(
            "Location",
            value="Hyderabad" if st.session_state.get('show_example', False) else "",
            key="prev_location",
            placeholder="e.g., Hyderabad"
        )
        
        # Employment Dates
        st.markdown("#### Employment Dates")
        col1a, col1b = st.columns(2)
        with col1a:
            prev_start_date = st.date_input(
                "Start Date",
                value=datetime(2022, 1, 1) if st.session_state.get('show_example', False) else datetime.now(),
                key="prev_start_date"
            )
        with col1b:
            prev_end_date = st.date_input(
                "End Date",
                value=datetime(2024, 1, 1) if st.session_state.get('show_example', False) else datetime.now(),
                key="prev_end_date"
            )
    
    with col2:
        st.markdown("### Updated Resume")
        
        # Candidate ID (auto-filled from previous)
        updated_candidate_id = st.text_input(
            "Candidate ID",
            value=prev_candidate_id,
            key="updated_candidate_id",
            disabled=True,
            help="Candidate ID is auto-filled from previous resume"
        )
        
        # Job Title
        updated_job_title = st.text_input(
            "Job Title",
            value="Full Stack Developer" if st.session_state.get('show_example', False) else "",
            key="updated_job_title",
            placeholder="e.g., Full Stack Developer"
        )
        
        # Skills
        updated_skills = st.text_input(
            "Skills (comma-separated)",
            value="Python, Django, PostgreSQL, Angular, Docker" if st.session_state.get('show_example', False) else "",
            key="updated_skills",
            placeholder="e.g., Python, Django, PostgreSQL, Angular, Docker"
        )
        
        # Employer
        updated_employer = st.text_input(
            "Employer",
            value="XYZ Solutions" if st.session_state.get('show_example', False) else "",
            key="updated_employer",
            placeholder="e.g., XYZ Solutions"
        )
        
        # Experience
        updated_experience = st.number_input(
            "Experience (years)",
            min_value=0.0,
            max_value=50.0,
            value=3.0 if st.session_state.get('show_example', False) else 0.0,
            step=0.5,
            key="updated_experience"
        )
        
        # Location
        updated_location = st.text_input(
            "Location",
            value="Bengaluru" if st.session_state.get('show_example', False) else "",
            key="updated_location",
            placeholder="e.g., Bengaluru"
        )
        
        # Employment Dates
        st.markdown("#### Employment Dates")
        col2a, col2b = st.columns(2)
        with col2a:
            updated_start_date = st.date_input(
                "Start Date",
                value=datetime(2024, 2, 1) if st.session_state.get('show_example', False) else datetime.now(),
                key="updated_start_date"
            )
        with col2b:
            updated_end_date = st.date_input(
                "End Date",
                value=datetime(2026, 7, 16) if st.session_state.get('show_example', False) else datetime.now(),
                key="updated_end_date"
            )
    
    # Compare button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Compare Resumes", type="primary", use_container_width=True):
            # Validate inputs
            if not prev_candidate_id:
                st.error("Please enter a Candidate ID")
            elif not prev_job_title and not updated_job_title:
                st.error("Please enter at least one job title")
            elif not prev_skills and not updated_skills:
                st.error("Please enter at least one skill")
            else:
                # Build profiles from form data
                prev_profile = {
                    "name": prev_candidate_id,
                    "job_titles": [prev_job_title] if prev_job_title else [],
                    "skills": [s.strip() for s in prev_skills.split(',') if s.strip()] if prev_skills else [],
                    "employers": [prev_employer] if prev_employer else [],
                    "experience_years": prev_experience,
                    "location": prev_location,
                    "email": "",
                    "phone": "",
                    "linkedin_url": "",
                    "education": [],
                    "employment_dates": [{
                        "employer": prev_employer,
                        "title": prev_job_title,
                        "start": prev_start_date.strftime("%Y-%m-%d"),
                        "end": prev_end_date.strftime("%Y-%m-%d"),
                        "isCurrent": False
                    }] if prev_employer or prev_job_title else []
                }
                
                updated_profile = {
                    "name": updated_candidate_id,
                    "job_titles": [updated_job_title] if updated_job_title else [],
                    "skills": [s.strip() for s in updated_skills.split(',') if s.strip()] if updated_skills else [],
                    "employers": [updated_employer] if updated_employer else [],
                    "experience_years": updated_experience,
                    "location": updated_location,
                    "email": "",
                    "phone": "",
                    "linkedin_url": "",
                    "education": [],
                    "employment_dates": [{
                        "employer": updated_employer,
                        "title": updated_job_title,
                        "start": updated_start_date.strftime("%Y-%m-%d"),
                        "end": updated_end_date.strftime("%Y-%m-%d"),
                        "isCurrent": False
                    }] if updated_employer or updated_job_title else []
                }
                
                with st.spinner("Comparing resumes..."):
                    ai_service = init_ai_service()
                    comparator = init_comparator()
                    
                    # Compare profiles
                    result = comparator.compare_profiles(prev_profile, updated_profile)
                    
                    # Save to database
                    candidate_id = db.create_or_get_candidate(
                        name=prev_candidate_id,
                        email=""
                    )
                    
                    # Create resume content as text
                    prev_content = f"""
                    Candidate: {prev_candidate_id}
                    Job Title: {prev_job_title}
                    Skills: {prev_skills}
                    Employer: {prev_employer}
                    Experience: {prev_experience} years
                    Location: {prev_location}
                    Start Date: {prev_start_date}
                    End Date: {prev_end_date}
                    """
                    
                    updated_content = f"""
                    Candidate: {updated_candidate_id}
                    Job Title: {updated_job_title}
                    Skills: {updated_skills}
                    Employer: {updated_employer}
                    Experience: {updated_experience} years
                    Location: {updated_location}
                    Start Date: {updated_start_date}
                    End Date: {updated_end_date}
                    """
                    
                    prev_resume_id = db.save_resume(
                        candidate_id=candidate_id,
                        version='previous',
                        content=prev_content,
                        profile=prev_profile
                    )
                    
                    updated_resume_id = db.save_resume(
                        candidate_id=candidate_id,
                        version='updated',
                        content=updated_content,
                        profile=updated_profile
                    )
                    
                    comparison_id = db.save_comparison(
                        candidate_id=candidate_id,
                        prev_resume_id=prev_resume_id,
                        updated_resume_id=updated_resume_id,
                        result=result
                    )
                    
                    st.session_state.comparison_result = result
                    st.session_state.comparison_id = comparison_id
                    
                    st.success("Comparison completed successfully!")
                    st.rerun()

# Tab 2: Comparison Results
with tab2:
    if 'comparison_result' in st.session_state:
        result = st.session_state.comparison_result
        
        # Overall Status
        status_colors = {
            "No Significant Changes": "green",
            "Minor Profile Update": "blue",
            "Moderate Profile Update": "orange",
            "Significant Profile Update": "red"
        }
        
        status = result.get('overall_status', 'No Changes')
        color = status_colors.get(status, 'gray')
        
        st.markdown(f"""
        <div style="padding: 20px; border-radius: 10px; background-color: {color}20; border: 2px solid {color};">
            <h2 style="color: {color}; margin: 0;">Overall Status: {status}</h2>
            <p style="margin: 5px 0 0 0;">{result.get('summary', 'No summary available')}</p>
            <p style="margin: 5px 0 0 0; font-size: 0.9em; color: gray;">
                Classification Method: {result.get('classification_method', 'N/A')} | 
                Summary Method: {result.get('summary_method', 'N/A')}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Statistics
        stats = result.get('statistics', {})
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Changes", stats.get('total', 0))
        with col2:
            st.metric("Important", stats.get('important', 0), delta_color="inverse")
        with col3:
            st.metric("Minor", stats.get('minor', 0))
        with col4:
            st.metric("Needs Review", stats.get('needs_review', 0))
        
        # Changes Table
        changes = result.get('changes', [])
        if changes:
            st.subheader("Detailed Changes")
            
            change_data = []
            for change in changes:
                change_data.append({
                    "Type": change.get('type', '').replace('_', ' ').title(),
                    "Title": change.get('title', ''),
                    "Severity": change.get('severity', 'N/A').title(),
                    "Previous Value": change.get('previous_value', 'N/A'),
                    "New Value": change.get('new_value', 'N/A'),
                    "Reason": change.get('classification_reason', '')
                })
            
            df = pd.DataFrame(change_data)
            
            def color_severity(val):
                if val == 'Important':
                    return 'background-color: #ff6b6b; color: white'
                elif val == 'Needs Review':
                    return 'background-color: #ffd93d; color: black'
                return ''
            
            st.dataframe(
                df.style.applymap(color_severity, subset=['Severity']),
                use_container_width=True,
                hide_index=True
            )
            
            # Export options
            col1, col2 = st.columns(2)
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV Report",
                    data=csv,
                    file_name=f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                json_data = json.dumps(result, default=str, indent=2)
                st.download_button(
                    label="Download JSON Report",
                    data=json_data,
                    file_name=f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True
                )
    else:
        st.info("No comparison results available. Please enter resume details and compare.")

# Tab 3: History
with tab3:
    st.subheader("Comparison History")
    
    comparisons = db.get_all_comparisons()
    
    if comparisons:
        history_data = []
        for comp in comparisons:
            history_data.append({
                "ID": comp.get('id', ''),
                "Candidate": comp.get('candidate_name', 'Unknown'),
                "Status": comp.get('overall_status', 'N/A'),
                "Changes": comp.get('total_changes', 0),
                "Important": comp.get('important_changes', 0),
                "Needs Review": comp.get('needs_review_changes', 0),
                "Date": comp.get('created_at', '')
            })
        
        df_history = pd.DataFrame(history_data)
        st.dataframe(df_history, use_container_width=True, hide_index=True)
        
        # View specific comparison
        selected_id = st.selectbox(
            "View specific comparison",
            options=[f"Comparison #{c['ID']} - {c['Date']}" for c in history_data] if history_data else []
        )
        
        if selected_id:
            comp_id = int(selected_id.split('#')[1].split(' ')[0])
            comp_details = db.get_comparison(comp_id)
            if comp_details:
                st.json(comp_details)
    else:
        st.info("No comparison history available")

# Tab 4: Analytics
with tab4:
    st.subheader("Profile Evolution Analytics")
    
    candidates = db.get_all_candidates()
    
    if candidates:
        candidate_names = [c.get('name', 'Unknown') for c in candidates]
        selected_candidate = st.selectbox("Select Candidate", candidate_names)
        
        if selected_candidate:
            candidate = next(c for c in candidates if c.get('name') == selected_candidate)
            candidate_id = candidate.get('id')
            
            candidate_comparisons = db.get_candidate_comparisons(candidate_id)
            
            if candidate_comparisons:
                timeline_data = []
                for comp in candidate_comparisons:
                    result = comp.get('result', {})
                    stats = result.get('statistics', {})
                    timeline_data.append({
                        "Date": comp.get('created_at', ''),
                        "Status": result.get('overall_status', ''),
                        "Changes": stats.get('total', 0),
                        "Important": stats.get('important', 0),
                        "Minor": stats.get('minor', 0),
                        "Needs Review": stats.get('needs_review', 0)
                    })
                
                if timeline_data:
                    df_timeline = pd.DataFrame(timeline_data)
                    
                    st.line_chart(
                        df_timeline.set_index('Date')[['Changes', 'Important', 'Minor', 'Needs Review']]
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        avg_changes = df_timeline['Changes'].mean()
                        st.metric("Average Changes", f"{avg_changes:.1f}")
                    with col2:
                        total_comparisons = len(df_timeline)
                        st.metric("Total Comparisons", total_comparisons)
                    with col3:
                        latest_status = df_timeline.iloc[-1]['Status'] if not df_timeline.empty else "N/A"
                        st.metric("Latest Status", latest_status)
            else:
                st.info("No comparison data available for this candidate")
    else:
        st.info("No candidates found in the system")

# Footer
st.divider()
st.caption("Candidate Profile Change Tracker v2.0 | Built with Streamlit + AI Fallback")