from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..models import Post, PostCreate, PostUpdate
from ..main import es
from datetime import datetime
from ..logger import get_logger

router = APIRouter()
logger = get_logger('posts')

@router.post("/", response_model=Post)
async def create_post(post: PostCreate):
    logger.info(f"Creating new post with title: {post.title}")
    post_dict = post.model_dump()
    post_dict["created_at"] = datetime.utcnow()
    post_dict["updated_at"] = datetime.utcnow()
    
    # Convert tags to lowercase before indexing
    if "tags" in post_dict and post_dict["tags"] is not None:
        post_dict["tags"] = [tag.lower() for tag in post_dict["tags"]]

    try:
        response = await es.index(
            index="posts",
            document=post_dict
        )
        logger.info(f"Post created successfully with ID: {response['_id']}")
        
        post_dict["id"] = response["_id"]
        return Post(**post_dict)
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to create post")

@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: str):
    logger.info(f"Fetching post with ID: {post_id}")
    try:
        response = await es.get(index="posts", id=post_id)
        post_data = response["_source"]
        post_data["id"] = response["_id"]
        logger.info(f"Successfully retrieved post: {post_id}")
        return Post(**post_data)
    except Exception as e:
        logger.error(f"Error fetching post {post_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=404, detail="Post not found")

@router.get("/", response_model=List[Post])
async def list_posts(page: int = 1, size: int = 10):
    logger.info(f"Listing posts (page={page}, size={size})")
    try:
        response = await es.search(
            index="posts",
            query={"match_all": {}},
            from_=(page - 1) * size,
            size=size,
            sort=[{"created_at": "desc"}]
        )
        
        posts = [Post(id=hit["_id"], **hit["_source"]) for hit in response["hits"]["hits"]]
        total = response["hits"]["total"]["value"]
        logger.info(f"Successfully retrieved {len(posts)} posts out of {total} total posts")
        return posts
    except Exception as e:
        logger.error(f"Error listing posts: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list posts")

@router.put("/{post_id}", response_model=Post)
async def update_post(post_id: str, post: PostUpdate):
    logger.info(f"Updating post {post_id}")
    try:
        current = await es.get(index="posts", id=post_id)
        current_data = current["_source"]
        
        update_data = post.model_dump(exclude_unset=True)
        
        # Convert tags to lowercase before updating
        if "tags" in update_data and update_data["tags"] is not None:
            update_data["tags"] = [tag.lower() for tag in update_data["tags"]]

        if update_data:
            logger.debug(f"Updating fields: {list(update_data.keys())}")
            current_data.update(update_data)
            current_data["updated_at"] = datetime.utcnow()
            
            await es.update(
                index="posts",
                id=post_id,
                doc=current_data
            )
            logger.info(f"Post {post_id} updated successfully with fields: {list(update_data.keys())}")
        else:
            logger.info(f"No changes provided for post {post_id}")
        
        current_data["id"] = post_id
        return Post(**current_data)
    except Exception as e:
        logger.error(f"Error updating post {post_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=404, detail="Post not found")

@router.delete("/{post_id}")
async def delete_post(post_id: str):
    logger.info(f"Deleting post with ID: {post_id}")
    try:
        await es.delete(index="posts", id=post_id)
        logger.info(f"Post {post_id} deleted successfully")
        return {"message": "Post deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting post {post_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=404, detail="Post not found") 