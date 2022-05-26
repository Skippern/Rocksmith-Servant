import os
import sqlite3

from time import sleep

from config.configReader import ConfigReader
from modules.cdlc_importer.load_cdlc_json_file import CDLCImporter
from modules.file_manager.cdlc_file_manager import FileManager
from modules.scene_switcher.scene_switcher import SceneSwitcher
from modules.setlist.setlist_logger import SetlistLogger
from modules.song_loader.song_loader import SongLoader
from utils import logger, rs_playlist
from utils.debug import Debugger
from utils.exceptions import RocksnifferConnectionError, ConfigError
from utils.rocksniffer import Rocksniffer

db = sqlite3.connect('servant.db')

debug_log_level = True


def check_enabled_module_dependencies():
    if song_loader.enabled and not file_manager.enabled:
        raise ConfigError("Please enable FileManager if you wanna use the SongLoader!")


HEARTBEAT = 0.1

logger.warning("------------------------------------------------------------------------")
logger.warning("----- SERVANT IS STARTING ----------------------------------------------")
logger.warning("------------------------------------------------------------------------")

# TODO move this to config.py and use it everywhere? Also in config reader we could use them!
# Section name definitions
SECTION_ROCK_SNIFFER = "RockSniffer"
SECTION_SETLIST_LOGGER = "SetlistLogger"
SECTION_CDLC_IMPORTER = "CDLCImporter"
SECTION_SONG_LOADER = "SongLoader"
SECTION_SCENE_SWITCHER = "SceneSwitcher"
SECTION_FILE_MANAGER = "FileManager"
# OBS
# Behaviour
SECTION_DEBUGGING = "Debugging"

# Key name definitions
KEY_ENABLED = "enabled"

# Initializing configuration
conf = ConfigReader()

# Initializing modules and utils
sniffer = Rocksniffer(
    conf.get_bool(SECTION_ROCK_SNIFFER, KEY_ENABLED),
    conf.get(SECTION_ROCK_SNIFFER, "host"),
    conf.get(SECTION_ROCK_SNIFFER, "port")
)
setlist_logger = SetlistLogger(
    conf.get_bool(SECTION_SETLIST_LOGGER, KEY_ENABLED),
    conf.get(SECTION_SETLIST_LOGGER, "setlist_path")
)
file_manager = FileManager(
    conf.get_bool(SECTION_FILE_MANAGER, KEY_ENABLED),
    conf.get_set(SECTION_FILE_MANAGER, "source_directories"),
    conf.get(SECTION_FILE_MANAGER, "destination_directory"),
    conf.get(SECTION_FILE_MANAGER, "using_cfsm")
)
cdlc_importer = CDLCImporter(db)
song_loader = SongLoader(
    conf.get_bool(SECTION_SONG_LOADER, KEY_ENABLED),
    conf.get(SECTION_SONG_LOADER, "PHPSESSID"),
    conf.get(SECTION_SONG_LOADER, "cdlc_dir"),
    conf.get(SECTION_SONG_LOADER, "cfsm_file_name"),
    conf.get(SECTION_SONG_LOADER, "cdlc_archive_dir"),
    file_manager.destination_directory,
    conf.get(SECTION_SONG_LOADER, "rocksmith_cdlc_dir"),
    conf.get(SECTION_SONG_LOADER, "cdlc_import_json_file"),
    conf.get_bool(SECTION_SONG_LOADER, "allow_load_when_in_game")
)
scene_switcher = SceneSwitcher(
    conf.get_bool(SECTION_SCENE_SWITCHER, KEY_ENABLED)
)
check_enabled_module_dependencies()

# TODO OBS
# TODO Behaviour

# Initializing Debugger
debugger = Debugger(
    conf.get_bool(SECTION_DEBUGGING, "debug"),
    conf.get(SECTION_DEBUGGING, "debug_log_interval", int)
)


# TODO extend with other values!
# TODO can not this be in the Module itself?
def update_config():
    if conf.reload_if_changed():
        # Updating Rocksniffer Configurations
        sniffer.enabled = conf.get_bool(SECTION_ROCK_SNIFFER, KEY_ENABLED)
        sniffer.host = conf.get(SECTION_ROCK_SNIFFER, "host")
        sniffer.port = conf.get(SECTION_ROCK_SNIFFER, "port")

        # Updating Setlist Configurations
        setlist_logger.enabled = conf.get_bool(SECTION_SETLIST_LOGGER, KEY_ENABLED)
        setlist_logger.setlist_path = conf.get(SECTION_SETLIST_LOGGER, "setlist_path")
        # TODO this should be maybe in run or in song_loader?
        setlist_logger.create_setlist_directory()

        # Updating Song Loader Configurations
        song_loader.enabled = conf.get_bool(SECTION_SONG_LOADER, KEY_ENABLED)
        song_loader.cdlc_dir = conf.get(SECTION_SONG_LOADER, "cdlc_dir")
        song_loader.cfsm_file_name = conf.get(SECTION_SONG_LOADER, "cfsm_file_name")
        song_loader.cdlc_archive_dir = song_loader.check_cdlc_archive_dir(
            conf.get(SECTION_SONG_LOADER, "cdlc_archive_dir"))
        song_loader.destination_directory = file_manager.destination_directory
        song_loader.rocksmith_cdlc_dir = song_loader.check_cdlc_archive_dir(
            conf.get(SECTION_SONG_LOADER, "rocksmith_cdlc_dir"))
        song_loader.cdlc_import_json_file = conf.get(SECTION_SONG_LOADER, "cdlc_import_json_file")
        song_loader.allow_load_when_in_game = conf.get_bool(SECTION_SONG_LOADER, "allow_load_when_in_game")
        song_loader.phpsessid = rs_playlist.check_phpsessid(conf.get(SECTION_SONG_LOADER, "phpsessid"))
        # TODO all this props should be maybe in run or in song_loader?
        song_loader.songs_to_load = os.path.join(song_loader.cdlc_dir, song_loader.cfsm_file_name)
        song_loader.create_directories()

        # Updating Scene Switcher Configurations
        scene_switcher.enabled = conf.get_bool(SECTION_SCENE_SWITCHER, KEY_ENABLED)

        # Updating FileManager Configurations
        file_manager.enabled = conf.get_bool(SECTION_FILE_MANAGER, KEY_ENABLED)
        file_manager.source_directories = conf.get_set(SECTION_FILE_MANAGER, "source_directories")
        file_manager.destination_directory = conf.get(SECTION_FILE_MANAGER, "destination_directory")
        file_manager.using_cfsm = conf.get(SECTION_FILE_MANAGER, "using_cfsm")

        # TODO OBS
        # TODO Behaviour

        # Updating Debug Configurations
        debugger.debug = conf.get_bool(SECTION_DEBUGGING, "debug")
        debugger.interval = conf.get_int_value(SECTION_DEBUGGING, "debug_log_interval")

        check_enabled_module_dependencies()


# TODO move to debug Class?
def get_debug_message():
    # TODO OBS
    # TODO Behaviour
    modules_str = "--- Enabled modules ---" + os.linesep
    if sniffer.enabled:
        modules_str += SECTION_ROCK_SNIFFER + os.linesep
    if setlist_logger.enabled:
        modules_str += SECTION_SETLIST_LOGGER + os.linesep
    if song_loader.enabled:
        modules_str += SECTION_CDLC_IMPORTER + os.linesep
        modules_str += SECTION_SONG_LOADER + os.linesep
    if scene_switcher.enabled:
        modules_str += SECTION_SCENE_SWITCHER + os.linesep
    if file_manager.enabled:
        modules_str += SECTION_FILE_MANAGER + os.linesep
    modules_str += "---------------" + os.linesep

    sniffer_str = "Song: {sniffer.artistName} - {sniffer.songName} " \
                  "({sniffer.albumYear}, {sniffer.albumName}), " \
                  "duration:{sniffer.songLength}s " \
                  "".format(sniffer=sniffer) + os.linesep

    debug_str = "Debug: {0} interval: {1}".format(str(debugger.debug), str(debugger.interval)) + os.linesep

    setlist = "Setlist: {0}".format(str(setlist_logger.setlist)) + os.linesep

    return os.linesep + modules_str + sniffer_str + debug_str + setlist


def in_game():
    return sniffer.enabled and sniffer.in_game and not sniffer.in_pause


def put_the_song_into_the_setlist():
    if setlist_logger.enabled and in_game():
        setlist_logger.log_a_song(sniffer.artistName + " - " + sniffer.songName)


def update_game_information():
    if sniffer.enabled:
        try:
            sniffer_not_loaded_before = sniffer_data_not_loaded()
            if sniffer_not_loaded_before:
                logger.warning("Trying to connect to RockSniffer to get the information from Rocksmith...")
            sniffer.update()
            if sniffer_not_loaded_before and sniffer_data_loaded():
                logger.warning("...connected to RockSniffer...sniffing")
        except RocksnifferConnectionError as rce:
            sniffer.memory = None
            raise rce


def sniffer_data_loaded():
    return sniffer.memory and sniffer.memory is not None


def sniffer_data_not_loaded():
    return not sniffer_data_loaded()


cdlc_importer.load()

# Main 'endless' loop
while True:

    try:
        # Sleep a bit to avoid too fast processing
        sleep(HEARTBEAT)

        update_config()

        scene_switcher.run()
        file_manager.run()
        song_loader.run()
        update_game_information()
        put_the_song_into_the_setlist()

        # Interval debugging
        debugger.log_on_interval(get_debug_message())

    # Catch and log all the exceptions, but keep app alive.
    except Exception as e:
        logger.error(e)
