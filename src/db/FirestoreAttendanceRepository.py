import os
from datetime import datetime
from google.cloud import firestore
from google.oauth2 import service_account

class FirestoreAttendanceRepository():

    def __init__(self):
        self._credentials = service_account.Credentials.from_service_account_file(
                                                                                  os.path.join(os.getcwd(), 
                                                                                  'keys', 
                                                                                  os.getenv('FIRESTORE_KEY_FILE_NAME'))
                                                                                  )

        self._db = firestore.Client(credentials=self._credentials)

    def get_attendance(self, raid_id, raid_type, guild_id, server):

        raid_collections = self._db.collection(server).document(guild_id).collection(raid_type).document(raid_id).collection('current').get()
        
        attendance_list = {}

        if len(raid_collections) > 0:
            for doc in raid_collections:
                attendance_list[doc.id] = doc.to_dict()
        else:
            print("Collection non trovata")

        return attendance_list        
    
    def add_attendance(self, server, guild_id, raid_id, raid_type, name, char_class, item, item_id, date, score):
        
        doc_ref = self._db.collection(server).document(guild_id).collection(raid_type).document(raid_id).collection('current').document(name)
        
        doc_ref.set({
            'class': char_class,
            'item': item,
            'item_id': item_id,
            'date': date,
            'score': score
        })

        return {"message": f"Attendance for player '{name}' added successfully."}

    def update_attendance(self, raid_id, raid_type, name, char_class, item, item_id, date, score, server, guild_id):
        
        doc_ref = self._db.collection(server).document(guild_id).collection(raid_type).document(raid_id).collection('current').document(name)
        
        doc_ref.update({
            'class': char_class,
            'item': item,
            'item_id': item_id,
            'date': date,
            'score': score
        })

        return {"message": f"Attendance for player '{name}' updated successfully."}

    def remove_attendance(self, raid_id, raid_type, player_name, server, guild_id):
        
        doc_ref = self._db.collection(server).document(guild_id).collection(raid_type).document(raid_id).collection('current').document(player_name)
        doc_ref.delete()

        return {"message": f"Attendance for player '{player_name}' removed successfully."}

    def set_history(self, user, guild_id, server, actual_time, raid_id, raid_type, name, char_class, old_item, old_item_id, new_item, new_item_id, date, old_score, new_score):

        history_doc_ref = self._db.collection(server)\
            .document(guild_id)\
            .collection(raid_type)\
            .document(raid_id)\
            .collection('history')\
            .document(str(actual_time))

        history_doc_ref.set({
            "timestamp": actual_time
        }, merge=True)

        history_doc_ref.collection(user).document(name).set({
            'char_class': char_class,
            'previous_item': old_item,
            'previous_item_id': old_item_id,
            'new_item': new_item,
            'new_item_id': new_item_id,
            'date': date,
            'previous_score': old_score,
            'new_score': new_score
        })

        return {"message": f"History for player '{name}' added successfully."}
    
    def get_raid_types(self, server, guild_id):
        raid_types_collections = self._db.collection(server).document(guild_id).collections()
        
        raid_types = []

        for collection in raid_types_collections:
            raid_types.append(collection.id)

        return raid_types
    
    def get_history_list(self, raid_id, raid_type, server, guild_id):

        base_ref = (
            self._db.collection(server)
            .document(guild_id)
            .collection(raid_type)
            .document(raid_id)
            .collection('history')
        )

        histories = []

        for doc in base_ref.stream():

            if doc.id == "$":
                continue

            date = datetime.fromtimestamp(int(doc.id))

            subcollections = list(base_ref.document(doc.id).collections())

            if not subcollections:
                continue

            name = subcollections[0].id

            histories.append({
                "date": date,
                "name": name
            })

        return histories
    
    def create_new_list(self, raid_type, server, guild_id):

        raid_ids = ["nax_10", "nax_25", 
                    "eoe_10", "eoe_25", 
                    "os_10", "os_25", 
                    "voa_10", "voa_25", 
                    "ulduar_10", "ulduar_25", 
                    "toc_10", "toc_25", 
                    "rs_10", "rs_25", 
                    "tgc_10", "tgc_25",
                    "icc_10", "icc_25"]
  
        for raid_id in raid_ids:
            base_ref = (
                self._db
                .collection(server)
                .document(guild_id)
                .collection(raid_type)
                .document(raid_id)
            )

            base_ref.collection("current").document("$").set({
                "$": "$"
            })

            base_ref.collection("history").document("$").set({
                "$": "$"
            })

        return {"message": f"New attendance lists for raid type '{raid_type}' created successfully."}

    def get_user_context(self, email):
        user_doc = self._db.collection('users').document(email).get()

        if user_doc.exists:
            return user_doc.to_dict()
        else:
            return {"message": f"User '{email}' not found."}
        
    def get_raid_history(self, server, guild_id, raid_type, raid_id, date, name):

        date = str(date)

        docs = self._db.collection(server) \
            .document(guild_id) \
            .collection(raid_type) \
            .document(raid_id) \
            .collection("history") \
            .document(date) \
            .collection(name) \
            .stream()

        results = {}

        for doc in docs:
            data = doc.to_dict()

            results[doc.id] = {
                "char_class": data.get("char_class"),
                "date": data.get("date"),
                "new_item": data.get("new_item"),
                "new_item_id": data.get("new_item_id"),
                "new_score": data.get("new_score"),
                "previous_item": data.get("previous_item"),
                "previous_item_id": data.get("previous_item_id"),
                "previous_score": data.get("previous_score")
                }
            

        return results
    
    def delete_all(self, server, guild_id, raid_type, raid_id):

        base_ref = self._db.collection(server).document(guild_id).collection(raid_type).document(raid_id).collection("current")

        docs = base_ref.stream()

        for doc in docs:
            if doc.id == "$":
                continue

            doc.reference.delete()
