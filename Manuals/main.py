from fastapi import FastAPI
from fastapi.routing import APIRoute
from apis.manual import ManualsRouter
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="Manuals")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify: ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("\n--- Registered Routes ---")
    for route in app.routes:
        if isinstance(route, APIRoute):
            methods = ','.join(route.methods)
            print(f"{methods:10s} {route.path}")
    print("-------------------------\n")



# Include the router
app.include_router(ManualsRouter)

@app.get("/ping")
def ping():
    return {"status": "ok"}

