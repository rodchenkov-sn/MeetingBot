import pytest

from lines import LinesRepo


ESSENTIAL_LANGUAGES = ['en', 'ru']
DEFAULT_USER_ID = 1
DEFAULT_USER_LANGUAGE = 'en'
DEFAULT_USER_UPDATE_LANGUAGE = 'ru'
DEFAULT_LINE_NAME = 'help_help'
DEFAULT_LINE_EN = 'to see this message'
DEFAULT_LINE_RU = 'чтобы увидеть это сообщение'


@pytest.fixture()
def repo() -> LinesRepo:
    repo = LinesRepo()
    return repo


def test_get_all_languages(repo: LinesRepo):
    repo_languages = repo.get_all_languages()
    for language in ESSENTIAL_LANGUAGES:
        assert language in repo_languages


def test_get_user_language(repo: LinesRepo):
    user_language = repo.get_user_language(DEFAULT_USER_ID)
    assert user_language == DEFAULT_USER_LANGUAGE


def test_update_user_language(repo: LinesRepo):
    user_language = repo.get_user_language(DEFAULT_USER_ID)
    assert user_language == DEFAULT_USER_LANGUAGE
    user_language = repo.update_user_language(DEFAULT_USER_ID, DEFAULT_USER_UPDATE_LANGUAGE)
    assert user_language == DEFAULT_USER_UPDATE_LANGUAGE
    user_language = repo.update_user_language(DEFAULT_USER_ID, DEFAULT_USER_LANGUAGE)
    assert user_language == DEFAULT_USER_LANGUAGE


def test_get_line(repo: LinesRepo):
    help_line = repo.get_line(DEFAULT_LINE_NAME, DEFAULT_USER_ID)
    assert help_line == DEFAULT_LINE_EN
    repo.update_user_language(DEFAULT_USER_ID, DEFAULT_USER_UPDATE_LANGUAGE)
    help_line = repo.get_line(DEFAULT_LINE_NAME, DEFAULT_USER_ID)
    assert help_line == DEFAULT_LINE_RU
