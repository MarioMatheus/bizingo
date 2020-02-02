from game import message

message = message.GameMessage()

obj = { 'foo': 'oi', 'bar': 'A1' }
data = message.encode(obj, 'MATCH')
print(data)
module, payload = message.decode(data)
print('Module: ' + module + '\nPayload: ' + str(payload))
