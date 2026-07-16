from plex_auto_languages.plex_server import PlexServer
from tests.fakes import FakeEpisode


class StubConfig:
    def __init__(self, **values):
        self._values = values

    def get(self, key):
        return self._values.get(key)


def _server(**config_values):
    """Bind the methods to a bare object carrying only .config.

    Constructing a real PlexServer would open a connection; these methods only
    ever read self.config.
    """
    server = object.__new__(PlexServer)
    server.config = StubConfig(**config_values)
    return server


def test_should_ignore_library_exact_match():
    s = _server(ignore_libraries=["Movies", "KidTube"])
    assert s.should_ignore_library("KidTube") is True
    assert s.should_ignore_library("TV Shows") is False


def test_should_ignore_library_is_case_sensitive():
    s = _server(ignore_libraries=["KidTube"])
    assert s.should_ignore_library("kidtube") is False


def test_should_ignore_filepath_returns_false_when_no_patterns():
    # The shipped default is [""], which filters to [] -> always False.
    s = _server(ignore_filepatterns=[""])
    assert s.should_ignore_filepath(FakeEpisode(files=("/media/anything.mkv",))) is False


def test_should_ignore_filepath_does_not_touch_media_when_disabled():
    # The early return must happen before episode.media is read: media access is
    # a lazy plexapi load, and this runs on the hot alert path.
    class Exploding(FakeEpisode):
        @property
        def media(self):
            raise AssertionError("episode.media must not be touched when no patterns are configured")

        @media.setter
        def media(self, value):
            pass

    s = _server(ignore_filepatterns=[""])
    assert s.should_ignore_filepath(Exploding()) is False


def test_should_ignore_filepath_matches_pattern_case_insensitively():
    s = _server(ignore_filepatterns=["/pinchflat/"])
    assert s.should_ignore_filepath(FakeEpisode(files=("/media/Pinchflat/x.mkv",))) is True


def test_should_ignore_filepath_false_when_no_part_matches():
    s = _server(ignore_filepatterns=["/pinchflat/"])
    assert s.should_ignore_filepath(FakeEpisode(files=("/media/tv/x.mkv",))) is False


def test_should_ignore_filepath_matches_any_part():
    s = _server(ignore_filepatterns=["/pinchflat/"])
    ep = FakeEpisode(files=("/media/tv/x.mkv", "/media/pinchflat/y.mkv"))
    assert s.should_ignore_filepath(ep) is True


def test_should_ignore_filepath_tolerates_invalid_regex():
    s = _server(ignore_filepatterns=["[unclosed"])
    assert s.should_ignore_filepath(FakeEpisode(files=("/media/tv/x.mkv",))) is False
