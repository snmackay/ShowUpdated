import sqlite3
import os
import csv


# -------------------- Create Database File --------------------
def create_DB() -> bool:
    if os.path.exists("show_state.db"):
        print("how the fuck did this run?")
        return False
    else:
        conn=sqlite3.connect("show_state.db")
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
                seasons     INTEGER,
                local       INTEGER,
                ended       INTEGER, 
                episodes    INTEGER, 
                studio      TEXT
            )
            '''
        )
        conn.commit() #base db format 
        conn.close()
        return True
    
# -------------------- Generate Missing Seasons Text File --------------------
def write_missing_file(materials: dict):
    with open("missing.csv","a") as f:
        writer=csv.writer(f)
        writer.writerow([materials["show"]])
        writer.writerow([materials["TVDB ID"]])
        writer.writerow(materials["missing"])
    f.close
