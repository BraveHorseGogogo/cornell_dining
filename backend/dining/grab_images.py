from sqlite3 import dbapi2 as sqlite3
import urllib

glob_sqlite_db = None

def connect_sqlite_db():
    """Connects to the sqlite database."""
    rv = sqlite3.connect("./dining.sqlite")
    rv.row_factory = sqlite3.Row
    return rv

def get_sqlite_db():
    """Return sqllite database connection"""
    global glob_sqlite_db
    if glob_sqlite_db == None:
        glob_sqlite_db = connect_sqlite_db()
    return glob_sqlite_db

sqlite_db = get_sqlite_db()
sqlite_cur = sqlite_db.cursor()
sqlite_cur.execute("SELECT hall_id, picture_url FROM hall_pictures")
sqlite_entries = sqlite_cur.fetchall()

pic_number = 0
for row in sqlite_entries:
    pic_array = row[1].split("/")
    pic_name = pic_array[len(pic_array)-1]
    curr_name = str(row[0])+"_"+pic_name
    new_url = "http://sf-sas-skoda01.serverfarm.cornell.edu/image?image_name="+curr_name
    urllib.urlretrieve(row[1],"./static/images/"+curr_name)
    pic_number += 1
    print "grab pic:"+pic_name+" NO:"+str(pic_number)
    sqlite_cur.execute("UPDATE hall_pictures SET picture_url = '{0}' WHERE picture_url='{1}' AND hall_id={2} ".format(new_url,row[1],row[0]))
    # row[2] = new_url

sqlite_db.commit()
