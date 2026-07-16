from plex_auto_languages.plex_server import PlexServer
from tests.fakes import FakeEpisode, FakeShow, _Raises

short_name = PlexServer.get_episode_short_name


def test_short_name_includes_show_and_pads_numbers():
    ep = FakeEpisode(season_number=1, episode_number=2, show=FakeShow(title="Deli Boys"))
    assert short_name(ep) == "'Deli Boys' (S01E02)"


def test_short_name_without_show():
    ep = FakeEpisode(season_number=3, episode_number=4)
    assert short_name(ep, include_show=False) == "S03E04"


def test_short_name_with_none_numbers_falls_back_to_zero():
    ep = FakeEpisode(season_number=None, episode_number=None, show=FakeShow(title="X"))
    assert short_name(ep) == "'X' (S00E00)"


def test_short_name_with_empty_show_title():
    ep = FakeEpisode(season_number=1, episode_number=1, show=FakeShow(title=""))
    assert short_name(ep) == "'' (S01E01)"


def test_short_name_with_none_show_title_stringifies_it():
    # Pins today's real behaviour on the KidTube show (ratingKey 258471), whose
    # title is empty and whose episodes report grandparentTitle = None.
    # Note this is NOT "Unknown Show" - the None goes through the f-string.
    ep = FakeEpisode(season_number=1, episode_number=1, show=FakeShow(title=None))
    assert short_name(ep) == "'None' (S01E01)"


def test_short_name_returns_unknown_episode_when_show_lookup_raises():
    # plexapi raises NotFound rather than returning None; the bare except
    # returns the literal string "Unknown Episode", not None.
    ep = FakeEpisode(season_number=1, episode_number=1, show=_Raises())
    assert short_name(ep) == "Unknown Episode"
