import asyncio
import time
from datetime import datetime
from functools import wraps


def time_logger(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start = time.time()
        result = func(self, *args, **kwargs)
        end = time.time()
        print(f"[{func.__name__}] executed in: {end-start} seconds")
        return result

    return wrapper


# ... GoodAsync 클래스와 기타 필요한 정의들 ...
class GoodAsync:
    @time_logger
    async def get_complex_list(self, s):
        a = await self.search_complex(s)
        return a

    @time_logger
    async def search_complex(self, s):
        a = await self.apt_scraper(s)
        print(a)
        return a

    @time_logger
    async def apt_scraper(self, s):
        await asyncio.sleep(s)
        return f"[{datetime.now()}] awake {s}"


async def main():
    good = GoodAsync()
    asyncio.create_task(good.get_complex_list(2))
    asyncio.create_task(good.get_complex_list(3))
    asyncio.create_task(good.get_complex_list(1))

    # 현재 실행 중인 이벤트 루프 가져오기
    current_loop = asyncio.get_running_loop()
    print(f"Current event loop: {current_loop}")

    # 잠시 대기하여 모든 태스크가 스케줄링되도록 함
    await asyncio.sleep(0.1)

    # 현재 이벤트 루프의 모든 태스크 가져오기
    tasks = asyncio.all_tasks(current_loop)
    print(f"Current tasks: {tasks}")


# 메인 함수 실행
asyncio.run(main())
