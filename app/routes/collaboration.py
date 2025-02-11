from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import CodeFile, User, collaborators_table
from app.middleware.dependencies import get_current_user
from sqlalchemy import insert, delete

router = APIRouter(prefix="/collaboration", tags=["Collaboration"])

@router.post("/add/{file_id}/{user_id}", summary="Add collaborator to a file")
async def add_collaborator(file_id: int, user_id: int, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    """Allows file owners to add a collaborator."""
    result = await db.execute(select(CodeFile).where(CodeFile.id == file_id))
    file = result.scalars().first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.owner_id != user["sub"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    result = await db.execute(select(User).where(User.id == user_id))
    collaborator = result.scalars().first()
    
    if not collaborator:
        raise HTTPException(status_code=404, detail="User not found")
    
    await db.execute(insert(collaborators_table).values(user_id=user_id, file_id=file_id))
    await db.commit()
    return {"message": "Collaborator added successfully"}

@router.delete("/remove/{file_id}/{user_id}", summary="Remove collaborator from a file")
async def remove_collaborator(file_id: int, user_id: int, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    """Allows file owners to remove a collaborator."""
    result = await db.execute(select(CodeFile).where(CodeFile.id == file_id))
    file = result.scalars().first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.owner_id != user["sub"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    await db.execute(delete(collaborators_table).where((collaborators_table.c.user_id == user_id) & (collaborators_table.c.file_id == file_id)))
    await db.commit()
    return {"message": "Collaborator removed successfully"}
