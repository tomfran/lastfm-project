from abstract_classes import AbstractLogCDC
import time
from datetime import datetime
import json

class ListeningSessionsCDC(AbstractLogCDC):

    def __init__(self, source, destination, syncFile, chrono_attr, sync_attr, songs_file_path):
        super().__init__(source, destination, syncFile, chrono_attr, sync_attr)
        self.songs_file_path = songs_file_path

    def save_songs_to_request(self, songs_dict):
        path = f"{self.songs_file_path}/{datetime.today().strftime('%Y%m%d')}.json"
        with open(path, 'a+') as f:
            f.write(json.dumps(songs_dict, indent=4, sort_keys=True))

    def access_fields(self, table):
        songs_dict = {}
        def process_track(tr, user):
            artist = tr['artist']['#text']
            name = tr['name']
            key = hash(artist + name)
            songs_dict[key] = {"artist": artist, "name" : name}
            return {
                'user_id' : user,
                'song_id' : key,
                'ts' : int(tr['date']['uts'])
            }
        user = table['recenttracks']['@attr']['user']
        ret = [process_track(e, user=user) for e in table['recenttracks']['track']]
        self.save_songs_to_request(songs_dict)
        return ret

if __name__ == "__main__":
    from api_source import ApiSource
    from cloud_datalake import CloudDatalake
    source = ApiSource(method='user.getrecenttracks', method_params={'user' : 'giacomo109', 'from' : '1608398626'}, other_params={'limit':500})
    datalake = CloudDatalake('data/datalake_log')
    cdc = ListeningSessionsCDC(source, datalake, 'data/datalake_log/sync.json', 'threshold', 'ts', 'data/datalake_log')
    cdc.get_fresh_rows()