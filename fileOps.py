import sqlite3
import os
import csv


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
    ended = "" #TODO
    missing =   str(contents["missing"])
    episodes = "" #TODO
    studio = "" #TODO

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
    with open("missing.csv","a") as f:
        writer=csv.writer(f)
        writer.writerow([materials["show"]])
        writer.writerow([materials["TVDB ID"]])
        writer.writerow(materials["missing"])
    f.close

    return True


