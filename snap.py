#!/usr/bin/python3
import time
import os
import btrfsutil
import sys

#Generate timestamp as a string in given format
def gents(unix_time=int(time.time())):
	return time.strftime("%d-%m-%Y_%H:%M:%S_UTC__"+str(unix_time), time.gmtime(unix_time))

class Snapname:
	
	@staticmethod
	def reconstruct(str_):
		if((not str_[0]=="@") or (not len(str_.split("__"))==3)):
			raise RuntimeError("Invalid name")
		else:
			str_=str_.split("@",1)[1]
		label=str_.split("__")[0]
		unix_time=int(str_.split("__")[2])
		return Snapname(label,unix_time)

	@staticmethod
	def valid(str_):
		if((not str_[0]=="@") or (not len(str_.split("__"))==3)):
			return False
		
		sn=Snapname.reconstruct(str_)
		return str_==Snapname(sn.label,sn.unix_time).str()

	def str(self):
		return "@"+self.label+"__"+gents(self.unix_time)

	def __init__(self,label,unix_time=int(time.time())):
		if(not label.isalpha() and label!=""):
			raise RuntimeError("Invalid snapshot label - only latin alphabet letters allowed")
		self.label=label
		self.unix_time=unix_time
		

#Execute an OS command to create snapshot
def snapcreate(path):
	btrfsutil.create_snapshot("/",path)

#Execute an OS command to delete snapshot
def snapdelete(path):
	btrfsutil.delete_subvolume(path)

def main(groupname,label):
	dir_="/snapshots/"+groupname+"/"

	#Input sanitization
	if(not groupname.isalpha()):
		raise RuntimeError("Invalid group name - only latin alphabet letters allowed")
	if(not label.isalpha() and label!=""):
		raise RuntimeError("Invalid snapshot label - only latin alphabet letters allowed")
	if(not os.path.isdir(dir_)):
		raise RuntimeError(dir_+" does not exist")
	
	sn=Snapname(label)
	snapcreate(dir_+sn.str())

if(__name__=="__main__"):
	if (len(sys.argv)!=2 and len(sys.argv)!=3):
		print("Usage: snap.py <snapshot group name> [snapshot label]")
		print("Create Btrfs snapshot of / under /snapshots/<snapshot group name>/@[snapshot label]__DD-MM-RRRR_HH:MM:SS_UTC__<unix_time>")
		print("Example: snap.py daily will make a snapshot under:")
		print("		/snapshots/daily/@__01-12-2034_12:34:56_UTC__2048589296")
		print("Example 2: snap.py containers steam will make a snapshot under:")
		print("		/snapshots/containers/@steam__01-12-2034_12:34:56_UTC__2048589296")
	else:
		groupname=sys.argv[1]
		if(len(sys.argv)==3):
			label=sys.argv[2]
		else:
			label=""
		main(groupname,label)

