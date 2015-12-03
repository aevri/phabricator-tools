#! /usr/bin/env python2

import json
import logging
import requests
import subprocess
import sys
import time

# arcyd start --foreground

_SERVICE_NAME = 'arcyd'


def main():
    logging.basicConfig(
        filename='/var/log/contend-leadership',
        level=logging.DEBUG)

    kv = json.load(sys.stdin)
    logging.debug("Got kv: {}".format(kv))

    has_leader = test_has_leader(kv)
    if has_leader:
        logging.debug("There is already a leader.")
    else:
        contend_leadership()


def test_has_leader(key_value):
    if not isinstance(key_value, dict):
        return False
    return True if key_value.get("Session", False) else False


def contend_leadership():
    consul_api = 'http://localhost:8500/v1/'

    session_id = get_response_json(
        requests.put(
            consul_api + 'session/create',
            json={'Name': _SERVICE_NAME}))['ID']
    logging.debug("Got session ID: {}".format(session_id))

    has_leader = False
    while not has_leader:
        is_leader = get_response_json(
            requests.put(
                '{}kv/{}/leader?acquire={}'.format(
                    consul_api, _SERVICE_NAME, session_id),
                'I am the leader'))
        logging.debug("Is leader:{}".format(is_leader))

        if is_leader:
            has_leader = True
            logging.info("This node is the leader.")
            logging.info(
                subprocess.check_output(
                    ['/bin/arcyd-do', 'start']))
        else:
            has_leader = test_has_leader(
                get_response_json(
                    requests.get(
                        '{}kv/{}/leader'.format(
                            consul_api, _SERVICE_NAME)))[0])
            logging.debug("Has leader:".format(has_leader))
            if has_leader:
                logging.info("This node is a follower.")
            else:
                logging.debug("Waiting to retry ..")

                # there may be a 'lock-delay', wait before retry
                time.sleep(5)


def get_response_json(response):
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    sys.exit(main())
