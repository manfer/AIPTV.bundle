#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Provides conversion from m3u to xspf format"""

import getopt
import re
import tempfile
import sys
import os.path
import shutil

__author__ = "Fernando San Julián"
__copyright__ = "Copyright 2015"

__license__ = "GPLv3"
__version__ = "0.1"

class M3U2XSPF:
  '''M3U to XSPF Parser'''

  RE_TRACK = re.compile(
    r'#EXTINF:-?\d+\s*?(?P<metadata>.+?)?,(?P<title>(?!\s?\[COLOR).+?)\n+?(?P<uri>.+?:\/\/.+)\n*'
  )
  RE_METADATA = re.compile(
    r'(.+?)="(.+?)"'
  )

  def __init__(self, input = '', output = ''):

    self.tmpfile = ""
    self.input = input

    if output:
      self.output = output
    elif input:
      ipath = os.path.abspath(input)
      idir = os.path.dirname(ipath)
      iname = os.path.basename(ipath)
      oname =  re.sub('\.m3u8?$', '.xspf', iname)
      self.output = os.path.join(idir, oname)

  def parse(self, m3ustring = ''):

    if self.tmpfile and os.path.exists(self.tmpfile.abspath): self.tmpfile.close()
    self.tmpfile = tempfile.TemporaryFile()

    icontent = ""
    if m3ustring:
      icontent = m3ustring
    else:
      with open(self.input, 'r') as ifile:
        icontent = ifile.read()

    self.tmpfile.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    self.tmpfile.write('<playlist version="1" xmlns="http://xspf.org/ns/0/">\n')
    self.tmpfile.write('  <trackList>\n')

    for (metadataString, title, uri) in re.findall(self.RE_TRACK, icontent):
      metadata = {}
      for (key, value) in re.findall(self.RE_METADATA, metadataString):
        metadata[key.strip()] = value.strip()

      self.tmpfile.write('    <track>\n')
      self.tmpfile.write('      <location><![CDATA[' + uri.strip() + ']]></location>\n')
      self.tmpfile.write('      <title><![CDATA[' + title.strip() + ']]></title>\n')
      
      if metadata.has_key('group-title'):
        self.tmpfile.write('      <meta rel="category"><![CDATA[' + metadata['group-title'].strip() + ']]></meta>\n')

      self.tmpfile.write('    </track>\n')

    self.tmpfile.write('  </trackList>\n')
    self.tmpfile.write('</playlist>\n')

    self.tmpfile.flush()

    return self

  def out(self):
    self.tmpfile.seek(0)
    try:
      shutil.copyfileobj(self.tmpfile, sys.stdout)
    except shutil.Error as e:
      print('Error: %s' % e)
    except IOError as e:
      print('Error: %s' % e.strerror)

  def read(self):
    self.tmpfile.seek(0)
    return self.tmpfile.read()

  def save(self, output = '', allowOverwrite = True, forceOverwrite = False):
    if not output: output = self.output
    self.tmpfile.seek(0)

    if os.path.exists(output):
      # if overwrite is not allowed exit
      if not allowOverwrite: sys.exit(0)
      # if no force on then prompt user for permission
      if not forceOverwrite:
        answer = raw_input("The file already exists. Overwrite? (yes/no) ")
        if answer != 'yes': sys.exit(0)

    try:
      with open(output, 'w') as fdest:
        shutil.copyfileobj(self.tmpfile, fdest)
    except shutil.Error as e:
      print('Error: {0}'.format(e))
    except IOError as e:
      print('Error: {0} {1}'.format(output, e.strerror))

  def __del__(self):
    if self.tmpfile: self.tmpfile.close()


def printhelp():
  print 'Usage: m3u2xspf.py [-f] -i <inputfile> -o <outputfile>'
  print 'Parses m3u inputfile into a xspf outputfile.'
  print ''
  print '  -f if outputfile already exists overwrite it.'
  print '  -h prints this help and exits.'
  print '  -i, --inputfile select m3u inputfile.'
  print '  -o, --outputfile select xsfp outputfile.'

def main(argv):
  inputfile = ''
  outputfile = ''
  force = False
  try:
    opts, args = getopt.getopt(argv,"hfi:o:",["ifile=","ofile="])
  except getopt.GetoptError:
    printhelp()
    sys.exit(2)
  for opt, arg in opts :
    if opt == '-h' :
      printhelp()
      sys.exit()
    elif opt in ("-i", "--ifile") :
      inputfile = arg
    elif opt in ("-o", "--ofile") :
      outputfile = arg
    elif opt == '-f' :
      force = True

  #selectSections()
  m2x = M3U2XSPF(inputfile, outputfile)
  m2x.parse().save(forceOverwrite = force)

if __name__ == "__main__":
  main(sys.argv[1:])