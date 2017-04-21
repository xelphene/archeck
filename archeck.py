#!/usr/bin/env python

import md5
import sys
import os
import re
import optparse
import time
import os.path

# compute the MD5 sum of a file this many bytes at a time
BLOCKSIZE=4096

class ParseError:
	def __init__(self,lineno):
		self.filename=None
		self.lineno=lineno
	def __str__(self):
		return "Error parsing datafile '%s' line %d." % (self.filename,self.lineno)

class NoSuchDirError:
	def __init__(self,path):
		self.path=path
	def __str__(self):
		return 'No such directory: %s' % self.path

# compute the hash for a file
def hashfile(path):
	hasher = md5.new()
	f=file(path)

	buf=f.read(BLOCKSIZE)
	while buf:
		hasher.update(buf)
		buf=f.read(BLOCKSIZE)

	return hasher.hexdigest()

# examine files in a directory within an archive.
# should be called from os.path.walk (called from sumdb() here)
# arg1 is an array: [sumdb,rootpath]
#   sumdb: the dictionary of checksums of files
#   rootpath: string, the path to the archive
# dirname: current directory we're looking at
# names: list of filenames in that directory to compute sums of
def procfile(arg1, dirname, names):
	sumdb=arg1[0]
	rootpath=arg1[1]
	for fn in names:
		fullpath=os.path.normpath(dirname+'/'+fn)
		relpath=fullpath[len(rootpath):]
		if os.path.isfile(fullpath):
			hash=hashfile(fullpath)
			if sumdb.has_key(hash):
				sumdb[hash].append(relpath)
			else:
				sumdb[hash]=[relpath]

def dumpdb(hashdb):
	for hash in hashdb.keys():
		print "%s: %s" % (hash,hashdb[hash])

# Read in a hash db from the passed file object.
# return the new db
def inputdb(infile):
	hashdb={}
	exp = re.compile('([0-9a-f]{32}): (.*)')
	lineno=1
	for line in infile:
		m=exp.match(line)
		if m:
			hash=m.group(1)
			filename=m.group(2)
			if hashdb.has_key(hash):
				hashdb[hash].append(filename)
			else:
				hashdb[hash]=[filename]
		else:
			raise ParseError(lineno)
		lineno+=1
	return hashdb

# load a hash db from a file previously created by writedb
# return the newly loaded hash db
def loaddb(filename):
	try:
		db=inputdb(file(filename))
	except ParseError, pe:
		pe.filename=filename
		raise pe
	return db

# print out a hash db in a nice way to stdout
# (for debugging)
def printdb(hashdb,file=sys.stdout,prefix=''):
	for hash in hashdb.keys():
		file.write('%s%s: %s\n' % (prefix, hash, str(hashdb[hash])))

# write out a hash db to a file object
def outputdb(hashdb,outfile):
	for hash in hashdb.keys():
		for filename in hashdb[hash]:
			outfile.write('%s: %s\n' % (hash,filename))

# write out a hash db to the specified file. 
def writedb(hashdb,destfile):
	outfile=file(destfile,'w')
	outputdb(hashdb,outfile)

# compute the sums of files in an archive directory, 
# generating a new hash db in the process.
# returns the new hash db
def sumdir(path):
	if not os.path.isdir(path):
		raise NoSuchDirError(path)
	sumdb={}
	os.path.walk(path,procfile,[sumdb,path])
	return sumdb

def usage():
	print """
Usage: 
    %s -r <root dir> -d <data file> [-l <log file>] [-f <fail data file>]

Options:
    -r <root dir>       Path of a directory that is the archive to check.
    -d <data file>      Path to the file that archeck will store its data in.
    -f <fail data file> If check fails, data file will be written here.
    -l <log file>       Optional path to a log file that will be written.
""" % sys.argv[0]

# return (missing,added) which are lists of [hash,paths] tuples
def diffdb(old,new):
	missing={}
	added={}

	for hash in old.keys():
		if not new.has_key(hash):
			missing[hash]=old[hash]
	
	for hash in new.keys():
		if not old.has_key(hash):
			added[hash]=new[hash]

	return (missing,added)

class UsageError(Exception):
	def __init__(self,errstr):
		self.errstr=errstr
	def __str__(self):
		return self.errstr

# parse options
def getparams():
	config={}

	optparser = optparse.OptionParser()
	optparser.add_option('-r','--root',dest='root',help='Archive root directory')
	optparser.add_option('-d','--datafile',dest='data',help='Data file name')
	optparser.add_option('-f','--faildatafile',dest='faildata',help='Data file name, used when integrity check fails')
	optparser.add_option('-l','--log',dest='log',help='Log file path')
	
	(options,args) = optparser.parse_args()

	# check for min reqs
	if options.root==None:
		raise UsageError('Must specify archive root with -r')
	if options.data==None:
		raise UsageError('Must specify data file with -d')
		
	return options
	
def main():
	try:
		opts=getparams()
	except UsageError, ue:
		print 'Error: '+str(ue)
		usage()
		sys.exit(1)

	log=sys.stdout
	if opts.log:
		log=file(opts.log,'w')

	log.write('archeck started at %s\n' % time.strftime("%Y-%m-%d %H:%M:%S") )

	# load the existing checksum DB data file	
	try:
		db_old=loaddb(opts.data)
	except ParseError, pe:
		print 'Error loading data file: '+str(pe)
		sys.exit(1)
	except IOError, ioe:
		print 'Error loading data file: %s' % (str(ioe))
		sys.exit(1)
	
	# generate a checksum DB for the archive directory
	try:
		db_new=sumdir(opts.root)
	except NoSuchDirError, nsde:
		print 'Error checking archive: '+str(nsde)
		sys.exit(1)
	
	# calculate differences between on disk files and the checksums
	# stored in the data file
	(missing,added) = diffdb(db_old,db_new)

	# print out a report of what was found
	printdb(added,log,'ADDED: ')	
	printdb(missing,log,'MISSING: ')
	log.write('%d file(s) were ADDED to the archive\n' % len(added) )
	log.write('%d file(s) were MISSING from the archive\n' % len(missing) )

	if len(missing) > 0:
		log.write('FAILURE: Some files were missing.\n')
		if opts.faildata:
			log.write('Data file saved to %s\n' % opts.faildata)
			writedb(db_new,opts.faildata)
		log.write('archeck finished at %s\n'% time.strftime("%Y-%m-%d %H:%M:%S") )
		sys.exit(1)
	else:
		log.write('SUCCESS: All files accounted for.\n')
		log.write('Data file saved to %s\n' % opts.data)
		writedb(db_new,opts.data)
		log.write('archeck finished at %s\n'% time.strftime("%Y-%m-%d %H:%M:%S") )
		sys.exit(0)		

if __name__=='__main__':
	main()
