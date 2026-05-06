import re
import requests
import time
import logging
from src.db.FirestoreAttendanceRepository import FirestoreAttendanceRepository

from src.schemas.AttendanceResponse import AttendanceResponse
from src.schemas.SoftresResponse import SoftresResponse
from src.schemas.AttendancePreviewResponse import AttendancePreviewResponse
from src.schemas.WowClass import WowClass
from src.schemas.AttendanceHistoryResponse import AttendanceHistoryResponse


class AttendanceService():

    def __init__(self):
        self._attendance_repository = FirestoreAttendanceRepository()
        self._logger = logging.getLogger()

    def get_raid_types(self, context):

        self._logger.info(f"[{context.username}]: Invoked 'get_raid_types' from service")

        raid_types = self._attendance_repository.get_raid_types(
            server=context.server,
            guild_id=context.guild_id
        )

        self._logger.info(f"[{context.username}]: Raid types fetched successfully")
        self._logger.debug(raid_types)

        return raid_types

    def get_attendance(self, raid_id, raid_type, context):

        self._logger.info(f"[{context.username}]: Invoked 'get_attendance' from service")
        self._logger.debug(f"[{context.username}]: Raid ID: {raid_id} - Raid Type: {raid_type}")

        attendance_list = self._attendance_repository.get_attendance(
            raid_id=raid_id,
            raid_type=raid_type,
            guild_id=context.guild_id,
            server=context.server
        )

        attendance_list.pop("$", None)

        self._logger.debug(f"[{context.username}]: Attendance list fetched successfully")
        self._logger.debug(attendance_list)

        result = []

        for key, value in attendance_list.items():

            result.append(
                AttendanceResponse(
                    item=value["item"],
                    item_id=value["item_id"],
                    name=key,
                    char_class=WowClass(value["class"]),
                    date=value["date"],
                    score=value['score']
                )
            )

        self._logger.info(f"[{context.username}]: Attendance response created successfully")

        return result

    def add_attendance(self, raid_id, raid_type, attendance_list, context):

        self._logger.info(f"[{context.username}]: Invoked 'add_attendance' from service")
        self._logger.debug(f"[{context.username}]: Raid Input parameters: Raid ID: {raid_id} - Raid Type: {raid_type}")
        self._logger.debug(f"[{context.username}]: Input Attendance List...")
        self._logger.debug(attendance_list)

        self._logger.debug(f"[{context.username}]: Calling 'get_attendance' from repository to get the current attendance...")
        current_attendance_list = self._attendance_repository.get_attendance(
            raid_id=raid_id,
            raid_type=raid_type,
            guild_id=context.guild_id,
            server=context.server
        )

        current_attendance_list.pop("$", None)

        self._logger.debug(f"[{context.username}]: Obtained the current attendance list...")
        self._logger.debug(current_attendance_list)

        self._logger.debug(f"[{context.username}]: Calling '_set_history' to save attendance history...")
        self._set_history(
            raid_id=raid_id,
            raid_type=raid_type,
            current_attendance_list=current_attendance_list,
            new_attendance_list=attendance_list,
            user=context.username,
            guild_id=context.guild_id,
            server=context.server
        )

        self._logger.debug(f"[{context.username}]: History saved successfully")

        messages = []

        self._logger.debug(f"[{context.username}]: Starting to add attendances into the repository...")

        for attendance in attendance_list:

            final_score = 1

            if attendance.item_id is None:
                self._logger.warning(f"[{context.username}]: Attendance skipped for '{attendance.name}' due to missing item_id")
                continue

            if attendance.name.lower() in current_attendance_list:

                if current_attendance_list[attendance.name.lower()]["item_id"] == attendance.item_id:
                    final_score = int(current_attendance_list[attendance.name.lower()]["score"]) + 1

            self._logger.debug(f"[{context.username}]: Adding character '{attendance.name}' into database...")

            message = self._attendance_repository.add_attendance(
                server=context.server,
                guild_id=context.guild_id,
                raid_id=raid_id,
                raid_type=raid_type,
                name=attendance.name.lower(),
                char_class=attendance.char_class.value,
                item=self._fetch_item_name(attendance.item_id),
                item_id=attendance.item_id,
                date=attendance.date,
                score=final_score
            )

            messages.append(message)

        self._logger.info(f"[{context.username}]: All attendances added succesfully")

        return messages

    def remove_attendance(self, raid_id, raid_type, player_names, context):

        self._logger.info(f"[{context.username}]: Invoked 'remove_attendance' from service")
        self._logger.debug(f"[{context.username}]: Players to remove...")
        self._logger.debug(player_names)

        messages = []

        for player_name in player_names:

            self._logger.debug(f"[{context.username}]: Removing player '{player_name}' from attendance...")

            message = self._attendance_repository.remove_attendance(
                raid_id=raid_id,
                raid_type=raid_type,
                player_name=player_name,
                server=context.server,
                guild_id=context.guild_id
            )

            messages.append(message)

        self._logger.info(f"[{context.username}]: Attendances removed successfully")

        return messages

    def update_attendance(self, raid_id, raid_type, attendances, context):

        self._logger.info(f"[{context.username}]: Invoked 'update_attendance' from service")
        self._logger.debug(f"[{context.username}]: Attendances to update...")
        self._logger.debug(attendances)

        messages = []

        for attendance in attendances:

            self._logger.debug(f"[{context.username}]: Processing attendance update for '{attendance.name}'")

            if attendance.score >= 1:

                self._logger.debug(f"[{context.username}]: Updating attendance for '{attendance.name}'")

                message = self._attendance_repository.update_attendance(
                    raid_id=raid_id,
                    raid_type=raid_type,
                    name=attendance.name.lower(),
                    char_class=attendance.char_class.value,
                    item=self._fetch_item_name(attendance.item_id),
                    item_id=attendance.item_id,
                    date=attendance.date,
                    score=attendance.score,
                    server=context.server,
                    guild_id=context.guild_id
                )

            else:

                self._logger.warning(f"[{context.username}]: Invalid score detected for '{attendance.name}'")

                message = {
                    "message": f"Attendance for player '{attendance.name}' not updated due to invalid score."
                }

            messages.append(message)

        self._logger.info(f"[{context.username}]: Attendance update completed successfully")

        return messages

    def _set_history(self, raid_id, raid_type, current_attendance_list, new_attendance_list, user, guild_id, server):

        self._logger.info(f"[{user}]: Invoked '_set_history' from service")

        actual_time = int(time.time())

        for new_attendance in new_attendance_list:

            self._logger.debug(f"[{user}]: Saving history for '{new_attendance.name}'")

            self._attendance_repository.set_history(
                user=user,
                guild_id=guild_id,
                server=server,
                actual_time=actual_time,
                raid_id=raid_id,
                raid_type=raid_type,
                name=new_attendance.name.lower(),
                char_class=new_attendance.char_class.value,
                old_item=current_attendance_list[new_attendance.name.lower()]["item"] if new_attendance.name.lower() in current_attendance_list else "None",
                old_item_id=current_attendance_list[new_attendance.name.lower()]["item_id"] if new_attendance.name.lower() in current_attendance_list else 0,
                new_item=self._fetch_item_name(new_attendance.item_id),
                new_item_id=new_attendance.item_id,
                date=new_attendance.date,
                old_score=current_attendance_list[new_attendance.name.lower()]["score"] if new_attendance.name.lower() in current_attendance_list else -1,
                new_score=int(current_attendance_list[new_attendance.name.lower()]["score"]) + 1 if new_attendance.name.lower() in current_attendance_list and current_attendance_list[new_attendance.name.lower()]["item_id"] == new_attendance.item_id else 1
            )

        self._logger.info(f"[{user}]: History saved successfully")

    def _fetch_item_name(self, item_id):

        self._logger.debug(f"Fetching item name for item_id '{item_id}'")

        url = f"https://nether.wowhead.com/tooltip/item/{item_id}"

        response = requests.get(url)

        if response.status_code != 200:

            self._logger.warning(f"Failed to fetch item name for item_id '{item_id}'")

            return item_id

        data = response.text

        match = re.search(r'"name":"([^"]+)"', data)

        if match:

            self._logger.debug(f"Item name fetched successfully for item_id '{item_id}'")

            return match.group(1)

        self._logger.warning(f"No item name found for item_id '{item_id}'")

        return item_id

    def fetch_attendance(self, link):

        self._logger.info("Invoked 'fetch_attendance' from service")

        softres_code = link.link.split("/")[-1]

        self._logger.debug(f"Softres code extracted: {softres_code}")

        url = f"https://softres.it/api/raid/{softres_code}"

        response = requests.get(url)

        if response.status_code != 200:

            self._logger.error("Error fetching attendance from Softres API")

            return {"message": "Error fetching attendance from the provided link."}

        data = response.json()

        self._logger.debug("Softres attendance fetched successfully")

        softres_reservations = []

        for reservation in data["reserved"]:

            if len(reservation["items"]) > 0:

                self._logger.debug(f"Processing reservation for '{reservation['name']}'")

                softres_reservations.append(
                    SoftresResponse(
                        item=self._fetch_item_name(int(reservation["items"][0])),
                        item_id=int(reservation["items"][0]),
                        name=reservation["name"],
                        char_class=WowClass(reservation["class"]),
                        date=reservation["updated"]
                    )
                )

        self._logger.info("Softres attendance parsed successfully")

        return softres_reservations

    def get_preview_attendance(self, raid_id, raid_type, new_attendances, context):

        self._logger.info(f"[{context.username}]: Invoked 'get_preview_attendance' from service")

        current_attendance_list = self._attendance_repository.get_attendance(
            raid_id=raid_id,
            raid_type=raid_type,
            guild_id=context.guild_id,
            server=context.server
        )

        current_attendance_list.pop("$", None)

        self._logger.debug(f"[{context.username}]: Current attendance fetched successfully")
        self._logger.debug(current_attendance_list)

        preview_list = []

        for new_attendance in new_attendances:

            self._logger.debug(f"[{context.username}]: Building preview for '{new_attendance.name}'")

            if new_attendance.name.lower() in current_attendance_list:

                current_score = int(current_attendance_list[new_attendance.name.lower()]["score"])

                next_score = current_score + 1 if current_attendance_list[new_attendance.name.lower()]["item_id"] == new_attendance.item_id else 1

            else:

                current_score = None
                next_score = 1

            preview_list.append(
                AttendancePreviewResponse(
                    current_item=current_attendance_list[new_attendance.name.lower()]["item"] if new_attendance.name.lower() in current_attendance_list else None,
                    current_item_id=current_attendance_list[new_attendance.name.lower()]["item_id"] if new_attendance.name.lower() in current_attendance_list else None,
                    current_score=current_score,
                    next_item=new_attendance.item,
                    next_item_id=new_attendance.item_id,
                    next_score=next_score,
                    name=new_attendance.name,
                    char_class=new_attendance.char_class,
                    date=new_attendance.date
                )
            )

        self._logger.info(f"[{context.username}]: Preview attendance generated successfully")

        return preview_list

    def get_history_list(self, raid_id, raid_type, context):

        self._logger.info(f"[{context.username}]: Invoked 'get_history_list' from service")

        history_list = self._attendance_repository.get_history_list(
            raid_id=raid_id,
            raid_type=raid_type,
            server=context.server,
            guild_id=context.guild_id
        )

        history_list.sort(key=lambda x: x["date"], reverse=True)

        self._logger.info(f"[{context.username}]: History list fetched successfully")
        self._logger.debug(history_list)

        return {"history_list": history_list}

    def create_new_list(self, raid_type, context):

        self._logger.info(f"[{context.username}]: Invoked 'create_new_list' from service")
        self._logger.debug(f"[{context.username}]: Raid type: {raid_type}")

        result = self._attendance_repository.create_new_list(
            raid_type=raid_type,
            server=context.server,
            guild_id=context.guild_id
        )

        self._logger.info(f"[{context.username}]: New attendance list created successfully")

        return result

    def get_raid_history(self, raid_type, raid_id, history, context):

        self._logger.info(f"[{context.username}]: Invoked 'get_raid_history' from service")

        date = str(int(history.date.timestamp()))
        name = history.name

        self._logger.debug(f"[{context.username}]: History lookup params -> Date: {date} - Name: {name}")

        hist_attendances = self._attendance_repository.get_raid_history(
            server=context.server,
            guild_id=context.guild_id,
            raid_type=raid_type,
            raid_id=raid_id,
            date=date,
            name=name
        )

        self._logger.debug(f"[{context.username}]: Raid history fetched successfully")
        self._logger.debug(hist_attendances)

        result = []

        for key, value in hist_attendances.items():

            result.append(
                AttendanceHistoryResponse(
                    char_class=WowClass(value.get("char_class")),
                    date=value.get("date"),
                    new_item=value.get("new_item"),
                    new_item_id=value.get("new_item_id"),
                    new_score=value.get("new_score"),
                    previous_item=value.get("previous_item"),
                    previous_item_id=value.get("previous_item_id"),
                    previous_score=value.get("previous_score"),
                    name=key
                )
            )

        self._logger.info(f"[{context.username}]: Raid history response generated successfully")

        return result

    def rollback_raid(self, raid_type, raid_id, rollbacks, context):

        self._logger.info(f"[{context.username}]: Invoked 'rollback_raid' from service")

        self._logger.debug(f"[{context.username}]: Deleting all current attendances before rollback...")

        self._attendance_repository.delete_all(
            server=context.server,
            guild_id=context.guild_id,
            raid_type=raid_type,
            raid_id=raid_id
        )

        self._logger.debug(f"[{context.username}]: Current attendance deleted successfully")

        messages = []

        for rollback in rollbacks:

            self._logger.debug(f"[{context.username}]: Processing rollback for '{rollback.name}'")

            if rollback.item_id == 0 and rollback.score == -1:

                self._logger.warning(f"[{context.username}]: Rollback skipped for '{rollback.name}'")

                continue

            message = self._attendance_repository.add_attendance(
                server=context.server,
                guild_id=context.guild_id,
                raid_id=raid_id,
                raid_type=raid_type,
                name=rollback.name,
                item=rollback.item,
                item_id=rollback.item_id,
                date=rollback.date,
                score=rollback.score,
                char_class=rollback.char_class
            )

            messages.append(message)

        self._logger.info(f"[{context.username}]: Rollback completed successfully")

        return messages