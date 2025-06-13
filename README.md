# Elasticsearch Forum Search

A modern forum search platform built with Elasticsearch, FastAPI, and Astro. This project demonstrates how to implement full-text search capabilities using Elasticsearch, making it a great learning resource for understanding search engine concepts and implementation.

## 📚 Table of Contents

1. [Learning Path](#-learning-path)
2. [Project Overview](#-project-overview)
3. [Architecture](#-architecture)
4. [Getting Started](#-getting-started)
5. [Elasticsearch Implementation](#-elasticsearch-implementation)
6. [Development Guide](#-development-guide)
7. [Learning Resources](#-learning-resources)

## 🎯 Learning Path

### 1. Understanding Elasticsearch
- **What is Elasticsearch?**
  - Distributed search and analytics engine
  - Built on Apache Lucene
  - Document-oriented database
  - RESTful API for data operations

- **Core Concepts**
  - Documents: JSON objects containing data
  - Indices: Collections of documents
  - Shards: Horizontal scaling units
  - Replicas: High availability copies
  - Inverted Index: Core search data structure

### 2. Project Features
- Full-text search with relevance scoring
- Field boosting for better results
- Fuzzy matching for typo tolerance
- Real-time search results
- Modern, responsive UI

## 🏗️ Project Overview

### Tech Stack
- **Search Engine**: Elasticsearch 8.12.1
- **Backend**: FastAPI (Python)
- **Frontend**: Astro + Tailwind CSS
- **Containerization**: Docker & Docker Compose
- **Visualization**: Kibana 8.12.1

### Prerequisites
- Docker and Docker Compose
- Python 3.12+
- Node.js 18+

## 🏗️ Architecture

### System Components
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │     │   Backend   │     │ Elasticsearch│
│   (Astro)   │◄────┤   (FastAPI) │◄────┤   8.12.1    │
└─────────────┘     └─────────────┘     └─────────────┘
                                            ▲
                                            │
                                      ┌─────────────┐
                                      │   Kibana    │
                                      │   8.12.1    │
                                      └─────────────┘
```

### Data Flow
1. **User Interaction**
   - User enters search query in frontend
   - Frontend sends request to backend API

2. **Search Processing**
   - Backend constructs Elasticsearch query
   - Query sent to Elasticsearch cluster
   - Results processed and returned to frontend

3. **Data Storage**
   - Posts stored as documents in Elasticsearch
   - Each document contains title, content, and metadata
   - Documents indexed for fast retrieval

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/elasticsearch-forum-search.git
   cd elasticsearch-forum-search
   ```

2. **Start the services**
   ```bash
   docker-compose up -d
   ```

3. **Access the applications**
   - Frontend: http://localhost:4321 (User interface)
   - Backend API: http://localhost:8000 (Internal API)
   - Kibana: http://localhost:5601 (Development tool)

## 🔍 Elasticsearch Implementation

### 1. Document Structure
```json
{
  "title": "String",    // Post title with higher search relevance
  "content": "String",  // Post content
  "created_at": "Date"  // Timestamp for sorting
}
```

### 2. Search Features

#### Field Boosting
- Title field has 3x boost (more important in search)
- Content field has 2x boost
- Example: A match in title is weighted higher than in content

#### Fuzzy Matching
- Handles typos and misspellings
- Example: "helo" will match "hello"
- Configurable fuzziness level

#### Multi-field Search
```json
{
  "multi_match": {
    "query": "search term",
    "fields": ["title^3", "content^2"],
    "type": "best_fields",
    "fuzziness": "AUTO"
  }
}
```

#### Sorting and Pagination
- Default sort by creation date (newest first)
- Secondary sort by relevance score
- Configurable page size and number

### 3. Backend Integration
```python
@router.get("/search")
async def search_posts(
    query: str,
    page: int = 1,
    size: int = 10,
    sort_by: Optional[str] = None
):
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^3", "content^2"]
            }
        },
        "sort": [
            {"created_at": "desc"},
            "_score"
        ]
    }
    
    response = await es.search(
        index="posts",
        body=search_body,
        from_=(page - 1) * size,
        size=size
    )
```

## 🛠️ Development Guide

### Codebase Overview
To help you navigate the project, here's a brief overview of the key directories and files:

**Backend (`backend/`)**
- `backend/app/`: Contains the core FastAPI application code, including: 
  - `main.py`: Main FastAPI application instance and setup.
  - `models.py`: Pydantic models for data validation and serialization.
  - `routers/`: API endpoints (e.g., `posts.py` for post-related operations, `search.py` for search functionality).
- `backend/Dockerfile`: Defines the Docker image for the backend service, including dependencies and startup commands.
- `backend/requirements.txt`: Lists all Python dependencies required for the backend.

**Frontend (`frontend/`)**
- `frontend/src/`: Contains the Astro source code, including:
  - `pages/`: Astro pages (e.g., `index.astro` for the home page, `search.astro` for the search page).
  - `layouts/`: Reusable Astro layouts (e.g., `Layout.astro` for the main page structure).
  - `components/`: UI components (e.g., for posts, search forms).
  - `styles/`: Global styles and Tailwind CSS configurations.
- `frontend/astro.config.mjs`: Astro project configuration, including integrations and build settings.
- `frontend/Dockerfile`: Defines the Docker image for the frontend service.
- `frontend/package.json`: Manages Node.js dependencies and scripts for the frontend.

### Kibana Dev Tools
Access Kibana at http://localhost:5601 to:
- Test search queries in real-time
- Monitor search performance
- Debug mapping issues
- Explore your data

### Common Commands
```bash
# Check index mapping
GET posts/_mapping

# Test search query
GET posts/_search
{
  "query": {
    "multi_match": {
      "query": "example",
      "fields": ["title^3", "content^2"]
    }
  }
}

# Check cluster health
GET _cluster/health
```

### Performance Tips
- Use field boosting for better relevance
- Implement fuzzy matching for user-friendly search
- Enable pagination for large result sets
- Cache frequent queries

## 📚 Learning Resources

1. **Official Documentation**
   - [Elasticsearch Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
   - [Elasticsearch Query DSL](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl.html)
   - [Elasticsearch Mapping](https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping.html)

2. **Recommended Books**
   - ["Elasticsearch: The Definitive Guide"](https://www.oreilly.com/library/view/elasticsearch-the-definitive/9781449358532/)
   - ["Relevant Search" by Doug Turnbull and John Berryman](https://www.manning.com/books/relevant-search)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Elasticsearch community
- FastAPI documentation
- Astro team 