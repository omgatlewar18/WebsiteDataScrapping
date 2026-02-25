import json
import time
import os
import pandas as pd
import streamlit as st
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fpdf import FPDF
import base64

# --- PIPELINE ENGINE ---
class OMGDataPipeline:
    def __init__(self):
        self.visited_urls = set()

    def discover_links(self, base_url):
        """OMG Discovery: Mapping the link architecture of the target domain."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        self.visited_urls.add(base_url)
        
        try:
            driver.get(base_url)
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            links = []
            domain = urlparse(base_url).netloc
            
            for a in soup.find_all('a', href=True):
                full_url = urljoin(base_url, a['href']).split('#')[0].rstrip('/')
                if urlparse(full_url).netloc == domain and full_url not in self.visited_urls:
                    links.append(full_url)
            
            return list(set(links))
        except Exception as e:
            st.error(f"Discovery Error: {e}")
            return []
        finally:
            driver.quit()

    def extract_content(self, url, mode, target, wait_time=5):
        """Universal Extraction Engine supporting multiple data modalities."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        extracted = []
        try:
            driver.get(url)
            WebDriverWait(driver, wait_time).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # 1. CSS SELECTOR
            if mode == 'CSS Selector':
                sel_list = ["p", "h1", "h2", "h3", "li", "td"] if target.lower() == "everything" else [target]
                for sel in sel_list:
                    for item in soup.select(sel):
                        txt = item.get_text(strip=True)
                        if len(txt) > 10:
                            extracted.append({"type": "Text", "payload": txt, "source": url, "node": item.name})

            # 2. FILE DISCOVERY
            elif mode == 'File Discovery':
                exts = [e.strip().lower() for e in target.split(',')]
                for a in soup.find_all('a', href=True):
                    href = a['href'].lower()
                    if any(href.endswith(ex) for ex in exts):
                        extracted.append({"type": "File Link", "payload": urljoin(url, a['href']), "source": url, "node": "a"})

            # 3. METADATA SCRAPER
            elif mode == 'Metadata':
                title = soup.title.string if soup.title else "Untitled"
                desc = soup.find("meta", attrs={"name": "description"})
                extracted.append({
                    "type": "Metadata",
                    "payload": f"TITLE: {title} | DESC: {desc['content'] if desc else 'None'}",
                    "source": url,
                    "node": "head"
                })

            # 4. KEYWORD SEARCH
            elif mode == 'Keyword Search':
                kw = target.lower()
                for tag in soup.find_all(['p', 'li', 'td', 'h1', 'h2']):
                    if kw in tag.get_text().lower():
                        extracted.append({"type": "Keyword Match", "payload": tag.get_text(strip=True), "source": url, "node": tag.name})

            # 5. IMAGE SCRAPER
            elif mode == 'Image Scraper':
                for img in soup.find_all('img', src=True):
                    img_url = urljoin(url, img['src'])
                    alt = img.get('alt', 'No label')
                    extracted.append({"type": "Image Resource", "payload": f"URL: {img_url} | ALT: {alt}", "source": url, "node": "img"})

            # 6. TABLE EXTRACTOR
            elif mode == 'Table Extractor':
                for table in soup.find_all('table'):
                    rows = []
                    for tr in table.find_all('tr'):
                        cols = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                        rows.append(" | ".join(cols))
                    if rows:
                        extracted.append({"type": "Table Data", "payload": " [ROW] ".join(rows), "source": url, "node": "table"})

            return extracted
        except Exception as e:
            st.warning(f"Failed to extract {url}: {e}")
            return []
        finally:
            driver.quit()

    def _safe_enc(self, text):
        """Cleans and encodes text to be compatible with PDF generation."""
        m = {'\u2018':"'", '\u2019':"'", '\u201c':'"', '\u201d':'"', '\u2013':'-', '\u2014':'-', '\u00a0':' ', '\u2022': '*'}
        for u, a in m.items(): text = str(text).replace(u, a)
        return text.encode('latin-1', 'ignore').decode('latin-1')

    def generate_pdf_bytes(self, df):
        """Phase 4: PDF Intelligence Report Generation."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, txt=self._safe_enc("OMG Universal Data Pipeline Report"), ln=True, align='C')
        pdf.ln(10)

        for i, row in df.iterrows():
            pdf.set_font("Arial", 'B', 10)
            pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 8, txt=self._safe_enc(f"Segment #{i + 1} | {row['type']}"), ln=True, fill=True)
            
            pdf.set_font("Arial", size=9)
            for col in df.columns:
                pdf.set_font("Arial", 'B', 8)
                pdf.write(5, self._safe_enc(f"{col.upper()}: "))
                pdf.set_font("Arial", size=9)
                pdf.write(5, self._safe_enc(f"{str(row[col])}\n"))
            pdf.ln(4)
            if pdf.get_y() > 250: pdf.add_page()

        # Output to string and then encode
        return pdf.output(dest='S').encode('latin-1')

# --- STREAMLIT UI ---
def main():
    st.set_page_config(page_title="OMG Scrapping Engine", page_icon="🔖", layout="wide")
    
    # Initialize Pipeline and Session State
    pipe = OMGDataPipeline()
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'cleaned_df' not in st.session_state:
        st.session_state.cleaned_df = None

    # Sidebar / Branding
    with st.sidebar:
        st.title("OMG Scrapping Engine")
        st.markdown("---")
        st.info("Universal Data Loader, Structuring & Cleaning Tool")
        
        # Step 1: Target Input
        url = st.text_input("Step 1: Target URL", placeholder="https://omgscrappingtool.com")
        
        # Step 2: Extraction Mode
        mode = st.selectbox("Step 2: Extraction Mode", 
                            ["CSS Selector", "File Discovery", "Metadata", "Keyword Search", "Image Scraper", "Table Extractor"])
        
        target = ""
        if mode in ["CSS Selector", "File Discovery", "Keyword Search"]:
            label = "Enter Selector (e.g. .news or everything)" if mode == "CSS Selector" else \
                    "Enter Extensions (e.g. .pdf,.zip)" if mode == "File Discovery" else \
                    "Enter Keyword"
            target = st.text_input(label)

        crawl_subpages = st.checkbox("Crawl top 3 internal links?")

        if st.button("🚀 Run Pipeline", use_container_width=True):
            if not url:
                st.error("Please enter a URL")
            else:
                with st.spinner("OMG Engine working..."):
                    all_extracted = []
                    # Discovery
                    links = pipe.discover_links(url)
                    # Primary Page
                    all_extracted.extend(pipe.extract_content(url, mode, target))
                    # Crawling
                    if crawl_subpages and links:
                        status_text = st.empty()
                        for i, l in enumerate(links[:3]):
                            status_text.text(f"Crawling link {i+1}/3: {l}")
                            all_extracted.extend(pipe.extract_content(l, mode, target))
                        status_text.empty()
                    
                    st.session_state.results = all_extracted
                    
                    if all_extracted:
                        df = pd.DataFrame(all_extracted)
                        df = df.drop_duplicates()
                        if 'payload' in df.columns:
                            df['payload'] = df['payload'].str.replace(r'\s+', ' ', regex=True).str.strip()
                        st.session_state.cleaned_df = df.fillna("N/A")
                        st.success(f"Extraction complete! Found {len(df)} records.")
                    else:
                        st.session_state.cleaned_df = None
                        st.warning("No data found matching your criteria.")

    # Main Dashboard
    st.header("📊 Extraction Dashboard")
    
    if st.session_state.cleaned_df is not None:
        # Stats Row
        c1, c2, c3 = st.columns(3)
        c1.metric("Records Found", len(st.session_state.cleaned_df))
        c2.metric("Pipeline Status", "100%", "Cleaned")
        c3.metric("Data Source", urlparse(url).netloc if url else "Unknown")

        st.markdown("### Processed Data Snapshot")
        st.dataframe(st.session_state.cleaned_df, use_container_width=True)

        # Export Options
        st.markdown("---")
        st.subheader("📁 Structured Export Options")
        col_ex1, col_ex2, col_ex3 = st.columns(3)

        with col_ex1:
            csv = st.session_state.cleaned_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "omg_data.csv", "text/csv", use_container_width=True)
        
        with col_ex2:
            json_str = st.session_state.cleaned_df.to_json(orient="records", indent=4).encode('utf-8')
            st.download_button("Download JSON", json_str, "omg_data.json", "application/json", use_container_width=True)

        with col_ex3:
            try:
                pdf_bytes = pipe.generate_pdf_bytes(st.session_state.cleaned_df)
                st.download_button("Generate PDF Report", pdf_bytes, "omg_intelligence_report.pdf", "application/pdf", use_container_width=True)
            except Exception as e:
                st.error(f"Error generating PDF: {e}")

    else:
        st.info("Configure the parameters in the sidebar and click 'Run Pipeline' to see results.")
        st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=1000", caption="OMG Intelligence Ready")

if __name__ == "__main__":
    # Ensure the script is run correctly via Streamlit
    import sys
    if "streamlit" in sys.modules or st._is_running_with_streamlit:
        main()
    else:
        print("\n" + "!"*60)
        print("ERROR: This script must be run using Streamlit.")
        print(f"Please use the following command in your terminal:")
        print(f"streamlit run {os.path.basename(__file__)}")
        print("!"*60 + "\n")