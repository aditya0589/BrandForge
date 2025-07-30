import streamlit as st
import requests
import io
from PIL import Image
import os
import json

def show_logo_generator():
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
        .generate-base>button {
            background-color: #3498db;
            color: white;
        }
        .generate-hd>button {
            background-color: #2ecc71;
            color: white;
        }
        .generate-fast>button {
            background-color: #e67e22;
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
        </style>
        """,
        unsafe_allow_html=True
    )

    # Main header
    st.markdown('<div class="main-header">Logo Generator</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sub-header">
        Create a unique logo for your brand by entering a detailed description below.  
        </div>
        """,
        unsafe_allow_html=True
    )

    # Check for Bria AI API key
    api_key = os.getenv("BRIA_API_TOKEN")
    if not api_key:
        st.error("Bria AI API key is missing. Please set the 'BRIA_API_TOKEN' environment variable or contact support@bria.ai to obtain one.")
        st.markdown("To get an API key, visit [Bria AI](https://www.bria.ai/) and sign up for their developer program.")
        return

    # Create two columns: left for prompt and images, right for controls
    col1, col2 = st.columns([3, 1])  # 3:1 ratio for left (main content) and right (controls)

    # Right column: Dedicated section for controls
    with col2:
        with st.container():
            st.markdown('<div class="sub-header">Generation Options</div>', unsafe_allow_html=True)
            num_results = st.selectbox(
                "Number of Logos to Generate",
                options=[1, 2],
                index=0,
                key="num_results"
            )
            st.markdown('<div class="sub-header">Additional Options</div>', unsafe_allow_html=True)
            st.write("More settings coming soon (e.g., styles, colors).")

    # Left column: Form and image display
    with col1:
        with st.form("logo_generator_form"):
            prompt = st.text_input(
                "Brand Description",
                placeholder="e.g., A modern logo for a tech startup, blue and silver, geometric design",
                key="logo_prompt"
            )
            # Create columns for multiple generate buttons
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                st.markdown('<div class="generate-base">', unsafe_allow_html=True)
                generate_base = st.form_submit_button("Generate Base")
                st.markdown('</div>', unsafe_allow_html=True)
            with btn_col2:
                st.markdown('<div class="generate-hd">', unsafe_allow_html=True)
                generate_hd = st.form_submit_button("Generate HD")
                st.markdown('</div>', unsafe_allow_html=True)
            with btn_col3:
                st.markdown('<div class="generate-fast">', unsafe_allow_html=True)
                generate_fast = st.form_submit_button("Generate Fast")
                st.markdown('</div>', unsafe_allow_html=True)

            if generate_base or generate_hd or generate_fast:
                if not prompt:
                    st.error("Please enter a brand description.")
                else:
                    # Set resolution based on button
                    if generate_base:
                        resolution = 512  # Standard quality
                    elif generate_hd:
                        resolution = 1024  # High quality
                    else:  # generate_fast
                        resolution = 256  # Fast generation

                    # Bria AI API request
                    model_version = "2.3"
                    url = f"https://engine.prod.bria-api.com/v1/text-to-image/base/{model_version}"
                    payload = {
                        "prompt": f"Professional logo: {prompt}",
                        "num_results": num_results,
                        "sync": True,
                        "height": resolution,
                        "width": resolution
                    }
                    headers = {
                        "Content-Type": "application/json",
                        "api_token": api_key
                    }

                    try:
                        response = requests.post(url, json=payload, headers=headers)
                        response.raise_for_status()
                        data = response.json()

                        # Debug: Show raw API response
                        with st.expander("Debug: View Raw API Response"):
                            st.json(data)

                        if "result" in data and data["result"]:
                            # Store images for download in right column
                            images = []
                            for i, result in enumerate(data["result"]):
                                if "urls" in result and result["urls"]:
                                    # Fetch image from URL
                                    image_url = result["urls"][0]
                                    image_response = requests.get(image_url)
                                    image_response.raise_for_status()
                                    image = Image.open(io.BytesIO(image_response.content))
                                    images.append(image)
                                    
                                    # Display the image in left column
                                    st.image(image, caption=f"Generated Logo {i+1} ({resolution}x{resolution})", use_column_width=True)
                                else:
                                    st.error(f"No image URL found for result {i+1}. Please try a different prompt.")

                            # Display download buttons in right column
                            with col2:
                                st.markdown('<div class="sub-header">Download Logos</div>', unsafe_allow_html=True)
                                for i, image in enumerate(images):
                                    img_buffer = io.BytesIO()
                                    image.save(img_buffer, format="PNG")
                                    img_buffer.seek(0)
                                    st.markdown('<div class="download-button">', unsafe_allow_html=True)
                                    st.download_button(
                                        label=f"Download Logo {i+1} as PNG",
                                        data=img_buffer,
                                        file_name=f"generated_logo_{i+1}.png",
                                        mime="image/png",
                                        key=f"download_logo_button_{i+1}"
                                    )
                                    st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.error(
                                "No images generated. Try a more specific prompt, e.g., "
                                "'A minimalist logo for a coffee shop, brown and green, with a coffee bean icon'."
                            )
                    except requests.exceptions.HTTPError as e:
                        if response.status_code == 401:
                            st.error("Invalid Bria AI API key. Please verify your API key or obtain a new one from https://www.bria.ai/.")
                        elif response.status_code == 429:
                            st.error("API rate limit exceeded. Please wait and try again or upgrade your Bria AI plan.")
                        else:
                            st.error(f"Error generating logo: {str(e)}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")