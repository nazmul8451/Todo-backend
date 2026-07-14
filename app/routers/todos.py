from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas, security

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)

@router.post("/", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo_in: schemas.TodoCreate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    db_todo = models.Todo(
        **todo_in.model_dump(),
        owner_id=current_user.id
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@router.get("/", response_model=List[schemas.TodoResponse])
def get_todos(
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    # Returns only the todos owned by the currently authenticated user
    return db.query(models.Todo).filter(models.Todo.owner_id == current_user.id).all()


@router.get("/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(
    todo_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    db_todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id, 
        models.Todo.owner_id == current_user.id
    ).first()
    
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return db_todo


@router.put("/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(
    todo_id: int,
    todo_update: schemas.TodoUpdate,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    db_todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id, 
        models.Todo.owner_id == current_user.id
    ).first()
    
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    # Exclude unset fields during updating
    update_data = todo_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)
        
    db.commit()
    db.refresh(db_todo)
    return db_todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    db_todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id, 
        models.Todo.owner_id == current_user.id
    ).first()
    
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
        
    db.delete(db_todo)
    db.commit()
    return


@router.post("/{todo_id}/suggest-subtasks", response_model=List[str])
def suggest_subtasks(
    todo_id: int,
    current_user: models.User = Depends(security.get_current_user),
    db: Session = Depends(get_db)
):
    db_todo = db.query(models.Todo).filter(
        models.Todo.id == todo_id, 
        models.Todo.owner_id == current_user.id
    ).first()
    
    if not db_todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
        
    from app import ai_service
    return ai_service.generate_subtasks(db_todo.title, db_todo.description)
