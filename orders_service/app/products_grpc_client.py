import grpc
from . import products_pb2, products_pb2_grpc
import asyncio

class ProductsGrpcClient:
    def __init__(self, host="products_service", port=50051):
        self.target = f"{host}:{port}"

    async def get_product(self, product_id: int):
        async with grpc.aio.insecure_channel(self.target) as channel:
            stub = products_pb2_grpc.ProductsStub(channel)
            request = products_pb2.ProductRequest(id=product_id)
            response = await stub.GetProduct(request)
            return response

    async def list_products(self, skip=0, limit=100):
        async with grpc.aio.insecure_channel(self.target) as channel:
            stub = products_pb2_grpc.ProductsStub(channel)
            request = products_pb2.ListProductsRequest(skip=skip, limit=limit)
            response = await stub.ListProducts(request)
            return response.products

# Пример использования:
# client = ProductsGrpcClient()
# asyncio.run(client.get_product(1))
