"""
This file is part of Ludolph: VCS integration plugin
Copyright (C) 2017 Erigones, s. r. o.

See the LICENSE file for copying permission.
"""
import logging
import hmac
import hashlib

from ludolph_vcs import __version__
from ludolph.plugins.plugin import LudolphPlugin
from ludolph.web import webhook, request, abort

logger = logging.getLogger(__name__)


class GitHub(LudolphPlugin):
    """
    Ludolph: GitHub integration.
    """
    __version__ = __version__
    _secret_token = None

    def __post_init__(self):
        self._secret_token = self.config.get('secret_token')

    def _room_message(self, msg):
        self.xmpp.msg_send(self.xmpp.room, '\n'.join(msg), mtype='groupchat')

    def _verify_github_signature(self):
        """Verify GitHub signature"""
        if self._secret_token:
            payload = request.body.read()
            signature = request.headers.get('X-Hub-Signature', '')
            mac = hmac.new(self._secret_token, msg=payload, digestmod=hashlib.sha1)

            if not hmac.compare_digest('sha1=' + mac.hexdigest(), signature):
                logger.error('Invalid GitHub secret token')
                abort('403', 'Invalid GitHub secret token')

    def _event_push(self, data):
        data['branch'] = data.get('ref', '').split('/', 2)[-1]

        msg = ['**[{repository[name]}]** The {branch} branch has been updated by '
               '{pusher[name]}: \n\t {repository[html_url]}'.format(**data)]

        for commit in data.get('commits', []):
            commit['message'] = commit.get('message', '').strip()
            msg.append('\t * {id:.8}: {message} ({author[name]})'.format(**commit))

        self._room_message(msg)

        return 'OK'

    def _event_repo_fork(self, data):
        msg = ['**[{repository[name]}]** Yeeey {sender[login]} has forked a repo!'.format(**data)]

        self._room_message(msg)

        return 'OK'

    def _event_issue_handler(self, data):
        msg = ['**[{repository[name]}]** {action} issue: #{issue[number]} {issue[title]} '
               '\n\t {issue[html_url]}'.format(**data)]

        self._room_message(msg)

        return 'OK'

    def _event_issue_comment(self, data):
        msg = ['**[{repository[name]}]** {comment[user][login]} {action} issue comment: '
               '#{issue[number]} {issue[title]} \n\t {comment[body]}'.format(**data)]

        self._room_message(msg)

        return 'OK'

    @webhook('/github-web-hook', methods=('POST',))
    def github_web_hook(self):
        event = request.headers.get('X-GitHub-Event', None)
        logger.info('Incoming GitHub Event: %s', event)
        self._verify_github_signature()

        data = request.json
        logger.debug('GitHub %s payload: %s', event, data)

        if event == 'push':
            return self._event_push(data)
        elif event == 'issues':
            return self._event_issue_handler(data)
        elif event == 'issue_comment':
            return self._event_issue_comment(data)
        elif event == 'fork':
            return self._event_repo_fork(data)
        elif event == 'ping':
            self._room_message(['**[GitHub]** Ping received!'])
            return 'OK'

        logger.error('Unsupported GitHub Web Hook request (%s)', event)
        abort(400, 'Unsupported GitHub Web Hook request (%s)' % event)
