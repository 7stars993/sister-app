import os
import grpc
from concurrent import futures
from worker_pb2_grpc import WorkerServiceServicer, add_WorkerServiceServicer_to_server
from worker_pb2 import FileStoreResponse, FileRetrieveResponse, FileRemoveResponse


class WorkerNode(WorkerServiceServicer):
    STORAGE_PATH = "./storage_2"

    def __init__(self):
        os.makedirs(self.STORAGE_PATH, exist_ok=True)

    def StoreFile(self, request, context):
        try:
            with open(os.path.join(self.STORAGE_PATH, request.file_name), "wb") as f:
                f.write(request.file_data)
            return FileStoreResponse(status="Success")
        except Exception as e:
            return FileStoreResponse(status="Failed")

    def RetrieveFile(self, request, context):
        try:
            with open(os.path.join(self.STORAGE_PATH, request.file_name), "rb") as f:
                return FileRetrieveResponse(file_data=f.read())
        except FileNotFoundError:
            return FileRetrieveResponse(file_data=b"")

    def RemoveFile(self, request, context):
        try:
            os.remove(os.path.join(self.STORAGE_PATH, request.file_name))
            return FileRemoveResponse(status="Success")
        except FileNotFoundError:
            return FileRemoveResponse(status="Failed")


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_WorkerServiceServicer_to_server(WorkerNode(), server)
    server.add_insecure_port("[::]:50053")  # Change port for multiple workers
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
