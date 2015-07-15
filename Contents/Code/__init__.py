# -*- coding: utf-8 -*-
from lxml import etree
from StringIO import StringIO
from random import randint
from m3u2xspf import M3U2XSPF

TITLE  = u'AIPTV'
PREFIX = '/video/aiptv'

AIPTV_ICON     = 'aiptv.png'
AIPTV_ART      = 'art.jpg'
AIPTV_DEFAULT  = AIPTV_ICON
AIPTV_SEARCH   = 'search.png'
AIPTV_SETTINGS = 'preferences.png'

AIPTV_ALL           = 'all.png'
AIPTV_CATEGORIES    = 'categories.png'
AIPTV_ALPHA         = 'alpha.png'
AIPTV_DOCUMENTORDER = 'documentorder.png'
AIPTV_DESCENDING    = 'descending.png'
AIPTV_ASCENDING     = 'ascending.png'
AIPTV_SHUFFLE       = 'shuffle.png'

AIPTV_NO_CATEGORY = 'No Category'

ALPHABET = u'0abcdefghijklmnñopqrstuvwxyz'

AIPTV_DEBUG = 1

################################################################################
def Start():

  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
  Plugin.AddViewGroup('PanelStream', viewMode='PanelStream', mediaType='items')

  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:29.0) Gecko/20100101 Firefox/29.0'
  HTTP.Headers['Connection'] = 'keep-alive'
  language = Prefs["language"].split("/")[1]
  HTTP.Headers['Accept-Language'] = str(language)

  ObjectContainer.title1 = TITLE
  #ObjectContainer.view_group = 'List'
  ObjectContainer.art = R(AIPTV_ART)
  DirectoryObject.thumb = R(AIPTV_DEFAULT)
  DirectoryObject.art = R(AIPTV_ART)
  PhotoAlbumObject.thumb = R(AIPTV_DEFAULT)

  if AIPTV_DEBUG:
    HTTP.CacheTime = 0
  else:
    HTTP.CacheTime = CACHE_1HOUR

################################################################################
@handler(PREFIX, TITLE, art=AIPTV_ART, thumb=AIPTV_ICON)
def aiptv_main_menu():

  oc = ObjectContainer()

  oc.add(DirectoryObject(
    key = Callback(aiptv_channels),
	  title = L("All Channels"),
    summary = L("all IPTV channels"),
    thumb = R(AIPTV_ALL)
  ))

  oc.add(DirectoryObject(
    key = Callback(aiptv_categories),
	  title = L("Categories"),
    summary = L("show IPTV channels category list"),
    thumb = R(AIPTV_CATEGORIES)
  ))

  oc.add(DirectoryObject(
    key = Callback(aiptv_alpha),
	  title = L("Alphabet"),
    summary = L("show IPTV channels in alphabetic order"),
    thumb = R(AIPTV_ALPHA)
  ))

  if Client.Product != 'PlexConnect':
    oc.add(InputDirectoryObject(
      key     = Callback(aiptv_search),
      title   = L('Search IPTV Channels'),
      prompt  = L('Search for IPTV Channels'),
      summary = L('Search for IPTV Channels'),
      thumb   = R(AIPTV_SEARCH)
    ))

  return oc

################################################################################
@route(PREFIX+'/channels')
def aiptv_channels():

  oc = ObjectContainer()

  oc.add(DirectoryObject(
    key = Callback(
      aiptv_channels_list,
      order = 'document'
    ),
	  title = L("Document Order"),
    summary = L("all IPTV channels in document order"),
    thumb = R(AIPTV_DOCUMENTORDER)
  ))

  oc.add(DirectoryObject(
    key = Callback(
      aiptv_channels_list,
      order = '+title'
    ),
	  title = L("Sort by Title - Asc"),
    summary = L("all IPTV channels in alphabetic ascending order"),
    thumb = R(AIPTV_ASCENDING)
  ))

  oc.add(DirectoryObject(
    key = Callback(
      aiptv_channels_list,
      order = '-title'
    ),
	  title = L("Sort by Title - Desc"),
    summary = L("all IPTV channels in alphabetic descending order"),
    thumb = R(AIPTV_DESCENDING)
  ))

  oc.add(DirectoryObject(
    key = Callback(
      aiptv_channels_list,
      order = 'shuffle'
    ),
	  title = L("Shuffle"),
    summary = L("show IPTV channels in random order"),
    thumb = R(AIPTV_SHUFFLE)
  ))

  return oc

################################################################################
@route(PREFIX+'/channels/list', page = int)
def aiptv_channels_list(order, page = 1):

  oc = ObjectContainer(
    title2 = L('All Channels') + ' | ' + L('Page') + ' ' + str(page)
  )

  if order == 'shuffle':
    oc = ObjectContainer(
      title2 = L('All Channels') + ' | ' + L('Page') + ' ' + str(page),
      no_cache = True
    )

  datastring = aiptv_get_XSPF_string(Prefs["playlist"])
  data = etree.parse(StringIO(datastring))

  if order == '+title':
    sortXSLT = Resource.Load("sort.xslt", binary = True)
    sortTransformation = etree.parse(StringIO(sortXSLT))
    data = data.xslt(sortTransformation, dir="'ascending'")
  elif order == '-title':
    sortXSLT = Resource.Load("sort.xslt", binary = True)
    sortTransformation = etree.parse(StringIO(sortXSLT))
    data = data.xslt(sortTransformation, dir="'descending'")
  elif order == 'shuffle':
    shuffleXSLT = Resource.Load("shuffle.xslt", binary = True)
    shuffleTransformation = etree.parse(StringIO(shuffleXSLT))
    rnumber = randint(1, 1000000)
    data = data.xslt(shuffleTransformation, iseed=unicode(rnumber))

  channels = data.xpath(
    '//p:track',
    namespaces = {
      'p': 'http://xspf.org/ns/0/'
    }
  )

  if len(channels) > 0:
    items_per_page = int( Prefs['items_per_page'] )
    first = ( page - 1 ) * items_per_page
    last = first + items_per_page
    for channel in channels[first:last]:
      (url, title, summary, thumb, art) = aiptv_compute(channel)
      oc.add(CreateVideoClipObject(
        url = url,
        title = title,
        summary = summary,
        thumb = thumb
      ))

    if len(channels) > last:
      oc.add(NextPageObject(
        key = Callback(
          aiptv_channels_list,
          order = order,
          page = page + 1
        ),
        title = L('Next') + ' >>'
      ))

  return oc

################################################################################
@route(PREFIX+'/category')
def aiptv_categories():

  oc = ObjectContainer(
    title2 = L('Categories')
  )

  datastring = aiptv_get_XSPF_string(Prefs["playlist"])
  data = XML.ElementFromString(datastring)
  if AIPTV_DEBUG: Log.Debug(data)
  categories = data.xpath(
    '//p:meta[@rel="group-title"]/text()',
    namespaces = {
      'p': 'http://xspf.org/ns/0/'
    }
  )
  categories = list(set(categories))
  categories.sort()
  if AIPTV_NO_CATEGORY not in categories: categories.append(AIPTV_NO_CATEGORY)

  for category in categories:
    oc.add(DirectoryObject(
      key = Callback(
        aiptv_category,
        category = category
      ),
      title = category.upper(),
      thumb = R(AIPTV_CATEGORIES)
    ))

  return oc

################################################################################
@route(PREFIX+'/category/{category}', page = int)
def aiptv_category(category):

  oc = ObjectContainer()

  oc.add(DirectoryObject(
    key = Callback(
      aiptv_category_list,
      category = category,
      order = 'document'
    ),
	  title = L("Document Order"),
    summary = category + " | " + L("Channels in document order"),
    thumb = R(AIPTV_DOCUMENTORDER)
  ))

  oc.add(DirectoryObject(
    key = Callback(
      aiptv_category_list,
      category = category,
      order = '+title'
    ),
	  title = L("Sort by Title - Asc"),
    summary = category + " | " + L("Channels in alphabetic ascending order"),
    thumb = R(AIPTV_ASCENDING)
  ))

  oc.add(DirectoryObject(
    key = Callback(
      aiptv_category_list,
      category = category,
      order = '-title'
    ),
	  title = L("Sort by Title - Desc"),
    summary = category + " | " + L("Channels in alphabetic descending order"),
    thumb = R(AIPTV_DESCENDING)
  ))

  oc.add(DirectoryObject(
    key = Callback(
      aiptv_category_list,
      category = category,
      order = 'shuffle'
    ),
	  title = L("Shuffle"),
    summary = category + " | " + L("Channels in random order"),
    thumb = R(AIPTV_SHUFFLE)
  ))

  return oc

################################################################################
@route(PREFIX+'/category/{category}/list', page = int)
def aiptv_category_list(category, order, page = 1):

  oc = ObjectContainer(
    title2 = unicode(category).upper() + ' | ' + L('Page') + ' ' + str(page)
  )

  if order == 'shuffle':
    oc = ObjectContainer(
      title2 = unicode(category).upper() + ' | ' + L('Page') + ' ' + str(page),
      no_cache = True
    )

  nochannels = ObjectContainer(
    title2 = unicode(L('No Channels')),
    header   = L('no channels'),
    message  = L('no channels on this category'),
    no_cache = True
  )

  datastring = aiptv_get_XSPF_string(Prefs["playlist"])
  data = etree.parse(StringIO(datastring))

  if order == '+title':
    sortXSLT = Resource.Load("sort.xslt", binary = True)
    sortTransformation = etree.parse(StringIO(sortXSLT))
    data = data.xslt(sortTransformation, dir="'ascending'")
  elif order == '-title':
    sortXSLT = Resource.Load("sort.xslt", binary = True)
    sortTransformation = etree.parse(StringIO(sortXSLT))
    data = data.xslt(sortTransformation, dir="'descending'")
  elif order == 'shuffle':
    shuffleXSLT = Resource.Load("shuffle.xslt", binary = True)
    shuffleTransformation = etree.parse(StringIO(shuffleXSLT))
    rnumber = randint(1, 1000000)
    data = data.xslt(shuffleTransformation, iseed=unicode(rnumber))

  if category == AIPTV_NO_CATEGORY:
    channels = data.xpath(
      '//p:track[not(p:meta[@rel="group-title"])]',
      namespaces = {
        'p': 'http://xspf.org/ns/0/'
      }
    )
  else:
    channels = data.xpath(
      '//p:track[p:meta[@rel="group-title"]/text() = "' + category + '"]',
      namespaces = {
        'p': 'http://xspf.org/ns/0/'
      }
    )

  if len(channels) > 0:
    items_per_page = int( Prefs['items_per_page'] )
    first = ( page - 1 ) * items_per_page
    last = first + items_per_page
    for channel in channels[first:last]:
      (url, title, summary, thumb, art) = aiptv_compute(channel)
      oc.add(CreateVideoClipObject(
        url = url,
        title = title,
        summary = summary,
        thumb = thumb
      ))

    if len(channels) > last:
      oc.add(NextPageObject(
        key = Callback(
          aiptv_category_list,
          category = category,
          order = order,
          page = page + 1
        ),
        title = L('Next') + ' >>'
      ))

    return oc
  else:
    return nochannels  

################################################################################
@route(PREFIX+'/alpha')
def aiptv_alpha():

  oc = ObjectContainer(
    title2 = L('Alphabetic')
  )

  for character in list(ALPHABET):
    oc.add(DirectoryObject(
      key = Callback(
        aiptv_alpha_list,
        char = character
      ),
      title = character.upper(),
      thumb = R(AIPTV_ALPHA)
    ))

  return oc

################################################################################
@route(PREFIX+'/alpha/{char}', page = int)
def aiptv_alpha_list(char, page = 1):

  oc = ObjectContainer(
    title2 = unicode(char).upper() + ' | ' + L('Page') + ' ' + str(page)
  )

  datastring = aiptv_get_XSPF_string(Prefs["playlist"])
  data = etree.parse(StringIO(datastring))

  sortXSLT = Resource.Load("sort.xslt", binary = True)
  sortTransformation = etree.parse(StringIO(sortXSLT))
  data = data.xslt(sortTransformation)

  xpathstring = '//p:track[p:title[starts-with(text(), "' + char.lower() + '")]] | //p:track[p:title[starts-with(text(), "' + char.upper() + '")]]'
  channels = data.xpath(
    xpathstring,
    namespaces = {
      'p': 'http://xspf.org/ns/0/'
    }
  )

  if len(channels) > 0:
    items_per_page = int( Prefs['items_per_page'] )
    first = ( page - 1 ) * items_per_page
    last = first + items_per_page
    for channel in channels[first:last]:
      (url, title, summary, thumb, art) = aiptv_compute(channel)
      oc.add(CreateVideoClipObject(
        url = url,
        title = title,
        summary = summary,
        thumb = thumb
      ))

    if len(channels) > last:
      oc.add(NextPageObject(
        key = Callback(
          aiptv_alpha_list,
          char = char,
          page = page + 1
        ),
        title = L('Next') + ' >>'
      ))

  return oc

################################################################################
@route(PREFIX + '/search', page = int)
def aiptv_search(query, page = 1):

  oc = ObjectContainer(
    title2 = L('Search Results') + ': ' + query + ' | ' + L('Page') + ' ' + str(page)
  )

  noresults = ObjectContainer(
    title2 = unicode(L('Search Results') + ': ' + query + ' | ' + L('Page') + ' ' + str(page)),
    header   = L('no matching channels'),
    message  = L('no matching channels'),
    no_cache = True
  )

  datastring = aiptv_get_XSPF_string(Prefs["playlist"])
  data = XML.ElementFromString(datastring)
  xpathstring = '//p:track[p:title[contains(translate(text(), "ABCDEFGHJIKLMNOPQRSTUVWXYZ", "abcdefghjiklmnopqrstuvwxyz"), "' + query.lower() + '")]]'
  channels = data.xpath(
    xpathstring,
    namespaces = {
      'p': 'http://xspf.org/ns/0/'
    }
  )

  if len(channels) > 0:
    items_per_page = int( Prefs['items_per_page'] )
    first = ( page - 1 ) * items_per_page
    last = first + items_per_page
    for channel in channels[first:last]:
      (url, title, summary, thumb, art) = aiptv_compute(channel)
      oc.add(CreateVideoClipObject(
        url = url,
        title = title,
        summary = summary,
        thumb = thumb
      ))

    if len(channels) > last:
      oc.add(NextPageObject(
        key = Callback(
          aiptv_search,
          query = query,
          page = page + 1
        ),
        title = L('Next') + ' >>'
      ))

    return oc
  else:
    return noresult

################################################################################
@route(PREFIX + '/createvideoclipobject')
def CreateVideoClipObject(url, title, summary, thumb, container = False):
  video = VideoClipObject(
    key = Callback(
      CreateVideoClipObject,
      url = url,
      title = title,
      summary = summary,
      thumb = thumb,
      container = True
    ),
    rating_key = url,
    title = title,
    thumb = Resource.ContentsOfURLWithFallback(url = thumb),
    summary = summary,
    items = [
      MediaObject(
        container = Container.MP4,
        video_codec = VideoCodec.H264,
        audio_codec = AudioCodec.AAC,
        audio_channels = 2,
        parts = [
          PartObject(
            key = url
          )
        ],
        optimized_for_streaming = True
      )
    ]
  )

  if container:
    return ObjectContainer(objects = [video])
  else:
    return video

################################################################################
def aiptv_compute(channel):

  url = channel.xpath(
    'p:location/text()',
    namespaces = {
      'p': 'http://xspf.org/ns/0/'
    }
  )[0]

  title = channel.xpath(
    'p:title/text()',
    namespaces = {
      'p': 'http://xspf.org/ns/0/'
    }
  )[0]

  try:
    summary = channel.xpath(
      'p:annotation/text()',
      namespaces = {
        'p': 'http://xspf.org/ns/0/'
      }
    )[0]
  except:
    summary = ""

  try:
    thumb = channel.xpath(
      'p:image/text()',
      namespaces = {
        'p': 'http://xspf.org/ns/0/'
      }
    )[0]
  except:
    thumb = ""

  try:
    art = channel.xpath(
      'p:meta[@rel="art"]/text()',
      namespaces = {
        'p': 'http://xspf.org/ns/0/'
      }
    )[0]
  except:
    art = thumb

  return (
    url,
    title,
    summary,
    thumb,
    art
  )

################################################################################
def aiptv_get_XSPF_string(filename):
  if filename.endswith('.xspf'):
    return Resource.Load(filename, binary = True)
  elif filename.endswith('.m3u') or filename.endswith('.m3u8'):
    return M3U2XSPF().parse(Resource.Load(filename, binary = True)).read()
  else:
    return ""

################################################################################
def L(string):
  Request.Headers['X-Plex-Language'] = Prefs["language"].split("/")[1]
  local_string = Locale.LocalString(string)
  return str(local_string).decode()
