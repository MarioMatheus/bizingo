class GameMessage:
    def encode(self, obj, module):
        data = module + '|' + str(obj)
        return data.encode()

    def decode(self, data):
        module, payload = data.decode('utf-8').split('|')
        str_data = str(
            payload
        ).replace('{', '').replace('}', '').split(',')
        payload = {}
        for attr in str_data:
            key, value = attr.split(':')
            payload[key.replace("'", '')] = value.replace("'", '')
        return module, payload
