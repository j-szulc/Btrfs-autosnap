#!/usr/bin/python3
import snap
import glob
import time

class Snapshot:	
	def __init__(self,sname,sdir):
		self.sname=sname
		self.sdir=sdir
	
	def delete(self):
		path=self.sdir+"/"+self.sname.str()
		snap.snapdelete(path)

	@staticmethod
	def valid(path):
		return snap.Snapname.valid(path.rsplit("/",1)[1])

	@staticmethod
	def reconstruct(path):
		sdir=path.rsplit("/",1)[0]
		sname=snap.Snapname.reconstruct(path.rsplit("/",1)[1])
		return Snapshot(sname,sdir)

#Class for making snaps with different frequencies etc
class Snapper:
	
	def __init__(self,groupname,delta,retention):	
		if(not groupname.isalpha()):
			raise RuntimeError("Invalid group name - only latin alphabet letters allowed")
		self.groupname=groupname
		self.delta=delta
		self.retention=retention
	
	def path(self):
		return "/snapshots/"+self.groupname+"/"

	def allsnaps(self):
		return [Snapshot.reconstruct(x) for x in glob.glob(self.path()+"*") if Snapshot.valid(x)]
	
	def isempty(self):
		return len(self.allsnaps())==0

	def latestsnap(self):
		return max(self.allsnaps(),key=lambda x: x.sname.unix_time)

	def oldestsnap(self):
		return min(self.allsnaps(),key=lambda x: x.sname.unix_time)
		
	def snapcreate(self):
		snap.main(self.groupname,"")

	def updatecreate(self):
		if(self.isempty() or (time.time() - self.latestsnap().sname.unix_time >= self.delta)):
			self.snapcreate()

	def updatedelete(self):
		if(self.retention>=0):
			while(len(self.allsnaps())>self.retention):
				self.oldestsnap().delete()
	
	def update(self):
		self.updatecreate()
		self.updatedelete()
	
if(__name__=="__main__"):
	snappers=[Snapper("daily",24*60*60-1,-1),Snapper("nightly",1*60*60-1,10)]
	[x.update() for x in snappers]
	
