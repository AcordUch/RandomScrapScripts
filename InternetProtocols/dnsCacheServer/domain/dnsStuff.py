from dnslib import RR, DNSLabel


class CacheKey:
    def __init__(self, name: DNSLabel, q_type: int):
        self.name = name
        self.q_type = q_type

    def __hash__(self):
        return hash(self.name) * hash(self.q_type)

    def __eq__(self, other):
        if other is None or type(other).__name__ != "CacheKey":
            return False
        else:
            return (self.name == other.name and
                    self.q_type == other.q_type)

    def __str__(self):
        return f"name: {self.name} " + f"type: {self.q_type}"

    def __repr__(self):
        return self.__str__()


class CacheValue:
    def __init__(self, ttl: int, data: set[RR], authoritative: bool):
        self.expiry_time = ttl
        self.data = data
        self.auth = authoritative

    def __hash__(self):
        return hash(self.expiry_time) * hash(self.data) * hash(self.auth)

    def __eq__(self, other):
        if other is None or type(other).__name__ != "CacheValue":
            return False
        else:
            return (self.expiry_time == other.expiry_time and
                    self.data == other.data and
                    self.auth == other.auth)

    def __str__(self):
        return f"expiry time: {self.expiry_time} " + f"auth: {self.auth} " + "data: " + " ".join(map(lambda x: str(x), self.data))

    def __repr__(self):
        return self.__str__()


class ForwarderTimeout(Exception):
    pass
