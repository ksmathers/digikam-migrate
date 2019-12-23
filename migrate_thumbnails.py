import os
from sqlite3 import dbapi2 as sqlite
import MySQLdb as mysql
import mysql.connector

src_dir = os.path.expanduser("~/Pictures")
src_db = sqlite.connect(os.path.join(src_dir, 'thumbnails-digikam.db'))
dest_db = mysql.connector.connect(
    host = 'db.host.local',
    user = 'digikam',
    password = 'mypassword',
    database = 'digikam'
)

def each_unique_hash(src_db):
    c = src_db.cursor()
    c.execute("select * from UniqueHashes")
    for row in c.fetchall():
        yield dict(zip(['uniqueHash', 'fileSize', 'thumbId'], list(row)))
    c.close()

def each_file_path(src_db):
    c = src_db.cursor()
    c.execute("select fp.path, fp.thumbId, uh.uniqueHash from FilePaths fp, UniqueHashes uh where fp.thumbId == uh.thumbId")
    for row in c.fetchall():
        yield dict(zip(['path', 'thumbId', 'uniqueHash'], list(row)))
    c.close()

def fetch_thumbnail(src_db, thumb_id):
    c = src_db.cursor()
    args = [ thumb_id, ]
    result = None
    for row in c.execute("select * from Thumbnails where id=?", args):
        # query returns either 0 or 1 row
        result = dict(zip(['id', 'type', 'modificationDate', 'orientationHint', 'data'], row))
    c.close()
    return result

dest_unique_hash = {}
dest_thumb_id = {}
def cache_dest_unique_hash(dest_db):
    global dest_unique_hash
    global dest_thumb_id
    c = dest_db.cursor()
    c.execute("select uniqueHash, thumbId from UniqueHashes")
    for row in c.fetchall():
        hashval = row[0]
        thumbId = row[1]
        dest_unique_hash[hashval] = thumbId
        dest_thumb_id[thumbId] = hashval

dest_filepaths = {}
dest_pathids = {}
def cache_dest_filepaths(dest_db):
    global dest_filepaths
    global dest_pathids
    c = dest_db.cursor()
    c.execute("select path, thumbId from FilePaths")
    for row in c.fetchall():
        path = row[0]
        thumbId = row[1]
        dest_filepaths[thumbId] = True
        dest_pathids[path] = thumbId

def has_filepath_path(dest_db, path):
    # Is the path already indexed?
    if path in dest_pathids:
        return True
    return False



def has_unique_hash(dest_db, uniqueHash):
    global dest_unique_hash
    result = False
    if uniqueHash in dest_unique_hash:
        result = True
    return result



def add_thumbnail(dest_db, thumbrow, hashrow):
    c = dest_db.cursor()
    args = [ thumbrow['type'], thumbrow['modificationDate'], thumbrow['orientationHint'], thumbrow['data']]
    c.execute("insert into Thumbnails (type, modificationDate, orientationHint, data) values (%s, %s, %s, %s)", args)  
    thumbId = c.lastrowid
    args = [ hashrow['uniqueHash'], hashrow['fileSize'], thumbId ]
    c.execute("insert into UniqueHashes (uniqueHash, fileSize, thumbId) values (%s, %s, %s)", args)
    c.close()
    dest_db.commit()
    return thumbId

def add_filepath(dest_db, data):
    c = dest_db.cursor()
    uhash = data['uniqueHash']
    if uhash in dest_unique_hash:
        new_thumbId = dest_unique_hash[uhash]
        args = [ data['path'], new_thumbId ]
        print(f"hash {uhash} thumbid {data['thumbId']} -> {new_thumbId}")
        c.execute("insert into FilePaths (path, thumbId) values (%s, %s)", args)
        c.close()
        dest_db.commit()

def part1():
    count = 0
    cache_dest_unique_hash(dest_db)
    for src_uh in each_unique_hash(src_db):
        #print(src_uh['uniqueHash'])
        if not has_unique_hash(dest_db, src_uh['uniqueHash']):
            thumb = fetch_thumbnail(src_db, src_uh['thumbId'])
            if not thumb is None:
                thumbId = add_thumbnail(dest_db, thumb, src_uh)
                print(f"copy {thumb['id']} with hash {src_uh['uniqueHash']} to {thumbId}")
            count +=1
            #if count > 1000: break
        else:
            #print(f"skip {src_uh['uniqueHash']}")
            pass

def part2():
    cache_dest_unique_hash(dest_db)
    cache_dest_filepaths(dest_db)
    for src_fp in each_file_path(src_db):
        #print(src_fp)
        if not has_filepath_path(dest_db, src_fp['path']):
            add_filepath(dest_db, src_fp)
            #break


#part1()
part2()



