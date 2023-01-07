from services.atlas.atlas_api import AtlasAPI


def get_api(func):
    api = AtlasAPI()

    async def wrapper(*args, **kwargs):
        return await func(api=api, *args, **kwargs)

    return wrapper
