import six
import requests
import structlog
from sphinx.ext.intersphinx import fetch_inventory

log = structlog.get_logger()


class DummyConfig(object):
    intersphinx_timeout = None
    tls_verify = False


class DummyApp(object):
    config = DummyConfig()
    srcdir = ""


def get_docs_urls(version, sources):
    version_url = "https://docs.djangoproject.com/en/{}".format(version)
    inventory_url = version_url + "/_objects"

    try:
        inventory_data = fetch_inventory(DummyApp(), version_url, inventory_url)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            log.debug("404 received for {}".format(inventory_url), version=version)
            return

        raise
    log.debug("Fetched docs URLs", version=version)

    # we only care about classes
    classes = inventory_data["py:class"]

    # str.startswith can take multiple items but they must be in a tuple
    sources = tuple(sources)

    # filter classes down to those with paths that start with any of our sources
    classes = filter(lambda x: x[0].startswith(sources), classes.items())

    for path, data in classes:
        _, _, url, _ = data  # data is a tuple of strings
        url = url.replace("/_objects", "")
        yield path, url
