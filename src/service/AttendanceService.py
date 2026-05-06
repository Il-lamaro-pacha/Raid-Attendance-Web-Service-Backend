import re
import requests
import time
from datetime import datetime
from src.db.FirestoreAttendanceRepository import FirestoreAttendanceRepository

from src.schemas.AttendanceResponse import AttendanceResponse
from src.schemas.SoftresResponse import SoftresResponse
from src.schemas.AttendancePreviewResponse import AttendancePreviewResponse
from src.schemas.WowClass import WowClass
from src.schemas.AttendanceHistoryResponse import AttendanceHistoryResponse

class AttendanceService():

    def __init__(self):
        self._attendance_repository = FirestoreAttendanceRepository()

    def get_raid_types(self, context):
        return self._attendance_repository.get_raid_types(server=context.server, guild_id=context.guild_id)

    def get_attendance(self, raid_id, raid_type, context):
        
        attendance_list = self._attendance_repository.get_attendance(raid_id=raid_id, raid_type=raid_type, guild_id = context.guild_id, server=context.server)
        attendance_list.pop("$", None)

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

        return result
    
    def add_attendance(self, raid_id, raid_type, attendance_list, context):
        
        current_attendance_list = self._attendance_repository.get_attendance(raid_id=raid_id, raid_type=raid_type, guild_id=context.guild_id, server=context.server)
        current_attendance_list.pop("$", None)

        self._set_history(raid_id=raid_id, raid_type=raid_type, current_attendance_list=current_attendance_list, new_attendance_list=attendance_list, user=context.username, guild_id=context.guild_id, server=context.server)

        messages = []

        for attendance in attendance_list:
            
            final_score = 1

            if attendance.item_id is None:
                continue

            if attendance.name.lower() in current_attendance_list:
                
                if current_attendance_list[attendance.name.lower()]["item_id"] == attendance.item_id:
                    final_score = int(current_attendance_list[attendance.name.lower()]["score"]) + 1

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

        return messages

    def remove_attendance(self, raid_id, raid_type, player_names, context):
        messages = []
        for player_name in player_names:
            message = self._attendance_repository.remove_attendance(raid_id=raid_id, raid_type=raid_type, player_name=player_name, server=context.server, guild_id=context.guild_id)
            messages.append(message)
        return messages

    def update_attendance(self, raid_id, raid_type, attendances, context):
        
        messages = []

        for attendance in attendances:

            if attendance.score >= 1:
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
                message = {"message": f"Attendance for player '{attendance.name}' not updated due to invalid score."}

            messages.append(message)

        return messages

    def _set_history(self, raid_id, raid_type, current_attendance_list, new_attendance_list, user, guild_id, server):

        actual_time = int(time.time())

        for new_attendance in new_attendance_list:

            self._attendance_repository.set_history(
                user=user,
                guild_id = guild_id,
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

    def _fetch_item_name(self, item_id):
        
        url = f"https://nether.wowhead.com/tooltip/item/{item_id}"
        response = requests.get(url)

        if response.status_code != 200:
            return item_id

        data = response.text

        match = re.search(r'"name":"([^"]+)"', data)

        if match:
            return match.group(1)
        
        return item_id
    
    def fetch_attendance(self, link):

        softres_code = link.link.split("/")[-1]

        url = f"https://softres.it/api/raid/{softres_code}"

        response = requests.get(url)
        if response.status_code != 200:
            return {"message": "Error fetching attendance from the provided link."}
        
        data = response.json()

        softres_reservations = []

        for reservation in data["reserved"]:
            
            if len(reservation["items"]) > 0:

                softres_reservations.append(
                    SoftresResponse(
                        item=self._fetch_item_name(int(reservation["items"][0])),
                        item_id=int(reservation["items"][0]),
                        name=reservation["name"],
                        char_class=WowClass(reservation["class"]),
                        date=reservation["updated"]
                    )
                )

        return softres_reservations

    def get_preview_attendance(self, raid_id, raid_type, new_attendances, context):

        current_attendance_list = self._attendance_repository.get_attendance(raid_id=raid_id, raid_type=raid_type, guild_id = context.guild_id, server=context.server)
        current_attendance_list.pop("$", None)

        preview_list = []

        for new_attendance in new_attendances:

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

        return preview_list
    
    def get_history_list(self, raid_id, raid_type, context):

        history_list = self._attendance_repository.get_history_list(raid_id=raid_id, raid_type=raid_type, server=context.server, guild_id=context.guild_id)
        history_list.sort(key=lambda x: x["date"], reverse=True)
        return {"history_list": history_list}

    def create_new_list(self, raid_type, context):
        return self._attendance_repository.create_new_list(raid_type=raid_type, server=context.server, guild_id=context.guild_id)
    
    def get_raid_history(self, raid_type, raid_id, history, context):

        date = str(int(history.date.timestamp()))
        name = history.name
        hist_attendances = self._attendance_repository.get_raid_history(server=context.server, guild_id = context.guild_id, raid_type=raid_type, raid_id=raid_id, date=date, name=name)

        result = []

        for key, value in hist_attendances.items():
            result.append(
                AttendanceHistoryResponse(
                    char_class = WowClass(value.get("char_class")),
                    date = value.get("date"),
                    new_item = value.get("new_item"),
                    new_item_id = value.get("new_item_id"),
                    new_score = value.get("new_score"),
                    previous_item = value.get("previous_item"),
                    previous_item_id = value.get("previous_item_id"),
                    previous_score = value.get("previous_score"),
                    name = key
                )
            )
        
        return result
    
    def rollback_raid(self, raid_type, raid_id, rollbacks, context):

        self._attendance_repository.delete_all(server = context.server, guild_id = context.guild_id, raid_type=raid_type, raid_id=raid_id)

        messages = []

        for rollback in rollbacks:

            if rollback.item_id == 0 and rollback.score == -1:
                continue
            
            message = self._attendance_repository.add_attendance(server=context.server,
                                                                 guild_id=context.guild_id,
                                                                 raid_id=raid_id,
                                                                 raid_type=raid_type,
                                                                 name=rollback.name,
                                                                 item=rollback.item,
                                                                 item_id=rollback.item_id,
                                                                 date=rollback.date,
                                                                 score=rollback.score,
                                                                 char_class=rollback.char_class)
            
            messages.append(message)

        return messages
