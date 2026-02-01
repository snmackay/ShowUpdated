import sqlite3
import csv
import os
import time


# -------------------- Create Database File --------------------
def create_DB() -> bool:
    
    conn=sqlite3.connect("show_status.db")
    #NOTE ended is a boolean field wherein 0 is true, 1 is false
    #NOTE episodes is a count of the total number of episodes ever released
    curr = conn.cursor()
    curr.execute( 
            '''
            CREATE TABLE IF NOT EXISTS shows(
                ID          TEXT PRIMARY KEY,
                title       TEXT,
                folder      TEXT,
                match       TEXT,
                seasons     TEXT,
                local       TEXT,
                ended       TEXT, 
                missing     TEXT,
                episodes    TEXT, 
                studio      TEXT,
                UNIQUE(ID)
            )
            '''
        )
    conn.commit() #base db format 
    conn.close()
    return True

# -------------------- Check If Show Is In DB  --------------------
def record_exists(ID: str, curr) ->bool: 
    curr.execute(
        "SELECT 1 FROM shows WHERE id = ? LIMIT 1",
        (ID,)
    )
    return curr.fetchone() is not None

# -------------------- Write Individual Show Details to DB  --------------------
def show_db_write(contents: dict) -> bool:
    #TODO write out to database a specific show to all fields.
    conn=sqlite3.connect("show_status.db")
    curr=conn.cursor()

    #set up vars for insertion
    ID =        contents["TVDB ID"]
    title =     contents["show"]
    folder =    contents["folder"]
    match =     contents["Score"]
    seasons =   str(contents["TVDB Seasons"])
    local =     str(contents["Local"])
    ended =     contents["status"]
    missing =   str(contents["missing"])
    episodes = "" #TODO
    studio = "" #TODO

    if record_exists(ID,curr):
        #TODO
        curr.execute(
            """ UPDATE shows SET seasons = ?, local = ?,missing = ?, ended = ? WHERE id = ? """,
            (seasons, local, missing, ended, ID)
        )   

    else:
        curr.execute(
            '''
            INSERT INTO shows (ID, title, folder, match, seasons, local, ended, missing, episodes, studio)
                  VALUES(?,?,?,?,?,?,?,?,?,?)''', 
        
            (ID,title,folder,match,seasons,local,ended,missing,episodes,studio))  
    conn.commit()
    conn.close()
    
    return True

# -------------------- Generate Missing Seasons Text File --------------------
def write_missing_file(materials: dict) ->bool:

    file_exists = os.path.exists("missing.csv")

    with open("missing.csv","a") as f:
        writer=csv.writer(f)
        if not file_exists:
            writer.writerow(["Show Title","Folder Name", "TVDB ID", "Missing Season #'s"])
        builtRow=[]
        builtRow.append(materials["show"])
        builtRow.append(materials["folder"])
        builtRow.append(materials["TVDB ID"])
        builtRow.append(materials["missing"])
        writer.writerow(builtRow)
    f.close

    return True

# -------------------- Log Errors During Search --------------------
def write_error_log(file: str, error: str) -> None:
    with open("./log/error_log_"+str(time.time())+"_.txt", "a") as f:
        f.write("Error Entry \n")
        f.write(file + "\n")
        f.write(str(error) + "\n")
        f.close()



