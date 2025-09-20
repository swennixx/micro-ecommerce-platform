import asyncio
from concurrent import futures
import grpc
from . import products_pb2, products_pb2_grpc, crud, deps
from .database import SessionLocal

class ProductsServicer(products_pb2_grpc.ProductsServicer):
    async def GetProduct(self, request, context):
        async with SessionLocal() as db:
            product = await crud.get_product(db, request.id)
            if not product:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details('Product not found')
                return products_pb2.ProductReply()
            return products_pb2.ProductReply(
                id=product.id,
                name=product.name,
                description=product.description or "",
                price=product.price,
                stock=product.stock
            )

    async def ListProducts(self, request, context):
        async with SessionLocal() as db:
            products = await crud.get_products(db, request.skip, request.limit)
            return products_pb2.ListProductsReply(
                products=[products_pb2.ProductReply(
                    id=p.id,
                    name=p.name,
                    description=p.description or "",
                    price=p.price,
                    stock=p.stock
                ) for p in products]
            )

def serve():
    server = grpc.aio.server()
    products_pb2_grpc.add_ProductsServicer_to_server(ProductsServicer(), server)
    server.add_insecure_port('[::]:50051')
    return server

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    grpc_server = serve()
    loop.run_until_complete(grpc_server.start())
    print("gRPC server started on port 50051")
    loop.run_until_complete(grpc_server.wait_for_termination())
