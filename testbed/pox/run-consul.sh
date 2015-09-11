docker run -d --name node1 -h node1 progrium/consul -server -bootstrap-expect 3
JOIN_IP="$(docker inspect -f '{{.NetworkSettings.IPAddress}}' node1)"
docker run -d --name node2 -h node2 progrium/consul -server -join $JOIN_IP
docker run -d --name node3 -h node3 progrium/consul -server -join $JOIN_IP
docker run -d -p 8400:8400 -p 8500:8500 -p 8600:53/udp --name node4 -h node4 progrium/consul -join $JOIN_IP
# -----------------------------------------------------------------------------
# Copyright (C) 2015 Bloomberg Finance L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------ END-OF-FILE ----------------------------------
