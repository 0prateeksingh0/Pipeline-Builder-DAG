from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

app = FastAPI()

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Node(BaseModel):
    id: str
    type: str
    position: Dict[str, float]
    data: Dict[str, Any]

class Edge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None
    targetHandle: Optional[str] = None

class PipelineRequest(BaseModel):
    nodes: List[Node]
    edges: List[Edge]

def is_dag(nodes: List[Dict], edges: List[Dict]) -> bool:
    """
    Check if the graph formed by nodes and edges is a Directed Acyclic Graph (DAG).
    Uses topological sort (Kahn's algorithm) to detect cycles.
    """
    if not edges:
        return True
    
    # Build adjacency list and in-degree count
    node_ids = {node['id'] for node in nodes}
    adjacency = {node_id: [] for node_id in node_ids}
    in_degree = {node_id: 0 for node_id in node_ids}
    
    for edge in edges:
        source = edge['source']
        target = edge['target']
        
        if source in node_ids and target in node_ids:
            adjacency[source].append(target)
            in_degree[target] += 1
    
    # Find all nodes with no incoming edges
    queue = [node_id for node_id in node_ids if in_degree[node_id] == 0]
    processed = 0
    
    # Process nodes with no incoming edges
    while queue:
        node = queue.pop(0)
        processed += 1
        
        # Remove this node and decrease in-degree of neighbors
        for neighbor in adjacency[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # If we processed all nodes, it's a DAG (no cycles)
    # If not, there's a cycle
    return processed == len(node_ids)

@app.get('/')
def read_root():
    return {'Ping': 'Pong'}

@app.post('/pipelines/parse')
def parse_pipeline(pipeline: PipelineRequest):
    # Convert Pydantic models to dicts for processing
    nodes_dict = [node.dict() for node in pipeline.nodes]
    edges_dict = [edge.dict() for edge in pipeline.edges]
    
    num_nodes = len(nodes_dict)
    num_edges = len(edges_dict)
    is_dag_result = is_dag(nodes_dict, edges_dict)
    
    return {
        'num_nodes': num_nodes,
        'num_edges': num_edges,
        'is_dag': is_dag_result
    }
