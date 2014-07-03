Mezz Archive
============

A collection of scripts to facilitate the archiving and recovering of mezzanine files from a NAS storage to an archival location which writes them to tape.

mezz_mover:
-----------
Cronable scripts which move files from the NAS to the archive location.
* file_monkey.py - Script to test throughput by timing the move of massive amounts of data.
* mezz_status.py - Calculates the amount of files that have been archived.
* mezz_to_archive.py - Moves the files
* send_mezz_results.py - Emails the results and any possible errors to configured reciepiants.

mezz_recovery:
--------------
Web interface to so that people can select files to recover from the archive location. It queues up the recoveries so the server/network is not crippled.
* [bottle.py](http://bottlepy.org/docs/dev/index.html) - micro web framework
* create_database.sh - script to create sqlite3 database
* get_from_tape.py - copies the files from the archive location to a recovery location
* main.py - main application to run
* static - static files, javascript and css from [Twitter Bootstrap](http://getbootstrap.com/)
* views - HTML views that are rendered
