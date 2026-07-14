from app.db.redis import redis_client
import json
from pydantic import BaseModel

async def redis_set(key: str, value, expire: int | None = None):
    if isinstance(value, BaseModel):
        value = value.model_dump(mode="json")
    elif isinstance(value, list):
        value = [item.model_dump(mode="json") if isinstance(item, BaseModel) else item for item in value]
    
    value = json.dumps(value)

    await redis_client.set(key, value, ex=expire)
    print("Redis setting values")


async def redis_get(key: str):
    value = await redis_client.get(key)
    print("Redis getting values")

    if value is None:
        return None

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


async def redis_delete(key: str):
    print("Redis deleting values")
    await redis_client.delete(key)


async def redis_is_exist(key: str):
    print("Redis checking if key exists")
    return await redis_client.exists(key)

async def redis_expire(key: str, seconds: int):
    await redis_client.expire(key, seconds)

async def redis_ttl(key: str):
    return await redis_client.ttl(key)