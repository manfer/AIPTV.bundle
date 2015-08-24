AIPTV alternative IPTV Plex Channel

Copyright © 2015 Fernando San Julián

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see [http://www.gnu.org/licenses/](http://www.gnu.org/licenses/).

## AIPTV - Alternative IPTV Plex Media Server plugin ##
by [manfer], version [0.7][Changelog]

1. [Why AIPTV][1]
2. [Requirements][2]
3. [Installation][3]
4. [XSPF Playlist Structure][4]
5. [XSPF Playlist Example][5]
6. [What about M3U Playlists][6]

### Why AIPTV ###
Most [IPTV] playlists are [Extended M3U] playlists. [M3U] is a format which purpose is to define a playlist in a simple way, understanding by playlist a list of sources to be played in sequential order.

The first [M3U] playlist format was just a sequence of URIs each in one line.

Later [M3U] was extended to include some details for each track, a title and its duration. Its format is:

```
  #EXTINF:<duration>,<title>
```

As we can see in the linked IETF [Extended M3U] informational documentation it supports some other tags but those are not important for IPTV playlists.

More recently and to be used in IPTV applications someone decided to add some more metadata for each track just after the duration and before the comma that separates duration and title. Its format is:

```
  #EXTINF:<duration> [<key>="<value>" <key>="<value>" ...],<title>
```

The most commonly used key is group-title and it is used to group tracks. Other used keys are tvg-logo, tvg-id, tvg-name which are interpreted as EPG metadata.

All good. But as explained above these are playlists to be played in sequential order. The M3U format is not well structured to be handle in other ways.

So, what to do? We have long ago an open and free no propietary [XML] format called XML Shareable Playlist Format ([XSPF]) sponsored by [Xiph]. Its last specification [XSPF version 1] dates November 2006.

This format is a lot better than [M3U] and besides on being a [XML] format we can do all sorts of processing easily and fast. Like transformations with [XSLT] or searches with [XPath].

So, why we don't just use the rich [XSPF] format and deprecate [M3U]?

### Requirements ###
[Plex Media Server][GetPlex] installed

### Installation ###
1. Download the last version [zip archive](https://github.com/manfer/AIPTV.bundle/archive/v0.7.zip) and extract it to Plex plugin folder. For more details read the [official channel installation guide](https://support.plex.tv/hc/en-us/articles/201187656-How-do-I-manually-install-a-channel-):
  * on Windows: *C:\Users\USERNAME\AppData\Local\Plex Media Server\Plug-ins*
  * on Mac: *~Library/Application Support/Plex Media Server/Plug-ins*
  * on Linux: */usr/lib/plexmediaserver/Resources/Plug-ins* or */var/lib/plex/Plex Media Server/Plug-ins*
  * on FreeBSD *usr/pbi/plexmediaserver-amd64/plexdata/Plex\ Media\ Server/Plug-ins/*
2. Rename folder from *AIPTV.bundle-0.7* to *AIPTV.bundle*;
3. The Channel comes with a sample [XSPF] playlist so you can start using AIPTV Channel just after install. Add your [XSPF] or [Extended M3U] playlist in AIPTV Resources folder and configure AIPTV to use that playlist if you prefer to use your own.

### XSPF Playlist Structure ###
We are not going to use all the elements available in [XSPF version 1] specification because we don't need all of them. So the structure we will be using looks like this.

It starts with a header.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
```

Followed by optional metadata for the whole playlist. It can include a title, the author, a summary, date and an image. This metadata is optional and it is not being used in any way in this Plex Channel so include any or none at will. The image will be used in a future version as the default thumb for a track that has no image itself.

```xml
  <title>Sample List</title>
  <creator>Fernando San Julián</creator>
  <annotation>Sample List for Alternative IPTV Plex Plugin</annotation>
  <date>2015-06-09T08:47:17</date>
  <image>aiptv.png</image>
```

And we then include our track list.

```xml
  <trackList>
    <track>
      <location>http://brodilo.tv/channel.php</location>
      <title>Brodilo TV</title>
      <annotation>Brodilo TV Broadcast</annotation>
      <image>http://cs9748.vk.me/g22263923/a_5a6dcab0.jpg</image>
      <meta rel="art">http://brodilo.tv/screenshots/PriElbrus_out_81.jpg</meta>
      <meta rel="group-title">Other</meta>
    </track>
    <track>
      <location>http://flash.asaweb.com.br:1935/8306/8306/playlist.m3u8</location>
      <title>TV Mundo Maior</title>
      <annotation>TV Mundo Maior - São Paulo, Brazil</annotation>
      <image>http://i.imgur.com/tlhCwDQ.jpg</image>
      <meta rel="group-title">Education</meta>
      <meta rel="group-title">Religious</meta>
    </track>
  </trackList>
```

The track elements are self explanatory.

  - The location must contain the url of the stream.
  - The title is the name of the IPTV Channel.
  - The annotation is a descriptive text of the IPTV Channel.
  - The image is a logo to be used as the thumbnail for the IPTV Channel.
  - The art meta is a larger image to be used as background art for the IPTV Channel.
  - The group-title meta is used to catalog the channel in as many groups as you like.

Just a warning. All the data in between the tags must be of type character data ([CDATA]). This means that if the text contains one of the special characters <, >, &, those must be converted into its corresponding [Character Entity]. For example.

```
John & Sons <johnsons>
```

Must be converted into:

```
John &amp; Sons &lt;jonhsons&gt;
```

or otherwise included inside a CDATA section:

```xml
<![CDATA[John & Sons <jonhsons>]]>
```

Finally we must not forget to close the playlist tag.

```xml
</playlist>
```

### XSPF Playlist Example ###
```xml
<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
  <title>Sample List</title>
  <creator>Fernando San Julián</creator>
  <annotation>Sample List for Alternative IPTV Plex Plugin</annotation>
  <date>2015-06-09T08:47:17</date>
  <image>aiptv.png</image>
  <trackList>
    <track>
      <location>http://brodilo.tv/channel.php</location>
      <title>Brodilo TV</title>
      <annotation><![CDATA[Brodilo TV <Broadcast>]]></annotation>
      <image>http://cs9748.vk.me/g22263923/a_5a6dcab0.jpg</image>
      <meta rel="art">http://brodilo.tv/screenshots/PriElbrus_out_81.jpg</meta>
    </track>
    <track>
      <location>http://flash.asaweb.com.br:1935/8306/8306/playlist.m3u8</location>
      <title>TV Mundo Maior</title>
      <annotation>TV Mundo Maior - São Paulo, Brazil</annotation>
      <image>http://i.imgur.com/tlhCwDQ.jpg</image>
      <meta rel="group-title">Education</meta>
      <meta rel="group-title">Religious</meta>
    </track>
  </trackList>
</playlist>
```

### What about M3U Playlists ###

AIPTV Plex channel comes with a [Extended M3U] to [XSPF] parser so you can use [Extended M3U] playlists if needed.

It would be even better if you use the library which is bundle with this Plex Channel to convert your [Extended M3U] playlist to [XSPF] in a terminal and use that [XSPF] version of the playlist instead of the original to save some processing when using the Channel. Though anyway the parsing done on the fly is quite fast. I have tested with an [IPTV] playlist containing nearly 1700 channels and it works fluid so it shouldn't be a problem. Anyway I will insists that is even better to parse the file into an [XSPF] playlist and use that one instead.

You need python installed on your system to be able to use the parser from a terminal. Just open a terminal and go to the folder where the library is installed. It is inside the folder where you installed the AIPTV channel at path:

```
.../AIPTV.bundle/Contents/Library/Shared
```

When you are on that folder you can just parse a [Extended M3U] file by running the command:

```
./m3u2xspf.py -i <path_to_m3u_file>
```

That will create a [XSPF] playlist version of your [Extended M3U] playlist in the same folder and with same name but with extension .xspf instead of .m3u or .m3u8.

Move that new [XSPF] playlist file into the Resources folder inside AIPTV channel and configure the channel to use that playlist.

  [1]: #why-aiptv "Why AIPTV"
  [2]: #requirements "Requirements"
  [3]: #installation "Installation"
  [4]: #xspf-playlist-structure "XSPF Playlist Structure"
  [5]: #xspf-playlist-example "XSPF Playlist Example"
  [6]: #what-about-m3u-playlists "What about M3U Playlists"
  [Changelog]: https://github.com/manfer/AIPTV.bundle/blob/master/CHANGELOG.md
  [manfer]: https://github.com/manfer
  [manferplexforums]: https://forums.plex.tv/profile/244463/manfer
  [GetPlex]: https://www.plex.tv/downloads
  [IPTV]: http://en.wikipedia.org/wiki/IPTV
  [M3U]: https://en.wikipedia.org/wiki/M3U
  [Extended M3U]: https://tools.ietf.org/html/draft-pantos-http-live-streaming-07
  [Xiph]: https://www.xiph.org/
  [XSPF]: http://www.xspf.org/
  [XSPF version 1]: http://www.xspf.org/xspf-v1.html
  [XML]: http://www.w3.org/XML/
  [CDATA]: https://en.wikipedia.org/wiki/CDATA
  [Character Entity]: http://dev.w3.org/html5/html-author/charref
  [XSLT]: http://www.w3.org/TR/xslt
  [XPath]: http://www.w3.org/TR/xpath/
