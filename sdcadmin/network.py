__author__ = 'ernm'

class Network(object):

    uuid = ''

    def __init__(self, datacenter, data=None, uuid=None):
        self.dc = datacenter

        if not data:
            if not uuid:
                raise Exception('Must pass either data or uuid')
            data = self.dc.get_network_raw(uuid=uuid)
        self._save(data)

    def _save(self, data):
        for k, v in data.iteritems():
            setattr(self, k, v)

    def __eq__(self, other):
        if isinstance(other, Network):
            return self.uuid == other.uuid
        return False


    def delete(self):
        pass

    def refresh(self):
        data, _ = self.dc.request('GET', 'napi', '/networks/' + self.uuid)
        self._save(data)

