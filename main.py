from fastapi import FastAPI
from apis.sitera import siterouter
from apis.processra import processrouter

app = FastAPI(title="Risk Assessment")

# Include the router
app.include_router(siterouter)
app.include_router(processrouter)



