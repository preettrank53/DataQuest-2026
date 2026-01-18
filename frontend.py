import streamlit as st
import requests
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="DataQuest 2026: Live AI Analyst",
    page_icon="📰",
    layout="wide"
)

# Title and header
st.title("📰 DataQuest 2026: Live AI Analyst")
st.markdown("**Real-Time News RAG System** powered by Gemini AI and live NewsAPI streams")
st.markdown("---")

# Backend URL
BACKEND_URL = "http://backend:8000/v1/chat"

# Session state for auto-refresh
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'last_response' not in st.session_state:
    st.session_state.last_response = None
if 'query_count' not in st.session_state:
    st.session_state.query_count = 0

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    auto_refresh = st.checkbox("🔄 Auto-Refresh (5s)", value=False)
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This system:
    - 📡 Streams live news from NewsAPI
    - 🤖 Uses Gemini 1.5 Flash AI
    - 🔍 Retrieves top-5 relevant articles
    - ✅ Provides source attribution
    - 📅 Includes publication dates
    """)
    st.markdown("---")
    st.markdown(f"**Queries made**: {st.session_state.query_count}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("💬 Ask a Question")
    
    # Question input
    question = st.text_input(
        "Enter your question:",
        placeholder="e.g., What is the latest technology news?",
        key="question_input"
    )
    
    # Sample questions
    st.markdown("**Quick Examples:**")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("📱 Tech News"):
            question = "What is the latest technology news?"
            st.session_state.last_query = question
    
    with col_b:
        if st.button("💼 Business News"):
            question = "Tell me about recent business developments"
            st.session_state.last_query = question
    
    with col_c:
        if st.button("🤖 AI Updates"):
            question = "What news is there about AI and machine learning?"
            st.session_state.last_query = question
    
    # Ask button
    ask_button = st.button("🚀 Ask", type="primary", use_container_width=True)
    
    # Process query
    if ask_button or (auto_refresh and st.session_state.last_query):
        if question or st.session_state.last_query:
            query_text = question if question else st.session_state.last_query
            st.session_state.last_query = query_text
            
            with st.spinner("🔍 Searching latest news and generating answer..."):
                try:
                    # Make request to backend
                    response = requests.post(
                        BACKEND_URL,
                        json={"prompt": query_text},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.session_state.last_response = result
                        st.session_state.query_count += 1
                        
                        # Display answer
                        st.success("✅ Answer generated!")
                        st.markdown("### 📝 Answer")
                        st.markdown(result.get("answer", "No answer provided"))
                        
                        # Display metadata if available
                        if "metadata" in result:
                            with st.expander("ℹ️ Query Metadata"):
                                st.json(result["metadata"])
                        
                        # Display sources/references
                        if "references" in result and result["references"]:
                            st.markdown("### 📚 Sources")
                            for idx, ref in enumerate(result["references"], 1):
                                with st.container():
                                    st.markdown(f"**{idx}. {ref.get('source', 'Unknown Source')}**")
                                    if 'date' in ref:
                                        st.caption(f"📅 {ref['date']}")
                                    if 'url' in ref:
                                        st.markdown(f"🔗 [{ref['url']}]({ref['url']})")
                                    st.markdown("---")
                        
                        # Timestamp
                        st.caption(f"🕐 Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        
                    else:
                        st.error(f"❌ Backend error: {response.status_code}")
                        st.code(response.text)
                
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to backend. Make sure the backend service is running.")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out. The backend might be processing a large query.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a question first!")

with col2:
    st.header("📊 System Status")
    
    # Check backend status
    try:
        health_response = requests.get("http://backend:8000/health", timeout=2)
        if health_response.status_code == 200:
            st.success("✅ Backend: Online")
        else:
            st.warning("⚠️ Backend: Degraded")
    except:
        st.error("❌ Backend: Offline")
    
    st.markdown("---")
    
    # Display last response info
    if st.session_state.last_response:
        st.markdown("### 📈 Last Query Stats")
        st.metric("Query Count", st.session_state.query_count)
        if "metadata" in st.session_state.last_response:
            meta = st.session_state.last_response["metadata"]
            if "retrieved_docs" in meta:
                st.metric("Docs Retrieved", meta["retrieved_docs"])

# Auto-refresh logic
if auto_refresh and st.session_state.last_query:
    time.sleep(5)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>🏆 <strong>DataQuest 2026 Hackathon</strong> | Built with Pathway + Gemini AI + NewsAPI</p>
    <p>Repository: <a href='https://github.com/preetiank53/DataQuest-2026'>GitHub</a></p>
</div>
""", unsafe_allow_html=True)
