#!/usr/bin/env python
import os
import sys
##########Trash###########
def getTrashPath():
	home=os.getenv("HOME")
	home+="/.Trash"
	return home
	pass
def touch(file):
	fp=open(file,"a+")
	fp.close()
	pass
def absPath(dir,file):
	if dir[-1]!='/':
		dir+='/'
		pass
	return dir+file
class Trash:
	def __init__(self):
		self.trashPath=getTrashPath()
		self.trashIndex="index"
		if not os.path.exists(self.trashPath):
			os.mkdir(self.trashPath)
			pass
		if not os.path.exists(absPath(self.trashPath,self.trashIndex)):
			fp=touch(absPath(self.trashPath,self.trashIndex))
			pass
		pass
	def __matchAndMove(self,line,id,idAsFilename=False):
			(myid,path,fn,num,type)=line.split(':')
			if (idAsFilename and fn==id) or id==myid: #id is only as filename
				return self.__mv(absPath(self.trashPath,fn+"_"+num),absPath(path,fn),type)
			else:
				if not idAsFilename and fn==id:
					return False
				if fn==id or id==absPath(path,fn):
					return self.__mv(absPath(self.trashPath,fn+"_"+num),absPath(path,fn),type)
				pass
			pass
	def __mv(self,srcFile,dstFile,type):
			if type[0]=='d':
				return self.__mvDir(srcFile,dstFile)
			elif type[0]=='f':
				return self.__mvFile(srcFile,dstFile)
			else :
				return False
			pass
	def __mvDir(self,srcFile,dstFile):
		"""move dir"""
		tmpFile=self.__ensureOnlyFile(dstFile)
		toDel=[]
		for root,dirs,files in os.walk(srcFile):
			tmproot=root
			toDel.append(root)
			if root==srcFile:
				tmpFile=dstFile
			else:
				tmproot=tmproot.replace(srcFile,"")
				tmpFile=dstFile+tmproot
			if not os.path.exists(tmpFile): os.mkdir(tmpFile)
			if files:
				for file in files:
					self.__move(absPath(root,file),absPath(tmpFile,file))
					pass
				pass
			pass
		"""delete dirs"""
		while True:
			if toDel:
				dir=toDel.pop()
				os.rmdir(dir)
				pass
			else: break
			pass
		return True
		pass
	def __mvFile(self,srcFile,dstFile):
		"""move normal file"""
		if not os.path.exists(srcFile):
			return False;
		dstFile=self.__ensureOnlyFile(dstFile)
		return self.__move(srcFile,dstFile)
		pass
	def __ensureOnlyFile(self,dst):
		i=1
		tmpfile=dst
		while True:
			if os.path.exists(tmpfile):
				i+=1
				tmpfile=dst+"("+str(i)+")"
			else:
				return tmpfile
			pass
		pass
	def __move(self,srcFile,dstFile):
		if os.path.exists(dstFile): return False
		fp1=open(srcFile,"r")
		fp2=open(dstFile,"a+")
		for line in fp1:
			fp2.write(line)
		fp1.close()
		fp2.close()
		os.unlink(srcFile)
		return True
	def list(self):
		fn=absPath(self.trashPath,self.trashIndex)
		fp=open(fn,"a+")
		for line in fp:
			line.strip()
			if line[0]=='#' or line[0]=='\n':
				continue
			(id,path,name,num,type)=line.split(':')
			print "ID:("+id+")"+" ----> "+absPath(path,name)
		fp.close()
		pass
	def yank(self,ids,idAsFilename=False):
		fn=absPath(self.trashPath,self.trashIndex)
		fp=open(fn,"r")
		tmpIndex= self.__ensureOnlyFile("/tmp/trash")
		fpTmp=open(tmpIndex,"a+")
		for line in fp:
			back=False
			for id in ids:
				flag=id.find('/')
				match=False
				if flag != -1 or id.isdigit():
					if self.__matchAndMove(line,id,idAsFilename):
						back=True
						match=True
						break
					pass
				else:
					if self.__matchAndMove(line,id,idAsFilename):
						match=True
						break
					pass
				pass
				if not match: fpTmp.write(line)
			if back:
				break
			pass
		for line in fp:
			fpTmp.write(line)
			pass
		fp.close()
		fpTmp.close()
		os.unlink(fn)
		self.__resetIndex(tmpIndex,absPath(self.trashPath,self.trashIndex))
		pass
	def __resetIndex(self,oldIndex,newIndex):
		if not os.path.exists(oldIndex):
			return False
		if not os.path.exists(newIndex):
			touch(newIndex)
			pass
		fp=open(oldIndex,"r")
		fp1=open(newIndex,"w")
		id=1
		for line in fp:
			line.strip()
			if line[0]=='#' or line[0]=='\n':
				continue
			(head,sep,tail)=line.partition(':')
			fp1.write(str(id)+sep+tail)
			id+=1
			pass
		fp.close()
		fp1.close()
		os.unlink(oldIndex)
		pass
	def move(self,file):
		type='f'
		num=111
		id=1
		if os.path.isdir(file): type='d'
		fp=open(absPath(self.trashPath,self.trashIndex),"a+")
		for line in fp:
			line.strip()
			if line[0]=='#' or line[0]=='\n':
				continue
			(id,path,name,num,ftype)=line.split(':')
			id=int(id)+1
			num=int(num)+1
			pass
		if type=='d': 
			if self.__mvDir(file,absPath(self.trashPath,os.path.basename(file)+"_"+str(num))):
				fp.write(self.__buildIndex(id,file,num,type))
		else:
			if self.__mvFile(file,absPath(self.trashPath,os.path.basename(file)+"_"+str(num))):
				fp.write(self.__buildIndex(id,file,num,type))
		fp.close()
		pass
	def __buildIndex(self,id,file,num,type):
		sep=":"
		return str(id)+sep+os.path.dirname(file)+sep+os.path.basename(file)+sep+str(num)+sep+type+"\n"
		pass
	def delete(self,ids=[],idAsFilename=False):
		if not ids: #delete all
			self.__rmDir(self.trashPath)
		else:
			tempFile="trash"
			fp=open(absPath(self.trashPath,self.trashIndex))
			tmp=open(absPath("/tmp",tempFile),"a+")
			for line in fp:
				line.strip()
				if line[0]=='#' or line[0]=='\n':
					continue
				(mid,path,fn,num,type)=line.split(':')
				back=False
				for id in ids:
					if id==mid and not idAsFilename:
						self.__rm(absPath(self.absPath,fn+"_"+num),type)
						back=True
						break
					elif idAsFilename and fn==id:
						self.__rm(absPath(self.trashPath,fn+"_"+num),type)
					elif id==absPath(path,fn):
						self.__rm(absPath(self.trashPath,fn+"_"+num),type)
						back=True
						break
					else:
						tmp.write(line)
						pass
					pass
				if back: break
				pass
			for line in fp:
				tmp.write(line)
				pass
			fp.close()
			os.unlink(absPath(self.trashPath,self.trashIndex))
			tmp.close()
			self.__resetIndex(absPath("/tmp",tempFile),absPath(self.trashPath,self.trashIndex))
	def __rm(self,file,type):
		if type[0]=='d':
			self.__rmDir(file)
		else:
			os.unlink(file)
	def __rmDir(self,dir):
		if not os.path.exists(dir):return False
		toDel=[]
		for (root,dirs,files) in os.walk(dir):
			toDel.append(root)
			for file in files:
				os.unlink(absPath(root,file))
				pass
			pass
		while True:
			if toDel:
				d=toDel.pop()
				os.rmdir(d)
				pass
			else:
				break
			pass
		return True
#######################main################################
def usage():
	print "Usage: trash [list|del|mv|yank] files"
	print "\t del"," delete trash"
	print "\t list"," cat trash"
	print "\t mv"," mv file to trash"
	print "\t yank","yank file from trash"
	pass
def listFile(ids):
	files = []
	for elem in ids:
		if elem.find('-') != -1:
			a = elem.split('-')
			if a[0].isdigit() and a[1].isdigit():
				if int(a[0]) >= int(a[1]):
					print "%s is must lt than %s" % a[0], a[1]
				tmp = range(int(a[0]), int(a[1]))
				for e in tmp: files.append(e)
			else:
				files.append(elem)
				pass
			pass
		else:
			files.append(elem)
			pass
		pass
	return files
trash=Trash()
cmd=["list","del","mv","yank","help"]
if len(sys.argv)==1:
	usage()
	quit(1)
	pass
if sys.argv[1] not in cmd:
	usage()
	quit(2)
	pass
if (sys.argv[1]==cmd[2] or sys.argv[1]==cmd[3]) and len(sys.argv)==2:
	usage()
	quit(1)
	pass
ids=sys.argv[2::]
if sys.argv[1]==cmd[0]:
	#list
	trash.list()
	pass
elif sys.argv[1]==cmd[1]:
	#del
	if not ids:
		trash.list()
		ask=raw_input("Warnning you delete all Trash<Y/N>:")
		if ask.lower()!="y":
			quit(0)
	trash.delete(ids)
	pass
elif sys.argv[1]==cmd[2]:
	#mv
	for file in ids:
		if not os.path.exists(file):
			continue
		trash.move(os.path.realpath(file))
elif sys.argv[1]==cmd[3]:
	#yank
	files = listFile(ids)
	trash.yank(files)
elif sys.argv[1]==cmd[4]:
	#help
	usage()
	quit()
else:
	usage()
	quit(3)
	pass
