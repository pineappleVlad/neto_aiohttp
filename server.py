from aiohttp import web
import json

from sqlalchemy.exc import IntegrityError

from models import Advertisements, engine, Session, Base

app = web.Application()


async def get_http_error(error_class, description:str):
    return error_class(
        text=json.dumps({"status": "error", "description": description}),
        content_type="application/json",
    )

async def context_orm(app: web.Application):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

@web.middleware
async def session_middleware(request: web.Request, handler):
    async with Session() as session:
        request['session'] = session
        response = await handler(request)
        return response

app.cleanup_ctx.append(context_orm)
app.middlewares.append(session_middleware)


async def get_adv(adv_id: int, session: Session):
    adv = await session.get(Advertisements, adv_id)
    if adv is None:
        raise get_http_error(web.HTTPNotFound, "User not found")
    return adv

async def add_adv(adv: Advertisements, session: Session):
    try:
        session.add(adv)
        await session.commit()
    except IntegrityError as er:
        raise get_http_error(web.HTTPConflict, "Adv already exists")
    return adv

class AdvView(web.View):
    @property
    def session(self):
        return self.request['session']

    @property
    def adv_id(self):
        return int(self.request.match_info["adv_id"])


    async def get(self):
        adv = await get_adv(self.adv_id, self.session)
        return web.json_response(
            {
                "header": adv.header,
                "description": adv.description,
                "owner": adv.owner,
            }
        )

    async def post(self):
        json_validated = await self.request.json()
        adv = Advertisements(**json_validated)
        adv = await add_adv(adv, self.session)
        return web.json_response(
            {
                "id": adv.id,
            }
        )

    async def patch(self):
        json_validated = await self.request.json()
        adv = await get_adv(self.adv_id, self.session)
        for field, value in json_validated.items():
            setattr(adv, field, value)
            adv = await add_adv(adv, self.session)
        return web.json_response(
            {
                "id": adv.id,
            }
        )

    async def delete(self):
        adv = await get_adv(self.adv_id, self.session)
        await self.session.delete(adv)
        await self.session.commit()
        return web.json_response(
            {
                "status": "success",
            }
        )



app.add_routes(
    [
        web.post("/adv", AdvView),
        web.get("/adv/{adv_id:\d+}", AdvView),
        web.delete("/adv/{adv_id:\d+}", AdvView),
        web.patch("/adv/{adv_id:\d+}", AdvView)
    ]
)

if __name__ == '__main__':
    web.run_app(app)