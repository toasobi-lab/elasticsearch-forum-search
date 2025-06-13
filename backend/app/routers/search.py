from fastapi import APIRouter, HTTPException, Request
from typing import List, Optional
from ..models import Post, SearchQuery, SearchResponse
from ..main import es
from ..logger import get_logger
import time

router = APIRouter()
logger = get_logger('search')

@router.get("/", response_model=SearchResponse)
async def search_posts(
    request: Request,
    query: str = "",
    page: int = 1,
    size: int = 10,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc"
):
    start_time = time.time()
    request_id = f"{request.client.host}-{int(start_time)}"
    
    logger.info(f"[{request_id}] Search request received")
    logger.info(f"[{request_id}] Parameters: query='{query}', Page: {page}, Size: {size}, sort_by={sort_by}, sort_order={sort_order}")
    
    if not query:
        logger.info(f"[{request_id}] No search query provided, returning empty results")
        return SearchResponse(total=0, hits=[], page=page, size=size)

    # Build the search query
    search_body = {
        "query": {
            "bool": {
                "must": [],
                "should": [],
                "filter": []
            }
        }
    }

    # Add text search if query is provided
    if query:
        search_body["query"]["bool"]["must"].append({
            "multi_match": {
                "query": query,
                "fields": ["title^3", "content^2"],
                "type": "best_fields",
                "fuzziness": "AUTO",
                "prefix_length": 2,
                "operator": "or"
            }
        })
        logger.debug(f"[{request_id}] Added text search with fields: title(boost=3), content(boost=2)")

    # Add sorting
    sort_config = []
    if sort_by:
        sort_config.append({sort_by: sort_order})
        logger.debug(f"[{request_id}] Added primary sort: {sort_by} {sort_order}")
    else:
        sort_config.append({"created_at": "desc"})
        logger.debug(f"[{request_id}] Using default sort: created_at desc")
    
    # Add score-based sorting as secondary sort
    sort_config.append("_score")
    logger.debug(f"[{request_id}] Added secondary sort by relevance score")

    try:
        logger.debug(f"[{request_id}] Executing search with body: {search_body}")
        response = await es.search(
            index="posts",
            body=search_body,
            from_=(page - 1) * size,
            size=size,
            sort=sort_config,
            track_total_hits=True
        )
        
        total_hits = response["hits"]["total"]["value"]
        hits = []
        
        for hit in response["hits"]["hits"]:
            post_data = hit["_source"]
            post_data["id"] = hit["_id"]
            post_data["score"] = hit["_score"]
            hits.append(Post(**post_data))
        
        execution_time = int((time.time() - start_time) * 1000)
        search_response = SearchResponse(
            total=total_hits,
            hits=hits,
            page=page,
            size=size,
            took_ms=execution_time
        )

        # Log detailed search results
        logger.info(f"[{request_id}] Search completed in {execution_time}ms")
        logger.info(f"[{request_id}] Found {total_hits} total matches, returning {len(hits)} results")
        
        if total_hits > 0:
            logger.debug(f"[{request_id}] Top result score: {response['hits']['hits'][0]['_score']}")
            logger.debug(f"[{request_id}] First result title: {hits[0].title}")
        
        # Log performance metrics
        logger.debug(f"[{request_id}] Elasticsearch took: {response['took']}ms")
        logger.debug(f"[{request_id}] Total processing time: {execution_time}ms")
        
        return search_response
        
    except Exception as e:
        execution_time = int((time.time() - start_time) * 1000)
        logger.error(f"[{request_id}] Search failed after {execution_time}ms: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search operation failed: {str(e)}"
        ) 