from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import CodeFile
from app.schemas import FileCreate, FileOut
from app.middleware.dependencies import require_role, get_current_user

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/", response_model=FileOut, summary="Create a new code file")
async def create_file(file: FileCreate, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    """Allows authenticated users to create a new code file."""
    new_file = CodeFile(filename=file.filename, content=file.content, owner_id=user["sub"])
    db.add(new_file)
    await db.commit()
    await db.refresh(new_file)
    return new_file

@router.get("/", response_model=list[FileOut], summary="List all code files")
async def list_files(db: AsyncSession = Depends(get_db)):
    """Retrieves all code files."""
    result = await db.execute(select(CodeFile))
    files = result.scalars().all()
    return files

@router.put("/{file_id}", response_model=FileOut, summary="Update a code file")
async def update_file(file_id: int, file_data: FileCreate, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    """Allows file owners to update file content."""
    result = await db.execute(select(CodeFile).where(CodeFile.id == file_id))
    file = result.scalars().first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.owner_id != user["sub"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    file.content = file_data.content  # Update file content
    await db.commit()
    await db.refresh(file)
    return file

@router.delete("/{file_id}", summary="Delete a code file")
async def delete_file(file_id: int, db: AsyncSession = Depends(get_db), user: dict = Depends(get_current_user)):
    """Allows file owners to delete their files."""
    result = await db.execute(select(CodeFile).where(CodeFile.id == file_id))
    file = result.scalars().first()
    
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    
    if file.owner_id != user["sub"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    await db.delete(file)
    await db.commit()
    return {"message": "File deleted successfully"}
