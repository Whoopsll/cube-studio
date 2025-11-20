from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
import os

# 数据库配置（从环境变量读取，便于在 Cube Studio 中配置）
MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql-service.infra')
MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'admin')
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'kubeflow')

# 数据库连接字符串
DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# 创建数据库引擎
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)

# 创建会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 数据库模型基类
Base = declarative_base()

# 用户模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# 创建表（如果不存在）
Base.metadata.create_all(bind=engine)

# Pydantic 模型（API 请求/响应）
class UserCreate(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    email: str
    created_at: datetime

# FastAPI 应用
app = FastAPI(
    title="FastAPI MySQL Demo",
    description="FastAPI 直接连接 MySQL 数据库示例",
    version="1.0.0"
)

# 数据库依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API 路由

@app.get("/")
async def root():
    """健康检查"""
    return {
        "message": "FastAPI MySQL Demo",
        "status": "running",
        "database": MYSQL_DATABASE
    }

@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """数据库连接检查"""
    try:
        # 执行简单查询测试连接
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": MYSQL_DATABASE,
            "connection": "ok"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failed: {str(e)}"
        )

@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建用户"""
    try:
        # 检查邮箱是否已存在
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {user.email} already exists"
            )
        
        # 创建新用户
        db_user = User(name=user.name, email=user.email)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}"
        )

@app.get("/api/users", response_model=List[UserResponse])
async def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取用户列表"""
    try:
        users = db.query(User).offset(skip).limit(limit).all()
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching users: {str(e)}"
        )

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """根据 ID 获取用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    return user

@app.get("/api/users/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str, db: Session = Depends(get_db)):
    """根据邮箱获取用户"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with email {email} not found"
        )
    return user

@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    """更新用户"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    # 检查邮箱是否被其他用户使用
    if user.email != db_user.email:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email {user.email} is already in use"
            )
    
    # 更新用户信息
    db_user.name = user.name
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    db.delete(db_user)
    db.commit()
    return None

# 自定义 SQL 查询示例
@app.get("/api/users/count")
async def get_user_count(db: Session = Depends(get_db)):
    """获取用户总数（使用 SQL 查询）"""
    try:
        result = db.execute(text("SELECT COUNT(*) as count FROM users"))
        count = result.scalar()
        return {"count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error counting users: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
