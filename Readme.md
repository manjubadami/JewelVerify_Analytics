# 💍 JewelVerify Analytics
**Automated jewelry tag extraction with real-time benefit analysis.**

This application leverages **Google Gemini 1.5 Flash** to digitize physical jewelry tags via computer vision and provides instant pricing comparisons against historical gold savings plans.

---

## 🛠️ Tech Stack
*   **Frontend/UI**: [Streamlit](https://streamlit.io/) (Python-based web framework)
*   **AI Engine**: [Google Generative AI (Gemini Pro Vision)](https://ai.google.dev/)
*   **Data Handling**: [Pandas](https://pandas.pydata.org/) (for tabular breakdowns)
*   **Date Logic**: [Python-Dateutil](https://dateutil.readthedocs.io/en/stable/) (for precise month-over-month delta calculations)
*   **Image Processing**: [Pillow (PIL)](https://python-pillow.org/)

---

## 🚀 Installation & Local Setup
To run this project locally for development or testing:

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/manjubadami/JewelVerify_Analytics.git
    cd JewelVerify_Analytics
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**
    Create a folder named `.streamlit` and a file inside it named `secrets.toml`:
    ```toml
    GEMINI_API_KEY = "YOUR_API_KEY_HERE"
    ```

5.  **Run the App**
    ```bash
    streamlit run app.py
    ```

---

## ☁️ Deployment Guide (Streamlit Cloud)
To deploy this app for mobile use:
1.  Push your code to **GitHub** (ensure `.streamlit/secrets.toml` is in your `.gitignore`).
2.  Login to [Streamlit Cloud](https://share.streamlit.io/) and click **"New App"**.
3.  Select your repository and branch.
4.  **Critical Step**: Go to **Advanced Settings > Secrets** and paste your API key:
    ```toml
    GEMINI_API_KEY = "AIzaSy..."
    ```
5.  Click **Deploy**.

---

## 📱 Mobile Usage Instructions
The application is optimized for mobile browsers (Safari/Chrome).

1.  **Capture**: Tap the **"Upload Tag Photo"** button. On mobile, this will prompt you to use your **Camera** or **Photo Library**.
2.  **Extraction**: The AI will automatically scan the tag for Net Weight (**Nw**), Value Addition (**VA**), and Stone Amount (**St. Amt**).
3.  **Input**: Enter the current gold rate. If using "Compare Mode," enter the plan start date and historical rate.
4.  **Apply**: Tap **"Apply Calculation"** to generate the breakdown.
5.  **View**: Use the **Tabs** to toggle between "Current" and "Plan" pricing.

---

## 📐 Calculation Logic
The application uses the following formulas for transparency:

*   **Gold Amount**: $Net\ Weight \times Gold\ Rate$
*   **Making Amount**: $Gold\ Amount \times (VA / 100)$
*   **GST**: $(Gold\ Amt + Making\ Amt + Stone\ Amt) \times 0.03$
*   **Plan Benefit**: A sliding scale reduces the VA percentage based on the maturity of the plan:
    *   *< 6 Months*: No VA discount.
    *   *6-9 Months*: Base VA - 16%.
    *   *9-12 Months*: Base VA - 18%.
    *   *> 12 Months*: 0% VA.

---

## 🛡️ Privacy & Security
*   **Data Processing**: Images uploaded are processed via the Google Gemini API. No images are permanently stored on the server.
*   **Secrets Management**: API Keys are managed via Streamlit's encrypted Secrets management system and are never hardcoded.