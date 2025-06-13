from fastapi import APIRouter
from typing import List
from ..main import es
from ..logger import get_logger
from fastapi import HTTPException

router = APIRouter()
logger = get_logger('tags')

@router.get("/", response_model=List[str])
async def list_tags():
    logger.info("Fetching unique tags from Elasticsearch")
    try:
        logger.debug("Executing tag aggregation query")
        response = await es.search(
            index="posts",
            size=0,
            aggs={
                "unique_tags": {
                    "terms": {
                        "field": "tags",
                        "size": 1000  # Adjust based on your needs
                    }
                }
            }
        )
        
        # Extract tag names from the aggregation results
        tags = [bucket["key"] for bucket in response["aggregations"]["unique_tags"]["buckets"]]
        tag_counts = {bucket["key"]: bucket["doc_count"] for bucket in response["aggregations"]["unique_tags"]["buckets"]}
        
        logger.info(f"Successfully retrieved {len(tags)} unique tags")
        logger.debug(f"Tag distribution: {tag_counts}")
        return tags
    except Exception as e:
        logger.error(f"Error fetching tags: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch tags") 