import asyncio
import os, sys

from db_manager import DBManager


async def main() -> None:
    db = DBManager()
    class_id = await db.class_.create_class(0, 9, "А", 36, "Владимир")
    await db.schedule.change_schedule_for_day(1, 1, "rus", "eng", "math", None, None, "information")
    await db.schedule.change_schedule_for_day(1, 3, "litra", "eng", "math", None, "information")
    await db.schedule.change_schedule_for_day(1, 4, "technology", "eng", "math", None, None, "information")
    await db.schedule.change_schedule_for_day(1, 6, "class hour")
    print(await db.invitation.make_invitation_to_user(123, 1, 2))
    print(await db.invitation.make_invitation_to_user(12345, 1, 123))

if __name__ == "__main__":
    asyncio.run(main())