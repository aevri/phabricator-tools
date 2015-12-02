#! /usr/bin/env python

import json
import requests
import sys
import time

# arcyd start --foreground

_SERVICE_NAME = 'arcyd'


def main():
    kv = json.load(sys.stdin)
    print "Got kv:", kv

    has_leader = test_has_leader(kv)
    if has_leader:
        print "There is already a leader."
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
    print "Got session ID:", session_id

    has_leader = False
    while not has_leader:
        is_leader = get_response_json(
            requests.put(
                '{}kv/{}/leader?acquire={}'.format(
                    consul_api, _SERVICE_NAME, session_id),
                'I am the leader'))
        print "Is leader:", is_leader

        if is_leader:
            has_leader = True
        else:
            has_leader = test_has_leader(
                get_response_json(
                    requests.get(
                        '{}kv/{}/leader'.format(
                            consul_api, _SERVICE_NAME)))[0])
            print "Has leader:", has_leader
            if not has_leader:
                print "Waiting to retry .."

                # there may be a 'lock-delay', wait before retry
                time.sleep(5)


def get_response_json(response):
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    sys.exit(main())
