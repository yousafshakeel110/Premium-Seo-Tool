import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import zipfile

st.set_page_config(page_title="Premium SEO Generator", layout="wide")

st.title("Premium SEO HTML Page Generator")
st.write("Screenshot → Keywords → Language → Fully Optimized HTML Pages")

# ----------------------------
# Helpers
# ----------------------------

def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def build_layout_prompt(language):
    return f"""
You are an expert web designer and SEO specialist.

Analyze the uploaded homepage screenshot and recreate the SAME layout in clean HTML5.
Use proper semantic structure: header, section, article, footer.
Do NOT add dummy text.
Do NOT explain anything.
Only return pure HTML code.

Language: {language}
"""

def build_page_prompt(keyword, location, language):
    return f"""
Create a fully SEO optimized HTML service page.

Target keyword: {keyword}
Target location: {location}

Rules:
- Use NLP and semantic SEO
- Proper H1–H3 hierarchy
- Local intent optimization
- Meta title & meta description
- Schema-ready clean HTML
- Conversion focused content
- No markdown
- No explanations

Language: {language}

Return ONLY HTML.
"""

# ----------------------------
# UI
# ----------------------------

openai_key = st.text_input("OpenAI API Key", type="password")

language = st.selectbox(
    "Language",
    ["English", "Urdu", "Arabic", "Spanish", "Korean", "Filipino"]
)

location = st.text_input("Target Location (city / country)", value="")

uploaded_image = st.file_uploader("Upload Homepage Screenshot", type=["png", "jpg", "jpeg"])

keywords_input = st.text_area(
    "Paste Keywords (one per line)",
    height=200
)

generate = st.button("Generate Premium SEO Pages")

# ----------------------------
# MAIN LOGIC
# ----------------------------

if generate:
    if not openai_key or not uploaded_image or not keywords_input:
        st.error("API key, screenshot, and keywords are required.")
        st.stop()

    client = OpenAI(api_key=openai_key)

    image = Image.open(uploaded_image)
    image_b64 = image_to_base64(image)

    with st.spinner("Analyzing layout..."):
        layout_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": build_layout_prompt(language)},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.3
        )

    base_html = layout_response.choices[0].message.content

    keywords = [k.strip() for k in keywords_input.splitlines() if k.strip()]

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for kw in keywords:
            with st.spinner(f"Generating page for: {kw}"):
                page_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You generate high-end SEO optimized HTML pages."
                        },
                        {
                            "role": "user",
                            "content": base_html + "\n\n" + build_page_prompt(kw, location, language)
                        }
                    ],
                    temperature=0.7
                )

                page_html = page_response.choices[0].message.content
                filename = kw.lower().replace(" ", "-") + ".html"
                zip_file.writestr(filename, page_html)

    st.success("Done! Pages generated successfully.")

    st.download_button(
        label="Download HTML Pages (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="seo_pages.zip",
        mime="application/zip"
    )
