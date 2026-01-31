import os
import re
import json
import sqlite3

import web





# -------------------- Scan and Handle a Show --------------------

def scan_show(token: str, show_path: str) -> dict:
    cleaned_name = web.clean_folder_name(show_path)
    results = web.search_tv_show(cleaned_name, token)

    if not results:
        print(f"\n❓ {cleaned_name}: No TVDB match found")
        return False

    best_score, best_match = web.pick_best_match(cleaned_name, results)

    if best_score < 70:
        print(f"\n  {cleaned_name}: Low confidence match ({best_score})")

    tvdb_id = best_match["tvdb_id"]
    tvdb_seasons = web.get_tvdb_seasons(tvdb_id, token)
    local_seasons = web.get_local_seasons(show_path)

    missing = sorted(tvdb_seasons - local_seasons)
    extra = sorted(local_seasons - tvdb_seasons)

    ret_val ={}
    ret_val["show"] = best_match.get('name')
    ret_val["folder"] = os.path.basename(show_path)
    ret_val["TVDB ID"] = tvdb_id
    ret_val["Score"] =best_score
    ret_val["TVDB Seasons"] = sorted(tvdb_seasons)
    ret_val["Local"] = sorted(local_seasons)
    ret_val["missing"] =missing
    ret_val["extra"] = extra

    print(ret_val)
    
    return ret_val

# -------------------- Do A Full Dir Scan --------------------
def fullScan(token: str, root_path: str) -> bool: 
    #TODO write logic for database entry into code
    print(f"\nScanning TV library: {root_path}")

    for entry in sorted(os.listdir(root_path)):
        show_path = os.path.join(root_path, entry)
        if os.path.isdir(show_path):
            try:
                ret_val = scan_show(token, show_path )
            except Exception as e:
                print(f"\n Error scanning {entry}: {e}")


    return false


# -------------------- Create Database File --------------------
def createDB() -> bool:
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

# -------------------- MAIN --------------------

def main(run_type: str, root_path: str):
    token = web.get_tvdb_token() #grab session token for instance 
    if (run_type == "full" and not os.path.exists("show_state.db")):
        completed = createDB()
        scanned = fullScan(token, root_path)
        
        #TODO
        sys.exit(0)
    elif (run_type == "full" and os.path.exists("show_status.db")):
        #TODO
        sys.exit(0)
    elif (run_type == "update" and os.path.exists("show_status.db")):
        #TODO
        sys.exit(0)
    elif (run_type == "update" and not os.path.exists("show_status.db")):
        print("exception: show_status.db does not exist")
        sys.exit(1)
    else:
        print("exception: invalid argument structure")
        sys.exit(1)


# -------------------- RUNNER --------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python scan_tv_library_tvdb.py <run type> <tv_library_root>")
        sys.exit(1)

    main(sys.argv[1],sys.argv[2])
