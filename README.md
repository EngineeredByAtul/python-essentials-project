# 📂 Project Title
**File Manager Dashboard using Streamlit**

---

## 📖 Overview
The **File Manager Dashboard** is a web‑based application built with **Python and Streamlit**.  
It provides a dark‑themed interactive interface to manage files and folders.  
Users can perform everyday file operations (Create, Read, Update, Delete) along with advanced tools like Metadata Viewer, Search, Preview, Upload/Download, Recycle Bin, Compression, and Permissions — all in one place.

---

## 🚀 Features
- Create, read, update, and delete files safely.
- Two‑step deletion system (Recycle Bin + Permanent Delete).
- File metadata viewer (size, creation time, modification time, permissions).
- Search tool with filters (extension, keyword, size).
- Preview tool for text, CSV, and images.
- Upload and download files directly from the dashboard.
- Compress multiple files into ZIP archives and extract them.
- View and change file permissions.
- Dashboard metrics: total files, total folders, folder size.

---

## 🛠️ Technologies / Tools Used
- **Python 3.10+**
- **Streamlit** (UI framework)
- **Pathlib / os / stat** (file handling)
- **Pandas** (CSV preview)
- **PIL (Pillow)** (image preview)
- **Zipfile** (compression)

---

## ⚙️ Steps to Install & Run the Project
**Step 1:** Install dependencies  
```bash
   pip install streamlit pandas
```

---

## 🧪 Instructions for Testing
- **Create File:** Enter a file name and content, then verify it appears in the directory.  
- **Read File:** Select a file and check if its content displays correctly.  
- **Update File:** Try renaming, appending, or overwriting a file and confirm changes.  
- **Delete File:** Delete a file and verify it moves to the Recycle Bin.  
- **Restore File:** Restore a file from the Recycle Bin and check if it reappears.  
- **Permanent Delete:** Permanently delete a file and confirm it is removed.  
- **Metadata Viewer:** Select a file and check size, timestamps, and permissions.  
- **Search Tool:** Search by extension, keyword, or size range to locate files.  
- **Preview Tool:** Preview text, CSV, or image files directly in the dashboard.  
- **Upload/Download:** Upload a file from your system or download an existing file.  
- **Compression:** Compress multiple files into a ZIP archive and extract them.  
- **Permissions:** View and change file permissions using numeric modes.

---

## ⚠️ Common Errors & Solutions
**Error 1: Windows Security — Smart App Control has blocked part of this app**  
- Solution: Go to **Windows Security → Smart App Control** and turn it off. Then try running the code again.  

**Error 2: ImportError: DLL load failed**  
- Solution:  
  Step:1. Uninstall Streamlit and Pandas:  
     ```bash
     pip uninstall streamlit
     pip uninstall pandas
     ```  
  Step:2. Create a virtual environment and reinstall:  

   **Windows Users:**  
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install streamlit pandas
   ```
   **Mac Users:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install streamlit pandas
  ```

  
