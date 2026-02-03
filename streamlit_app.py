import streamlit as st
import requests
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
import io
import base64

# Configure page
st.set_page_config(
    page_title="NeuralScan AI | Intelligent Resume Analysis",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =============================================================================
# NEURAL NEXUS DESIGN SYSTEM — GLOBAL STYLES
# =============================================================================

def load_css():
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    :root {
        --neon-cyan: #00f0ff;
        --neon-purple: #bc13fe;
        --neon-green: #0aff68;
        --neon-amber: #ffb800;
        --deep-void: #050508;
        --glass-surface: rgba(255, 255, 255, 0.03);
        --glass-border: rgba(255, 255, 255, 0.08);
        --text-primary: #ffffff;
        --text-secondary: #a0a0b0;
        --success: #00d084;
        --warning: #ff9f43;
        --danger: #ff4757;
    }
    
    /* Global Reset & Background */
    .stApp {
        background: 
            radial-gradient(ellipse at 0% 0%, rgba(0, 240, 255, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 100% 0%, rgba(188, 19, 254, 0.15) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 100%, rgba(10, 255, 104, 0.08) 0%, transparent 50%),
            linear-gradient(180deg, #050508 0%, #0a0a0f 50%, #050508 100%);
        background-attachment: fixed;
        font-family: 'Inter', sans-serif;
        color: var(--text-primary);
    }
    
    /* Hide Streamlit Chrome */

    
    /* Typography Scale */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--text-primary);
    }
    
    .hero-title {
        font-size: 3.5rem !important;
        background: linear-gradient(135deg, #fff 0%, var(--neon-cyan) 50%, var(--neon-purple) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        animation: titlePulse 4s ease-in-out infinite;
    }
    
    @keyframes titlePulse {
        0%, 100% { filter: brightness(1); }
        50% { filter: brightness(1.2); }
    }
    
    .subtitle {
        text-align: center;
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 1rem;
        letter-spacing: 0.05em;
    }
    
    /* Neural Grid Overlay */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-image: 
            linear-gradient(rgba(0, 240, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 240, 255, 0.03) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: 0;
        mask-image: radial-gradient(circle at center, black 40%, transparent 100%);
    }
    
    /* Floating Orbs */
    .orb {
        position: fixed;
        border-radius: 50%;
        filter: blur(80px);
        opacity: 0.4;
        pointer-events: none;
        z-index: 0;
        animation: float 20s infinite ease-in-out;
    }
    .orb-1 { width: 400px; height: 400px; background: var(--neon-cyan); top: -10%; left: -10%; animation-delay: 0s; }
    .orb-2 { width: 300px; height: 300px; background: var(--neon-purple); top: 40%; right: -5%; animation-delay: -5s; }
    .orb-3 { width: 250px; height: 250px; background: var(--neon-green); bottom: -5%; left: 30%; animation-delay: -10s; }
    
    @keyframes float {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(30px, -30px) scale(1.1); }
        66% { transform: translate(-20px, 20px) scale(0.9); }
    }
    
    /* Navigation Tabs — Cyberpunk Style */
    .stTabs [data-baseweb="tab-list"] {
       display:flex;
       justify-content:center;
        gap: 0;
        background: var(--glass-surface);
        backdrop-filter: blur(20px);
        border-radius: 16px;
        padding: 8px;
        border: 1px solid var(--glass-border);
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        padding: 0 24px;
        border-radius: 12px;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.05em;
        color: var(--text-secondary);
        border: none;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stTabs [data-baseweb="tab"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s;
    }
    
    .stTabs [data-baseweb="tab"]:hover::before {
        left: 100%;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: var(--text-primary);
        background: rgba(255,255,255,0.05);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.15), rgba(188, 19, 254, 0.15)) !important;
        color: var(--neon-cyan) !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
    }    
    /* Input Fields — Neon Glow */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stFileUploader > div {
        background: rgba(0,0,0,0.3) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--neon-cyan) !important;
        box-shadow: 0 0 0 3px rgba(0, 240, 255, 0.1) !important;
    }
    
    /* File Uploader Specific */
    .stFileUploader > div {
        background: rgba(0,0,0,0.2) !important;
        border: 2px dashed rgba(0, 240, 255, 0.3) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--neon-cyan) !important;
        background: rgba(0, 240, 255, 0.05) !important;
    }
    
    /* Buttons — Cybernetic */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, rgba(0, 240, 255, 0.1), rgba(188, 19, 254, 0.1)) !important;
        border: 1px solid rgba(0, 240, 255, 0.3) !important;
        color: var(--neon-cyan) !important;
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 1rem 2rem !important;
        border-radius: 12px !important;
        position: relative;
        overflow: hidden;
        transition: all 0.3s ease;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.1);
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.6s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.3);
        border-color: var(--neon-cyan) !important;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Primary Action Button */
    .primary-btn {
        background: linear-gradient(135deg, var(--neon-cyan), var(--neon-purple)) !important;
        color: #000 !important;
        border: none !important;
        font-weight: 800 !important;
    }
    
    /* Progress Bars — Energy Flow */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--neon-cyan), var(--neon-purple), var(--neon-green)) !important;
        border-radius: 10px;
        box-shadow: 0 0 10px rgba(0, 240, 255, 0.5);
        animation: shimmer 2s infinite linear;
        background-size: 200% 100% !important;
    }
    
    @keyframes shimmer {
        0% { background-position: 100% 0; }
        100% { background-position: -100% 0; }
    }
    
    /* Metrics — HUD Style */
    [data-testid="stMetric"] {
        background: var(--glass-surface);
        backdrop-filter: blur(10px);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        position: relative;
        overflow: hidden;
    }
    
    [data-testid="stMetric"]::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, var(--neon-cyan), var(--neon-purple));
    }
    
    [data-testid="stMetricLabel"] {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-secondary) !important;
    }
    
    [data-testid="stMetricValue"] {
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        background: linear-gradient(135deg, #fff, var(--neon-cyan));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* DataFrames — Terminal Style */
    .stDataFrame {
        background: rgba(0,0,0,0.2) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        overflow: hidden;
    }
    
    .stDataFrame thead tr th {
        background: rgba(0, 240, 255, 0.1) !important;
        color: var(--neon-cyan) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-bottom: 1px solid rgba(0, 240, 255, 0.2) !important;
    }
    
    .stDataFrame tbody tr:hover {
        background: rgba(0, 240, 255, 0.05) !important;
    }
    
    /* Expanders — Collapsible Panels */
    .streamlit-expander {
        background: var(--glass-surface) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 16px !important;
        overflow: hidden;
    }
    
    .streamlit-expanderHeader {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 600 !important;
        color: var(--neon-cyan) !important;
        padding: 1rem 1.5rem !important;
        background: rgba(0, 240, 255, 0.05) !important;
    }
    
    /* Alerts — Status Indicators */
    .stAlert {
        background: var(--glass-surface) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
    }
    
    .stSuccess {
        border-left: 4px solid var(--neon-green) !important;
    }
    
    .stError {
        border-left: 4px solid var(--danger) !important;
    }
    
    .stWarning {
        border-left: 4px solid var(--warning) !important;
    }
    
    .stInfo {
        border-left: 4px solid var(--neon-cyan) !important;
    }
    
    /* Match Score Rings */
    .score-ring {
        position: relative;
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: conic-gradient(var(--neon-cyan) calc(var(--score) * 1%), transparent 0);
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
    }
    
    .score-ring::before {
        content: '';
        position: absolute;
        width: 100px;
        height: 100px;
        border-radius: 50%;
        background: var(--deep-void);
    }
    
    .score-value {
        position: relative;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--neon-cyan);
    }
    
    /* Section Dividers */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--glass-border), transparent);
        margin: 2rem 0;
        border: none;
    }
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.2);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 240, 255, 0.3);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 240, 255, 0.5);
    }
    
    /* Loading States */
    .stSpinner > div {
        border-top-color: var(--neon-cyan) !important;
        border-right-color: var(--neon-purple) !important;
    }
    
    /* Skill Tags */
    .skill-tag {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        background: rgba(0, 240, 255, 0.1);
        border: 1px solid rgba(0, 240, 255, 0.3);
        border-radius: 20px;
        font-size: 0.85rem;
        color: var(--neon-cyan);
        transition: all 0.2s ease;
    }
    
    .skill-tag:hover {
        background: rgba(0, 240, 255, 0.2);
        transform: scale(1.05);
    }
    
    .skill-tag-missing {
        background: rgba(255, 71, 87, 0.1);
        border-color: rgba(255, 71, 87, 0.3);
        color: var(--danger);
    }
    
    /* Comparison Cards */
    .compare-card {
        background: linear-gradient(135deg, rgba(0,0,0,0.4), rgba(0,0,0,0.2));
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .compare-card:hover {
        border-color: var(--neon-cyan);
        box-shadow: 0 0 30px rgba(0, 240, 255, 0.1);
    }
    
    .compare-winner {
        border-color: var(--neon-green);
        box-shadow: 0 0 30px rgba(10, 255, 104, 0.2);
    }
    
    /* Responsive Grid */
    @media (max-width: 768px) {
        .hero-title { font-size: 2rem !important; }
        .stTabs [data-baseweb="tab"] { font-size: 0.8rem; padding: 0 12px; }
    }
    </style>
    
    <!-- Floating Background Orbs -->
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    """
    return css

st.markdown(load_css(), unsafe_allow_html=True)

# =============================================================================
# API CONFIGURATION
# =============================================================================

API_BASE_URL = "http://localhost:8000/api/v1"

def make_api_request(endpoint: str, files=None, data=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if files:
            response = requests.post(url, files=files, data=data, timeout=60)
        else:
            response = requests.post(url, json=data, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("🔌 Connection failed. Ensure FastAPI server is running on port 8000")
        return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_score_ring(score: float, size: int = 120):
    """Render animated score ring"""
    color = "#0aff68" if score >= 80 else "#ffb800" if score >= 60 else "#ff4757"
    css_score = min(score, 100)
    
    html = f"""
    <div style="
        position: relative;
        width: {size}px;
        height: {size}px;
        margin: 0 auto;
    ">
        <svg viewBox="0 0 36 36" style="transform: rotate(-90deg);">
            <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="rgba(255,255,255,0.1)"
                stroke-width="3"
            />
            <path
                d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                fill="none"
                stroke="{color}"
                stroke-width="3"
                stroke-dasharray="{css_score}, 100"
                style="transition: stroke-dasharray 1s ease;"
            />
        </svg>
        <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
        ">
            <div style="
                font-size: 1.5rem;
                font-weight: 700;
                color: {color};
                font-family: 'Space Grotesk', sans-serif;
            ">{score:.0f}%</div>
            <div style="
                font-size: 0.7rem;
                color: #a0a0b0;
                text-transform: uppercase;
                letter-spacing: 0.1em;
            ">Match</div>
        </div>
    </div>
    """
    return html

def render_skill_tags(skills: list, matched: bool = True):
    """Render skill tags"""
    if not skills:
        return "<span style='color: #666;'>None detected</span>"
    
    tags = ""
    color_class = "skill-tag" if matched else "skill-tag skill-tag-missing"
    for skill in skills[:15]:  # Limit to 15 tags
        tags += f'<span class="{color_class}">{skill}</span>'
    if len(skills) > 15:
        tags += f'<span class="{color_class}">+{len(skills)-15} more</span>'
    return tags

def render_match_badge(score: float):
    """Render match status badge"""
    if score >= 80:
        return "🟢 EXCEPTIONAL MATCH", "#0aff68"
    elif score >= 60:
        return "🟡 STRONG MATCH", "#ffb800"
    elif score >= 40:
        return "🟠 MODERATE MATCH", "#ff9f43"
    else:
        return "🔴 LOW MATCH", "#ff4757"

# =============================================================================
# HEADER SECTION
# =============================================================================

st.markdown("""
<div style="text-align: center; padding: 0rem 0 0.5rem 0;">
    <h1 class="hero-title">NeuralScan AI</h1>
    <p class="subtitle">Advanced Neural Resume Analysis & Candidate Matching</p>
</div>
""", unsafe_allow_html=True)

# =============================================================================
# NAVIGATION TABS
# =============================================================================

tab1, tab2, tab3, tab4 = st.tabs(["Single Analysis", "Batch Processing", "Compare Candidates", "System Info"])

# =============================================================================
# TAB 1: SINGLE RESUME SCREENING
# =============================================================================

with tab1:
    st.markdown('<div class="glass-card" style="margin-bottom: 2rem;">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.markdown("### 📎 Upload Resume")
        st.caption("Supported: PDF, DOCX (ATS-friendly formats preferred)")
        resume_file = st.file_uploader(
            "Drop resume here",
            type=['pdf', 'docx'],
            key="single_resume",
            label_visibility="collapsed"
        )
        
        if resume_file:
            st.success(f"✅ Loaded: {resume_file.name}")
    
    with col2:
        st.markdown("### 🎯 Job Requirements")
        st.caption("Paste the complete job description")
        job_description = st.text_area(
            "",
            height=200,
            placeholder="Paste job description here...",
            label_visibility="collapsed"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    analyze_col1, analyze_col2, analyze_col3 = st.columns([1, 2, 1])
    with analyze_col2:
        analyze_btn = st.button("🔮 INITIATE NEURAL ANALYSIS", use_container_width=True, type="primary")
    
    if analyze_btn:
        if resume_file and job_description:
            with st.spinner("🧠 Processing neural embeddings..."):
                try:
                    file_bytes = resume_file.read()
                    files = {'resume': (resume_file.name, io.BytesIO(file_bytes), 'application/octet-stream')}
                    data = {'job_description': job_description}
                    
                    url = f"{API_BASE_URL}/screen-resume"
                    response = requests.post(url, files=files, data=data, timeout=60)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get('status') == 'success':
                            match_score = result['match_score']
                            explanation = result['explanation']
                            
                            # Results Header
                            st.markdown("---")
                            st.markdown("## 📈 Analysis Results")
                            
                            # Score Section
                            score_col1, score_col2, score_col3 = st.columns([1, 2, 1])
                            with score_col2:
                                st.markdown(render_score_ring(match_score), unsafe_allow_html=True)
                                label, color = render_match_badge(match_score)
                                st.markdown(f"""
                                <div style="text-align: center; margin-top: 1rem;">
                                    <span style="
                                        background: {color}20;
                                        color: {color};
                                        padding: 0.5rem 1rem;
                                        border-radius: 20px;
                                        font-weight: 700;
                                        font-size: 0.9rem;
                                        border: 1px solid {color}40;
                                    ">{label}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            
                            # Metrics Grid
                            st.markdown("### 📊 Detailed Metrics")
                            metrics = explanation['score_breakdown']
                            
                            m1, m2, m3, m4 = st.columns(4)
                            with m1:
                                st.metric("Skill Alignment", f"{metrics['skill_match']}%")
                            with m2:
                                st.metric("Experience Fit", f"{metrics['experience_match']}%")
                            with m3:
                                st.metric("Education Match", f"{metrics['education_match']}%")
                            with m4:
                                st.metric("Semantic Similarity", f"{metrics['semantic_similarity']}%")
                            
                            st.progress(min(match_score / 100, 1.0))
                            
                            # Analysis Text
                            st.markdown("---")
                            st.markdown("### 🧠 AI Assessment")
                            st.markdown(f"""
                            <div style="
                                background: rgba(0,0,0,0.2);
                                border-left: 4px solid var(--neon-cyan);
                                padding: 1.5rem;
                                border-radius: 0 12px 12px 0;
                                margin: 1rem 0;
                            ">
                                <strong style="color: var(--neon-cyan); font-size: 1.1rem;">{explanation['verdict']}</strong>
                                <p style="margin: 0.5rem 0 0 0; color: #a0a0b0;">{explanation['verdict_reason']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.write(explanation['narrative'])
                            
                            # Skills Analysis
                            st.markdown("---")
                            st.markdown("### 💼 Skills Matrix")
                            
                            skill_col1, skill_col2 = st.columns(2)
                            with skill_col1:
                                st.markdown("**✅ Matched Capabilities**")
                                for category, skills in result['matched_skills'].items():
                                    if skills:
                                        st.markdown(f"*{category}*")
                                        st.markdown(render_skill_tags(skills, True), unsafe_allow_html=True)
                            
                            with skill_col2:
                                st.markdown("**❌ Development Areas**")
                                for category, skills in result['missing_skills'].items():
                                    if skills:
                                        st.markdown(f"*{category}*")
                                        st.markdown(render_skill_tags(skills, False), unsafe_allow_html=True)
                            
                            # Strengths & Gaps
                            st.markdown("---")
                            sg_col1, sg_col2 = st.columns(2)
                            with sg_col1:
                                st.markdown("### 💪 Key Strengths")
                                for strength in explanation['key_strengths']:
                                    st.markdown(f"✨ {strength}")
                            
                            with sg_col2:
                                st.markdown("### ⚠️ Skill Gaps")
                                for gap in explanation['key_gaps']:
                                    st.markdown(f"🔸 {gap}")
                            
                            # Additional Stats
                            st.markdown("---")
                            analysis = result['analysis']
                            stat_col1, stat_col2, stat_col3 = st.columns(3)
                            with stat_col1:
                                st.metric("Years Experience", f"{analysis['years_of_experience']:.1f}")
                            with stat_col2:
                                st.metric("Education Entries", len(analysis['education']))
                            with stat_col3:
                                st.metric("Semantic Hits", analysis['semantic_matches'])
                            
                            # Top Matches
                            if analysis['top_matches']:
                                st.markdown("### 🎯 Top Concept Matches")
                                for match in analysis['top_matches'][:3]:
                                    with st.expander(f"Relevance: {match['similarity_score']:.1%}"):
                                        st.markdown(f"**Job Req:** {match['job_requirement']}")
                                        st.markdown(f"**Resume Evidence:** {match['resume_match']}")
                        else:
                            st.error("Analysis failed: Invalid response structure")
                    else:
                        st.error(f"API Error: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"Processing error: {str(e)}")
        else:
            st.warning("⚠️ Please provide both resume and job description")

# =============================================================================
# TAB 2: BATCH SCREENING
# =============================================================================

with tab2:
    st.markdown('<div class="glass-card" style="margin-bottom: 2rem;">', unsafe_allow_html=True)
    
    batch_col1, batch_col2 = st.columns([1, 1], gap="large")
    
    with batch_col1:
        st.markdown("### 📁 Bulk Upload")
        st.caption("Upload multiple resumes for comparative analysis")
        resume_files = st.file_uploader(
            "Select files",
            type=['pdf', 'docx'],
            accept_multiple_files=True,
            key="batch_resumes",
            label_visibility="collapsed"
        )
        
        if resume_files:
            st.info(f"📦 {len(resume_files)} files staged for processing")
    
    with batch_col2:
        st.markdown("### 🎯 Position Requirements")
        st.caption("Job description for batch comparison")
        job_desc_batch = st.text_area(
            "",
            height=200,
            placeholder="Paste job description here...",
            key="batch_job_desc",
            label_visibility="collapsed"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    batch_btn_col1, batch_btn_col2, batch_btn_col3 = st.columns([1, 2, 1])
    with batch_btn_col2:
        batch_btn = st.button("🚀 EXECUTE BATCH ANALYSIS", use_container_width=True)
    
    if batch_btn:
        if resume_files and job_desc_batch:
            with st.spinner(f"⚡ Processing {len(resume_files)} candidates..."):
                try:
                    files = []
                    for f in resume_files:
                        file_bytes = f.read()
                        files.append(('resumes', (f.name, io.BytesIO(file_bytes), 'application/octet-stream')))
                    
                    data = {'job_description': job_desc_batch}
                    
                    url = f"{API_BASE_URL}/batch-screen"
                    response = requests.post(url, files=files, data=data, timeout=120)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get('status') == 'success':
                            st.success(f"✅ Analysis complete: {result['total_processed']} candidates processed")
                            
                            df = pd.DataFrame(result['results'])
                            df = df.sort_values('match_score', ascending=False)
                            
                            # Leaderboard
                            st.markdown("### 🏆 Candidate Leaderboard")
                            st.dataframe(
                                df[['filename', 'match_score', 'verdict', 'skill_match_percentage', 'years_of_experience']],
                                use_container_width=True,
                                height=400
                            )
                            
                            # Visualization
                            st.markdown("### 📊 Score Distribution")
                            chart_data = df.set_index('filename')['match_score']
                            st.bar_chart(chart_data, use_container_width=True)
                            
                            # Download option
                            csv = df.to_csv(index=False)
                            st.download_button(
                                "📥 Download Full Report (CSV)",
                                csv,
                                "neuralscan_results.csv",
                                "text/csv",
                                key='download-csv'
                            )
                    else:
                        st.error(f"Batch processing failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"Batch error: {str(e)}")
        else:
            st.warning("⚠️ Upload resumes and provide job description")

# =============================================================================
# TAB 3: COMPARE RESUMES
# =============================================================================

with tab3:
    st.markdown('<div class="glass-card" style="margin-bottom: 2rem;">', unsafe_allow_html=True)
    st.markdown("### ⚖️ Candidate Comparison")
    st.caption("Upload 2 or more resumes for side-by-side analysis")
    
    compare_files = st.file_uploader(
        "Select candidates to compare",
        type=['pdf', 'docx'],
        accept_multiple_files=True,
        key="compare_resumes",
        label_visibility="collapsed"
    )
    
    if compare_files:
        st.info(f"📊 {len(compare_files)} candidates loaded for comparison")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    compare_btn_col1, compare_btn_col2, compare_btn_col3 = st.columns([1, 2, 1])
    with compare_btn_col2:
        compare_btn = st.button("🔍 GENERATE COMPARISON MATRIX", use_container_width=True)
    
    if compare_btn:
        if compare_files and len(compare_files) >= 2:
            with st.spinner("⚖️ Analyzing candidate profiles..."):
                try:
                    files = []
                    for f in compare_files:
                        file_bytes = f.read()
                        files.append(('resumes', (f.name, io.BytesIO(file_bytes), 'application/octet-stream')))
                    
                    url = f"{API_BASE_URL}/compare-resumes"
                    response = requests.post(url, files=files, timeout=60)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        if result.get('status') == 'success':
                            st.success(f"✅ Comparison matrix generated for {result['total_resumes']} candidates")
                            
                            # Create comparison grid
                            comparison_data = []
                            for idx, resume in enumerate(result['comparison']):
                                is_winner = idx == 0  # Assuming sorted by some metric
                                comparison_data.append({
                                    'Candidate': resume['filename'],
                                    'Experience (Yrs)': f"{resume['experience_years']:.1f}",
                                    'Skill Count': resume['total_skills'],
                                    'Education': '✓ Verified' if resume['has_education'] else '✗ Not found',
                                    'Profile Strength': '⭐⭐⭐' if resume['experience_years'] > 5 else '⭐⭐' if resume['experience_years'] > 2 else '⭐'
                                })
                            
                            comp_df = pd.DataFrame(comparison_data)
                            
                            # Display as cards for visual impact
                            st.markdown("### 📋 Comparative Analysis")
                            st.dataframe(comp_df, use_container_width=True, height=300)
                            
                            # Visual comparison
                            st.markdown("### 📊 Capability Radar")
                            chart_cols = st.columns(len(result['comparison']))
                            for idx, (col, resume) in enumerate(zip(chart_cols, result['comparison'])):
                                with col:
                                    st.markdown(f"**{resume['filename'][:20]}...**")
                                    st.metric("Experience", f"{resume['experience_years']:.1f} yrs")
                                    st.metric("Skills", resume['total_skills'])
                                    if resume['has_education']:
                                        st.markdown("🎓 Education verified")
                                        
                    else:
                        st.error(f"Comparison failed: {response.text}")
                        
                except Exception as e:
                    st.error(f"Comparison error: {str(e)}")
        else:
            st.warning("⚠️ Please upload at least 2 resumes for comparison")

# =============================================================================
# TAB 4: SYSTEM INFO
# =============================================================================

with tab4:
    st.markdown("""
    <div class="glass-card">
        <h2 style="margin-top: 0;">🧬 NeuralScan Architecture</h2>
        <p style="color: #a0a0b0; line-height: 1.6;">
            Advanced AI-powered resume analysis utilizing transformer-based embeddings and 
            semantic similarity algorithms to match candidates with precision.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.markdown("""
        ### 🚀 Core Capabilities
        
        <div style="margin: 1rem 0;">
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="color: var(--neon-cyan); margin-right: 0.5rem;">▹</span>
                <span>Neural embedding extraction (BERT/SBERT)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="color: var(--neon-cyan); margin-right: 0.5rem;">▹</span>
                <span>Semantic similarity matching</span>
            </div>
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="color: var(--neon-cyan); margin-right: 0.5rem;">▹</span>
                <span>Multi-dimensional skill gap analysis</span>
            </div>
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="color: var(--neon-cyan); margin-right: 0.5rem;">▹</span>
                <span>Explainable AI scoring (XAI)</span>
            </div>
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="color: var(--neon-cyan); margin-right: 0.5rem;">▹</span>
                <span>Batch processing pipeline</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with info_col2:
        st.markdown("""
        ### ⚙️ Technical Stack
        
        <div style="margin: 1rem 0;">
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="color: var(--neon-purple); margin-right: 0.5rem;">◈</span>
                <span><strong>FastAPI</strong> — High-performance API layer</span>
            </div>
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="color: var(--neon-purple); margin-right: 0.5rem;">◈</span>
                <span><strong>Sentence-Transformers</strong> — Embedding engine</span>
            </div>
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="color: var(--neon-purple); margin-right: 0.5rem;">◈</span>
                <span><strong>spaCy</strong> — NLP preprocessing</span>
            </div>
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="color: var(--neon-purple); margin-right: 0.5rem;">◈</span>
                <span><strong>scikit-learn</strong> — ML utilities</span>
            </div>
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span style="color: var(--neon-purple); margin-right: 0.5rem;">◈</span>
                <span><strong>Streamlit</strong> — Interactive frontend</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("""
    ### 📊 Scoring Methodology
    
    The match score is computed using a weighted ensemble of four neural indicators:
    
    | Component | Weight | Description |
    |-----------|--------|-------------|
    | **Skill Alignment** | 40% | Direct skill extraction and matching |
    | **Semantic Similarity** | 30% | BERT-based contextual understanding |
    | **Experience Relevance** | 15% | Years and domain alignment |
    | **Education Fit** | 15% | Qualification level matching |
    
    <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px; margin-top: 1rem; border-left: 3px solid var(--neon-cyan);">
        <strong style="color: var(--neon-cyan);">Threshold Guide:</strong><br>
        🟢 80-100% — Exceptional fit | 
        🟡 60-79% — Strong candidate | 
        🟠 40-59% — Moderate match | 
        🔴 0-39% — Not recommended
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# FOOTER
# =============================================================================

st.markdown("---")
st.markdown("""
<div style="
    text-align: center;
    padding: 2rem;
    color: #666;
    font-size: 0.9rem;
    letter-spacing: 0.05em;
">
    <p style="margin: 0.5rem 0;">
        <strong style="color: var(--neon-cyan);">NeuralScan AI</strong>
    </p>
    <p style="margin: 0.5rem 0; font-size: 0.8rem; opacity: 0.6;">
        Made by Surendra
    </p>
</div>
""", unsafe_allow_html=True)