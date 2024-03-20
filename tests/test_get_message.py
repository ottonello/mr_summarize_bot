import pytest

from mr.slack_bot import get_message, get_attachment_text


@pytest.fixture
def body():
    return {
        'token': 'rBDWXzdTkDzQo8ieKmXh2Ib4',
        'team_id': '', 'context_team_id': '',
        'context_enterprise_id': None,
        'api_app_id': '',
        'event': {
            'subtype': 'bot_message',
            'text': 'Hello, this is a message.', 'username': 'ET', 'icons': {'emoji': 'ghost'},
            'attachments': [
                {'id': 1, 'color': '2eb886',
                 'fallback': 'Hello, this is an attachment.',
                 'text': 'Hello, this is an attachment.'}
            ],
            'type': 'message',
            'ts': '1710932590.946109',
            'bot_id': '', 'channel': '',
            'event_ts': '1710932590.946109',
            'channel_type': 'channel'
        },
        'type': 'event_callback',
        'event_id': '', 'event_time': 1710932590, 'authorizations': [
            {'enterprise_id': None, 'team_id': '', 'user_id': '', 'is_bot': True,
             'is_enterprise_install': False}], 'is_ext_shared_channel': False,
        'event_context': '4-'}


def test_get_message_from_first_attachment(body:dict):
    assert get_attachment_text(body) == "Hello, this is an attachment."


def test_get_message_with_text(body:dict):
    assert get_message(body) == "Hello, this is a message."
