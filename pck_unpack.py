import struct
import os
import sys
import subprocess
from time import sleep
from pathlib import Path


ENDIANNESS = '<' # Little endian
STRUCT_SIGNS = {
	1 : 'c',
	2 : 'H',
	4 : 'I',
	8 : 'Q'
}

def log(msg, errcode):
	print(f"Log: {msg}")
	print("Exiting in 5 seconds..")
	sleep(5)
	sys.exit(errcode)

# Error checking
args = sys.argv
if len(args) != 2:
	log("Please specify a target .pck file! ie, pck_unpack.py target.pck")

if not Path(args[1]).is_file():
	log(f"Error, that file does not exist!", -1)

if not Path('./ww2ogg').is_dir():
	log("Error, where the hell is the ww2ogg folder?", -1)

def unpack(_bytes):
	return struct.unpack(ENDIANNESS + STRUCT_SIGNS[len(_bytes)], _bytes)[0]

def set_pointer(file):
	if file.read(4) != b'AKPK':
		log("Error, this file does not have a valid AKPK structure!")

	file.read(8) # Padding
	file.seek(25 + unpack(file.read(4))) # 25 skips to the sfx header

def extract(wems, file):
	# Create directory for the extracted files
	extracted_path = Path("extracted")
	extracted_path.mkdir(exist_ok=True)

	print(f"Log: Extracting {len(wems)} sound files..")

	# Create the .wem files
	for w in wems:
		file.seek(wems[w]['offset'])
		data = file.read(wems[w]['length'])
		Path(extracted_path.joinpath(str(w) + '.wem')).write_bytes(data)

	# Convert the .wem files to .ogg
	for f in sorted(extracted_path.glob('*.wem')):
		subprocess.call(f"ww2ogg/ww2ogg {str(f)} --pcb ww2ogg/packed_codebooks_aoTuV_603.bin", stdout=open(os.devnull, 'wb'))
		os.system("del " + str(f))

with open(args[1], 'rb') as file:
	
	set_pointer(file)
	file.read(23) if unpack(file.read(4)) != 0 else file.read(3) # Handles for Magic Arena files

	# Get wems
	wems = {}
	for i in range(unpack(file.read(4))):
		wem_id = unpack(file.read(4))
		wem_type = unpack(file.read(4))
		wem_length = unpack(file.read(4))
		wem_offset = unpack(file.read(4))

		file.read(4) # Padding

		wems[wem_id] = {'length' : wem_length, 'offset' : wem_offset}

	extract(wems, file)
	log("Finished, look inside the 'extracted' folder.", 0)