from src.service.AttendanceService import AttendanceService

class AttendanceController():

    def __init__(self):
        self._attendance_service = AttendanceService()

    def add_attendance(self, raid_type, raid_id, context, attendance_list):
        return self._attendance_service.add_attendance(raid_id=raid_id, raid_type=raid_type, context = context, attendance_list=attendance_list)
        
    def remove_attendance(self, raid_type, raid_id, player_names, context):
        return self._attendance_service.remove_attendance(raid_id=raid_id, raid_type=raid_type, player_names=player_names, context=context)

    def update_attendance(self, raid_type, raid_id, attendances, context):
        return self._attendance_service.update_attendance(raid_id=raid_id, raid_type=raid_type, attendances=attendances, context=context)

    def get_attendance(self, raid_type, raid_id, context):
        return self._attendance_service.get_attendance(raid_id=raid_id, raid_type=raid_type, context = context)
                    
    def get_raid_types(self, context):
        return self._attendance_service.get_raid_types(context=context)
        
    def fetch_attendance(self, link):
        return self._attendance_service.fetch_attendance(link=link)

    def get_preview_attendance(self, raid_id, raid_type, new_attendances, context):
        return self._attendance_service.get_preview_attendance(raid_id=raid_id, raid_type=raid_type, new_attendances=new_attendances, context=context)

    def get_history_list(self, raid_id, raid_type, context):
        return self._attendance_service.get_history_list(raid_id=raid_id, raid_type=raid_type, context=context)
    
    def create_new_list(self, raid_type, context):
        return self._attendance_service.create_new_list(raid_type=raid_type, context=context)
    
    def get_raid_history(self, raid_type, raid_id, history, context):
        return self._attendance_service.get_raid_history(raid_type=raid_type, raid_id=raid_id, history=history, context=context)
    
    def rollback_raid(self, raid_type, raid_id, rollbacks, context):
        return self._attendance_service.rollback_raid(raid_type=raid_type, raid_id=raid_id, rollbacks=rollbacks, context=context)
