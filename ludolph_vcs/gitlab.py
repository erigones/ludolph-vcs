"""
This file is part of Ludolph: VCS integration plugin
Copyright (C) 2017 Erigones, s. r. o.

See the LICENSE file for copying permission.
"""
import logging

from ludolph_vcs import __version__
from ludolph.plugins.plugin import LudolphPlugin
from ludolph.web import webhook, request, abort

logger = logging.getLogger(__name__)


class Gitlab(LudolphPlugin):
    """
    Ludolph: GitLab integration.
    """
    __version__ = __version__
    _secret_token = None

    def __post_init__(self):
        self._secret_token = self.config.get('secret_token')

    def _room_message(self, msg):
        self.xmpp.msg_send(self.xmpp.room, '\n'.join(msg), mtype='groupchat')

    def _verify_secret_token(self):
        if self._secret_token and self._secret_token != request.headers.get('X-Gitlab-Token', None):
            logger.error('Invalid GitLab secret token')
            abort('403', 'Invalid GitLab secret token')

    def _event_push(self, data):
        data['branch'] = data.get('ref', '').split('/', 2)[-1]

        msg = ['**[{project[name]}]** The {branch} branch has been updated by {user_name}: '
               '\n\t {project[web_url]}'.format(**data)]

        for commit in data.get('commits', []):
            commit['message'] = commit.get('message', '').strip()
            msg.append('\t * {id:.8}: {message} ({author[name]})'.format(**commit))

        self._room_message(msg)

        return 'OK'

    def _event_tag_push(self, data):
        data['tag'] = data.get('ref', '').split('/', 2)[-1]

        msg = ['**[{project[name]}]** A new tag {tag} has been pushed by {user_name}: '
               '\n\t {project[web_url]}'.format(**data)]

        self._room_message(msg)

        return 'OK'

    @webhook('/gitlab-web-hook', methods=('POST',))
    def gitlab_web_hook(self):
        event = request.headers.get('X-Gitlab-Event', None)
        logger.info('Incoming GitLab Event: %s', event)

        self._verify_secret_token()

        data = request.json
        logger.debug('GitLab %s payload: %s', event, data)

        if event == 'Push Hook':
            return self._event_push(data)
        elif event == 'Tag Push Hook':
            return self._event_tag_push(data)

        logger.error('Unsupported GitLab Web Hook request (%s)', event)
        abort(400, 'Unsupported GitLab Web Hook request (%s)' % event)
