# Description: Add your page endpoints here.

from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from lnbits.core.models import User
from lnbits.decorators import check_user_exists
from lnbits.helpers import template_renderer

from .crud import get_owner_data_by_id

lnbits_cloud_connect_generic_router = APIRouter()


def lnbits_cloud_connect_renderer():
    return template_renderer(["lnbits_cloud_connect/templates"])


#######################################
##### ADD YOUR PAGE ENDPOINTS HERE ####
#######################################


# Backend admin page


@lnbits_cloud_connect_generic_router.get("/", response_class=HTMLResponse)
async def index(req: Request, user: User = Depends(check_user_exists)):
    return lnbits_cloud_connect_renderer().TemplateResponse(
        "lnbits_cloud_connect/index.html", {"request": req, "user": user.json()}
    )


# Frontend shareable page


