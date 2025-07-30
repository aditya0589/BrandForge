import streamlit as st
import requests
import io
from PIL import Image
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage

def show_brand_kit_generator():
    # Custom CSS for professional styling
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
        .stTextInput>div>input {
            border-radius: 5px;
            border: 1px solid #bdc3c7;
            padding: 10px;
        }
        .stSelectbox {
            border-radius: 5px;
        }
        .stImage {
            border-radius: 8px;
            margin-top: 20px;
        }
        .caption-display {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 15px;
            background-color: #ffffff;
            margin-top: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Main header
    st.markdown('<div class="main-header">Brand Kit Generator</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sub-header">
        Create cohesive Instagram posts, stories, banners, or profile icons for your brand. For Instagram posts, a matching caption will be generated. Enter a detailed prompt describing your brand's aesthetics, colors, and themes.  
        **Tips for better assets**:  
        - Be specific (e.g., "A vibrant Instagram post for MaddyTrends, women’s fashion, bold pinks, modern and empowering").  
        - Include style preferences (e.g., minimalist, bold, vintage).  
        - Avoid vague prompts or copyrighted content.  
        **Examples**:  
        - A sleek Instagram story for TechTrend, tech startup, blue and silver, futuristic design  
        - A bold banner for EcoBites, sustainable snacks, green and earthy tones, organic aesthetic  
        - A minimalist profile icon for a coffee shop, brown and beige, with a coffee bean symbol
        </div>
        """,
        unsafe_allow_html=True
    )

    # Check for API keys
    bria_api_key = os.getenv("BRIA_API_TOKEN")
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not bria_api_key:
        st.error("Bria AI API key is missing. Please set the 'BRIA_API_TOKEN' environment variable or contact support@bria.ai to obtain one.")
        st.markdown("To get an API key, visit [Bria AI](https://www.bria.ai/).")
        return
    if not google_api_key:
        st.error("Google API key is missing. Please set the 'GOOGLE_API_KEY' environment variable or obtain one from https://ai.google.dev/gemini-api/docs/api-key.")
        st.markdown("To get an API key, visit [Google AI Studio](https://ai.google.dev/gemini-api/docs/api-key).")
        return

    # Initialize LangChain LLM for captions
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=google_api_key,
            temperature=0.7,
            max_tokens=200
        )
    except Exception as e:
        st.error(f"Failed to initialize Google Generative AI: {str(e)}")
        return

    # Initialize session state for captions
    if "brand_kit_captions" not in st.session_state:
        st.session_state.brand_kit_captions = []

    # Create two columns: left for inputs and images, right for controls
    col1, col2 = st.columns([3, 1])

    # Right column: Controls
    with col2:
        with st.container():
            st.markdown('<div class="sub-header">Asset Options</div>', unsafe_allow_html=True)
            num_results = st.selectbox(
                "Number of Assets to Generate",
                options=[1, 2],
                index=0,
                key="num_results_kit"
            )
            st.markdown('<div class="sub-header">Additional Options</div>', unsafe_allow_html=True)
            st.write("More settings coming soon (e.g., styles, themes).")

    # Left column: Form and image/caption display
    with col1:
        with st.form("brand_kit_form"):
            prompt = st.text_input(
                "Brand Asset Prompt",
                placeholder="e.g., A vibrant Instagram post for MaddyTrends, women’s fashion, bold pinks, modern and empowering",
                key="kit_prompt"
            )
            asset_type = st.selectbox(
                "Asset Type",
                options=["Instagram Post (1080x1080)", "Instagram Story (1080x1920)", "Banner (1200x628)", "Profile Icon (512x512)"],
                key="asset_type"
            )
            st.markdown('<div class="generate-button">', unsafe_allow_html=True)
            generate_button = st.form_submit_button("Generate Asset")
            st.markdown('</div>', unsafe_allow_html=True)

            if generate_button:
                if not prompt:
                    st.error("Please enter a brand asset prompt.")
                else:
                    # Set resolution based on asset type
                    asset_configs = {
                        "Instagram Post (1080x1080)": {"width": 1080, "height": 1080, "name": "post"},
                        "Instagram Story (1080x1920)": {"width": 1080, "height": 1920, "name": "story"},
                        "Banner (1200x628)": {"width": 1200, "height": 628, "name": "banner"},
                        "Profile Icon (512x512)": {"width": 512, "height": 512, "name": "icon"}
                    }
                    config = asset_configs[asset_type]

                    # Bria AI API request for image
                    model_version = "2.3"
                    url = f"https://engine.prod.bria-api.com/v1/text-to-image/base/{model_version}"
                    payload = {
                        "prompt": f"Professional {config['name']} for social media: {prompt}",
                        "num_results": num_results,
                        "sync": True,
                        "height": config["height"],
                        "width": config["width"]
                    }
                    headers = {
                        "Content-Type": "application/json",
                        "api_token": bria_api_key
                    }

                    try:
                        response = requests.post(url, json=payload, headers=headers)
                        response.raise_for_status()
                        data = response.json()

                        # Debug: Show raw API response
                        with st.expander("Debug: View Raw API Response"):
                            st.json(data)

                        if "result" in data and data["result"]:
                            # Store images and captions
                            images = []
                            st.session_state.brand_kit_captions = []
                            
                            # Generate caption for Instagram Post
                            if asset_type == "Instagram Post (1080x1080)":
                                caption_prompt = ChatPromptTemplate.from_messages([
                                    ("system", (
                                        "You are a social media content creator specializing in Instagram captions. "
                                        "Generate a concise, engaging caption (50-150 words) for an Instagram post based on the provided prompt. "
                                        "Ensure the caption aligns with the brand’s identity, is emotionally resonant, and includes a call-to-action. "
                                        "Use hashtags relevant to the brand and theme."
                                    )),
                                    ("human", prompt)
                                ])
                                chain = caption_prompt | llm
                                try:
                                    caption_response = chain.invoke({"prompt": prompt})
                                    st.session_state.brand_kit_captions = [caption_response.content] * num_results
                                except Exception as e:
                                    st.error(f"Error generating caption: {str(e)}")
                                    st.session_state.brand_kit_captions = [""] * num_results

                            # Process images
                            for i, result in enumerate(data["result"]):
                                if "urls" in result and result["urls"]:
                                    # Fetch image from URL
                                    image_url = result["urls"][0]
                                    image_response = requests.get(image_url)
                                    image_response.raise_for_status()
                                    image = Image.open(io.BytesIO(image_response.content))
                                    images.append(image)
                                    
                                    # Display image and caption (if applicable)
                                    st.image(image, caption=f"Generated {config['name'].capitalize()} {i+1} ({config['width']}x{config['height']})", use_column_width=True)
                                    if asset_type == "Instagram Post (1080x1080)" and st.session_state.brand_kit_captions[i]:
                                        st.markdown('<div class="caption-display">', unsafe_allow_html=True)
                                        st.markdown(f"**Caption {i+1}**:\n{st.session_state.brand_kit_captions[i]}")
                                        st.markdown('</div>', unsafe_allow_html=True)
                                else:
                                    st.error(f"No image URL found for result {i+1}. Please try a different prompt.")

                            # Display download buttons in right column
                            with col2:
                                st.markdown('<div class="sub-header">Download Assets</div>', unsafe_allow_html=True)
                                for i, image in enumerate(images):
                                    # Download image
                                    img_buffer = io.BytesIO()
                                    image.save(img_buffer, format="PNG")
                                    img_buffer.seek(0)
                                    st.markdown('<div class="download-button">', unsafe_allow_html=True)
                                    st.download_button(
                                        label=f"Download {config['name'].capitalize()} {i+1} as PNG",
                                        data=img_buffer,
                                        file_name=f"brand_{config['name']}_{i+1}.png",
                                        mime="image/png",
                                        key=f"download_kit_button_{i+1}"
                                    )
                                    st.markdown('</div>', unsafe_allow_html=True)
                                    
                                    # Download caption for Instagram Post
                                    if asset_type == "Instagram Post (1080x1080)" and st.session_state.brand_kit_captions[i]:
                                        caption_buffer = io.StringIO(st.session_state.brand_kit_captions[i])
                                        st.markdown('<div class="download-button">', unsafe_allow_html=True)
                                        st.download_button(
                                            label=f"Download Caption {i+1} as TXT",
                                            data=caption_buffer.getvalue(),
                                            file_name=f"brand_caption_{i+1}.txt",
                                            mime="text/plain",
                                            key=f"download_caption_button_{i+1}"
                                        )
                                        st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.error(
                                "No assets generated. Try a more specific prompt, e.g., "
                                "'A vibrant Instagram post for MaddyTrends, women’s fashion, bold pinks, modern and empowering'."
                            )
                    except requests.exceptions.HTTPError as e:
                        if response.status_code == 401:
                            st.error("Invalid Bria AI API key. Please verify your API key or obtain a new one from https://www.bria.ai/.")
                        elif response.status_code == 429:
                            st.error("API rate limit exceeded. Please wait and try again or upgrade your Bria AI plan.")
                        elif response.status_code == 408:
                            st.error("Prompt rejected due to content moderation. Please revise your prompt to comply with Bria's ethical guidelines.")
                        else:
                            st.error(f"Error generating asset: {str(e)}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")