import os
import streamlit as st
from app.crew import run
from app.tools.bedrock_clients import presigned_http_url

# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(page_title="AI Ad Video Generator", layout="centered")

st.title("🎥 AI Advertisement Video Generator")
st.markdown("Generate cinematic product ads automatically using **Nova Reel** and **Bedrock AI**.")

# -------------------------------
# User Inputs
# -------------------------------
with st.form("product_form"):
    product_name = st.text_input("🧴 Product Name", placeholder="e.g. Lomaz Perfumes")
    product_desc = st.text_area(
        "📝 Product Description",
        placeholder="e.g. Premium luxury perfumes with long-lasting fragrance and elegant design."
    )
    submitted = st.form_submit_button("🚀 Generate Video")

# -------------------------------
# Video Generation Pipeline
# -------------------------------
if submitted:
    if not product_name.strip() or not product_desc.strip():
        st.warning("⚠️ Please enter both product name and description before generating.")
    else:
        st.info("🧠 Generating cinematic product ad... please wait (5 mins).")

        try:
            # Run the full AI ad pipeline
            result = run(product_name, product_desc)

            # -------------------------------
            # Extract final or scene video
            # -------------------------------
            bucket = os.getenv("S3_BUCKET", "vi-gen-dev")

            # Prefer final video if present
            video_key = (
                result.get("final_video_key")
                or result.get("video_s3_key")
                or result.get("video_key")
                or result.get("output_video_key")
            )

            if not video_key and "first_scene_output" in result:
                # fallback to first scene’s video if full video missing
                video_key = result["first_scene_output"].get("video")

            if video_key:
                # Generate presigned URL for private S3 video
                video_url = presigned_http_url(bucket, video_key)
                st.success("✅ Video generation complete!")
                st.video(video_url)

                # Optional: provide a download link
                st.markdown(
                    f"[🔗 Download Final Video]({video_url}) _(link expires in 1 hour)_",
                    unsafe_allow_html=True
                )

                # Show optional metadata
                if "idea_used" in result:
                    st.info(f"💡 Idea used: {result['idea_used']}")

            else:
                st.error("❌ No video found in output. Check logs for details.")

        except Exception as e:
            st.error(f"🚨 An error occurred: {e}")
