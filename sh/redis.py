# pyrefly: ignore [missing-import]
import redis.asyncio

redissession = redis.asyncio.Redis(host='redis', port=6379, decode_responses=True)