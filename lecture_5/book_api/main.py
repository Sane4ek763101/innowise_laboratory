from typing import Optional, List
from fastapi import FastAPI, Depends, status, HTTPException, Query
from sqlalchemy import create_engine, Column, Integer, String, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, ConfigDict, Field

# Initialize FastAPI application
app = FastAPI(title="Book Collection API")

# Database setup
engine = create_engine('sqlite:///books.db', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Book(Base):
    """SQLAlchemy model representing the books table in the database."""
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    author = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=True)

Base.metadata.create_all(bind=engine)

# Pydantic models
class BookBase(BaseModel):
    """Base model containing common book attributes."""
    title: str
    author: str
    year: Optional[int] = None

class BookCreate(BookBase):
    """Model for creating a new book (POST request)."""
    pass

class BookResponse(BookBase):
    """Model for book responses, includes database ID."""
    id: int
    model_config = ConfigDict(from_attributes=True)

class BookUpdate(BaseModel):
    """Model for updating existing books (PUT request)."""
    title: Optional[str] = Field(None, min_length=1)
    author: Optional[str] = Field(None, min_length=1)
    year: Optional[int] = Field(None, ge=0, le=2100)

    model_config = ConfigDict(from_attributes=True)

def get_db():
    """
    Dependency function that provides a database session.
    Yields:
        Session: SQLAlchemy database session
    Ensures proper session lifecycle management:
    - Creates a new session for each request
    - Yields the session to the endpoint
    - Closes the session after request completion
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post('/books/', response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book: BookCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new book entry in the database.
    Args:
        book (BookCreate): Book data from request body
        db (Session): Database session dependency
    Returns:
        BookResponse: Created book with assigned ID
    Raises:
        HTTPException: If database operation fails
    """
    db_book = Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get('/books/', response_model=List[BookResponse])
def get_books(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=100, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Retrieve paginated list of all books in the collection.
    Args:
        skip (int): Number of records to skip (default: 0)
        limit (int): Maximum number of records to return (default: 100, max: 100)
        db (Session): Database session dependency
    Returns:
        List[BookResponse]: List of book objects
    Notes:
        - Default pagination returns first 100 books
        - Use skip/limit parameters for pagination
    """
    books = db.query(Book).offset(skip).limit(limit).all()
    return books

@app.delete('/books/{book_id}', status_code= status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a book by ID.
    Args:
        book_id (int): ID of the book to delete
        db (Session): Database session dependency
    Raises:
        HTTPException: 404 if book with given ID doesn't exist
    """
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return None

@app.put('/books/{book_id}', response_model= BookResponse)
def update_book(
    book_id: int,
    book_update: BookUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing book's details.
    Args:
        book_id (int): ID of the book to update
        book_update (BookUpdate): Updated book data (partial updates supported)
        db (Session): Database session dependency
    Returns:
        BookResponse: Updated book object
    Raises:
        HTTPException: 404 if book with given ID doesn't exist
    Notes:
        - Only provided fields are updated (partial update)
        - Unchanged fields retain their original values
    """
    db_book = db.query(Book).filter(Book.id == book_id).first()
    if not db_book:
        raise HTTPException(status_code=404, detail="Book not found")
    update_data = book_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_book, field, value)

    db.commit()
    db.refresh(db_book)
    return db_book


@app.get("/books/search/", response_model=List[BookResponse])
def search_books(
        title: Optional[str] = Query(None, description="Search in book titles"),
        author: Optional[str] = Query(None, description="Search in authors"),
        year: Optional[int] = Query(None, description="Filter by year"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """
    Search books with multiple filter criteria.
    Args:
        title (Optional[str]): Search term in book titles
        author (Optional[str]): Search term in author names
        year (Optional[int]): Exact publication year filter
        skip (int): Pagination offset
        limit (int): Pagination limit
        db (Session): Database session dependency
    Returns:
        List[BookResponse]: List of books matching search criteria
    Notes:
        - Title and author searches are case-insensitive and support partial matches
        - Multiple filters are combined with AND logic
        - Results are ordered by book ID
    """
    query = db.query(Book)

    if title:
        query = query.filter(func.lower(Book.title).contains(title.lower()))
    if author:
        query = query.filter(func.lower(Book.author).contains(author.lower()))
    if year:
        query = query.filter(Book.year == year)

    return query.order_by(Book.id).offset(skip).limit(limit).all()