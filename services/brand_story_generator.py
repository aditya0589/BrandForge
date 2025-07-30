import streamlit as st
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
import io

def show_brand_story_generator():
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
        .refine-button>button {
            background-color: #2ecc71;
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
        .story-display {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            background-color: #ffffff;
            margin-top: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Main header
    st.markdown('<div class="main-header">Brand Story Generator</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sub-header">
        Create an immersive brand story by describing your brand, target audience, and core values. Refine the story with feedback to make it more engaging.  
        **Tips for better stories**:  
        - Be specific (e.g., "A story for MaddyTrends, women’s fashion for ages 20-50, focusing on empowerment and sustainability").  
        - Include tone or themes (e.g., inspirational, adventurous, heartfelt).  
        - Avoid vague prompts or copyrighted content.  
        **Examples**:  
        - A story for EcoBites, a sustainable snack brand, targeting health-conscious millennials, emphasizing eco-friendly values.  
        - A narrative for TechTrend Innovations, a tech startup, for young professionals, focusing on innovation and community.
        </div>
        """,
        unsafe_allow_html=True
    )

    # Check for Google API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("Google API key is missing. Please set the 'GOOGLE_API_KEY' environment variable or obtain one from https://ai.google.dev/gemini-api/docs/api-key.")
        st.markdown("To get an API key, visit [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key) and generate one.")
        return

    # Initialize LangChain LLM
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.7,
            max_tokens=1000
        )
    except Exception as e:
        st.error(f"Failed to initialize Google Generative AI: {str(e)}")
        return

    # Initialize session state for story and history
    if "brand_story" not in st.session_state:
        st.session_state.brand_story = ""
        st.session_state.story_history = []

    # Create two columns: left for inputs and story, right for controls
    col1, col2 = st.columns([3, 1])

    # Right column: Controls
    with col2:
        with st.container():
            st.markdown('<div class="sub-header">Story Options</div>', unsafe_allow_html=True)
            story_length = st.selectbox(
                "Story Length",
                options=["Short (~300 words)", "Medium (~500 words)", "Long (~800 words)"],
                index=1,
                key="story_length"
            )
            # Map to approximate token counts
            length_to_tokens = {
                "Short (~300 words)": 400,
                "Medium (~500 words)": 700,
                "Long (~800 words)": 1000
            }
            max_tokens = length_to_tokens[story_length]
            st.markdown('<div class="sub-header">Additional Options</div>', unsafe_allow_html=True)
            st.write("More settings coming soon (e.g., tone, themes).")

    # Left column: Form and story display
    with col1:
        with st.form("brand_story_form"):
            prompt = st.text_input(
                "Brand Story Prompt",
                placeholder="e.g., A story for MaddyTrends, women’s fashion for ages 20-50, focusing on empowerment and sustainability",
                key="story_prompt"
            )
            feedback = st.text_area(
                "Feedback for Refinement (optional)",
                placeholder="e.g., Make it more emotional, emphasize sustainability",
                key="story_feedback"
            )
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                st.markdown('<div class="generate-button">', unsafe_allow_html=True)
                generate_button = st.form_submit_button("Generate Story")
                st.markdown('</div>', unsafe_allow_html=True)
            with btn_col2:
                st.markdown('<div class="refine-button">', unsafe_allow_html=True)
                refine_button = st.form_submit_button("Refine Story")
                st.markdown('</div>', unsafe_allow_html=True)

            if generate_button or refine_button:
                if not prompt:
                    st.error("Please enter a brand story prompt.")
                else:
                    # Define prompts
                    system_prompt = (
                        "You are a creative storytelling assistant specializing in brand narratives. "
                        "Generate an immersive, engaging brand story based on the user's prompt, incorporating the brand's values, target audience, and desired tone. "
                        "The story should be compelling, emotionally resonant, and aligned with the brand's identity. "
                        "Structure the story with a clear beginning, middle, and end, and aim for approximately {word_count} words."
                    )
                    reflection_prompt = (
                        "You are a critical editor reviewing a brand story. "
                        "Analyze the provided story for strengths, weaknesses, and alignment with the brand’s values and audience. "
                        "Provide constructive feedback, identifying specific areas for improvement (e.g., emotional impact, clarity, brand consistency). "
                        "If user feedback is provided, prioritize it in your critique. "
                        "Then, suggest a revised version of the story incorporating the feedback."
                    )

                    # Create LangChain prompt templates
                    generate_prompt = ChatPromptTemplate.from_messages([
                        ("system", system_prompt),
                        MessagesPlaceholder(variable_name="messages")
                    ])
                    reflection_prompt_template = ChatPromptTemplate.from_messages([
                        ("system", reflection_prompt),
                        MessagesPlaceholder(variable_name="messages")
                    ])

                    # Prepare messages
                    if generate_button:
                        messages = [HumanMessage(content=prompt)]
                        chain = generate_prompt | llm
                        try:
                            response = chain.invoke({
                                "messages": messages,
                                "word_count": max_tokens // 3  # Approximate word count
                            })
                            st.session_state.brand_story = response.content
                            st.session_state.story_history.append(("Generated", response.content))
                        except Exception as e:
                            st.error(f"Error generating story: {str(e)}")
                            return
                    elif refine_button:
                        if not st.session_state.brand_story:
                            st.error("No story to refine. Please generate a story first.")
                            return
                        feedback_text = feedback if feedback else "No user feedback provided."
                        messages = [
                            HumanMessage(content=f"Original story: {st.session_state.brand_story}\nUser feedback: {feedback_text}")
                        ]
                        chain = reflection_prompt_template | llm
                        try:
                            response = chain.invoke({"messages": messages})
                            st.session_state.brand_story = response.content
                            st.session_state.story_history.append(("Refined", response.content))
                        except Exception as e:
                            st.error(f"Error refining story: {str(e)}")
                            return

                    # Display story
                    if st.session_state.brand_story:
                        st.markdown('<div class="story-display">', unsafe_allow_html=True)
                        st.markdown(f"**Brand Story**:\n{st.session_state.brand_story}")
                        st.markdown('</div>', unsafe_allow_html=True)

                        # Download button in right column
                        with col2:
                            st.markdown('<div class="sub-header">Download Story</div>', unsafe_allow_html=True)
                            story_buffer = io.StringIO(st.session_state.brand_story)
                            st.markdown('<div class="download-button">', unsafe_allow_html=True)
                            st.download_button(
                                label="Download Story as TXT",
                                data=story_buffer.getvalue(),
                                file_name="brand_story.txt",
                                mime="text/plain",
                                key="download_story_button"
                            )
                            st.markdown('</div>', unsafe_allow_html=True)

                    # Debug: Show history
                    with st.expander("Debug: View Story History"):
                        for i, (action, story) in enumerate(st.session_state.story_history):
                            st.write(f"{action} Story {i+1}:")
                            st.write(story)