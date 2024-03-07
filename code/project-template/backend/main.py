
import uvicorn # web server
import os

if __name__ == "__main__":
    # we just call the run method to start the API
    uvicorn.run(
        "api:app", 
        host="0.0.0.0", 
        reload=True, 
        port=int(os.environ.get("PORT", 8080))
    )



