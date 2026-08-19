import asyncio

from aiogram import (
    Bot, 
    Dispatcher
)

from bot.config import (
    BOTTOKEN
)

from bot.core.checker import (
    service_checker
)

from bot.routers.handlers import (
    router
)

dp = Dispatcher()

dp.include_router(router)

bot = Bot(token=BOTTOKEN)

async def main():
    asyncio.create_task(service_checker(bot))
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())