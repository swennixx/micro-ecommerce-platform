import uvicorn
from fastapi import FastAPI
from ariadne import QueryType, make_executable_schema, gql
from ariadne.asgi import GraphQL
import grpc
import sys
sys.path.append("../../products_service/app")
from products_pb2 import ProductRequest, ListProductsRequest
from products_pb2_grpc import ProductsStub

# GraphQL type definitions

type_defs = gql('''
    type Product {
        id: Int!
        name: String!
        description: String
        price: Float!
        stock: Int!
    }
    type Query {
        product(id: Int!): Product
        products(skip: Int, limit: Int): [Product!]!
    }
''')

query = QueryType()

@query.field("product")
def resolve_product(*_, id):
    with grpc.insecure_channel("products_service:50051") as channel:
        stub = ProductsStub(channel)
        req = ProductRequest(id=id)
        resp = stub.GetProduct(req)
        if resp.id == 0:
            return None
        return {
            "id": resp.id,
            "name": resp.name,
            "description": resp.description,
            "price": resp.price,
            "stock": resp.stock
        }

@query.field("products")
def resolve_products(*_, skip=0, limit=100):
    with grpc.insecure_channel("products_service:50051") as channel:
        stub = ProductsStub(channel)
        req = ListProductsRequest(skip=skip, limit=limit)
        resp = stub.ListProducts(req)
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "stock": p.stock
            } for p in resp.products
        ]

schema = make_executable_schema(type_defs, query)

app = FastAPI()
app.mount("/graphql", GraphQL(schema, debug=True))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
