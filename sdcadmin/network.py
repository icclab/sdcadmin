__author__ = 'ernm'

class Network(object):

    uuid = ''
    vlan_id = ''
    subnet = ''


    api = 'napi'
    base_url = '/networks/'
    identifier_field = 'uuid'


    def __init__(self, datacenter, data=None, uuid=None):
        self.dc = datacenter

        if not data:
            if not uuid:
                raise Exception('Must pass either data or uuid')
            data, response = self.dc.request('GET', self.api, self.base_url + uuid)
            if not data.get(self.identifier_field):
                return
        self._save(data)

    def _save(self, data):
        for k, v in data.iteritems():
            setattr(self, k, v)

    def __eq__(self, other):
        if isinstance(other, Network):
            return self.uuid == other.uuid
        return False


    def delete(self):
        _, response = self.dc.request('DELETE', self.api, self.base_url + self.uuid)
        response.raise_for_status()

    def refresh(self):
        data, _ = self.dc.request('GET', self.api, self.base_url + self.uuid)
        self._save(data)

