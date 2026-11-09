from contextlib import asynccontextmanager
import asyncio
import logging

from fastapi import FastAPI, HTTPException
from app.api import api
from app.database import Base, engine
from app.models.user import User  # noqa: F401  必须导入，否则 create_all 不知道这张表
from app.models.lab import Lab  # noqa: F401
from app.models.equipment import Equipment  # noqa: F401
from app.models.reservation import Reservation  # noqa: F401
from starlette.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from app.config import UPLOAD_DIR, settings
from app.services import kb_service, reservation_service
from app.common.exceptions import (
    BusinessException,
    bussiness_excpetion_hadler,
    http_excpetion_hadler,
    validation_excpetion_hadler,
    global_excpetion_hadler,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 预热向量库：模型加载（约 15s）挪到启动阶段，避免拖慢首个请求、触发前端超时
    if settings.KB_WARMUP_ENABLED:
        try:
            await asyncio.to_thread(kb_service.warmup)  # to_thread：别阻塞事件循环
        except Exception:
            logger.exception("向量库预热失败，服务继续启动")
    # 启动项目开启异步的扫描任务
    task = asyncio.create_task(reservation_service.run_expire_scan())
    try:
        yield
    finally:
        task.cancel()  # 关闭项目同时取消异步任务
        try:
            await task
        except asyncio.CancelledError:
            pass


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # 允许的前端源，不要直接写 ["*"]
    allow_credentials=True,  # 关键：允许前端携带 Authorization token
    allow_methods=["*"],  # 允许所有请求方法 GET POST PUT DELETE OPTIONS
    allow_headers=["*"],  # 允许所有请求头（包含Authorization）
)

app.include_router(api)
Base.metadata.create_all(bind=engine)  # 建表：表已存在时是幂等的，不会重复建

# 注册异常处理器
app.add_exception_handler(BusinessException, bussiness_excpetion_hadler)
app.add_exception_handler(HTTPException, http_excpetion_hadler)
app.add_exception_handler(RequestValidationError, validation_excpetion_hadler)
# 全局的异常兜底，必须放在最后注册
app.add_exception_handler(Exception, global_excpetion_hadler)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.get("/")
def root():
    return {"message": "Hello FastAPI"}
