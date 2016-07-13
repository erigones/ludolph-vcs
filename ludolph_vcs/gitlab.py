"""
This file is part of Ludolph: VCS integration plugin
Copyright (C) 2016 Erigones, s. r. o.

See the LICENSE file for copying permission.
"""
from ludolph_vcs import __version__
from ludolph.plugins.plugin import LudolphPlugin
from ludolph.web import webhook, request, abort


class Gitlab(LudolphPlugin):
    """
    Ludolph: GitLab integration.
    """
    __version__ = __version__
    _secret_token = None

    def __post_init__(self):
        self._secret_token = self.config.get('gitlab_secret_token')

    def _room_message(self, msg):
        self.xmpp.msg_send(self.xmpp.room, '\n'.join(msg), mtype='groupchat')

    def _verify_secret_token(self):
        if self._secret_token and self._secret_token != request.headers.get('X-Gitlab-Token', None):
            abort('403', 'Invalid GitLab Secret Token')

    def _event_push(self, data):
        data['branch'] = data.get('ref', '').split('/', 2)[-1]

        msg = ['**[{project[name]}]** The {branch} branch has been updated by {user_name}: '
               '\n{project[web_url]}'.format(**data)]

        for commit in data.get('commits', []):
            msg.append('\t * {id:.8}: __{message}__ ({author[name]})'.format(**commit))

        self._room_message(msg)

        return 'OK'

    def _event_tag_push(self, data):
        data['tag'] = data.get('ref', '').split('/', 2)[-1]

        msg = ['**[{project[name]}]** A new tag {tag} has been pushed by {user_name}: '
               '\n{project[web_url]}'.format(**data)]

        self._room_message(msg)

        return 'OK'

    @webhook('/gitlab-web-hook', methods=('POST',))
    def web_hook(self):
        self._verify_secret_token()
        event = request.headers.get('X-Gitlab-Event', None)
        data = request.json

        if event == 'Tag Push Hook':
            return self._event_push(data)
        elif event == 'Tag Push Hook':
            return self._event_tag_push(data)

        abort(400, 'Unsupported GitLab Web Hook request')
