from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.config import settings
from app.db import Base, engine
from app.routes import (
    auth_routes,
    items,
    reminders,
    teams,
    workflow_groups,
    external_contacts,
    payments,
)
from app.routes import settings as settings_router
from .routes import industry_templates
from app.api import reminder_jobs

# from .routes import webhook
#from slowapi import Limiter
#from slowapi.util import get_remote_address

#limiter = Limiter(key_func=get_remote_address)

#app.state.limiter = limiter

#app.include_router(webhook.router, prefix="/webhooks")


#Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    debug=False   # 🔥 hardcode
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.expireheros.app",
        "https://expireheros.app",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    industry_templates.router,
    prefix="/industry-templates",
    tags=["industry-templates"],
)




@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.environment,
    }


app.include_router(auth_routes.router, prefix="/api/auth", tags=["auth"])
app.include_router(items.router, prefix="/api/items", tags=["items"])
app.include_router(reminders.router, prefix="/api/reminders", tags=["reminders"])
app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
app.include_router(
    payments.router,
    prefix="/api/billing",
    tags=["Billing"],
)
app.include_router(
    workflow_groups.router,
    prefix="/api/workflow-groups",
    tags=["Workflow Groups"]
)
app.include_router(
    external_contacts.router,
    prefix="/api/external-contacts",
    tags=["External Contacts"]
)
app.include_router(settings_router.router, prefix="/api/settings", tags=["Settings"])
app.include_router(reminder_jobs.router, prefix="/jobs", tags=["jobs"])

@app.get("/")
def root():
    return {"message": "ExpireHero API is running 🚀"}

@app.get("/ping")
def ping():
    return {"ping": "ok"}
