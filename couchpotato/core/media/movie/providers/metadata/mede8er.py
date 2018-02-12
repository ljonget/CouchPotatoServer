from xml.etree.ElementTree import Element, SubElement, tostring
import os
import re
import traceback
import xml.dom.minidom

from couchpotato.core.media.movie.providers.metadata.base import MovieMetaData
from couchpotato.core.helpers.encoding import toUnicode
from couchpotato.core.helpers.variable import getTitle
from couchpotato.core.logger import CPLog

autoload = 'Mede8er'

log = CPLog(__name__)


class Mede8er(MovieMetaData):

    def getFanartName(self, name, root, i):
        return self.createMetaName('%s-fanart.jpg', name, root)
    
    def getThumbnailName(self, name, root, i):
        return self.createMetaName('%s.jpg', name, root)

    def createMetaName(self, basename, name, root):
        return os.path.join(root, basename.replace('%s', name))

    def getNfoName(self, name, root, i):
        return self.createMetaName('%s.xml', name, root)

    def getNfo(self, movie_info=None, data=None, i=0):
        if not data: data = {}
        if not movie_info: movie_info = {}

        xml = Element('details')
        movie_root = SubElement(xml, 'movie')
        movie_root.attrib["isExtra"] = "false"
        movie_root.attrib["isSet"] = "false"
        movie_root.attrib["isTV"] = "false"

        # Title
        try:
            el = SubElement(movie_root, 'title')
            el.text = toUnicode(getTitle(data))
        except:
            pass

        # IMDB id
        try:
            imdb_id = etree.SubElement(movie_root, "id")
            imdb_id.attrib["moviedb"] = "imdb"
            imdb_id.text = myShow['imdb_id']
        except:
            pass

        # Runtime
        try:
            runtime = SubElement(movie_root, 'runtime')
            runtime.text = '%s min' % movie_info.get('runtime')
        except:
            pass

        # Other values
        types = ['year', 'mpaa', 'original_title', 'outline', 'plot', 'tagline', 'releaseDate:released']
        for type in types:

            if ':' in type:
                name, type = type.split(':')
            else:
                name = type

            try:
                if movie_info.get(type):
                    el = SubElement(movie_root, name)
                    el.text = toUnicode(movie_info.get(type, ''))
            except:
                pass

        # Rating
        for rating_type in ['imdb', 'rotten', 'tmdb']:
            try:
                r, v = movie_info['rating'][rating_type]
                rating = SubElement(movie_root, 'rating')
                rating.text = str(r)
                votes = SubElement(movie_root, 'votes')
                votes.text = str(v)
                break
            except:
                log.debug('Failed adding rating info from %s: %s', (rating_type, traceback.format_exc()))

        # Genre
        Genres = SubElement(movie_root, "genres")
        for genre in movie_info.get('genres', []):
                genres = SubElement(Genres, "Genre")
                genres.text = toUnicode(genre)          

        # Actors
        Actors = SubElement(movie_root, "cast")
        for actor_name in movie_info.get('actor_roles', {}):
            actor = SubElement(Actors, 'actor')
            actor.text = toUnicode(actor_name)

        # Directors
        for director_name in movie_info.get('directors', []):
            director = SubElement(movie_root, 'director')
            director.text = toUnicode(director_name)

        # Images / Thumbnail
        for image_url in movie_info['images']['poster_original']:
            image = SubElement(movie_root, 'thumb')
            image.text = toUnicode(image_url)

        # Images / Thumbnail
        for image_url in movie_info['images']['backdrop_original']:
            image = SubElement(movie_root, 'fanart')
            image.text = toUnicode(image_url)

        # Add file metadata
        # Video data
        if data['meta_data'].get('video'):
            vcodec = SubElement(movie_root, 'videoCodec')
            vcodec.text = toUnicode(data['meta_data']['video'])
            resolution = SubElement(movie_root, 'resolution')
            resolution.text = str(data['meta_data']['resolution_width']) + "x" + str(data['meta_data']['resolution_height'])

        # Audio data
        if data['meta_data'].get('audio'):
            acodec = SubElement(movie_root, 'audioCodec')
            acodec.text = toUnicode(data['meta_data'].get('audio'))
            channels = SubElement(movie_root, 'audioChannels')
            channels.text = toUnicode(data['meta_data'].get('audio_channels'))

        # Clean up the xml and return it
        xml = xml.dom.minidom.parseString(tostring(xml))
        xml_string = xml.toprettyxml(indent = '  ')
        text_re = re.compile('>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)
        xml_string = text_re.sub('>\g<1></', xml_string)

        return xml_string.encode('utf-8')


config = [{
    'name': 'mede8er',
    'groups': [
        {
            'tab': 'renamer',
            'subtab': 'metadata',
            'name': 'mede8er_metadata',
            'label': 'Mede8er',
            'description': 'Metadata for Mede8er',
            'options': [
                {
                    'name': 'meta_enabled',
                    'default': False,
                    'type': 'enabler',
                },
                {
                    'name': 'meta_xml',
                    'label': 'XML',
                    'default': True,
                    'type': 'bool',
                    'description': 'Generate metadata xml',
                },
                {
                    'name': 'meta_thumbnail',
                    'label': 'Thumbnail',
                    'default': True,
                    'type': 'bool',
                    'description': 'Generate thumbnail jpg',
                },
                {
                    'name': 'meta_fanart',
                    'label': 'Fanart ',
                    'default': True,
                    'type': 'bool',
                    'description': 'Generate Fanart jpg',
                }
            ],
        },
    ],
}]
