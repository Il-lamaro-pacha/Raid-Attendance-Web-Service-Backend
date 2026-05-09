import logging
from src.service.AttendanceService import AttendanceService

class AttendanceController():

    def __init__(self):
        self._attendance_service = AttendanceService()
        self._logger = logging.getLogger()

    def add_attendance(self, raid_type, raid_id, context, attendance_list):
        self._logger.info(f"[{context.username}]: Invoked 'add_attendance' from controller")
        return self._attendance_service.add_attendance(raid_id=raid_id, 
                                                       raid_type=raid_type, 
                                                       context = context, 
                                                       attendance_list=attendance_list)
        
    def remove_attendance(self, raid_type, raid_id, player_names, context):
        self._logger.info(f"[{context.username}]: Invoked 'remove_attendance' from controller")
        return self._attendance_service.remove_attendance(raid_id=raid_id, 
                                                          raid_type=raid_type, 
                                                          player_names=player_names, 
                                                          context=context)

    def update_attendance(self, raid_type, raid_id, attendances, context):
        self._logger.info(f"[{context.username}]: Invoked 'update_attendance' from controller")
        return self._attendance_service.update_attendance(raid_id=raid_id, 
                                                          raid_type=raid_type, 
                                                          attendances=attendances, 
                                                          context=context)

    def get_attendance(self, raid_type, raid_id, context):
        self._logger.info(f"[{context.username}]: Invoked 'get_attendance' from controller")
        return self._attendance_service.get_attendance(raid_id=raid_id, 
                                                       raid_type=raid_type, 
                                                       context = context)
                    
    def get_raid_types(self, context):
        self._logger.info(f"[{context.username}]: Invoked 'get_raid_types' from controller")
        return self._attendance_service.get_raid_types(context=context)
        
    def fetch_attendance(self, link):
        self._logger.info(f"Invoked 'fetch_attendance' from controller")
        return self._attendance_service.fetch_attendance(link=link)

    def get_preview_attendance(self, raid_id, raid_type, new_attendances, context):
        self._logger.info(f"[{context.username}]: Invoked 'get_preview_attendance' from controller")
        return self._attendance_service.get_preview_attendance(raid_id=raid_id, 
                                                               raid_type=raid_type, 
                                                               new_attendances=new_attendances, 
                                                               context=context)

    def get_history_list(self, raid_id, raid_type, context):
        self._logger.info(f"[{context.username}]: Invoked 'get_history_list' from controller")
        return self._attendance_service.get_history_list(raid_id=raid_id, 
                                                         raid_type=raid_type, 
                                                         context=context)
    
    def create_new_list(self, raid_type, context):
        self._logger.info(f"[{context.username}]: Invoked 'create_new_list' from controller")
        return self._attendance_service.create_new_list(raid_type=raid_type, 
                                                        context=context)
    
    def get_raid_history(self, raid_type, raid_id, history, context):
        self._logger.info(f"[{context.username}]: Invoked 'get_raid_history' from controller")
        return self._attendance_service.get_raid_history(raid_type=raid_type, 
                                                         raid_id=raid_id, 
                                                         history=history, 
                                                         context=context)
    
    def rollback_raid(self, raid_type, raid_id, rollbacks, context):
        self._logger.info(f"[{context.username}]: Invoked 'rollback_raid' from controller")
        return self._attendance_service.rollback_raid(raid_type=raid_type, 
                                                      raid_id=raid_id, 
                                                      rollbacks=rollbacks, 
                                                      context=context)

    def publish_list(self, raid_type, raid_id, attendance_list, context):
        self._logger.info(f"[{context.username}]: Invoked 'publish_list' from controller")
        return self._attendance_service.publish_list(raid_type=raid_type, 
                                                     raid_id=raid_id, 
                                                     attendance_list=attendance_list, 
                                                     context=context)

    def get_player_history(self, raid_type, raid_id, player_name, context):
        self._logger.info(f"[{context.username}]: Invoked 'get_player_history' from controller")
        return self._attendance_service.get_player_history(raid_type=raid_type, 
                                                           raid_id=raid_id, 
                                                           player_name=player_name, 
                                                           context=context)
    
    def register_user(self, user):
        self._logger.info(f"Invoked 'register_user' from controller")
        return self._attendance_service.register_user(user=user) 