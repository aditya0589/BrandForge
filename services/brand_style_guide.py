import streamlit as st
import os
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage
from PIL import Image
import base64

def show_brand_style_guide():
    # Custom CSS for professional styling (consistent with other services)
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        .sub-header {
            font-size: 18px;
            color: #34495e;
            margin-bottom: 20px;
        }
        .right-container {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            background-color: #f8f9fa;
        }
        .stButton>button {
            border-radius: 5px;
            padding: 8px 16px;
            font-weight: bold;
        }
        .generate-button>button {
            background-color: #3498db;
            color: white;
        }
        .download-button>button {
            background-color: #7f8c8d;
            color: white;
            width: 100%;
            margin-top: 10px;
        }
        .stTextInput>div>input, .stTextArea textarea {
            border-radius: 5px;
            border: 1px solid #bdc3c7;
            padding: 10px;
        }
        .stSelectbox {
            border-radius: 5px;
        }
        .style-guide-display {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            background-color: #ffffff;
            margin-top: 20px;
        }
        .color-palette {
            display: flex;
            gap: 10px;
            margin: 10px 0;
        }
        .color-swatch {
            width: 50px;
            height: 50px;
            border-radius: 5px;
            border: 2px solid #ddd;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Main header
    st.markdown('<div class="main-header">Brand Style Guide Generator</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sub-header">
        Create a comprehensive brand style guide PDF with colors, typography, logo usage, and brand guidelines. Generate professional documentation that ensures brand consistency across all platforms.  
        **Tips for better style guides**:  
        - Be specific about your brand identity (e.g., "Modern tech startup with blue and white colors, clean typography").  
        - Include brand values and target audience.  
        - Mention specific use cases or industry requirements.  
        **Examples**:  
        - A style guide for EcoBites, sustainable food brand, green and earth tones, organic aesthetic  
        - A guide for TechTrend Innovations, tech startup, blue and silver, modern and professional  
        - A guide for MaddyTrends, women's fashion, bold pinks and purples, empowering and modern
        </div>
        """,
        unsafe_allow_html=True
    )

    # Check for Google API key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        st.error("Google API key is missing. Please set the 'GOOGLE_API_KEY' environment variable or obtain one from https://ai.google.dev/gemini-api/docs/api-key.")
        st.markdown("To get an API key, visit [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key).")
        return

    # Initialize LangChain LLM
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=google_api_key,
            temperature=0.7,
            max_tokens=2000
        )
    except Exception as e:
        st.error(f"Failed to initialize Google Generative AI: {str(e)}")
        return

    # Initialize session state for style guide
    if "brand_style_guide" not in st.session_state:
        st.session_state.brand_style_guide = ""
        st.session_state.style_guide_sections = {}

    # Create two columns: left for inputs and preview, right for controls
    col1, col2 = st.columns([3, 1])

    # Right column: Controls
    with col2:
        with st.container():
            st.markdown('<div class="sub-header">Style Guide Options</div>', unsafe_allow_html=True)
            page_size = st.selectbox(
                "Page Size",
                options=["Letter (8.5x11)", "A4 (210x297mm)"],
                index=0,
                key="page_size"
            )
            include_sections = st.multiselect(
                "Include Sections",
                options=["Brand Overview", "Color Palette", "Typography", "Logo Usage", "Imagery Guidelines", "Voice & Tone", "Applications"],
                default=["Brand Overview", "Color Palette", "Typography", "Logo Usage"],
                key="include_sections"
            )
            st.markdown('<div class="sub-header">Additional Options</div>', unsafe_allow_html=True)
            st.write("More settings coming soon (e.g., custom templates).")

    # Left column: Form and style guide display
    with col1:
        with st.form("brand_style_guide_form"):
            brand_name = st.text_input(
                "Brand Name",
                placeholder="e.g., MaddyTrends, EcoBites, TechTrend",
                key="brand_name"
            )
            brand_description = st.text_area(
                "Brand Description",
                placeholder="Describe your brand's identity, values, target audience, and visual style...",
                key="brand_description"
            )
            primary_colors = st.text_input(
                "Primary Colors (comma-separated)",
                placeholder="e.g., #FF6B6B, #4ECDC4, #45B7D1",
                key="primary_colors"
            )
            secondary_colors = st.text_input(
                "Secondary Colors (comma-separated)",
                placeholder="e.g., #96CEB4, #FFEAA7, #DDA0DD",
                key="secondary_colors"
            )
            fonts = st.text_input(
                "Fonts (comma-separated)",
                placeholder="e.g., Montserrat, Open Sans, Roboto",
                key="fonts"
            )
            st.markdown('<div class="generate-button">', unsafe_allow_html=True)
            generate_button = st.form_submit_button("Generate Style Guide")
            st.markdown('</div>', unsafe_allow_html=True)

            if generate_button:
                if not brand_name or not brand_description:
                    st.error("Please enter a brand name and description.")
                else:
                    # Prepare the prompt for style guide generation
                    style_guide_prompt = f"""
                    Create a comprehensive brand style guide for {brand_name}.
                    
                    Brand Description: {brand_description}
                    
                    Primary Colors: {primary_colors if primary_colors else 'Not specified'}
                    Secondary Colors: {secondary_colors if secondary_colors else 'Not specified'}
                    Fonts: {fonts if fonts else 'Not specified'}
                    
                    Please generate the following sections in a structured format:
                    
                    1. BRAND OVERVIEW
                    - Brand mission and vision
                    - Target audience
                    - Brand personality and values
                    
                    2. COLOR PALETTE
                    - Primary colors with hex codes and usage guidelines
                    - Secondary colors with hex codes and usage guidelines
                    - Color combinations and accessibility considerations
                    
                    3. TYPOGRAPHY
                    - Primary font family and usage
                    - Secondary font family and usage
                    - Font hierarchy and sizing guidelines
                    
                    4. LOGO USAGE
                    - Logo variations and clear space requirements
                    - Minimum size requirements
                    - Logo placement guidelines
                    - What not to do with the logo
                    
                    5. IMAGERY GUIDELINES
                    - Photography style and aesthetic
                    - Icon style and usage
                    - Graphic elements and patterns
                    
                    6. VOICE & TONE
                    - Brand voice characteristics
                    - Tone variations for different contexts
                    - Writing style guidelines
                    
                    7. APPLICATIONS
                    - Digital applications (website, social media)
                    - Print applications (business cards, brochures)
                    - Environmental applications (signage, packaging)
                    
                    Format the response with clear section headers and detailed guidelines for each section.
                    """

                    # Generate style guide content
                    try:
                        response = llm.invoke([HumanMessage(content=style_guide_prompt)])
                        st.session_state.brand_style_guide = response.content
                        
                        # Parse sections for PDF generation
                        sections = parse_style_guide_sections(response.content)
                        st.session_state.style_guide_sections = sections
                        
                        # Display preview
                        st.markdown('<div class="style-guide-display">', unsafe_allow_html=True)
                        st.markdown(f"**Style Guide Preview**:\n{st.session_state.brand_style_guide}")
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Generate and display download button
                        with col2:
                            st.markdown('<div class="sub-header">Download Style Guide</div>', unsafe_allow_html=True)
                            
                            # Generate PDF
                            pdf_buffer = generate_style_guide_pdf(
                                brand_name, 
                                st.session_state.style_guide_sections, 
                                page_size,
                                include_sections
                            )
                            
                            st.markdown('<div class="download-button">', unsafe_allow_html=True)
                            st.download_button(
                                label="Download Style Guide as PDF",
                                data=pdf_buffer.getvalue(),
                                file_name=f"{brand_name.replace(' ', '_')}_style_guide.pdf",
                                mime="application/pdf",
                                key="download_style_guide_button"
                            )
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Download text version
                            text_buffer = io.StringIO(str(st.session_state.brand_style_guide))
                            st.markdown('<div class="download-button">', unsafe_allow_html=True)
                            st.download_button(
                                label="Download as TXT",
                                data=text_buffer.getvalue(),
                                file_name=f"{brand_name.replace(' ', '_')}_style_guide.txt",
                                mime="text/plain",
                                key="download_text_button"
                            )
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                    except Exception as e:
                        st.error(f"Error generating style guide: {str(e)}")
                        return

def parse_style_guide_sections(content):
    """Parse the generated content into sections for PDF generation"""
    sections = {}
    current_section = None
    current_content = []
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this is a section header
        if line.isupper() or (line.startswith('#') and '#' in line) or any(keyword in line.upper() for keyword in ['BRAND OVERVIEW', 'COLOR PALETTE', 'TYPOGRAPHY', 'LOGO USAGE', 'IMAGERY GUIDELINES', 'VOICE & TONE', 'APPLICATIONS']):
            if current_section:
                sections[current_section] = '\n'.join(current_content)
            current_section = line.replace('#', '').strip()
            current_content = []
        else:
            if current_section:
                current_content.append(line)
    
    # Add the last section
    if current_section and current_content:
        sections[current_section] = '\n'.join(current_content)
    
    return sections

def generate_style_guide_pdf(brand_name, sections, page_size, include_sections):
    """Generate a PDF style guide"""
    buffer = io.BytesIO()
    
    # Set page size
    if page_size == "A4 (210x297mm)":
        doc = SimpleDocTemplate(buffer, pagesize=A4)
    else:
        doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#2c3e50')
    )
    
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.HexColor('#34495e')
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        leading=14
    )
    
    # Build the story
    story = []
    
    # Title page
    story.append(Paragraph(f"{brand_name.upper()}", title_style))
    story.append(Paragraph("BRAND STYLE GUIDE", title_style))
    story.append(Spacer(1, 50))
    story.append(Paragraph(f"Generated on {st.session_state.get('generation_date', 'Current Date')}", body_style))
    story.append(PageBreak())
    
    # Table of contents (simplified)
    story.append(Paragraph("TABLE OF CONTENTS", section_style))
    story.append(Spacer(1, 20))
    
    for section in include_sections:
        if section in sections:
            story.append(Paragraph(f"• {section}", body_style))
    
    story.append(PageBreak())
    
    # Add sections
    for section in include_sections:
        if section in sections:
            story.append(Paragraph(section.upper(), section_style))
            story.append(Paragraph(sections[section], body_style))
            story.append(Spacer(1, 20))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer 