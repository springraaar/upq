# This file is part of the "upq" program used on springfiles.com to manage file
# uploads, mirror distribution etc. It is published under the GPLv3.
#
#Copyright (C) 2011 Daniel Troeder (daniel #at# admin-box #dot# com)
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#called with fileid, extracts/inserts metadata
#calls upload

from upqjob import UpqJob

import sys
import os
import ctypes
import Image
import shutil
import getopt
import base64

import sys
sys.path.append('jobs')
from unitsync import unitsync as unitsyncpkg
sys.path.remove('jobs')
sys.path.append('jobs/metalink')
import metalink
sys.path.remove('jobs/metalink')

from xml.dom import minidom

class Extract_metadata(UpqJob):
	#TODO: make it possible to hash only a single file
	#this could be done by creating an empty directory + symlink the file there
	def run(self):
		unitsync=self.jobcfg['unitsync']
		outputpath=self.jobcfg['outputpath']
		datadir=self.jobcfg['datadir']

		outputpath = os.path.abspath(outputpath)
		os.environ["SPRING_DATADIR"]=outputpath
		usync = unitsyncpkg.Unitsync(unitsync)

		usync.Init(True,1)
		mapcount = usync.GetMapCount()
		gamescount = usync.GetPrimaryModCount()
		self.createdict(usync,gamescount, mapcount)
		for i in range(0, mapcount):
			maparchivecount = usync.GetMapArchiveCount(usync.GetMapName(i)) # initialization for GetMapArchiveName()
			filename = os.path.basename(usync.GetMapArchiveName(0))
			archivepath=usync.GetArchivePath(filename)+filename
			self.logger.debug("["+str(i) +"/"+ str(mapcount)+ "] extracting data from "+filename)
			springname = usync.GetMapName(i)
			self.dumpmap(usync, springname, outputpath, filename,i)
			self.writeMapXmlData(usync, springname, i, outputpath +"/" +filename+".metadata.xml",maparchivecount, archivepath)
			self.create_torrent(archivepath, outputpath +"/" +filename+".torrent")
		for i in range (0, gamescount):
			springname=usync.GetPrimaryModName(i)
			filename=usync.GetPrimaryModArchive(i)
			archivepath=usync.GetArchivePath(filename)+filename
			self.logger.debug("["+str(i) +"/"+ str(gamescount)+ "] extracting data from "+filename)
			gamearchivecount=usync.GetPrimaryModArchiveCount(i) # initialization for GetPrimaryModArchiveList()
			self.writeGameXmlData(usync, springname, i, outputpath + "/" + filename + ".metadata.xml", gamearchivecount, archivepath)
			self.create_torrent(archivepath, outputpath +"/" +filename+".torrent")
		self.logger.debug( "Parsed "+ str(gamescount) + " games, " + str(mapcount) + " maps")

	#calls extract metadata script
	#if no category set, use category from metadata, move + rename file there

	springcontent = [ 'bitmaps.sdz', 'springcontent.sdz', 'maphelper.sdz', 'cursors.sdz' ]

	def getXmlData(self, doc, parent, element, value):
		node = doc.createElement(element)
		value = str(value)
		value = value.decode('utf-8','replace')
		subnode = doc.createTextNode(value)
		node.appendChild(subnode)
		parent.appendChild(node)

	def getMapPositions(self, usync,doc, idx, Map):
		positions = doc.createElement("Positions")
		startpositions = usync.GetMapPosCount(idx)
		for i in range(0, startpositions):
			startpos=doc.createElement("StartPos")
			self.getXmlData(doc, startpos, "X", str(usync.GetMapPosX(idx, i)))
			self.getXmlData(doc, startpos, "Z", str(usync.GetMapPosZ(idx, i)))
			positions.appendChild(startpos)
		Map.appendChild(positions)

	def getMapDepends(self, usync,doc,idx,Map,maparchivecount):
		for j in range (1, maparchivecount): # get depends for file, idx=0 is filename itself
			deps=os.path.basename(usync.GetMapArchiveName(j))
			node = doc.createElement("Depends")
			if not deps in self.springcontent:
				self.getXmlData(doc, node, "Depend", str(deps))
		Map.appendChild(node)
	def getMapResources(self, usync,doc,idx,Map, maparchivecount):
		resources = doc.createElement("MapResources")
		resourceCount=usync.GetMapResourceCount(idx)
		for i in range (0, resourceCount):
			resource=doc.createElement("Resource")
			self.getXmlData(doc, resource, "Name", str(usync.GetMapResourceName(idx, i)))
			self.getXmlData(doc, resource, "Max", str(usync.GetMapResourceMax(idx, i)))
			self.getXmlData(doc, resource, "ExtractorRadius", str(usync.GetMapResourceExtractorRadius(idx, i)))
			resources.appendChild(resource)
		Map.appendChild(resources)

	def writeMapXmlData(self, usync, smap, idx, filename,maparchivecount,archivename):
		if os.path.isfile(filename):
			self.logger.debug("[skip] " +filename + " already exists, skipping...")
		else:
			doc = minidom.Document()
			archive = doc.createElement("Archive")
			self.getXmlData(doc, archive, "Type", "Map")
			mapname=usync.GetMapName(idx)
			self.getXmlData(doc, archive, "Name", mapname)
			self.getXmlData(doc, archive, "Author", usync.GetMapAuthor(idx))
			self.getXmlData(doc, archive, "Description", usync.GetMapDescription(idx))
			self.getXmlData(doc, archive, "Gravity", str(usync.GetMapGravity(idx)))
			self.getXmlData(doc, archive, "MaxWind", str(usync.GetMapWindMax(idx)))
			self.getXmlData(doc, archive, "MinWind", str(usync.GetMapWindMin(idx)))
			self.getXmlData(doc, archive, "TidalStrength", str(usync.GetMapTidalStrength(idx)))

			self.getXmlData(doc, archive, "Height", str(usync.GetMapHeight(idx)))
			self.getXmlData(doc, archive, "Width", str(usync.GetMapWidth(idx)))

			self.getXmlData(doc, archive, "Gravity", str(usync.GetMapGravity(idx)))
			self.getXmlData(doc, archive, "FileName", str(usync.GetMapFileName(idx)))
			self.getXmlData(doc, archive, "MapMinHeight", str(usync.GetMapMinHeight(mapname)))
			self.getXmlData(doc, archive, "MapMaxHeight", str(usync.GetMapMaxHeight(mapname)))

			self.getMapResources(usync, doc, idx,archive, maparchivecount)

			self.getMapPositions(usync,doc,idx,archive)
			self.getMapDepends(usync,doc,idx,archive,maparchivecount)
			doc.appendChild(archive)
			tmp=".tmp.xml"
			metadata = open(tmp,'w')
			metadata.write(doc.toxml("utf-8"))
			metadata.close()
			shutil.move(tmp,filename)
			self.logger.debug("[created] " +filename +" ok")

	# extracts minimap from given file
	def createMapImage(self, usync, mapname, outfile, size):
		if os.path.isfile(outfile):
			self.logger.debug("[skip] " +outfile + " already exists, skipping...")
			return
		data=ctypes.string_at(usync.GetMinimap(mapname, 0), 1024*1024*2)
		im = Image.frombuffer("RGB", (1024, 1024), data, "raw", "BGR;16")
		im=im.resize(size)
		tmp=".tmp.jpg" # first create tmp file
		im.save(tmp)
		shutil.move(tmp,outfile) # rename to dest
		self.logger.debug("[created] " +outfile +" ok")

	def createMapInfoImage(self, usync, mapname, maptype, byteperpx, decoder,decoderparm, outfile, size):
		if os.path.isfile(outfile):
			self.logger.debug("[skip] " +outfile + " already exists, skipping...")
			return
		width = ctypes.pointer(ctypes.c_int())
		height = ctypes.pointer(ctypes.c_int())
		usync.GetInfoMapSize(mapname, maptype, width, height)
		width = width.contents.value
		height = height.contents.value
		data = ctypes.create_string_buffer(int(width*height*byteperpx*2))
		data.restype = ctypes.c_void_p
		ret=usync.GetInfoMap(mapname, maptype, data, byteperpx)
		if (ret<>0):
			im = Image.frombuffer(decoder, (width, height), data, "raw", decoderparm)
			im=im.convert("L")
			im=im.resize(size)
			tmp=".tmp.jpg"
			im.save(tmp)
			shutil.move(tmp,outfile)
			self.logger.debug("[created] " +outfile +" ok")


	def dumpmap(self, usync, springname, outpath, filename, idx):
		metalmap = outpath + '/' + filename + ".metalmap" + ".jpg"
		heightmap = outpath + '/' + filename + ".heightmap" + ".jpg"
		mapimage = outpath + '/' + filename + ".jpg"
		if os.path.isfile(metalmap) and os.path.isfile(heightmap) and os.path.isfile(mapimage):
			self.logger.debug("[skip] " +metalmap + " already exists, skipping...")
			self.logger.debug("[skip] " +heightmap + " already exists, skipping...")
			self.logger.debug("[skip] " +mapimage + " already exists, skipping...")
		else:
			mapwidth=float(usync.GetMapWidth(idx))
			mapheight=float(usync.GetMapHeight(idx))
			if mapwidth>mapheight:
				scaledsize=(1024, int(((mapheight/mapwidth) * 1024)))
			else:
				scaledsize=(int(((mapwidth/mapheight) * 1024)), 1024)
			self.createMapImage(usync,springname,mapimage, scaledsize)
			self.createMapInfoImage(usync,springname, "height",2, "RGB","BGR;15", heightmap, scaledsize)
			self.createMapInfoImage(usync,springname, "metal",1, "L","L;I", metalmap, scaledsize)

	def getGameDepends(self, usync, idx, gamearchivecount, doc, game):
		depends = doc.createElement("Depends")
		game.appendChild(depends)
		for i in range (1, gamearchivecount): # get depends for file, idx=0 is filename itself
			deps=os.path.basename(usync.GetPrimaryModArchiveList(i))
			if not deps in self.springcontent and not deps.endswith(".sdp"): #FIXME: .sdp is returned wrong by unitsync
				if deps in self.springnames:
					depend=self.springnames[deps]
				else:
					depend=deps
				self.getXmlData(doc, depends, "Depend", depend)

	def writeGameXmlData(self, usync, springname, idx, filename,gamesarchivecount, archivename):
		if os.path.isfile(filename):
			self.logger.debug("[skip] " +filename + " already exists, skipping...")
			return
		doc = minidom.Document()
		archive = doc.createElement("Archive")
		doc.appendChild(archive)
		version=usync.GetPrimaryModVersion(idx)
		if springname.endswith(version) : # Hack to get version independant string
			springname=springname[:len(springname)-len(version)]
			if springname.endswith(" ") : #remove space at end (added through unitsync hack)
				springname=springname[:len(springname)-1]
		self.getXmlData(doc, archive, "Type", "Game")
		self.getXmlData(doc, archive, "Name", springname)
		self.getXmlData(doc, archive, "Description", usync.GetPrimaryModDescription(idx))
		self.getXmlData(doc, archive, "Version", version)
		self.getGameDepends(usync, idx, gamesarchivecount, doc, archive)
		tmp=".tmp.xml"
		f=open(tmp, 'w')
		f.write(doc.toxml("utf-8"))
		f.close()
		shutil.move(tmp,filename)
		self.logger.debug("[created] " +filename +" ok")

	springnames={}
	def createdict(self,usync,gamescount, mapcount):
		#create dict with springnames[filename]=springname
		for i in range(0, gamescount):
			springname=usync.GetPrimaryModName(i)
			filename=usync.GetPrimaryModArchive(i)
			self.springnames[filename]=springname
		for i in range(0, mapcount):
			maparchivecount = usync.GetMapArchiveCount(usync.GetMapName(i)) # initialization for GetMapArchiveName()
			filename = os.path.basename(usync.GetMapArchiveName(0))
			self.logger.debug( "["+str(i) +"/"+ str(mapcount)+ "] extracting data from "+filename)
			springname = usync.GetMapName(i)
			self.springnames[filename]=springname

	def create_torrent(self, filename, output):
		if os.path.isdir(filename):
			self.logger.debug("[skip] " +filename + "is a directory, can't create torrent")
			return
		if os.path.isfile(output):
			self.logger.debug("[skip] " +output + " already exists, skipping...")
			return
		metalink._opts = { 'overwrite': False }
		filesize=os.path.getsize(filename)
		torrent = metalink.Torrent(filename)
		m = metalink.Metafile()
		m.hashes.filename=filename
		m.scan_file(filename, True, 255, 1)
		m.hashes.get_multiple('ed2k')
		torrent_options = {'files':[[metalink.encode_text(filename), int(filesize)]],
			'piece length':int(m.hashes.piecelength),
			'pieces':m.hashes.pieces,
			'encoding':'UTF-8',
			}
		data=torrent.create(torrent_options)
		tmp=".tmp.torrent"
		f=open(tmp,"wb")
		f.write(data)
		f.close()
		shutil.move(tmp,output)
		self.logger.debug("[created] " +output +" ok")
