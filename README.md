# 🏛️ eCourts Cause List Scraper (Semi-Automatic)

This Python script automates data extraction from the **eCourts (India)** website’s **Cause List** page.  
It helps users quickly collect court case details such as **Case Number, Parties, Purpose, and Advocate** — while letting you **manually handle the CAPTCHA** for compliance and accuracy.

---

## 🚀 Features

✅ Automatically opens the eCourts website  
✅ You manually fill form details (State, District, Court, Date, Captcha, etc.)  
✅ Script waits until you confirm that results are visible  
✅ Extracts all cause list entries from the loaded page  
✅ Saves results in both **JSON** and **TXT** formats  
✅ Debug screenshot saved if no data found  
✅ Works with any court complex in India

---

## 🧠 How It Works

1. Run the script — Chrome browser opens automatically.  
2. Manually complete the form and CAPTCHA on the eCourts website.  
3. Once the cause list table is visible, **return to the terminal** and press **Enter**.  
4. Script extracts data and saves it locally.

---

## 🧩 Installation

### 1️⃣ Install Python Packages
Make sure you have **Python 3.8+** and **Google Chrome** installed.  
Then, in your terminal or command prompt, run:

```bash
pip install selenium webdriver-manager
