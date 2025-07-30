import streamlit as st
import requests
import io
from PIL import Image
import os
import json
import base64

def show_image_editor():
    # Custom CSS for professional styling (consistent with logo_generator.py)
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
        .stFileUploader {
            border-radius: 5px;
            border: 1px solid #bdc3c7;
            padding: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Main header
    st.markdown('<div class="main-header">Image Editor</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="sub-header">
        Edit an existing logo by uploading an image and providing a text description of the desired changes.  
        **Tips for better edits**:  
        - Be specific (e.g., "Change the background to a modern office setting, add blue accents").  
        - Describe modifications like colors, textures, or styles.  
        - Avoid vague prompts or copyrighted content.  
        **Examples**:  
        - Change the background to a modern office setting, add blue accents  
        - Apply a vintage texture, use warm colors  
        - Add a geometric pattern, make it minimalist
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

    # Create two columns: left for inputs and images, right for controls
    col1, col2 = st.columns([3, 1])  # 3:1 ratio for left (main content) and right (controls)

    # Right column: Dedicated section for controls
    with col2:
        with st.container():
            st.markdown('<div class="sub-header">Edit Options</div>', unsafe_allow_html=True)
            num_results = st.selectbox(
                "Number of Logos to Edit",
                options=[1, 2],
                index=0,
                key="num_results_edit"
            )
            st.markdown('<div class="sub-header">Additional Options</div>', unsafe_allow_html=True)
            st.write("More settings coming soon (e.g., styles, influence levels).")

    # Left column: Form and image display
    with col1:
        with st.form("image_editor_form"):
            uploaded_image = st.file_uploader(
                "Upload Logo Image (JPEG, PNG, WebP, max 12MB)",
                type=["jpg", "jpeg", "png", "webp"],
                key="image_upload"
            )
            edit_prompt = st.text_input(
                "Edit Description",
                placeholder="e.g., Change the background to a modern office setting, add blue accents",
                key="edit_prompt"
            )
            # Create columns for multiple edit buttons
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                st.markdown('<div class="generate-base">', unsafe_allow_html=True)
                edit_base = st.form_submit_button("Edit Base")
                st.markdown('</div>', unsafe_allow_html=True)
            with btn_col2:
                st.markdown('<div class="generate-hd">', unsafe_allow_html=True)
                edit_hd = st.form_submit_button("Edit HD")
                st.markdown('</div>', unsafe_allow_html=True)
            with btn_col3:
                st.markdown('<div class="generate-fast">', unsafe_allow_html=True)
                edit_fast = st.form_submit_button("Edit Fast")
                st.markdown('</div>', unsafe_allow_html=True)

            if edit_base or edit_hd or edit_fast:
                if not uploaded_image:
                    st.error("Please upload an image to edit.")
                elif not edit_prompt:
                    st.error("Please enter an edit description.")
                else:
                    # Set resolution based on button
                    if edit_base:
                        resolution = 512  # Standard quality
                    elif edit_hd:
                        resolution = 1024  # High quality
                    else:  # edit_fast
                        resolution = 256  # Fast generation

                    # Convert uploaded image to Base64
                    image_bytes = uploaded_image.read()
                    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

                    # Bria AI Reimagine API request
                    url = "https://engine.prod.bria-api.com/v1/reimagine"
                    payload = {
                        "prompt": edit_prompt,
                        "file": image_base64,
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
                                    st.image(image, caption=f"Edited Logo {i+1} ({resolution}x{resolution})", use_column_width=True)
                                else:
                                    st.error(f"No image URL found for result {i+1}. Please try a different edit prompt.")

                            # Display download buttons in right column
                            with col2:
                                st.markdown('<div class="sub-header">Download Edited Logos</div>', unsafe_allow_html=True)
                                for i, image in enumerate(images):
                                    img_buffer = io.BytesIO()
                                    image.save(img_buffer, format="PNG")
                                    img_buffer.seek(0)
                                    st.markdown('<div class="download-button">', unsafe_allow_html=True)
                                    st.download_button(
                                        label=f"Download Edited Logo {i+1} as PNG",
                                        data=img_buffer,
                                        file_name=f"edited_logo_{i+1}.png",
                                        mime="image/png",
                                        key=f"download_edit_button_{i+1}"
                                    )
                                    st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            st.error(
                                "No images edited. Try a more specific edit prompt, e.g., "
                                "'Change the background to a modern office setting, add blue accents'."
                            )
                    except requests.exceptions.HTTPError as e:
                        if response.status_code == 401:
                            st.error("Invalid Bria AI API key. Please verify your API key or obtain a new one from https://www.bria.ai/.")
                        elif response.status_code == 429:
                            st.error("API rate limit exceeded. Please wait and try again or upgrade your Bria AI plan.")
                        elif response.status_code == 408:
                            st.error("Prompt rejected due to content moderation. Please revise your edit prompt to comply with Bria's ethical guidelines.")
                        else:
                            st.error(f"Error editing logo: {str(e)}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")