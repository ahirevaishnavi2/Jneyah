
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from contextlib import asynccontextmanager
import os
import uvicorn
from pathlib import Path
from citizen_mode.citizen_controller import router as citizen_router
from citizen_mode import citizen_controller
from datetime import datetime
from database.db_connection import Database
from scan import scan_controller
from auth.auth_controller import router as auth_router
from scan.scan_controller import router as scan_router

# Directories
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# Ensure uploads folder exists
os.makedirs("uploads", exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting up Ingredient Safety Intelligence Platform...")
    Database.connect()
    print("✅ Database connected")
    yield
    print("🛑 Shutting down...")
    Database.disconnect()
    print("✅ Database disconnected")

app = FastAPI(
    title="Ingredient Safety Intelligence Platform",
    description="Cross-industry platform for ingredient safety analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS (Safe for frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # keep like before since frontend already connected
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static folders
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# IMPORTANT: No prefix added (so frontend keeps working)
app.include_router(auth_router)
app.include_router(scan_router)
app.include_router(citizen_router)
app.include_router(scan_controller.router)
app.include_router(citizen_controller.router)

# ================= LANDING PAGE =================

@app.get("/")
async def serve_landing():
    file_path = FRONTEND_DIR / "LandingPage.html"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return JSONResponse({"error": "LandingPage.html not found"}, status_code=404)

# ================= CITIZEN =================

@app.get("/citizen/{page_name}")
async def serve_citizen_page(page_name: str):

    # SECURITY FIX (properly indented inside function)
    if ".." in page_name or "/" in page_name or "\\" in page_name:
        return JSONResponse({"error": "Invalid page name"}, status_code=400)

    if page_name.endswith(".html"):
        page_name = page_name[:-5]

    file_path = FRONTEND_DIR / "citizen" / f"{page_name}.html"

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())

    return JSONResponse({"error": f"Citizen page '{page_name}' not found"}, status_code=404)

# ================= EXPERT =================

@app.get("/expert/{page_name}")
async def serve_expert_page(page_name: str):

    if ".." in page_name or "/" in page_name or "\\" in page_name:
        return JSONResponse({"error": "Invalid page name"}, status_code=400)

    if page_name.endswith(".html"):
        page_name = page_name[:-5]

    file_path = FRONTEND_DIR / "expert" / f"{page_name}.html"

    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())

    return JSONResponse({"error": f"Expert page '{page_name}' not found"}, status_code=404)

# ================= HEALTH =================

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# ================= RUN =================

if __name__ == "__main__":
    import uvicorn

    print("\n🚀 Server running at http://localhost:8000\n")

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import HTMLResponse, JSONResponse
# from contextlib import asynccontextmanager
# import os
# from pathlib import Path

# from database.db_connection import Database
# from auth.auth_controller import router as auth_router
# from scan.scan_controller import router as scan_router  # ADD THIS LINE

# # Get the base directory
# BASE_DIR = Path(__file__).resolve().parent
# FRONTEND_DIR = BASE_DIR.parent / "frontend"

# print(f"📁 Frontend directory: {FRONTEND_DIR}")
# print(f"📁 Citizen directory exists: {(FRONTEND_DIR / 'citizen').exists()}")
# print(f"📁 Expert directory exists: {(FRONTEND_DIR / 'expert').exists()}")

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     print("🚀 Starting up Ingredient Safety Intelligence Platform...")
#     Database.connect()
#     print("✅ Database connected")
#     yield
#     # Shutdown
#     print("🛑 Shutting down...")
#     Database.disconnect()
#     print("✅ Database disconnected")

# app = FastAPI(
#     title="Ingredient Safety Intelligence Platform",
#     description="Cross-industry platform for ingredient safety analysis",
#     version="1.0.0",
#     lifespan=lifespan
# )

# # Configure CORS
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:8000"],
#     allow_credentials=True,

#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Mount static files (frontend)
# os.makedirs("uploads", exist_ok=True)

# app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")  # ADD THIS LINE
# app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# # Include API routers FIRST (before catch-all route)
# app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
# app.include_router(scan_router, prefix="/api/scan", tags=["Scan"])

# # ============== HTML ROUTES ==============

# @app.get("/")
# async def serve_landing():
#     """Serve the landing page"""
#     file_path = FRONTEND_DIR / "LandingPage.html"
#     if file_path.exists():
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 return HTMLResponse(f.read())
#         except Exception as e:
#             return JSONResponse(
#                 {"error": f"Error reading landing page: {str(e)}"},
#                 status_code=500
#             )
#     else:
#         return JSONResponse(
#             {"error": f"LandingPage.html not found at {file_path}"},
#             status_code=404
#         )

# if ".." in page_name or "/" in page_name or "\\" in page_name:
#     return JSONResponse({"error": "Invalid page name"}, status_code=400)

# @app.get("/citizen/{page_name}")
# async def serve_citizen_page(page_name: str):
#     """Serve citizen HTML pages"""
#     print(f"📄 Serving citizen page: {page_name}")
    
#     # Remove .html if present
#     if page_name.endswith('.html'):
#         page_name = page_name[:-5]
    
#     # Try with .html extension
#     file_path = FRONTEND_DIR / "citizen" / f"{page_name}.html"
    
#     if file_path.exists():
#         print(f"✅ Found file at: {file_path}")
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 return HTMLResponse(f.read())
#         except Exception as e:
#             print(f"❌ Error reading file: {e}")
#             return JSONResponse(
#                 {"error": f"Error reading file: {str(e)}"},
#                 status_code=500
#             )
#     else:
#         print(f"❌ File not found at: {file_path}")
#         # Try alternative paths
#         alt_paths = [
#             FRONTEND_DIR / "citizen" / page_name,  # Without .html
#             FRONTEND_DIR / f"citizen/{page_name}.html",  # Alternative path
#             FRONTEND_DIR / page_name,  # Direct in frontend
#             FRONTEND_DIR / f"{page_name}.html"  # With .html in frontend
#         ]
        
#         for alt_path in alt_paths:
#             if alt_path.exists():
#                 print(f"✅ Found alternative path: {alt_path}")
#                 try:
#                     with open(alt_path, "r", encoding="utf-8") as f:
#                         return HTMLResponse(f.read())
#                 except Exception as e:
#                     print(f"❌ Error reading alternative file: {e}")
        
#         # List available files for debugging
#         citizen_dir = FRONTEND_DIR / "citizen"
#         if citizen_dir.exists():
#             available_files = [f.name for f in citizen_dir.iterdir() if f.is_file()]
#             print(f"📂 Available files in citizen directory: {available_files}")
        
#         return JSONResponse({
#             "error": f"Citizen page '{page_name}' not found",
#             "searched_path": str(file_path),
#             "available_files": available_files if citizen_dir.exists() else "citizen directory not found"
#         }, status_code=404)

# if ".." in page_name or "/" in page_name or "\\" in page_name:
#     return JSONResponse({"error": "Invalid page name"}, status_code=400)

# @app.get("/expert/{page_name}")
# async def serve_expert_page(page_name: str):
#     """Serve expert HTML pages"""
#     # Remove .html if present
#     if page_name.endswith('.html'):
#         page_name = page_name[:-5]
    
#     file_path = FRONTEND_DIR / "expert" / f"{page_name}.html"
    
#     if file_path.exists():
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 return HTMLResponse(f.read())
#         except Exception as e:
#             return JSONResponse(
#                 {"error": f"Error reading file: {str(e)}"},
#                 status_code=500
#             )
#     else:
#         # Try alternative path
#         alt_path = FRONTEND_DIR / "expert" / page_name
#         if alt_path.exists():
#             try:
#                 with open(alt_path, "r", encoding="utf-8") as f:
#                     return HTMLResponse(f.read())
#             except Exception as e:
#                 return JSONResponse(
#                     {"error": f"Error reading file: {str(e)}"},
#                     status_code=500
#                 )
        
#         return JSONResponse({"error": f"Expert page '{page_name}' not found"}, status_code=404)

# # ============== DIRECT FILE ROUTES ==============

# @app.get("/citizen/CitizenHome.html")
# async def direct_citizen_home():
#     """Direct route for CitizenHome.html"""
#     return await serve_citizen_page("CitizenHome")

# @app.get("/citizen/Profile.html")
# async def direct_citizen_profile():
#     """Direct route for Profile.html"""
#     return await serve_citizen_page("Profile")

# @app.get("/citizen/UploadAndKnow.html")  # ADD THIS LINE
# async def direct_upload_and_know():
#     """Direct route for UploadAndKnow.html"""
#     return await serve_citizen_page("UploadAndKnow")

# @app.get("/expert/ExpertHome.html")
# async def direct_expert_home():
#     """Direct route for ExpertHome.html"""
#     return await serve_expert_page("ExpertHome")

# # ============== API HEALTH CHECK ==============

# @app.get("/api/health")
# async def health_check():
#     return {"status": "healthy", "service": "ingredient-safety-platform"}

# @app.get("/api/test")
# async def test_endpoint():
#     return {"message": "API is working", "timestamp": "now"}

# # ============== CATCH-ALL ROUTE (LAST!) ==============

# @app.get("/{full_path:path}")
# async def catch_all(full_path: str):
#     """Catch-all route for other paths"""
#     print(f"🌐 Catch-all route called for: {full_path}")
    
#     # Skip API routes
#     if full_path.startswith("api/"):
#         return JSONResponse({"error": f"API endpoint not found: {full_path}"}, status_code=404)
    
#     # Try to serve as HTML file
#     if not full_path.endswith('.html'):
#         html_path = FRONTEND_DIR / f"{full_path}.html"
#         if html_path.exists():
#             try:
#                 with open(html_path, "r", encoding="utf-8") as f:
#                     return HTMLResponse(f.read())
#             except Exception as e:
#                 pass
    
#     # Try as direct file
#     file_path = FRONTEND_DIR / full_path
#     if file_path.exists() and file_path.is_file():
#         try:
#             with open(file_path, "r", encoding="utf-8") as f:
#                 return HTMLResponse(f.read())
#         except Exception as e:
#             return JSONResponse(
#                 {"error": f"Error reading file: {str(e)}"},
#                 status_code=500
#             )
    
#     # Check if it's a citizen/expert page without the prefix
#     if full_path.endswith('.html'):
#         page_name = full_path[:-5]
#         # Try citizen
#         citizen_path = FRONTEND_DIR / "citizen" / f"{page_name}.html"
#         if citizen_path.exists():
#             return await serve_citizen_page(page_name)
        
#         # Try expert
#         expert_path = FRONTEND_DIR / "expert" / f"{page_name}.html"
#         if expert_path.exists():
#             return await serve_expert_page(page_name)
    
#     return JSONResponse({
#         "error": f"Page not found: {full_path}",
#         "note": "Make sure the HTML file exists in the frontend folder"
#     }, status_code=404)

# # Include API routers
# app.include_router(auth_router, prefix="/api/auth", tags=["Auth"])
# app.include_router(scan_router, prefix="/api/scan", tags=["Scan"])

# if __name__ == "__main__":
#     import uvicorn
    
#     print("\n" + "="*60)
#     print("🚀 INGREDIENT SAFETY INTELLIGENCE PLATFORM")
#     print("="*60)
#     print(f"📁 Serving from: {FRONTEND_DIR}")
#     print("🌐 Server running at: http://localhost:8000")
#     print("🏠 Landing page: http://localhost:8000/")
#     print("👤 Citizen Home: http://localhost:8000/citizen/CitizenHome")
#     print("📸 Upload & Know: http://localhost:8000/citizen/UploadAndKnow")  # ADD THIS LINE
#     print("👤 Citizen Profile: http://localhost:8000/citizen/Profile")
#     print("🔬 Expert Home: http://localhost:8000/expert/ExpertHome")
#     print("📊 API: http://localhost:8000/api")
#     print("📚 API Docs: http://localhost:8000/docs")
#     print("="*60 + "\n")
    
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)