### SDC Networking

a few notes on SDC Networking (to help me understand & as a reference)

A Compute Node has one or multiple physical NICs ```(e1000g0, e1000g1)```
A physical NIC has zero, one or multiple NIC Tags ```[], [external], [admin, customer-a]```
A NIC Tag has zero, one or multiple Networks on it ```[], [{name: external, ...}, [{name: external, ...},{name: cust-a, ...}]```
A Network either has no VLAN (value 0) or a VLAN ID (not 1) ```0, 2, 454```
A Network Pool has one or more Networks, it acts as a collection of Networks and may be used in the same way. This is useful for multiple small ip-ranges. Used in order. ```[network_uuid_1, network_uuid_2]```
Address collisions are only checked against VM IPs, MAC and VRID (#TODO: what is this?), not against the first 32 addresses of the admin-network.
The Node.JS client lib does not handle any collision detection. provide possibility to add this later, i.e. stub out a check_collissions
 