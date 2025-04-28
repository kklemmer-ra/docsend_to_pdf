import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import time
import os
import shutil
from datetime import datetime

st.set_page_config(page_title="DocSend Slide Capturer", layout="centered")
st.title("📸 DocSend Slide Capturer")

st.markdown("""
1. Paste your **DocSend URL** below  
2. Enter how many slides you'd like to capture  
3. Click **Launch DocSend** and log in manually  
4. Then click **Start Screenshot Loop** to begin
""")

# UI Inputs
url = st.text_input("🔗 DocSend URL")
num_slides = st.number_input("📄 Number of Slides", min_value=1, max_value=100, step=1)
pdf_name = st.text_input("📄 PDF file name (no extension)", value="docsend_slides")

# Session state to store browser and tmp path
if "driver" not in st.session_state:
    st.session_state.driver = None
if "tmp_dir" not in st.session_state:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    tmp_path = os.path.join(os.getcwd(), f"tmp_{timestamp}")
    os.makedirs(tmp_path, exist_ok=True)
    st.session_state.tmp_dir = tmp_path

# Step 1: Launch browser
if st.button("🚀 Launch DocSend"):
    if not url:
        st.warning("Please enter a valid DocSend link.")
    else:
        try:
            options = Options()
            options.add_argument("--start-maximized")
            service = Service(ChromeDriverManager().install())
            st.session_state.driver = webdriver.Chrome(service=service, options=options)
            st.session_state.driver.get(url)
            time.sleep(5)
            st.success("✅ Chrome launched! Please complete login and cookie prompts.")
        except Exception as e:
            st.error(f"❌ Failed to launch browser: {e}")

# Step 2: Screenshot loop
if st.session_state.driver and st.button("📸 Start Screenshot Loop"):
    driver = st.session_state.driver
    tmp_dir = st.session_state.tmp_dir

    with st.spinner("Capturing slides..."):
        for i in range(1, int(num_slides) + 1):
            time.sleep(2)
            filename = os.path.join(tmp_dir, f"slide_{i:02}.png")
            driver.save_screenshot(filename)
            webdriver.ActionChains(driver).send_keys(Keys.ARROW_RIGHT).perform()
            st.write(f"✅ Captured: `{os.path.basename(filename)}`")

    driver.quit()
    st.session_state.driver = None
    st.success(f"🎉 All slides captured to `{tmp_dir}`")

# Step 3: Save as PDF
if st.button("📄 Generate PDF"):
    try:
        tmp_dir = st.session_state.tmp_dir
        image_files = [os.path.join(tmp_dir, file) for file in os.listdir(tmp_dir)
                       if file.endswith(".png") and file.startswith("slide_")]

        image_files.sort(key=lambda x: os.path.getmtime(x))
        images = [Image.open(img).convert("RGB") for img in image_files]

        pdf_path = os.path.join(os.getcwd(), pdf_name + ".pdf")
        images[0].save(pdf_path, save_all=True, append_images=images[1:])
        st.success(f"📄 PDF saved as `{pdf_path}`")

        # Optionally open folder
        if os.name == "nt":
            os.startfile(os.path.dirname(pdf_path))
        elif os.name == "posix":
            os.system(f"open {os.path.dirname(pdf_path)}")

    except Exception as e:
        st.error(f"❌ Failed to create PDF: {e}")
