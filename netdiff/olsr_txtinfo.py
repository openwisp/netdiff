"""
Convert output from the olsrd txtinfo plug-in into a dict
"""

class AliasManager(object):
        "a MID is an IP alias in OLSR terminology. This class manages all IP addresses"
        def __init__(self):
            self.aliasdict = dict() # keys are ip addresses, values are unique ids
            self.idcounter = -2     # -1 is reserved, we start from -2
            self.unknownIPs = list()
        def addalias(self, ip, alias):
            # all aliases of the same ip share the same unique id, stored as value of aliasdict.
            if ip in self.aliasdict:
                    # if we already have this ip, use the same id for the alias
                    ipid = self.aliasdict[ip]
                    self.aliasdict.update({alias: ipid})
            elif alias in self.aliasdict:
                    # if we already have this alias, use the same id for the ip
                    ipid = self.aliasdict[alias]
                    self.aliasdict.update({ip: ipid})
            else:
                    # if a link already exists, update
                    # we need a new id
                    newid = self.idcounter
                    self.idcounter -= 1
                    self.aliasdict.update({ip: newid, alias: newid})
        def getIdFromIP(self, ip):
            if ip in self.aliasdict:
                    return self.aliasdict[ip]
            else:
                    self.idcounter -= 1
                    newid = self.idcounter
                    self.aliasdict.update({ip: newid})
                    return newid
        def getAliasesFromIP(self, ipaddr):
            iid = self.getIdFromIP(ipaddr)
            r = [ip for ip in self.aliasdict.keys() if self.aliasdict[ip] == iid]
            if not ipaddr in r:
                r.append(ipaddr)
            return r
        def getAllAliases(self):
            r = [(ip, self.getAliasesFromIP(ip)) for ip in self.aliasdict.keys()]
            return r
        def __str__(self):
            return str(self.aliasdict)


class TopologyParser(object):
        def __init__(self, txtinfo_output):
            self.topologylines = [l.strip() + " " for l in txtinfo_output.splitlines()]
            self.linklist = list()
            self.topolist = list()
            self.aliasmanager = AliasManager()
            self.hnalist = list()
            self.parsed = False

        def parse(self):
            "parse the txtinfo plugin output and make two lists: a link list and an alias (MID) list"
            # parse Topology info
            print ("Parsing Topology Information ...")
            if len(self.topologylines) < 1:
                print("WARNING: no topology information in %s :( " % self.topology_url)
                return

            i = 0
            line = self.topologylines[i]

            linkstablefound = True
            while line.find('Table: Links') == -1:
                i += 1
                if i < len(self.topologylines):
                    line = self.topologylines[i]
                else:
                    i = 0
                    line = self.topologylines[i]
                    linkstablefound = False
                    break

            if linkstablefound:
                print("Links table found.")
                i += 2 # skip the heading line
                line = self.topologylines[i]
                while not line.isspace():
                    try:
                            ipaddr1, ipaddr2, hyst, lq, nlq, etx = line.split()
                            print("Link: %s --[%s]--> %s" % (ipaddr1, etx, ipaddr2))
                            self.linklist.append((ipaddr1, ipaddr2, float(etx)))
                            self.linklist.append({
                                "localIP": ipaddr1,
                                "remoteIP": ipaddr2,
                                "validityTime": 154581, # made up
                                "linkQuality": float(lq),
                                "neighborLinkQuality": float(nlq),
                                "linkCost": 1536 # made up TODO: understand
                            })
                    except ValueError:
                            print ("wrong line or INFINITE ETX: %s" % line)
                            pass
                    i+=1
                    if i < len(self.topologylines):
                        line = self.topologylines[i]
                    else:
                        return
            # TODO: process neighbors table

            topologytablefound = True
            while line.find('Table: Topology') == -1:
                if i < len(self.topologylines):
                    i += 1
                    line = self.topologylines[i]
                else:
                    i = 0
                    line = self.topologylines[i]
                    topologytablefound = False
                    break

            if topologytablefound:
                print("Topology table found.")
                i += 2 # skip the heading line
                line = self.topologylines[i]
                while not line.isspace():
                    try:
                            ipaddr1, ipaddr2, lq, nlq, etx = line.split()
                            print("Link: %s --[%s]--> %s" % (ipaddr1, etx, ipaddr2))
                            self.topolist.append({
                                "destinationIP": ipaddr1,
                                "lastHopIP": ipaddr2,
                                "linkQuality": float(lq),
                                "neighborLinkQuality": float(nlq),
                                "tcEdgeCost": 1024, #made up TODO: understand
                                "validityTime": 561622 # made up
                            })

                    except ValueError:
                            print ("wrong line or INFINITE ETX: %s" % line)
                            pass
                    i+=1
                    if i < len(self.topologylines):
                        line = self.topologylines[i]
                    else:
                        return

            j = i + 1
            # parse HNA info
            print ("Parsing HNA Information...")
            while i < len(self.topologylines) and line.find('Table: HNA') == -1:
                line = self.topologylines[i]
                i += 1

            if i < len(self.topologylines):
                i += 1 # skip the heading line
                line = self.topologylines[i]
                while not line.isspace() and i < len(self.topologylines):
                    try:
                            hna, announcer = line.split()
                            print("HNA: %s by %s" % (hna, announcer))
                            self.hnalist.append({
                                "destination": hna.split('/')[0],
                                "genmask": hna.split('/')[1],
                                "gateway": announcer,
                                "validityTime": 118446 # made up
                            })
                    except ValueError:
                            pass
                    i+=1
                    if i < len(self.topologylines):
                        line = self.topologylines[i]
                    else:
                        return
            else:
                i = j


            # parse MID info
            print ("Parsing MID Information...")
            while i < len(self.topologylines) and line.find('Table: MID') == -1:
                line = self.topologylines[i]
                i += 1

            if i >= len(self.topologylines):
                return

            i += 1 # skip the heading line
            line = self.topologylines[i]
            while i < len(self.topologylines) and not line.isspace():
                try:
                        ipaddr, aliases = line.split()
                        for alias in aliases.split(';'):
                            print("MID: %s == %s" % (ipaddr, alias))
                            self.aliasmanager.addalias(ipaddr, alias)
                except ValueError:
                        pass
                i+=1
                if i < len(self.topologylines):
                    line = self.topologylines[i]
                else:
                    return

            self.parsed = True
        
        def toDict(self):
            "return olsrd JSONinfo format"
            if not self.parsed:
                self.parse()
            d = {}
            d['links'] = self.linklist
            d['topology'] = self.topolist
            d['hna'] = self.hnalist
            d['mid'] = []
            for ip, aliases in self.aliasmanager.getAllAliases():
                d['mid'].append({
                    "ipAddress": ip,
                    "aliases": [{"ipAddress": alias, "validityTime": 286445} for alias in aliases]
                })

            return d

