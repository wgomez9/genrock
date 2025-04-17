import streamlit as st
from openai import OpenAI
from io import BytesIO
from PIL import Image
import base64
import requests
import time

# Import the prompt enhancer function
def add_prompt_enhancer_sidebar(openai_api_key):
    """Add a prompt enhancer sidebar that uses o4-mini to improve prompts through conversation."""
    
    with st.sidebar:
        st.title("🔮 Prompt Enhancer")
        st.write("Improve your prompts through a guided conversation with an AI assistant.")
        
        # Initialize conversation state if not already done
        if "enhancer_messages" not in st.session_state:
            st.session_state.enhancer_messages = []
            st.session_state.enhanced_prompt = ""
            st.session_state.conversation_started = False
            st.session_state.conversation_complete = False
        
        # Display current enhanced prompt if available
        if st.session_state.enhanced_prompt:
            st.success("Enhanced Prompt:")
            st.code(st.session_state.enhanced_prompt)
            if st.button("Use Enhanced Prompt", key="use_enhanced_prompt"):
                # Set the prompt in the main area
                st.session_state.user_prompt = st.session_state.enhanced_prompt
                st.rerun()
        
        # Start new conversation button
        if not st.session_state.conversation_started:
            original_prompt = st.text_area("Enter your initial prompt:", 
                                         placeholder="A cat riding a bicycle...",
                                         key="original_prompt_sidebar")
            
            if st.button("Start Conversation", key="start_enhancer_convo"):
                if not original_prompt:
                    st.warning("Please enter an initial prompt first.")
                    return
                
                if not openai_api_key:
                    st.warning("Please enter your OpenAI API key in the main panel first.")
                    return
                
                # Initialize the conversation
                system_msg = (
                    "You are a creative and helpful prompt engineering assistant. "
                    "Your goal is to improve the user's image generation prompt through a brief conversation. "
                    "Ask 2-3 targeted questions to understand what they want, then provide an enhanced prompt. "
                    "Your questions should be brief and focused. Use your expertise in prompt engineering to "
                    "create detailed, vivid descriptions that will work well with image generation AI. "
                    "When you've asked enough questions, provide a final enhanced prompt prefixed with 'ENHANCED PROMPT: '"
                )
                
                # Create OpenAI client
                client = OpenAI(api_key=openai_api_key)
                
                # Initialize conversation with system message and user's original prompt
                st.session_state.enhancer_messages = [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": f"My initial prompt is: {original_prompt}"}
                ]
                
                # Get first response from AI
                try:
                    with st.spinner("Getting response..."):
                        response = client.chat.completions.create(
                            model="o4-mini",
                            messages=st.session_state.enhancer_messages,
                        )
                        ai_response = response.choices[0].message.content
                        
                        # Add AI response to conversation
                        st.session_state.enhancer_messages.append(
                            {"role": "assistant", "content": ai_response}
                        )
                        
                        # Set conversation started
                        st.session_state.conversation_started = True
                        
                        # Force a rerun to update the UI
                        st.rerun()
                except Exception as e:
                    st.error(f"Error communicating with OpenAI: {str(e)}")
        
        # Continue conversation if started but not complete
        elif st.session_state.conversation_started and not st.session_state.conversation_complete:
            # Display conversation history
            st.subheader("Conversation")
            for msg in st.session_state.enhancer_messages:
                if msg["role"] == "user":
                    st.text_area("You:", value=msg["content"], height=80, disabled=True, key=f"user_{time.time()}")
                elif msg["role"] == "assistant" and msg["role"] != "system":
                    # Check if this is the final message with enhanced prompt
                    if "ENHANCED PROMPT: " in msg["content"]:
                        parts = msg["content"].split("ENHANCED PROMPT: ")
                        conversation_part = parts[0]
                        enhanced_prompt = parts[1] if len(parts) > 1 else ""
                        
                        st.text_area("Assistant:", value=conversation_part, height=100, disabled=True, key=f"ai_{time.time()}")
                        
                        # Save the enhanced prompt
                        st.session_state.enhanced_prompt = enhanced_prompt
                        st.session_state.conversation_complete = True
                    else:
                        st.text_area("Assistant:", value=msg["content"], height=100, disabled=True, key=f"ai_{time.time()}")
            
            # Only show input if conversation is not complete
            if not st.session_state.conversation_complete:
                user_response = st.text_area("Your response:", key="user_response")
                
                if st.button("Send", key="send_response"):
                    if user_response:
                        # Add user response to conversation
                        st.session_state.enhancer_messages.append(
                            {"role": "user", "content": user_response}
                        )
                        
                        # Get AI response
                        try:
                            client = OpenAI(api_key=openai_api_key)
                            
                            with st.spinner("Getting response..."):
                                response = client.chat.completions.create(
                                    model="o4-mini",
                                    messages=st.session_state.enhancer_messages,
                                )
                                ai_response = response.choices[0].message.content
                                
                                # Add AI response to conversation
                                st.session_state.enhancer_messages.append(
                                    {"role": "assistant", "content": ai_response}
                                )
                                
                                # Check if conversation is complete
                                if "ENHANCED PROMPT: " in ai_response:
                                    enhanced_prompt = ai_response.split("ENHANCED PROMPT: ")[1]
                                    st.session_state.enhanced_prompt = enhanced_prompt
                                    st.session_state.conversation_complete = True
                                
                                # Force a rerun to update the UI
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error communicating with OpenAI: {str(e)}")
        
        # Reset button (always visible)
        if st.button("Reset Enhancer", key="reset_enhancer"):
            st.session_state.enhancer_messages = []
            st.session_state.enhanced_prompt = ""
            st.session_state.conversation_started = False
            st.session_state.conversation_complete = False
            st.rerun()

# Initialize session state for prompt
if "user_prompt" not in st.session_state:
    st.session_state.user_prompt = ""

# Show title and description
st.title("🎨GenRock")
st.write(
    "Generate images using OpenAI's DALL-E models. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

# Ask user for their OpenAI API key
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Add the prompt enhancer sidebar
    add_prompt_enhancer_sidebar(openai_api_key)
    
    # Create an OpenAI client
    client = OpenAI(api_key=openai_api_key)
    
    # Create tabs for different DALL-E functionalities
    tab1, tab2, tab3 = st.tabs(["Generate Images", "Create Variations (DALL-E 2)", "Edit Images (DALL-E 2)"])
    
    with tab1:
        st.header("Generate Images")
        
        # Model selection
        model = st.radio("Select Model", ["DALL-E 2", "DALL-E 3"], horizontal=True)
        
        # Prompt input - now using session state to allow the enhancer to set it
        prompt = st.text_area("Enter your prompt:", 
                             height=100, 
                             value=st.session_state.user_prompt,
                             key="main_prompt_input")
        
        # Size options
        if model == "DALL-E 2":
            size_options = ["256x256", "512x512", "1024x1024"]
            num_images = 1  # Fixed to 1 image
        else:  # DALL-E 3
            size_options = ["1024x1024", "1024x1792", "1792x1024"]
            quality = st.radio("Quality", ["standard", "hd"], horizontal=True)
            num_images = 1  # DALL-E 3 allows only 1 image per request
            
            # Add DALL-E 3 prompt information - only shown when DALL-E 3 is selected
            st.info("""
            With the release of DALL·E 3, the model takes in your prompt and automatically rewrites it:
            * For safety reasons
            * To add more detail (more detailed prompts generally result in higher quality images)
            
            You can't disable this feature, but you can get outputs closer to your requested image by adding the following to your prompt:
            
            `I NEED to test how the tool works with extremely simple prompts. DO NOT add any detail, just use it AS-IS:`
            """)
        
        size = st.selectbox("Size", options=size_options, key="generate_size")
        
        # Generate button
        if st.button("Generate Image"):
            if prompt:
                try:
                    with st.spinner("Generating image..."):
                        if model == "DALL-E 2":
                            response = client.images.generate(
                                model="dall-e-2",
                                prompt=prompt,
                                size=size,
                                n=num_images,
                            )
                        else:  # DALL-E 3
                            response = client.images.generate(
                                model="dall-e-3",
                                prompt=prompt,
                                size=size,
                                quality=quality,
                                n=1,
                            )
                        
                        # Display the revised prompt (DALL-E 3 specific)
                        if hasattr(response.data[0], 'revised_prompt') and response.data[0].revised_prompt:
                            st.subheader("Revised Prompt:")
                            st.write(response.data[0].revised_prompt)
                        
                        # Display generated image
                        st.subheader("Generated Image:")
                        st.image(response.data[0].url, use_container_width=True)
                        
                        # Get image data for download
                        image_url = response.data[0].url
                        try:
                            response_image = requests.get(image_url)
                            img_data = response_image.content
                            
                            # Create a download button using HTML to avoid page refresh
                            img_b64 = base64.b64encode(img_data).decode()
                            href = f'<a href="data:image/png;base64,{img_b64}" download="dalle_generated_image.png">Download Image</a>'
                            st.markdown(href, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error preparing download: {str(e)}")
                            # Fallback to the regular link
                            st.markdown(f"[Download Image]({image_url})", unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.warning("Please enter a prompt first.")
    with tab2:
        st.header("Create Variations (DALL-E 2 Only)")
        st.write("Upload an image to create variations of it.")
        
        # Upload image for variation
        variation_image = st.file_uploader("Upload image (PNG format)", type=["png"], key="variation_image_uploader")
        
        if variation_image:
            # Display the uploaded image
            st.subheader("Original Image")
            st.image(variation_image, use_container_width=True)
        
        # Number of variations fixed to 1
        num_variations = 1
        
        # Size selection for variations
        variation_size = st.selectbox("Size", options=["256x256", "512x512", "1024x1024"], key="variation_size")
        
        # Generate variations button
        if st.button("Generate Variations"):
            if variation_image:
                try:
                    with st.spinner("Generating variations..."):
                        response = client.images.create_variation(
                            model="dall-e-2",
                            image=variation_image,
                            n=num_variations,
                            size=variation_size
                        )
                        
                        # Display the variations
                        st.subheader("Image Variation:")
                        st.image(response.data[0].url, use_container_width=True)
                        
                        # Get image data for download
                        image_url = response.data[0].url
                        try:
                            response_image = requests.get(image_url)
                            img_data = response_image.content
                            
                            # Create a download button using HTML to avoid page refresh
                            img_b64 = base64.b64encode(img_data).decode()
                            href = f'<a href="data:image/png;base64,{img_b64}" download="dalle_variation.png">Download Variation</a>'
                            st.markdown(href, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error preparing download: {str(e)}")
                            # Fallback to the regular link
                            st.markdown(f"[Download Variation]({image_url})", unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.warning("Please upload an image first.")   
    with tab3:
        st.header("Edit Images (DALL-E 2 Only)")
        st.write("Upload an image and a mask to edit specific parts of the image.")
        
        # Upload original image
        uploaded_image = st.file_uploader("Upload image to edit (PNG format)", type=["png"], key="edit_image_uploader")
        
        st.write("Use https://www.photopea.com/ to make transparent area")
        # Upload mask
        uploaded_mask = st.file_uploader("Upload mask (transparent areas will be edited)", type=["png"], key="mask_uploader")
        
        if uploaded_image and uploaded_mask:
            # Display the uploaded images
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original Image")
                st.image(uploaded_image, use_container_width=True)
            with col2:
                st.subheader("Mask")
                st.image(uploaded_mask, use_container_width=True)
        
        # Prompt for edited image
        edit_prompt = st.text_area("Enter prompt for the edited image:", 
                                  help="Describe the full new image, not just the edited area.",
                                  height=100, 
                                  key="edit_prompt")
        
        # Size selection for edit
        edit_size = st.selectbox("Size", options=["256x256", "512x512", "1024x1024"], key="edit_size")
        
        # Generate edit button
        if st.button("Generate Edit"):
            if uploaded_image and uploaded_mask and edit_prompt:
                try:
                    with st.spinner("Generating edited image..."):
                        response = client.images.edit(
                            model="dall-e-2",
                            image=uploaded_image,
                            mask=uploaded_mask,
                            prompt=edit_prompt,
                            n=1,
                            size=edit_size
                        )
                        
                        # Display the edited image
                        st.subheader("Edited Image:")
                        st.image(response.data[0].url, use_container_width=True)
                        
                        # Get image data for download
                        image_url = response.data[0].url
                        try:
                            response_image = requests.get(image_url)
                            img_data = response_image.content
                            
                            # Create a download button using HTML to avoid page refresh
                            img_b64 = base64.b64encode(img_data).decode()
                            href = f'<a href="data:image/png;base64,{img_b64}" download="dalle_edited_image.png">Download Edited Image</a>'
                            st.markdown(href, unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Error preparing download: {str(e)}")
                            # Fallback to the regular link
                            st.markdown(f"[Download Edited Image]({image_url})", unsafe_allow_html=True)
                
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
            else:
                st.warning("Please upload both an image and mask, and enter a prompt.")
    
