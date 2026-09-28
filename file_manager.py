import streamlit as st
from pathlib import Path
import os
import stat
from datetime import datetime
import pandas as pd        # for CSV preview
from PIL import Image      # for image preview
import zipfile

RECYCLE_BIN = Path("RecycleBin")
RECYCLE_BIN.mkdir(exist_ok=True)


#page setup
st.set_page_config(
    page_title = "File Manager",
    page_icon = "📂",
    layout = "centered",
    initial_sidebar_state = "expanded"
)


#Shows the files that present in folder.
def list_files():
    files = os.listdir()           #get all items in current folder
    only_files = []                #empty list to store files
    for f in files:                #loops throug each item
        if os.path.isfile(f):       #check if it's a file
            only_files.append(f)   #add to list
    return only_files              #return the list of file


# ---  Shows file size, creation date, and last modified date ---
def file_metadata():
    files = os.listdir()
    metadata = []
    for f in files:
        if os.path.isfile(f):
            stats = os.stat(f)

            # Handle creation time in a portable way
            if hasattr(stats,"st_birthtime"):
                created_time = datetime.fromtimestamp(stats.st_birthtime)
            else:
                created_time = datetime.fromtimestamp(stats.st_ctime)

            # Handle creation time 
            modified_time = datetime.fromtimestamp(stats.st_mtime)
            
            metadata.append({
                "Name": f,
                "Size (KB)": round(stats.st_size / 1024, 2),
                "Created": created_time,
                "Modified": modified_time
            })
    return metadata

# --- Search files by extension, keyword, and size ---
def search_files(extension=None, keyword=None, min_size=0, max_size=None):
    results = []
    files = os.listdir()
    for f in files:
        if os.path.isfile(f):
            #Filter by extension
            if extension and not f.endswith(extension):
                continue

            #Get file stats
            stats = os.stat(f)
            size = stats.st_size

            #Filter by size
            if size < min_size:
                continue
            if max_size and size > max_size:
                continue

            #Filter by keyword inside file
            if keyword:
                try:
                    with open(f,"r", encoding="utf-8", errors="ignore") as file:
                        content = file.read()
                        if keyword.lower() not in content.lower():
                            continue
                except Exception:
                    pass

            #Append results
            results.append({
                "Name": f,
                "Size (KB)": round(size / 1024, 2),
                "Modified": datetime.fromtimestamp(stats.st_mtime)
            })

    return results

# --- Preview file content ---
def preview_file(name):
    path = Path(name)
    if path.exists():
        ext = path.suffix.lower()

        # Preview text files
        if ext in [".txt", ".py", ".md"]:
            with open(path,"r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            st.text_area("File content", content, height=200)

        #Preview CSV files
        elif ext == ".csv":
            df = pd.read_csv(path)
            st.dataframe(df)

        #Preview images
        elif ext in [".jpg", ".jpeg", ".png"]:
            img = Image.open(path)
            st.image(img)

        else:
            st.warning("⚠️ Preview not supported for this file type.")
    else:
        st.error(f"❌ File '{name}' does not exist.")

# --- Upload file ---
def upload_file(uploaded_file):
    if uploaded_file is not None:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
    else:
        st.warning("⚠️ No file selected for upload.")

# --- Download file ---
def download_file(name):
    path = Path(name)
    if path.exists():
        with open(path,"rb") as f:
            st.download_button(
                label=f"Download {name}",
                data=f,
                file_name=name
            )
    else:
        st.error(f"❌ File '{name}' does not exists.")
        


# --- To Create file ---
def createfile(name,data):
    path = Path(name)                 #creates path for file
    if not path.exists():             #checks file does not exists
        with open(path,"w") as f:
            f.write(data)             #writes your content
        st.success(f"✅ File '{name}' created successfully!")
    else:
        st.warning(f"⚠️ File '{name}' already exist.")


# --- To Read file ---
def readfile(name):
    path = Path(name)
    if path.exists():
        with open(path,"r") as f:
            content = f.read()          #read the file content
        st.text_area("File content", content, height=200)
    else:
        st.error(f"❌ File '{name}' does not exist.")


# --- To update file ---
def updatefile(name, choice, new_data = None, new_name = None):
    path = Path(name)
    if path.exists():
        
        if choice == "Rename":
            new_path = Path(new_name)
            if not new_path.exists():
                path.rename(new_path)   #Rename the file
                st.success(f"✅ File renamed successfully!")
            else:
                st.warning("⚠️ New file name already exist.")

        elif choice == "Append":
            with open(path,"a") as f:
                f.write("  \n"+new_data)
            st.success("✅ File Appended successfully!")

        elif choice == "Overwrite":
            with open(path,"w") as f:
                f.write("  \n"+new_data)
            st.success("✅ File Overwritten successfully!")
    else:
        st.error(f"❌ File '{name}' does not exist")


# --- To Delete file ---
def deletefile(name):
    path = Path(name)
    if path.exists():
        target = RECYCLE_BIN / path.name
        path.rename(target)
        st.success(f"✅ File '{name}' moved to RecycleBin!")
    else:
        st.error(f"❌ File '{name}' does not exist.")


# --- Restore file from RecycleBin ---
def restore_file(name):
    path = RECYCLE_BIN / name
    if path.exists():
        target = Path(name)
        path.rename(target)    
        st.success(f"✅ File '{name}' restored successfully!")
    else:
        st.error(f"❌ File '{name}' not found in RecycleBin.")


# --- Permanently delete file from RecycleBin ---
def permanent_delete(filename):
    path = RECYCLE_BIN / filename
    if path.exists():
        try:
            path.unlink()    
            st.success(f"✅ File '{filename}' Permanently deleted!")
        except Exception as e:
            st.error(f"❌ Could not delete '{filename}': {e}")
    else:
        st.error(f"❌ File '{filename}' not found in RecycleBin.")    


# --- Compress selected files into a Zip with optional deletion ---
def compress_files(file_list, zip_name, delete_originals=False):
    if file_list and zip_name:
        added_any = False   # flag to track if any file was added
        
        with zipfile.ZipFile(zip_name, "w") as zipf:
            for f in file_list:
                file_path = Path(f)

                #Check if file exists
                if file_path.exists():
                    zipf.write(f)
                    st.info(f"Added '{f}' to {zip_name}")
                    added_any = True

                    #Delete originals only if user selected the option
                    if delete_originals:
                        try:
                            file_path.unlink()
                            st.warning(f"⚠️ Original file '{f}' deleted after compression.")
                        except Exception as e:
                            st.error(f"❌ Could not delete '{f}': {e}.")
                else:
                    st.warning(f"⚠️ File '{f}' does not exists and was skipped")
        
        #only show success if something was actually added
        if added_any:
            st.success(f"✅ Compression finished. Archive '{zip_name}' created!")
        else:
            # remove empty archive if created
            Path(zip_name).unlink(missing_ok=True)
            st.error("❌ No valid files found. Zip archive was not created.")
    else:
        st.error("❌ Please provide valid file names and a zip name.")       


# --- Extract files from a Zip ---
def extract_zip(zip_name, extract_to="Extracted", delete_zip=False):
    path = Path(zip_name)
    if path.exists():
        target_folder = Path(extract_to)
        target_folder.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(path, "r") as zipf:
            zipf.extractall(target_folder)
        
        st.success(f"✅ Files extracted to '{extract_to}' successfully!")

        #Delete zip only if user selected the option
        if delete_zip:
            try:
                path.unlink()
                st.warning(f"⚠️ Archive '{zip_name}' deleted after extraction.")
            except Exception as e:
                st.error(f"❌ Could not delete archive '{zip_name}': {e}")
    else:
        st.error(f"❌ Zip file '{zip_name}' does not exists.")

# --- View file permissions ---
def view_permissions(name):
    path = Path(name)
    if path.exists():
        mode = path.stat().st_mode
        perms = {
            "Read": bool(mode & stat.S_IRUSR),
            "Write": bool(mode & stat.S_IWUSR),
            "Execute": bool(mode & stat.S_IXUSR) 
        }
        st.info(f"ℹ️ Permissions for '{name}': {perms}")
    else:
        st.error(f"❌ File '{name}' does not exists.")

# --- Change file permissions ---
def change_permissions(name, read, write, execute):
    path = Path(name)
    if path.exists():
        mode = 0
        if read:
            mode |= stat.S_IRUSR
        if write:
            mode |= stat.S_IWUSR
        if execute:
            mode |= stat.S_IXUSR

        try:
            os.chmod(path, mode)
            st.success(f"✅ Permissions updated for '{name}'!")
        except Exception as e:
            st.error(f"❌ Could not change permissions: {e}")
    else:
        st.error(f"❌ File '{name}' does not exist.")



# -----Streamlit fronted------
st.title("📊 File Manager Dashboard")
st.write("Manage, organize, and analyze your files with ease.")

#Separate counts for files and folders
all_items = os.listdir(".")
files_only = [f for f in all_items if os.path.isfile(f)]
folders_only = [f for f in all_items if os.path.isdir(f)]

total_files = len(files_only)
total_folders = len(folders_only)        

# calculates the total storage used by those files in KB.
total_file_size = sum(os.path.getsize(f) for f in files_only) // 1024   # In KB

#Calculate folder size(KB) recursively
def get_folder_size(folder):
    size = 0
    for root, dirs, files in os.walk(folder):
        for f in files:
            fp = os.path.join(root, f)
            if os.path.isfile(fp):
                size += os.path.getsize(fp)
    return size

total_folder_size = sum(get_folder_size(f) for f in folders_only) // 1024

#two coloumn layout
col1, col2 = st.columns(2)

#Files column
col1.metric("📄 Total Files", total_files)
col1.metric("💾 Total File Size (KB)", total_file_size)

#Folders column
col2.metric("📁 Total Folders", total_folders)
col2.metric("📁 Total Folder Size (KB)", total_folder_size)


# --- Sidebar Navigation ---
st.sidebar.header("📂 File Manager Menu")

menu = st.sidebar.selectbox(
    "📌 Select Operation",
    [
        "— 📄 Basic Operations —",
        "Create",
        "Read",
        "Update",
        "Delete",
        "— 🔧 Advanced Tools —",
        "Metadata",
        "Search",
        "Preview",
        "— 🗄️ File Management —",
        "Upload/Download",
        "Recycle Bin",
        "Compression",
        "Permissions"
    ]
)

#Ignore section header when assigning
if menu.startswith("—"):
    menu = None

#Show active section highlight
if menu:
    st.sidebar.markdown(f"🎯 **Active Section:** {menu}")

#Footer
st.sidebar.markdown("---")
st.sidebar.caption("© 2026 Vityarthi Project | Version 1.0")



#Show available files
st.sidebar.markdown("### Current Files")
files = list_files()

if files:
    st.sidebar.write(files)
else:
    st.sidebar.write("No files yet.")

if menu == "Create":
    st.header("Create a New File")
    filename = st.text_input("Enter file name")
    content = st.text_area("Enter file content")
    if st.button("Create File"):
        createfile(filename, content)


elif menu == "Read":
    st.header("Read a File")
    filename = st.text_input("Enter file name")
    if st.button("Read File"):
        readfile(filename)


elif menu == "Update":
    st.header("✏️ Update a File")
    filename = st.text_input("Enter file name")

    #Tabs for different update operations
    tab1, tab2, tab3 = st.tabs(["✏️ Rename", "➕ Append", "📝 Overwrite"])

    with tab1:
        new_name = st.text_input("Enter new file name")
        if st.button("Rename File"):
            updatefile(filename, "Rename", new_name=new_name)
    with tab2:
        new_data = st.text_area("Enter content to append")
        if st.button("Append File"):
            updatefile(filename, "Append", new_data=new_data)
    with tab3:
        new_data = st.text_area("Enter new content (overwrite)")
        if st.button("Overwrite File"):
            updatefile(filename, "Overwrite", new_data=new_data)


elif menu == "Delete":
    st.header("Delete a File")
    filename = st.text_input("Enter file name")
    if st.button("Delete File"):
        deletefile(filename)
    

elif menu == "Metadata":
    st.header("📊 File Metadata Viewer")
    data = file_metadata()
    if data:
        st.table(data)
    else:
        st.info("No files found.")


elif menu == "Search":
    st.header("🔍 File Search Tool")

    extension = st.text_input("Filter by extension (e.g., .txt, .py):")
    keyword = st.text_input("Search keyword inside files:")
    min_size = st.number_input("Minimum file size (bytes):", min_value=0)
    max_size = st.number_input("Maximum file size (bytes):", min_value=0)

    if st.button("Search"):
        data = search_files(extension if extension else None,
                            keyword if keyword else None,
                            min_size,
                            max_size if max_size > 0 else None )
        if data:
            st.table(data)
        else:
            st.warning("⚠️ No files found matching your criteria.")


elif menu == "Preview":
    st.header("👀 File Preview")
    filename = st.text_input("Enter file name to preview")
    if st.button("Preview File"):
        preview_file(filename)


elif menu == "Upload/Download":
    st.header("📤 Upload & 📥 Download Files")

    #Upload section
    uploaded_file = st.file_uploader("Choose a file to upload")
    if st.button("Upload File"):
        upload_file(uploaded_file)

    # Download section
    filename = st.text_input("Enter file name to download")
    if st.button("Download File"):
        download_file(filename)


elif menu == "Recycle Bin":
    st.header("🗑️ Recycle Bin Manager")

    #Show files currently in RecycleBin
    recycle_files = os.listdir(RECYCLE_BIN)
    if recycle_files:
        st.write("Files in RecycleBin", recycle_files)
    else:
        st.info("ℹ️ RecycleBin is empty.")

    #Tabs for restore and permanent delete
    tab1, tab2 = st.tabs(["♻️ Restore File", "❌ Permanent Delete"])

    with tab1:
        #Restore section
        restore_name = st.text_input("Enter file name to restore")
        if st.button("Restore File"):
            restore_file(restore_name)

    with tab2:
        #Permanent delete section
        delete_name = st.text_input("Enter file name to permanently delete")
        if  st.button("Permanently Delete File"):
            permanent_delete(delete_name)


elif menu == "Compression":
    st.header("📦 File Compression Tool")

    # Tabs for compression and extraction
    tab1, tab2 = st.tabs(["📦 Compress Files", "📂 Extract Zip"])
    
    # --- Compress Files ---
    with tab1:
        files_to_compress = st.text_input("Enter file names to compress (comma separated)")
        zip_name = st.text_input("Enter zip file name (eg., archive.zip)")
        delete_originals = st.checkbox("Delete original files after compression?")
        if st.button("Compress Files"):
            raw_files = files_to_compress.split(",")
            file_list = [f.strip() for f in raw_files if f.strip()]
            compress_files(file_list, zip_name, delete_originals)

    # --- Extract Zip ---
    with tab2:
        zip_file = st.text_input("Enter zip file name to extract")
        extract_folder = st.text_input("Enter folder name to extract into", value="Extracted")
        delete_zip = st.checkbox("Delete zip file after extraction?")
        if st.button("Extract Zip"):
            extract_zip(zip_file, extract_folder, delete_zip)

elif menu == "Permissions":
    st.header("🔐 File Permissions Manager")
    filename = st.text_input("Enter file name")

    #Tabs for viewing and changing permissions 
    tab1, tab2 = st.tabs(["👀 View Permissions", "✏️ Change Permissions"])

    with tab1:
        if st.button("View Permissions"):
            view_permissions(filename)

    with tab2:
        st.subheader("Change Permissions")
        read = st.checkbox("Read")
        write = st.checkbox("Write")
        execute = st.checkbox("Execute")
        if st.button("Update Permissions"):
            change_permissions(filename, read, write, execute)
    

