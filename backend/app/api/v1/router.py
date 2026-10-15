from fastapi import APIRouter

from app.api.v1.endpoints import auth, books, members, issues, fines, reports, settings

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(books.router, prefix="/books", tags=["Books"])
api_router.include_router(members.router, prefix="/members", tags=["Members"])
api_router.include_router(issues.router, prefix="/issues", tags=["Issues & Returns"])
api_router.include_router(fines.router, prefix="/fines", tags=["Fines"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])