import uvicorn
import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Run the application
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)