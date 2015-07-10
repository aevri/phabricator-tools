#! /usr/bin/env bash
../../proto/arcyd-tester --phab-uri http://127.0.0.1:8090
../../bin/arcyon query --uri http://127.0.0.1:8091 --user me --cert squirrel
