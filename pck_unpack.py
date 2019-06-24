import struct
import os
from glob import glob
from time import sleep
import sys
import subprocess

def log(msg, errcode):
	print(f"Log: {msg}")
	print("Exiting in 5 seconds..")
	sleep(5)
	sys.exit(errcode)

args = sys.argv
if len(args) != 2:
	log("Please specify a target .pck file! ie, pck_unpack.py target.pck")

if not os.path.isfile(args[1]):
	log(f"Error, the file {args[1]} was not found!", -1)

if not os.path.isdir('./ww2ogg'):
	log("Error, where the hell is the ww2ogg folder?", -1)

ENDIANNESS = '<' #Little endian
STRUCT_SIGNS = {
	1 : 'c',
	2 : 'H',
	4 : 'I',
	8 : 'Q'
}

def unpack(_bytes):
	return struct.unpack(ENDIANNESS + STRUCT_SIGNS[len(_bytes)], _bytes)[0]

def set_pointer(file):
	if file.read(4) != b'AKPK':
		log("Error, this file does not have a valid AKPK structure!")

	file.read(8) #Padding
	file.seek(25 + unpack(file.read(4))) #25 skips to the sfx header


def extract(wems, file):
	#Create directory for the extracted files
	if not os.path.isdir("./extracted"):
		os.system('mkdir extracted')
	os.chdir('extracted')

	print(f"Log: Converting {len(wems)} .wem files..")

	for w in wems:
		file.seek(wems[w]['offset'])
		data = file.read(wems[w]['length'])

		with open(str(w) + '.wem', 'wb') as ff:
			ff.write(data)

	wem_files = glob('*.wem')

	os.chdir("../")
	#Convert them to .ogg
	for f in wem_files:
		subprocess.call(f"ww2ogg/ww2ogg {'./extracted/' + f} --pcb ww2ogg/packed_codebooks_aoTuV_603.bin", stdout=open(os.devnull, 'wb'))
		os.system("del .\\extracted\\" + f)


with open(args[1], 'rb') as file:
	
	set_pointer(file)
	file.read(23) if unpack(file.read(4)) != 0 else file.read(3) #Handles for Magic Arena files

	#Get wems
	wems = {}
	for i in range(unpack(file.read(4))):
		wem_id = unpack(file.read(4))
		wem_type = unpack(file.read(4))
		wem_length = unpack(file.read(4))
		wem_offset = unpack(file.read(4))

		file.read(4)

		#print(f"{str(i)} id:{wem_id}, wem_type:{wem_type}, length:{wem_length}, offset:{wem_offset}")

		#Add it
		wems[wem_id] = {'length' : wem_length, 'offset' : wem_offset}

	extract(wems, file)

	print("Log: Please look inside ./extracted folder for your files.")

log("Program finished.", 0)
