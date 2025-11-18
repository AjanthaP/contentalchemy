import streamlit as st
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.workflow.langgraph_flow import generate_content
from src.memory.conversation_manager import ConversationManager, UserProfileManager
from src.optimization.seo_optimizer import SEOOptimizer
from src.optimization.content_validator import ContentValidator
from langchain_openai import ChatOpenAI
from src.core.config import settings

# Page config
st.set_page_config(
    page_title="ContentAlchemy - AI Content Marketing",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'conversation_manager' not in st.session_state:
    st.session_state.conversation_manager = ConversationManager()
    st.session_state.profile_manager = UserProfileManager()
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">✨ ContentAlchemy</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Powered Content Marketing Assistant</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Content type selector
    content_type_display = st.selectbox(
        "What do you want to create?",
        [
            "🔍 Research Report",
            "📝 SEO Blog Post",
            "💼 LinkedIn Post",
            "🎨 AI-Generated Image",
            "📊 Content Strategy"
        ]
    )
    
    # Map display names to intents
    content_type_map = {
        "🔍 Research Report": "research",
        "📝 SEO Blog Post": "blog",
        "💼 LinkedIn Post": "linkedin",
        "🎨 AI-Generated Image": "image",
        "📊 Content Strategy": "strategy"
    }
    
    button_label_map = {
        "🔍 Research Report": "✨ Generate Research Report",
        "📝 SEO Blog Post": "✨ Generate Blog Post",
        "💼 LinkedIn Post": "✨ Generate LinkedIn Post",
        "🎨 AI-Generated Image": "✨ Generate Image",
        "📊 Content Strategy": "✨ Generate Strategy"
    }

    st.divider()
    
    # Advanced settings
    with st.expander("🎯 Advanced Settings"):
        user_tone = st.select_slider(
            "Content Tone",
            options=["Casual", "Conversational", "Professional", "Formal", "Technical"],
            value="Professional"
        )
        
        enable_seo = st.checkbox("Enable SEO Optimization", value=True)
        include_sources = st.checkbox("Include Source Citations", value=True)
        
        if content_type_display == "📝 SEO Blog Post":
            target_words = st.slider(
                "Target Word Count",
                min_value=800,
                max_value=2500,
                value=1500,
                step=100
            )
        
        if content_type_display == "🎨 AI-Generated Image":
            image_size = st.select_slider(
                "Image Size",
                options=["1024x1024", "1024x1792", "1792x1024"],
                value="1024x1024"
            )
            image_quality = st.radio("Image Quality", ["standard", "hd"], index=0)
    
    st.divider()
    
    # Profile management
    st.subheader("👤 Profile")
    user_id = st.text_input("User ID", value="default")
    
    if st.button("💾 Save Current Settings"):
        profile_updates = {
            "preferences": {
                "tone": user_tone.lower(),
                "seo_optimization": enable_seo,
                "include_sources": include_sources
            }
        }
        st.session_state.profile_manager.update_profile(user_id, profile_updates)
        st.success("Settings saved!")

# Main content area
col1, col2 = st.columns([3, 2])

with col1:
    st.header("📝 Content Request")
    
    # Main input
    user_query = st.text_area(
        "Describe what you want to create:",
        placeholder="""Examples:

• Research the latest trends in AI marketing for 2024
• Write an SEO blog post about sustainable fashion
• Create a LinkedIn post about my company's new product launch
• Generate an image of a futuristic workspace with AI elements
• Develop a content strategy for promoting a SaaS product""",
        height=150,
        key="main_query"
    )
    
    # Additional context
    with st.expander("➕ Additional Context (Optional)"):
        target_audience = st.text_input(
            "Target Audience",
            placeholder="e.g., Marketing professionals, Tech startups, B2B companies"
        )
        
        keywords = st.text_input(
            "Target Keywords (comma-separated)",
            placeholder="e.g., AI marketing, automation, ROI"
        )
        
        additional_notes = st.text_area(
            "Additional Requirements",
            placeholder="Any specific requirements, constraints, or preferences...",
            height=80
        )
    
    # Generate button
    generate_clicked = st.button(
        button_label_map.get(content_type_display, "✨ Generate Content"),
        type="primary",
        use_container_width=True
    )

with col2:
    st.header("💡 Tips & Examples")
    
    tips_tab, examples_tab = st.tabs(["Tips", "Examples"])
    
    with tips_tab:
        st.markdown("""
        **For Best Results:**
        
        📌 **Be Specific**
        - Include your topic, target audience, and purpose
        - Mention any key points you want covered
        
        🎯 **Set Context**
        - Describe your industry or niche
        - Specify content goals (educate, promote, inspire)
        
        🔍 **Research-Based Content**
        - Let the AI research first for factual accuracy
        - Review sources and adjust as needed
        
        ✏️ **Iterate & Refine**
        - Edit the generated content
        - The system learns from your edits
        """)
    
    with examples_tab:
        st.markdown("""
        **Research Report:**
        "Research emerging AI tools for content marketing in 2024"
        
        **Blog Post:**
        "Write an SEO blog about email marketing automation for small businesses"
        
        **LinkedIn Post:**
        "Create a LinkedIn post announcing our company's sustainability initiative"
        
        **Image:**
        "Generate a professional header image for a tech blog about cloud computing"
        """)

# Content Generation
if generate_clicked:
    if not user_query.strip():
        st.error("⚠️ Please enter a content request")
    else:
        with st.spinner("🤖 Creating your content..."):
            try:
                # Enhance query with additional context
                enhanced_query = user_query
                if target_audience:
                    enhanced_query += f"\n\nTarget Audience: {target_audience}"
                if keywords:
                    enhanced_query += f"\n\nKeywords: {keywords}"
                if additional_notes:
                    enhanced_query += f"\n\nAdditional Notes: {additional_notes}"
                
                # Add to conversation
                st.session_state.conversation_manager.add_message(
                    "user",
                    enhanced_query,
                    {"content_type": content_type_map[content_type_display]}
                )
                
                # Generate content
                result = generate_content(
                    user_query=enhanced_query,
                    image_size=image_size if content_type_display == "🎨 AI-Generated Image" else "1024x1024",
                    image_quality=image_quality if content_type_display == "🎨 AI-Generated Image" else "standard"
                )
                
                # Store result
                st.session_state.last_result = result
                st.session_state.last_query = user_query
                
                # Add to conversation
                st.session_state.conversation_manager.add_message(
                    "assistant",
                    result.get("final_content", ""),
                    {"result": result}
                )
                
                st.success("✅ Content generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.info("💡 Tip: Check your API keys in the .env file")

# Display Results
if 'last_result' in st.session_state:
    st.divider()
    st.header("📄 Generated Content")
    
    result = st.session_state.last_result
    content_type = result.get("content_type", "unknown")
    
    # Metadata display
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Content Type", content_type.replace("_", " ").title())
    with col2:
        if content_type in ["blog", "research_report"]:
            word_count = result.get("word_count", len(result.get("final_content", "").split()))
            st.metric("Word Count", f"{word_count:,}")
        elif content_type == "linkedin":
            char_count = result.get("char_count", len(result.get("final_content", "")))
            st.metric("Characters", f"{char_count:,}")
    with col3:
        st.metric("Status", "✅ Complete")
    with col4:
        timestamp = datetime.now().strftime("%H:%M:%S")
        st.metric("Generated", timestamp)
    
    # Content tabs
    content_tab, analysis_tab, sources_tab = st.tabs(["📝 Content", "📊 Analysis", "🔗 Sources"])
    
    with content_tab:
        if content_type == "image":
            # Display image
            image_url = result.get("image_url", "")
            if image_url:
                st.image(image_url, caption="Generated Image", width="stretch")
                st.text_area(
                    "Image Prompt Used:",
                    value=result.get("image_prompt", ""),
                    height=100,
                    key="image_prompt_display"
                )
        else:
            # Editable text content
            edited_content = st.text_area(
                "Edit your content:",
                value=result.get("final_content", ""),
                height=500,
                key="content_editor"
            )
            
            # Track edits
            if edited_content != result.get("final_content", ""):
                st.info("💡 Content modified - changes will be saved for learning")
    
    with analysis_tab:
        if content_type in ["blog", "research_report"]:
            # Validate content
            validator = ContentValidator()
            validation = validator.validate_content(
                result.get("final_content", ""),
                content_type
            )
            
            st.subheader("Quality Score")
            st.progress(validation.score / 100)
            st.metric("Overall Score", f"{validation.score}/100")
            
            if validation.issues:
                st.error("**Issues Found:**")
                for issue in validation.issues:
                    st.write(f"• {issue}")
            
            if validation.warnings:
                st.warning("**Warnings:**")
                for warning in validation.warnings:
                    st.write(f"• {warning}")
            
            if validation.suggestions:
                st.info("**Suggestions:**")
                for suggestion in validation.suggestions:
                    st.write(f"• {suggestion}")
            
            # SEO Analysis
            if enable_seo and content_type == "blog":
                st.subheader("SEO Analysis")
                llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)
                seo_optimizer = SEOOptimizer(llm)
                
                keywords_list = keywords.split(",") if keywords else ["content", "marketing"]
                seo_analysis = seo_optimizer.analyze_content(
                    result.get("final_content", ""),
                    [k.strip() for k in keywords_list]
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("SEO Score", f"{seo_analysis.get('seo_score', 0)}/100")
                with col2:
                    st.metric("Structure Score", f"{seo_analysis.get('structure_score', 0)}/100")
                
                if seo_analysis.get("improvements"):
                    st.write("**SEO Improvements:**")
                    for imp in seo_analysis["improvements"]:
                        st.write(f"• {imp}")
        else:
            st.info("Analysis available for blog posts and research reports")
    
    with sources_tab:
        research_report = result.get("research_report", {})
        sources = research_report.get("sources", [])
        
        if sources:
            st.subheader(f"📚 {len(sources)} Sources Found")
            for i, source in enumerate(sources, 1):
                with st.expander(f"{i}. {source.get('title', 'Source')}"):
                    st.write(f"**URL:** {source.get('url', 'N/A')}")
                    st.write(f"**Snippet:** {source.get('snippet', 'No description')}")
        else:
            st.info("No sources available for this content type")
    
    # Action buttons
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Download as Markdown
        st.download_button(
            "📥 Download MD",
            data=result.get("final_content", ""),
            file_name=f"content_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            width="stretch"
        )
    
    with col2:
        # Download as TXT
        st.download_button(
            "📄 Download TXT",
            data=result.get("final_content", ""),
            file_name=f"content_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            width="stretch"
        )
    
    with col3:
        if st.button("🔄 Generate New", width="stretch"):
            del st.session_state.last_result
            st.rerun()
    
    with col4:
        if st.button("💾 Save & Learn", width="stretch"):
            # Learn from edits if content was modified
            if 'content_editor' in st.session_state:
                original = result.get("final_content", "")
                edited = st.session_state.content_editor
                if edited != original:
                    st.session_state.profile_manager.learn_from_edits(
                        user_id,
                        original,
                        edited
                    )
            
            # Save conversation
            st.session_state.conversation_manager.save_session(st.session_state.session_id)
            st.success("✅ Saved and learned from your edits!")

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.caption("Built with ❤️ using LangChain & LangGraph")
with col2:
    st.caption(f"Session: {st.session_state.session_id}")
with col3:
    st.caption("v1.0.0")
