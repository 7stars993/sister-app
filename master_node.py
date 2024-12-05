import grpc
from concurrent import futures
from master_pb2_grpc import MasterServiceServicer, add_MasterServiceServicer_to_server
from master_pb2 import FileUploadResponse, FileDownloadResponse, FileDeleteResponse, ListFilesResponse
from worker_pb2_grpc import WorkerServiceStub
from worker_pb2 import FileStoreRequest, FileRetrieveRequest, FileRemoveRequest


class MasterNode(MasterServiceServicer):
    def __init__(self):
        self.metadata = {}  # Metadata file (file_name -> node address)
        self.worker_nodes = ["localhost:50052", "localhost:50053", "localhost:50054", "localhost:50055"]  # List of worker nodes
        self.current_node = 0

    def get_next_node(self):
        node = self.worker_nodes[self.current_node]
        self.current_node = (self.current_node + 1) % len(self.worker_nodes)
        return node

    def UploadFile(self, request, context):
        worker_address = self.get_next_node()
        channel = grpc.insecure_channel(worker_address)
        worker_stub = WorkerServiceStub(channel)

        worker_request = FileStoreRequest(file_name=request.file_name, file_data=request.file_data)
        worker_response = worker_stub.StoreFile(worker_request)

        if worker_response.status == "Success":
            self.metadata[request.file_name] = worker_address
            return FileUploadResponse(status="Success", message="File uploaded successfully.")
        return FileUploadResponse(status="Failed", message="File upload failed.")

    def DownloadFile(self, request, context):
        if request.file_name not in self.metadata:
            return FileDownloadResponse(file_data=b"")

        worker_address = self.metadata[request.file_name]
        channel = grpc.insecure_channel(worker_address)
        worker_stub = WorkerServiceStub(channel)

        worker_request = FileRetrieveRequest(file_name=request.file_name)
        worker_response = worker_stub.RetrieveFile(worker_request)
        return FileDownloadResponse(file_data=worker_response.file_data)

    def DeleteFile(self, request, context):
        if request.file_name not in self.metadata:
            return FileDeleteResponse(status="Failed", message="File not found.")

        worker_address = self.metadata.pop(request.file_name)
        channel = grpc.insecure_channel(worker_address)
        worker_stub = WorkerServiceStub(channel)

        worker_request = FileRemoveRequest(file_name=request.file_name)
        worker_response = worker_stub.RemoveFile(worker_request)
        return FileDeleteResponse(status=worker_response.status, message="File deleted successfully.")

    def ListFiles(self, request, context):
        return ListFilesResponse(file_names=list(self.metadata.keys()))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MasterServiceServicer_to_server(MasterNode(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
