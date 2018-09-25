# (sshank) REMOVE THIS LATER ON

"""
initial blank neutron db
[]

sent_to_agent(port1 p_key1 gid1 request1)

[(port1, p_key1, gid1)] from neutron db

      bound                                        # unbound
[(port1, p_key1, gid1), (port2, p_key1, gid2), (port3, p_key2, [])]

delete port2 (implicit)

[(port1, p_key1, gid1), (port3, p_key2, [])]

# xid -> (uuid) ->
        request (uuid -> sync([(port1, p_key1, gid1), (port2, p_key1, gid2), (port3, p_key2, [])])

# if checkwithopenagent(uuid):
    yes I remember (no crash) continue
# else
    forgot (crashed) send again? or redo request (uuid -> sync([(port1, p_key1, gid1), (port2, p_key1, gid2), (port3, p_key2, [])])

block (maintainer thread in ODL) # we do this so that only one thread has access to openmanagement agent.
sent_to_agent()
    full sync -> copy from neutron DB to OpenManagement Agent
    request from nova to bind gid3 to port3 (port upgate) (return sucess)

        full sync: # tell openmanagement agent to attach gid3 to p_key2 (all the 3 ports info is sent)
            # inside openmanagement agent
            (gid3) -> p_key2 # attach server gid into tenant p_key2
            omni will take time and attach gid with p_key2
            attach is success return

    [(port1, p_key1, gid1), (port2, p_key1, gid1), (port3, p_key2, gid3)]

    return nova (saying port3 is now bound) (return port status up notification)
unblock

# inititially full sync we want to send all. But we want to send only diff. This is where we use
the revision number (from OVN). (later optimization)

# if no diff, no need to sync.

# delete port(port3)


type driver:
    create model for omnipath
    create alembic for the omnipath model
    create object for the omnipath model
    use the object in the type_omnipath

agent_port_status_list = self.client.get_port_status([(gid, vf)])
port_details = self.find_port_details(gid, vf, agent_port_status_list)

while port_details[3] != "UP":
    agent_port_status_list = self.client.get_port_status([(gid, vf)])
    port_details = self.find_port_details(gid, vf, agent_port_status_list)
"""