from .channel import Channel

class Guild:
    def __init__(self, data, instance):
        print(data.keys())
        self.channels:list[Channel] = []
        for channel in data["channels"]:
            self.channels.append(Channel(channel, instance))
        self.id = data['id']
        self.member_count = data['member_count']