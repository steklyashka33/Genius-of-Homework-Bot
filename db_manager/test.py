import asyncio
import os, sys

# import DBManager
main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, main_dir)
from db_manager import DBManager



async def main() -> None:
    db = DBManager()
    class_id = await db.models.create_class(9, "А", 36, "Владимир")
    await db.schedule.change_schedule_for_day(1, 1, "rus", "eng", "math", None, None, "information")
    await db.schedule.change_schedule_for_day(1, 3, "litra", "eng", "math", None, "information")
    await db.schedule.change_schedule_for_day(1, 4, "technology", "eng", "math", None, None, "information")
    await db.schedule.change_schedule_for_day(1, 6, "class hour")
    print(await db.invitation.make_invitation_to_user(123, 1, 2))
    print(await db.invitation.make_invitation_to_user(12345, 1, 123))

if __name__ == "__main__":
    asyncio.run(main())