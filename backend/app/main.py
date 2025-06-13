from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from elasticsearch import AsyncElasticsearch
import os
from .logger import get_logger
from fastapi import HTTPException
from datetime import datetime

# Get logger instance
logger = get_logger('main')

app = FastAPI(
    title="Forum Search API",
    description="API for searching and managing forum posts with Elasticsearch",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:4321"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Elasticsearch client
es = AsyncElasticsearch(
    hosts=[os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")],
    verify_certs=os.getenv("ELASTICSEARCH_VERIFY_CERTS", "true").lower() == "true"
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the application...")
    # Initialize Elasticsearch indices
    await create_indices()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the application...")
    await es.close()
    logger.info("Application shutdown complete")

async def create_indices():
    logger.info("Checking and creating Elasticsearch indices...")
    # Create posts index with mappings
    if not await es.indices.exists(index="posts"):
        logger.info("Creating 'posts' index...")
        await es.indices.create(
            index="posts",
            mappings={
                "properties": {
                    "title": {"type": "text", "analyzer": "standard"},
                    "content": {"type": "text", "analyzer": "standard"},
                    "tags": {"type": "keyword"},
                    "created_at": {"type": "date"},
                    "updated_at": {"type": "date"}
                }
            }
        )
        logger.info("'posts' index created successfully")
    else:
        logger.info("'posts' index already exists")

@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "Welcome to the Forum Search API"}

# --- Debug Endpoints (Conditionally Enabled) ---
if os.getenv("ENABLE_DEBUG_ENDPOINTS", "false").lower() == "true":
    logger.info("Debug endpoints are ENABLED. Ensure this is not enabled in production!")

    @app.get("/debug/index-stats")
    async def get_index_stats():
        logger.info("Fetching index statistics")
        try:
            stats = await es.indices.stats(index="posts")
            count = await es.count(index="posts")
            logger.info(f"Index stats: {stats}")
            logger.info(f"Document count: {count}")
            return {
                "stats": stats,
                "count": count
            }
        except Exception as e:
            logger.error(f"Error fetching index stats: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to fetch index statistics")

    @app.get("/debug/get-post/{post_id}")
    async def debug_get_post(post_id: str):
        logger.info(f"[DEBUG] Fetching raw post data for ID: {post_id}")
        try:
            response = await es.get(index="posts", id=post_id)
            logger.info(f"[DEBUG] Raw post data retrieved for ID: {post_id}")
            return response["_source"]
        except Exception as e:
            logger.error(f"[DEBUG] Error fetching raw post data {post_id}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=404, detail="Post not found for debugging")

    @app.get("/debug/create-test-post")
    async def create_test_post():
        logger.info("Creating test post")
        try:
            test_post = {
                "title": "Test Post",
                "content": "This is a test post for debugging search functionality.",
                "tags": ["test".lower(), "debug".lower()],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            response = await es.index(
                index="posts",
                document=test_post
            )
            logger.info(f"Test post created with ID: {response['_id']}")
            return {"message": "Test post created", "id": response["_id"]}
        except Exception as e:
            logger.error(f"Error creating test post: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to create test post")
else:
    logger.warning("Debug endpoints are DISABLED. Set ENABLE_DEBUG_ENDPOINTS=true to enable them.")

# Import and include routers
from app.routers import posts, search, tags

app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(search.router, prefix="/api/search", tags=["search"])
app.include_router(tags.router, prefix="/api/tags", tags=["tags"]) 