# digikam-migrate

A Tool for migrating thumbnail data from SQLite to MySQL for DigiKam

## Usage

The migration tool is written as a Python script with dependencies on Python MySQLdb and mysql.connector for the export
side, and Python sqlite3.dbapi2 for the import side.

Make any modifications to the source code that you need to with particular attention to the hostname, database, and 
password needed to access your MySQL or MariaDB server.  

The thumbnail migration tool is intended for use following use of Digikam's built in database migration tool.  The
built in tool stops with a working database, but does not copy over the thumbnail database which as a consequence 
will be rebuilt a page at a time as you scroll through your photos (or at least that is what happened to me).

This tool copies over three tables. The "Thumbnails" table contains the thumbnail images and a little bit of metadata.
"UniqueHashes" is a mapping table from the uniqueHash field of the Images table to the id field of the Thumbnails
table.  And "FilePaths" maps from the id field of the Thumbnails to a directory path that is used to load the referenced
image.

Thumbnail IDs from the old database are replaced with their equivalent IDs from the new database as the missing entries 
are being written since that field is an autoincrementing field which is under database control, and so will not match
between the two databases.


