import os
from enum import unique, Enum


@unique
class State(Enum):
    # -- New request on the rsplaylist
    NEW_REQUEST = 10
    # -- Could not be found in the archive and not loaded in the game
    TO_DOWNLOAD = 20
    # --
    FOUND_IN_ARCHIVE = 30
    MOVED_FROM_ARCHIVE = 31
    LOADED = 32
    # --
    OUT_FROM_THE_PLAYLIST = 40


class SongData:
    def __init__(self, rspl_request_id, cdlc_id, rspl_song_id, artist=None, title=None, song_file_name=None):
        self.rspl_request_id = rspl_request_id  # id of the request on RSPL
        self.rspl_song_id = rspl_song_id  # id of the request on RSPL
        self.cdlc_id = cdlc_id
        self.artist = artist
        self.title = title
        self.artist_title = None
        if artist and title:
            self.artist_title = artist + " - " + title

        self.rspl_official = None
        self.rspl_position = None
        self.song_file_name = song_file_name
        # --
        self.state = State.NEW_REQUEST
        self.tags = set()
        # --
        self.found_in_db = False
        self.loaded_under_the_game = False

    @property
    def is_official(self):
        # TODO is there any other official numbers? Maybe only 0 means non official?
        return self.rspl_official and (self.rspl_official == 3 or self.rspl_official == 4)

    # @property
    # def rspl_official(self):
    #     return self.rspl_official

    # @__rspl_official.setter
    # def rspl_official(self, value):
    #     self.rspl_official = value

    # TODO rspl_request_id? or cdlc_id? or something else?
    def __eq__(self, other):
        return self.rspl_request_id == other.rspl_request_id

    def __hash__(self):
        return hash(self.rspl_request_id)

    def __repr__(self):
        return os.linesep + '<SongData: ' \
                            'rspl_request_id={}, ' \
                            'rspl_song_id={}, ' \
                            'cdlc_id={}, ' \
                            'artist={}, ' \
                            'title={}, ' \
                            'artist_title={}, ' \
                            'rspl_official={}, ' \
                            'song_file_name={}' \
                            '>'.format(self.rspl_request_id,
                                       self.rspl_song_id,
                                       self.cdlc_id,
                                       self.artist,
                                       self.title,
                                       self.artist_title,
                                       self.rspl_official,
                                       self.song_file_name)

# TODO remove this later if the eq is decided!
# s1 = SongData(1, 555, 'asd')
# s2 = SongData(2, 666, 'qwe')
# s3 = SongData(1, 777, '123')

# song_data_set = {s1, s2, s3}
# print(song_data_set)
# output:
# {
# <SongData: rspl_request_id=1, cdlc_id=555, song_file_name=asd>,
# <SongData: rspl_request_id=2, cdlc_id=666, song_file_name=qwe>}
