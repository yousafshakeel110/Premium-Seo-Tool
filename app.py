import streamlit as st
from openai import OpenAI
from PIL import Image
import base64
import io
import zipfile
import os

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Premium SEO Bulk Page Generator", layout="wide")
st.title("Premium SEO Bulk Page Generator")
st.write("Upload your homepage screenshot, provide keywords, and generate fully optimized HTML pages.")

# ----------------------------
# HELPERS
# ----------------------------
def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def build_layout_prompt(language):
    return f"""
You are an expert front-end developer and UI/UX designer.

Analyze the uploaded homepage screenshot and recreate the SAME layout in fully styled HTML + CSS.
Include:
- Flexbox / CSS Grid for layout
- Responsive design (mobile-friendly)
- Colors, fonts, spacing, buttons, headers as per the screenshot
- Include placeholders for images
- Proper semantic HTML (header, section, article, footer)
- No dummy text
- Only return HTML + inline or internal CSS

Language: {language}
"""

def build_page_prompt(keyword, location, language):
    return f"""
You are an expert front-end developer and SEO specialist.

Create a fully SEO optimized HTML service page for the following:

Target keyword: {keyword}
Target location: {location}

Requirements:
- Use NLP and semantic SEO for content generation
- Proper H1–H3 hierarchy
- Local intent optimization
- Include meta title & meta description
- Schema-ready clean HTML
- Conversion-focused content
- Match home page design (colors, layout, images)
- Include all necessary CSS inline or in <style> tag inside <head>
- Responsive design (mobile-friendly)
- Include placeholders for images where needed
- Do NOT use markdown
- Return complete HTML + CSS

Language: {language}
""""""

def read_keywords_file(file):
    content = file.read().decode("utf-8")
    return [k.strip() for k in content.splitlines() if k.strip()]

# ----------------------------
# USER INPUTS
# ----------------------------
openai_key = st.text_input("Enter your OpenAI API Key", type="password")

language = st.selectbox(
    "Select Language",
    ["English", "Urdu", "Arabic", "Spanish", "Korean", "Filipino"]
)

location = st.text_input("Target Location (City / State / Country)")

uploaded_image = st.file_uploader("Upload Homepage Screenshot", type=["png", "jpg", "jpeg"])

keywords_text = st.text_area(
    "Enter Keywords (one per line)",
    height=200
)

keywords_file = st.file_uploader("Or Upload Keywords File (.txt)", type=["txt"])

generate = st.button("Generate Bulk SEO Pages")

# ----------------------------
# MAIN LOGIC
# ----------------------------
if generate:
    if not openai_key or not uploaded_image or (not keywords_text and not keywords_file):
        st.error("OpenAI key, homepage screenshot, and keywords (text or file) are required.")
        st.stop()

    # Initialize OpenAI client
    client = OpenAI(api_key=openai_key)

    # Read image and convert to base64
    image = Image.open(uploaded_image)
    image_b64 = image_to_base64(image)

    # Prepare keywords
    keywords = []
    if keywords_text:
        keywords.extend([k.strip() for k in keywords_text.splitlines() if k.strip()])
    if keywords_file:
        keywords.extend(read_keywords_file(keywords_file))

    if not keywords:
        st.error("No valid keywords found.")
        st.stop()

    # ---------------- Generate Layout HTML ----------------
    with st.spinner("Analyzing homepage layout..."):
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

    # ---------------- Generate Pages for Each Keyword ----------------
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for kw in keywords:
            with st.spinner(f"Generating page for: {kw}"):
                page_response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You generate high-end SEO optimized HTML pages."},
                        {"role": "user", "content": base_html + "\n\n" + build_page_prompt(kw, location, language)}
                    ],
                    temperature=0.7
                )

                page_html = page_response.choices[0].message.content
                filename = kw.lower().replace(" ", "-") + ".html"
                zip_file.writestr(filename, page_html)

    st.success("All pages generated successfully!")
    st.download_button(
        label="Download All HTML Pages (ZIP)",
        data=zip_buffer.getvalue(),
        file_name="seo_pages.zip",
        mime="application/zip"
    )

# ----------------------------
# PREMIUM FEATURES IDEA
# ----------------------------
st.markdown("""
*Premium Features (Future / Optional):*
- Live preview of generated pages
- Drag & drop multiple images for placeholders
- Advanced semantic content tuning via sliders (e.g., conversion-focused, keyword density)
- Export structured JSON for CMS import
- Automatic Open Graph & Twitter meta tags
- Mobile & desktop preview toggle
""")
