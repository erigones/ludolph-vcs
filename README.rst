ludolph-vcs
###########

`Ludolph <https://github.com/erigones/Ludolph>`_: vcs plugin

VCS plugin that provides notifications for Ludolph from GitHub and GitLab. Ludolph has to be on a public IP (URL) where VCS provider will POST data to a `Ludolph's webhook <https://github.com/erigones/Ludolph/wiki/Webhooks-and-cron-jobs>`_. Make sure Ludolph's webserver can receive this message. We do recommend using a proxy server in front of Ludolph's webserver in order not to expose it to public internet.

.. image:: https://badge.fury.io/py/ludolph-vcs.png
    :target: http://badge.fury.io/py/ludolph-vcs


Installation
------------

- Install the latest released version using pip::

    pip install ludolph-vcs

- Add new plugin section into Ludolph configuration file::

    [ludolph_vcs.gitlab]
    secret_token = secret_key_gitlab_gave_you

    [ludolph_vcs.github]
    sectet_token = secret_key_you_defined_on_github

- Reload Ludolph::

    service ludolph reload


**Dependencies:**

- `Ludolph <https://github.com/erigones/Ludolph>`_ (0.6.0+)


Links
-----

- Wiki: https://github.com/erigones/Ludolph/wiki/How-to-create-a-plugin#create-3rd-party-plugin
- Bug Tracker: https://github.com/erigones/ludolph-vcs/issues
- Google+ Community: https://plus.google.com/u/0/communities/112192048027134229675
- Twitter: https://twitter.com/danubecloud


License
-------

For more information see the `LICENSE <https://github.com/erigones/ludolph-vcs/blob/master/LICENSE>`_ file.

