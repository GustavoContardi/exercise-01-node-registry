"""
Exercise 01 — Node Registry API

Implement a FastAPI application with the following endpoints:

GET    /health          → health check with DB status
POST   /api/nodes       → register a new node
GET    /api/nodes       → list all nodes
GET    /api/nodes/{name} → get a node by name
PUT    /api/nodes/{name} → update a node
DELETE /api/nodes/{name} → soft-delete a node (set status=inactive)

See README.md for full specification.
"""

# TODO: Implement your FastAPI app here

from fastapi import FastAPI, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from .database import engine, get_db, Base
from .models import Node
from .schemas import NodeCreate, NodeUpdate, NodeOut, HealthOut

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Node Registry")


@app.get("/health", response_model=HealthOut)
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    count = db.query(Node).filter(Node.status == "active").count() if db_status == "connected" else 0
    return HealthOut(status="ok", db=db_status, nodes_count=count)


@app.post("/api/nodes", response_model=NodeOut, status_code=status.HTTP_201_CREATED)
def create_node(payload: NodeCreate, db: Session = Depends(get_db)):
    existing = db.query(Node).filter(Node.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Node already exists")

    node = Node(name=payload.name, host=payload.host, port=payload.port, status="active")
    db.add(node)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Node already exists")
    db.refresh(node)
    return node

# GET ALL
@app.get("/api/nodes", response_model=list[NodeOut])
def list_nodes(db: Session = Depends(get_db)):
    return db.query(Node).all()

# GET 
@app.get("/api/nodes/{name}", response_model=NodeOut)
def get_node(name: str, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.name == name).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return node

# UPDATE
@app.put("/api/nodes/{name}", response_model=NodeOut)
def update_node(name: str, payload: NodeUpdate, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.name == name).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(node, key, value)
    db.commit()
    db.refresh(node)
    return node

# DELETE
@app.delete("/api/nodes/{name}", status_code=status.HTTP_204_NO_CONTENT)
def delete_node(name: str, db: Session = Depends(get_db)):
    node = db.query(Node).filter(Node.name == name).first()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    node.status = "inactive"
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)