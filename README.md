🔖 OMG Data Pipeline

Universal Web Intelligence & Automated Data Structuring Tool

🌐 Live Demo

Access the fully functional web dashboard here:

https://omgdatapipeline.streamlit.app/

🚀 Project Overview

The OMG Data Pipeline is a comprehensive intelligence tool designed to bridge the gap between raw web data and structured analysis. Originally conceptualized for high-integrity environments, this universal scraper automates the Extraction, Structuring, and Cleaning of information from any public URL.

By utilizing a dual-engine approach (Selenium for dynamic JS rendering and BeautifulSoup for parsing), the pipeline ensures 100% data capture accuracy across diverse web architectures.

✨ Key Features

The pipeline operates in six distinct operational modes:

CSS Selector: Target specific HTML elements (classes, IDs, or tags). Use the "everything" keyword for a broad semantic sweep.

File Discovery: Automatically identify and catalog download links for specific extensions (e.g., .pdf, .docx, .zip).

Metadata Scraper: Extract hidden SEO intelligence, including page titles and meta-descriptions.

Keyword Search: Scan and retrieve only the content segments containing your specific search terms.

Image Scraper: Capture high-resolution image URLs along with their descriptive Alt-text.

Table Extractor: Convert complex HTML tables into normalized, structured datasets.

🛠️ Tech Stack

Frontend: Streamlit (Responsive Web Dashboard)

Engine: Selenium WebDriver (Headless Chrome)

Parser: BeautifulSoup4

Data Handling: Pandas (Normalization & De-duplication)

Reporting: FPDF (Automated PDF Intelligence Reports)

📦 Installation & Local Setup

Clone the repository:

git clone [https://github.com/yourusername/omg-data-pipeline.git](https://github.com/yourusername/omg-data-pipeline.git)
cd omg-data-pipeline


Install Python dependencies:

pip install -r requirements.txt


Install Browser Drivers:
Ensure Google Chrome is installed. Selenium will manage the driver automatically in most environments.

Run the App:

streamlit run data_pipeline.py


☁️ Deployment Notes (Streamlit Cloud)

To run this pipeline in a cloud environment, the following configuration files are required to handle headless Chromium:

packages.txt: Includes chromium and chromium-driver for system-level browser support.

requirements.txt: Includes all Python libraries (Pandas, Selenium, BS4, etc.).

📑 Data Workflow

Extraction: Automated loading and rendering via Selenium.

Structuring: JSON normalization of raw payloads.

Cleaning: Deduplication and Unicode character sanitization.

Storage: Export capabilities to CSV, JSON, and PDF Intelligence Reports.

🔖 Signature

OMG Automated Intelligence Environment Optimized for Universal Web Intelligence.
