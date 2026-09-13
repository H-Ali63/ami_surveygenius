import os
import mysql.connector  # Or psycopg2 for PostgreSQL
import paramiko

# --- CONFIGURATION ---
# Local settings
LOCAL_FOLDER = "C:/venv/qualityreview_new_api/quality/media/audio"

# Server settings
SERVER_HOST = "192.168.1.251"
SERVER_PORT = 22
SERVER_USER = "root"
SERVER_PASS = "axis@123"  # Or use private_key_path
REMOTE_FOLDER = "/opt/tomcat/webapps/Audio/"

# Database settings
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "axis@123",
    "database": "quality",
}


def process_survey_audio_files():
    # 1. Check for local files first
    local_files = [
        f
        for f in os.listdir(LOCAL_FOLDER)
        if f.endswith((".mp3", ".wav", ".flac", ".m4a"))
    ]
    if not local_files:
        print("No audio files found to process.")
        return

    # 2. Initialize SSH and SFTP Connections
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    db_conn = None
    db_cursor = None

    try:
        # Connect to Server
        print("Connecting to remote server...")
        ssh.connect(
            SERVER_HOST, port=SERVER_PORT, username=SERVER_USER, password=SERVER_PASS
        )
        sftp = ssh.open_sftp()

        # Connect to Database
        print("Connecting to database...")
        db_conn = mysql.connector.connect(**DB_CONFIG)
        db_cursor = db_conn.cursor()

        # 3. Process each file
        for file_name in local_files:
            local_path = os.path.join(LOCAL_FOLDER, file_name)
            remote_path = os.path.join(REMOTE_FOLDER, file_name)

            try:
                # Step A: Upload file to server
                print(f"Uploading {file_name} to server...")
                sftp.put(local_path, remote_path)

                file_name = file_name.split(".")[0]
                # Step B: Run SQL query to update path
                print(f"Updating database for {file_name}...")
                sql = """UPDATE quality.search_surveyresponse
                            SET params = REPLACE(
                                params,
                                '/media/audio/',
                                'http://192.168.1.251:8080/Audio/'
                            )
                            WHERE uid = %s AND params LIKE '%/media/audio/%';"""
                db_cursor.execute(sql, (file_name,))
                db_conn.commit()

                # Step C: Delete local file only after successful upload and DB update
                print(f"Deleting local file: {file_name}")
                os.remove(local_path)

            except Exception as file_error:
                print(f"Failed to process {file_name}: {file_error}")
                db_conn.rollback()  # Rollback DB changes if upload/update failed
                continue

        # Close SFTP session
        sftp.close()

    except Exception as e:
        print(f"An error occurred during connection: {e}")

    finally:
        # 4. Clean up connections
        if db_cursor:
            db_cursor.close()
        if db_conn and db_conn.is_connected():
            db_conn.close()
        ssh.close()
        print("Process complete. Connections closed.")


if __name__ == "__main__":
    process_survey_audio_files()
