import struct
import os
import ctypes
from glob import glob
import sys
import time

#Change this to True if you're dealing with a Magic Gather Arena PCK file
MGA = False

def log(msg, errcode):
	print(f"Log: {msg}")
	print("Exiting in 5 seconds..")
	time.sleep(5)
	sys.exit(errcode)

args = sys.argv
if len(args) != 2:
	log("Please specify a target .pck file! ie, pck_unpack.py target.pck")

STRUCT_SIGNS = {
	1 : 'c',
	2 : 'H',
	4 : 'I',
	8 : 'Q'
}
ENDIANNESS = '<' #Little endian
HEADER = {
	'identifier' : 	{'_size' : 4, 'unpack' : False},
	'length' : 		{'_size' : ctypes.c_uint32, 'unpack' : True},
	'unk1' : 		{'_size' : 44, 'unpack' : False},
	'wem_count' : 	{'_size' : ctypes.c_uint32, 'unpack' : True}
}
def unpack(_bytes):
	return struct.unpack(ENDIANNESS + STRUCT_SIGNS[len(_bytes)], _bytes)[0]

def set_header(file):
	for prop in HEADER:
		w_header = HEADER[prop]

		if w_header['unpack']:
			w_header['data'] = unpack(file.read(ctypes.sizeof(w_header['_size'])))
		else:
			w_header['data'] = file.read(w_header['_size'])

if not os.path.isfile(args[1]):
	log(f"Error, the file {args[1]} was not found!", -1)


def extract(wems, file):
	#Create directory for the extracted files
	if not os.path.isdir("./extracted"):
		os.system('mkdir extracted')
	os.chdir('extracted')

	print("Log: Converting files..")

	for w in wems:
		file.seek(wems[w]['offset'])
		data = file.read(wems[w]['length'])

		with open(str(w) + '.wem', 'wb') as ff:
			ff.write(data)

	wem_files = glob('*.wem')

	os.chdir("../")
	#Convert them to .ogg
	for f in wem_files:
		os.system(f"ww2ogg {'./extracted/' + f} --pcb packed_codebooks_aoTuV_603.bin")
		os.system("del .\\extracted\\" + f)

with open(args[1], 'rb') as file:
	#Collect header values
	if MGA:
		#For now
		file.read(72)
		HEADER['wem_count']['data'] = unpack(file.read(4))
	else:
		set_header(file)

	#Get wems
	wems = {}
	for i in range(HEADER['wem_count']['data']):
		wem_id = unpack(file.read(4))
		wem_type = unpack(file.read(4))
		wem_length = unpack(file.read(4))
		wem_offset = unpack(file.read(4))

		file.read(4)

		print(f"{str(i)} id:{wem_id}, wem_type:{wem_type}, length:{wem_length}, offset:{wem_offset}")

		#Add it
		wems[wem_id] = {'length' : wem_length, 'offset' : wem_offset}

	extract(wems, file)

log("Program finished.", 0)
