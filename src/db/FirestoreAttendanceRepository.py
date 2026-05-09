import os
import logging
from datetime import datetime
from google.cloud import firestore
from google.oauth2 import service_account


class FirestoreAttendanceRepository():

    def __init__(self):

        self._logger = logging.getLogger()

        self._logger.info("Initializing repository instance")

        credentials_path = os.path.join(
            os.getcwd(),
            'etc',
            'secrets',
            os.getenv('FIRESTORE_KEY_FILE_NAME')
        )

        self._logger.debug(f"Credentials path resolved -> {credentials_path}")

        self._credentials = service_account.Credentials.from_service_account_file(
            credentials_path
        )

        self._logger.debug("Credentials loaded successfully")

        self._db = firestore.Client(credentials=self._credentials)

        self._logger.info("Firestore client initialized successfully")

    def get_attendance(self, raid_id, raid_type, guild_id, server):

        self._logger.info("Invoked 'get_attendance'")
        self._logger.debug(f"Input parameters -> Server: {server} - Guild ID: {guild_id} - Raid Type: {raid_type} - Raid ID: {raid_id}")

        self._logger.debug("Fetching attendance collection from Firestore...")

        raid_collections = self._db.collection(server) \
            .document(guild_id) \
            .collection(raid_type) \
            .document(raid_id) \
            .collection('current') \
            .get()

        self._logger.debug(f"Documents fetched -> {len(raid_collections)}")

        attendance_list = {}

        if len(raid_collections) > 0:

            self._logger.debug("Starting attendance mapping...")

            for doc in raid_collections:

                self._logger.debug(f"Processing document -> {doc.id}")

                attendance_list[doc.id] = doc.to_dict()

                self._logger.debug(f"Document data -> {attendance_list[doc.id]}")

        else:

            self._logger.warning("Attendance collection not found or empty")

        self._logger.debug("Final attendance list...")
        self._logger.debug(attendance_list)

        self._logger.info("Attendance fetched successfully")

        return attendance_list

    def add_attendance(self, server, guild_id, raid_id, raid_type, name, char_class, item, item_id, date, score):

        self._logger.info("Invoked 'add_attendance'")
        self._logger.debug(f"Input parameters -> Server: {server} - Guild ID: {guild_id} - Raid Type: {raid_type} - Raid ID: {raid_id}")
        self._logger.debug(f"Attendance payload -> Name: {name} - Class: {char_class} - Item: {item} - Item ID: {item_id} - Date: {date} - Score: {score}")

        self._logger.debug(f"Building document reference for player '{name}'")

        doc_ref = self._db.collection(server) \
            .document(guild_id) \
            .collection(raid_type) \
            .document(raid_id) \
            .collection('current') \
            .document(name)

        self._logger.debug(f"Writing attendance document for '{name}'")

        doc_ref.set({
            'class': char_class,
            'item': item,
            'item_id': item_id,
            'date': date,
            'score': score
        })

        self._logger.info(f"Attendance for player '{name}' added successfully")

        return {"message": f"Attendance for player '{name}' added successfully."}

    def update_attendance(self, raid_id, raid_type, name, char_class, item, item_id, date, score, server, guild_id):

        self._logger.info("Invoked 'update_attendance'")
        self._logger.debug(f"Input parameters -> Server: {server} - Guild ID: {guild_id} - Raid Type: {raid_type} - Raid ID: {raid_id}")
        self._logger.debug(f"Update payload -> Name: {name} - Class: {char_class} - Item: {item} - Item ID: {item_id} - Date: {date} - Score: {score}")

        doc_ref = self._db.collection(server) \
            .document(guild_id) \
            .collection(raid_type) \
            .document(raid_id) \
            .collection('current') \
            .document(name)

        self._logger.debug(f"Updating document for player '{name}'")

        doc_ref.update({
            'class': char_class,
            'item': item,
            'item_id': item_id,
            'date': date,
            'score': score
        })

        self._logger.info(f"Attendance for player '{name}' updated successfully")

        return {"message": f"Attendance for player '{name}' updated successfully."}

    def remove_attendance(self, raid_id, raid_type, player_name, server, guild_id):

        self._logger.info("Invoked 'remove_attendance'")
        self._logger.debug(f"Input parameters -> Server: {server} - Guild ID: {guild_id} - Raid Type: {raid_type} - Raid ID: {raid_id} - Player: {player_name}")

        doc_ref = self._db.collection(server) \
            .document(guild_id) \
            .collection(raid_type) \
            .document(raid_id) \
            .collection('current') \
            .document(player_name)

        self._logger.debug(f"Deleting attendance document for '{player_name}'")

        doc_ref.delete()

        self._logger.info(f"Attendance for player '{player_name}' removed successfully")

        return {"message": f"Attendance for player '{player_name}' removed successfully."}

    def set_history(self, user, guild_id, server, actual_time, raid_id, raid_type, name, char_class, old_item, old_item_id, new_item, new_item_id, date, old_score, new_score):

        self._logger.info("Invoked 'set_history'")
        self._logger.debug(f"Input parameters -> User: {user} - Server: {server} - Guild ID: {guild_id}")
        self._logger.debug(f"History payload -> Name: {name} - Previous Item: {old_item} - New Item: {new_item}")
        self._logger.debug(f"Previous Score: {old_score} - New Score: {new_score}")
        self._logger.debug(f"Timestamp -> {actual_time}")

        self._logger.debug("Building history document reference...")

        history_doc_ref = self._db.collection(server) \
            .document(guild_id) \
            .collection(raid_type) \
            .document(raid_id) \
            .collection('history') \
            .document(str(actual_time))

        self._logger.debug("Writing history timestamp metadata")

        history_doc_ref.set({
            "timestamp": actual_time
        }, merge=True)

        self._logger.debug(f"Writing history entry for '{name}'")

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

        self._logger.info(f"History for player '{name}' added successfully")

        return {"message": f"History for player '{name}' added successfully."}

    def get_raid_types(self, server, guild_id):

        self._logger.info("Invoked 'get_raid_types'")
        self._logger.debug(f"Input parameters -> Server: {server} - Guild ID: {guild_id}")

        self._logger.debug("Fetching raid type collections from Firestore...")

        raid_types_collections = self._db.collection(server).document(guild_id).collections()

        raid_types = []

        for collection in raid_types_collections:

            self._logger.debug(f"Found raid type collection -> {collection.id}")

            raid_types.append(collection.id)

        self._logger.debug(f"Total raid types found -> {len(raid_types)}")
        self._logger.debug(raid_types)

        self._logger.info("Raid types fetched successfully")

        return raid_types

    def get_history_list(self, raid_id, raid_type, server, guild_id):

        self._logger.info("Invoked 'get_history_list'")
        self._logger.debug(f"Input parameters -> Server: {server} - Guild ID: {guild_id} - Raid Type: {raid_type} - Raid ID: {raid_id}")

        base_ref = (
            self._db.collection(server)
            .document(guild_id)
            .collection(raid_type)
            .document(raid_id)
            .collection('history')
        )

        self._logger.debug("Base history reference built successfully")

        histories = []

        self._logger.debug("Streaming history documents...")

        for doc in base_ref.stream():

            self._logger.debug(f"Processing history document -> {doc.id}")

            if doc.id == "$":

                self._logger.debug("Skipping placeholder document '$'")

                continue

            date = datetime.fromtimestamp(int(doc.id))

            self._logger.debug(f"Parsed timestamp -> {date}")

            subcollections = list(base_ref.document(doc.id).collections())

            self._logger.debug(f"Subcollections found -> {len(subcollections)}")

            if not subcollections:

                self._logger.warning(f"No subcollections found for history document '{doc.id}'")

                continue

            name = subcollections[0].id

            self._logger.debug(f"History owner resolved -> {name}")

            histories.append({
                "date": date,
                "name": name
            })

        self._logger.debug("Final history list...")
        self._logger.debug(histories)

        self._logger.info("History list fetched successfully")

        return histories

    def create_new_list(self, raid_type, server, guild_id):

        self._logger.info("Invoked 'create_new_list'")
        self._logger.debug(f"Input parameters -> Server: {server} - Guild ID: {guild_id} - Raid Type: {raid_type}")

        raid_ids = [
            "nax_10", "nax_25",
            "eoe_10", "eoe_25",
            "os_10", "os_25",
            "voa_10", "voa_25",
            "ulduar_10", "ulduar_25",
            "toc_10", "toc_25",
            "rs_10", "rs_25",
            "tgc_10", "tgc_25",
            "icc_10", "icc_25"
        ]

        self._logger.debug(f"Total raid IDs to initialize -> {len(raid_ids)}")

        for raid_id in raid_ids:

            self._logger.debug(f"Creating structures for raid '{raid_id}'")

            base_ref = (
                self._db
                .collection(server)
                .document(guild_id)
                .collection(raid_type)
                .document(raid_id)
            )

            self._logger.debug(f"Creating 'current' placeholder document for '{raid_id}'")

            base_ref.collection("current").document("$").set({
                "$": "$"
            })

            self._logger.debug(f"Creating 'history' placeholder document for '{raid_id}'")

            base_ref.collection("history").document("$").set({
                "$": "$"
            })

        self._logger.info(f"New attendance lists for raid type '{raid_type}' created successfully")

        return {"message": f"New attendance lists for raid type '{raid_type}' created successfully."}

    def get_user_context(self, email):

        self._logger.info("Invoked 'get_user_context'")
        self._logger.debug(f"Fetching user context for email '{email}'")

        user_doc = self._db.collection('users').document(email).get()

        self._logger.debug(f"User document exists -> {user_doc.exists}")

        if user_doc.exists:

            self._logger.debug("User context fetched successfully")
            self._logger.debug(user_doc.to_dict())

            return user_doc.to_dict()

        else:

            self._logger.warning(f"User '{email}' not found")

            return {"message": f"User '{email}' not found."}

    def get_raid_history(self, server, guild_id, raid_type, raid_id, date, name):

        self._logger.info("Invoked 'get_raid_history'")
        self._logger.debug(f"Input parameters -> Server: {server} - Guild ID: {guild_id}")
        self._logger.debug(f"Raid Type: {raid_type} - Raid ID: {raid_id}")
        self._logger.debug(f"History lookup -> Date: {date} - Name: {name}")

        date = str(date)

        self._logger.debug("Streaming raid history documents...")

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

            self._logger.debug(f"Processing history document -> {doc.id}")

            data = doc.to_dict()

            self._logger.debug(f"Document payload -> {data}")

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

        self._logger.debug("Final raid history results...")
        self._logger.debug(results)

        self._logger.info("Raid history fetched successfully")

        return results

    def delete_all(self, server, guild_id, raid_type, raid_id):

        self._logger.info("Invoked 'delete_all'")
        self._logger.debug(f"Input parameters -> Server: {server} - Guild ID: {guild_id} - Raid Type: {raid_type} - Raid ID: {raid_id}")

        base_ref = self._db.collection(server) \
            .document(guild_id) \
            .collection(raid_type) \
            .document(raid_id) \
            .collection("current")

        self._logger.debug("Streaming current attendance documents for deletion...")

        docs = base_ref.stream()

        deleted_count = 0

        for doc in docs:

            self._logger.debug(f"Processing document -> {doc.id}")

            if doc.id == "$":

                self._logger.debug("Skipping placeholder document '$'")

                continue

            self._logger.debug(f"Deleting document for player '{doc.id}'")

            doc.reference.delete()

            deleted_count += 1

        self._logger.debug(f"Total deleted documents -> {deleted_count}")

        self._logger.info("All attendance documents deleted successfully")
    
    def get_player_history(self, raid_id, raid_type, player_name, server, guild_id):

        self._logger.info("Invoked 'get_player_history'")
        self._logger.debug(
            f"Input parameters -> Server: {server} - Guild ID: {guild_id} - "
            f"Raid Type: {raid_type} - Raid ID: {raid_id} - Player: {player_name}"
        )

        base_ref = (
            self._db.collection(server)
            .document(guild_id)
            .collection(raid_type)
            .document(raid_id)
            .collection("history")
        )

        self._logger.debug("Base history reference built successfully")

        results = []
        docs = base_ref.stream()

        self._logger.debug("Streaming history documents...")

        total_partecipations = 0

        for doc in docs:

            self._logger.debug(f"Processing history document -> {doc.id}")

            timestamp = doc.id

            subcollection = next(
                base_ref.document(doc.id).collections(),
                None
            )

            if subcollection is None:

                self._logger.debug(f"No subcollections found for document '{doc.id}'")
                continue

            attendances = subcollection.stream()

            for attendance in attendances:

                self._logger.debug(f"Checking attendance document -> {attendance.id}")

                if attendance.id == player_name.lower():

                    self._logger.debug(f"Match found for player '{player_name}'")

                    total_partecipations += 1

                    data = attendance.to_dict() or {}

                    self._logger.debug(f"Attendance data -> {data}")

                    results.append({
                        "timestamp": timestamp,
                        "name": attendance.id,
                        "item": data.get("new_item")
                    })

        self._logger.debug(f"Total participations counted -> {total_partecipations}")
        self._logger.debug("Final player history result...")
        self._logger.debug(results)

        self._logger.info("Player history fetched successfully")

        return {
            "total_attendances": total_partecipations,
            "details": results
        }
    
    def register_user(self, email, username, guild_id, server):

        self._logger.info("Invoked 'register_user'")
        self._logger.debug(
            f"Input parameters -> Email: {email} - Username: {username} - "
            f"Guild ID: {guild_id} - Server: {server}"
        )

        self._logger.debug("Building user document reference...")

        base_ref = self._db.collection('users').document(email)

        self._logger.debug(f"Writing user document for '{email}'")

        base_ref.set({
            "email": email,
            "username": username,
            "guild_id": guild_id,
            "server": server
        })

        self._logger.info(f"User '{email}' registered successfully")

        return True