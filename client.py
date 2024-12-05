import streamlit as st
import grpc
from master_pb2_grpc import MasterServiceStub
from master_pb2 import FileUploadRequest, FileDownloadRequest, FileDeleteRequest, ListFilesRequest

# Koneksi ke Master Node
channel = grpc.insecure_channel("localhost:50051")
stub = MasterServiceStub(channel)

st.title("Distributed Cloud Storage System")

# **1. Upload Multiple Files**
st.header("Upload Files")
uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True)

if st.button("Upload All"):
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_data = uploaded_file.read()
            request = FileUploadRequest(file_name=file_name, file_data=file_data)
            response = stub.UploadFile(request)
            if response.status == "Success":
                st.success(f"Uploaded {file_name} successfully!")
            else:
                st.error(f"Failed to upload {file_name}.")
    else:
        st.error("No files selected. Please upload files.")

# **2. List Files**
st.header("List Files")
if st.button("Show Files"):
    request = ListFilesRequest()
    response = stub.ListFiles(request)
    st.write("Files in storage:")
    for file_name in response.file_names:
        st.write(f"- {file_name}")

# **3. Download File**
st.header("Download File")
file_to_download = st.text_input("Enter the file name to download:")
if st.button("Download"):
    if file_to_download:
        request = FileDownloadRequest(file_name=file_to_download)
        response = stub.DownloadFile(request)
        if response.file_data:
            st.download_button(label="Download File", data=response.file_data, file_name=file_to_download)
        else:
            st.error("File not found.")

# **4. Delete File**
st.header("Delete File")
file_to_delete = st.text_input("Enter the file name to delete:")
if st.button("Delete"):
    if file_to_delete:
        request = FileDeleteRequest(file_name=file_to_delete)
        response = stub.DeleteFile(request)
        st.success(response.message)
    else:
        st.error("Please enter a file name.")
