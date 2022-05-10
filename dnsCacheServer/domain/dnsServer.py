import pickle
import socket
import time

from dnslib import DNSRecord, QTYPE, RR
from .dnsStuff import CacheKey, CacheValue, ForwarderTimeout
from .config_loader import ConfigLoader


class DNSServer:
    NSA_QTYPE = -1

    def __init__(self, debug: bool = False):
        self._debug = debug
        self.cache_file_name = "dnsCache"

        cfg_loader = ConfigLoader()
        self.cache_server = cfg_loader.cache_server
        self.forwarder_server = cfg_loader.forwarder_server

        try:
            with open(self.cache_file_name, "rb") as file:
                self.cache: dict[CacheKey, CacheValue] = pickle.load(file)

            self.clear_expired()
            print(
                "-----Load from disk:-----\n" +
                "\n".join((str(key) + " --- " + str(self.cache[key]) for key in self.cache)) +
                "\n"
            )
        except IOError:
            self.cache: dict[CacheKey, CacheValue] = dict()

    def clear_expired(self) -> None:
        to_remove = list()

        for key in self.cache:
            if self.cache[key].expiry_time < int(time.time()):
                to_remove.append(key)

        for key in to_remove:
            del self.cache[key]

    def start(self) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.bind(self.cache_server)
            sock.settimeout(2)
            while True:
                try:
                    req_bytes, addr = sock.recvfrom(1024)
                    sock.sendto(self.__make_answer(req_bytes), addr)
                except socket.timeout:
                    continue
                except Exception as err:
                    print(err)
                    continue

    def __make_answer(self, req_bytes) -> bytes:
        client_data = DNSRecord.parse(req_bytes)
        key = CacheKey(client_data.q.qname, client_data.q.qtype)

        if (
                key in self.cache and
                self.cache[key].expiry_time > int(time.time())
        ):
            self.debug_print("from cache\n" + f"type: {client_data.q.qtype}")
            return self.__from_cache(client_data)
        else:
            self.debug_print("from server\n" + f"type: {client_data.q.qtype}")
            try:
                return self.__get_and_save_answer(req_bytes)
            except ForwarderTimeout:
                return client_data.reply().pack()

    def __get_and_save_answer(self, req_bytes: bytes) -> bytes:
        ans = self.__ask_forwarder(req_bytes)
        self.__caching(ans)
        return ans

    def __caching(self, ans: bytes) -> None:
        ans_data = DNSRecord.parse(ans)
        match ans_data.q.qtype:
            case QTYPE.A:
                self.cache[CacheKey(ans_data.q.qname, QTYPE.A)] = CacheValue(
                    int(time.time()) + ans_data.a.ttl,
                    ans_data.rr,
                    True
                )
                self.cache[CacheKey(ans_data.q.qname, QTYPE.NS)] = CacheValue(
                    int(time.time()) + ans_data.a.ttl,
                    ans_data.auth,
                    False
                )
                self.cache[CacheKey(ans_data.q.qname, self.NSA_QTYPE)] = CacheValue(
                    int(time.time()) + ans_data.a.ttl,
                    ans_data.ar,
                    False
                )
            case QTYPE.PTR:
                if len(ans_data.auth) == 0:
                    self.cache[CacheKey(ans_data.q.qname, QTYPE.PTR)] = CacheValue(
                        int(time.time()) + ans_data.a.ttl,
                        ans_data.rr,
                        True
                    )
                else:
                    self.cache[CacheKey(ans_data.q.qname, QTYPE.PTR)] = CacheValue(
                        int(time.time()) + ans_data.auth[0].ttl,
                        ans_data.auth,
                        True
                    )
            case QTYPE.NS:
                self.cache[CacheKey(ans_data.q.qname, QTYPE.NS)] = CacheValue(
                    int(time.time()) + ans_data.a.ttl,
                    ans_data.rr,
                    True
                )
                self.cache[CacheKey(ans_data.q.qname, self.NSA_QTYPE)] = CacheValue(
                    int(time.time()) + ans_data.a.ttl,
                    ans_data.ar,
                    False
                )

    def __from_cache(self, client_data: DNSRecord) -> bytes:
        query = client_data.reply()
        match client_data.q.qtype:
            case QTYPE.A:
                a_value = self.cache[CacheKey(client_data.q.qname, QTYPE.A)]
                if not a_value.auth:
                    try:
                        return self.__get_and_save_answer(client_data.pack())
                    except ForwarderTimeout:
                        pass
                for answer in a_value.data:
                    query.add_answer(
                        RR(
                            rname=answer.rname,
                            rclass=answer.rclass,
                            rtype=answer.rtype,
                            ttl=int(a_value.expiry_time - time.time()),
                            rdata=answer.rdata
                        )
                    )
                ns_value = self.cache[CacheKey(client_data.q.qname, QTYPE.NS)]
                for ns in ns_value.data:
                    query.add_auth(
                        RR(
                            rname=ns.rname,
                            rclass=ns.rclass,
                            rtype=ns.rtype,
                            ttl=int(ns_value.expiry_time - time.time()),
                            rdata=ns.rdata
                        )
                    )
                nsa_value = self.cache[CacheKey(client_data.q.qname, self.NSA_QTYPE)]
                for nsa in nsa_value.data:
                    query.ar(
                        RR(
                            rname=nsa.rname,
                            rclass=nsa.rclass,
                            rtype=nsa.rtype,
                            ttl=int(ns_value.expiry_time - time.time()),
                            rdata=nsa.rdata
                        )
                    )
            case QTYPE.PTR:
                ptr_value = self.cache[CacheKey(client_data.q.qname, QTYPE.PTR)]
                if not ptr_value.auth:
                    try:
                        return self.__get_and_save_answer(client_data.pack())
                    except ForwarderTimeout:
                        pass
                for ptr in ptr_value.data:
                    query.add_auth(
                        RR(
                            rname=ptr.rname,
                            rclass=ptr.rclass,
                            rtype=ptr.rtype,
                            ttl=int(ptr_value.expiry_time - time.time()),
                            rdata=ptr.rdata
                        )
                    )
            case QTYPE.NS:
                ns_value = self.cache[CacheKey(client_data.q.qname, QTYPE.NS)]
                if not ns_value.auth:
                    try:
                        return self.__get_and_save_answer(client_data.pack())
                    except ForwarderTimeout:
                        pass
                for ns in ns_value.data:
                    query.add_answer(
                        RR(
                            rname=ns.rname,
                            rclass=ns.rclass,
                            rtype=ns.rtype,
                            ttl=int(ns_value.expiry_time - time.time()),
                            rdata=ns.rdata
                        )
                    )
                nsa_value = self.cache[CacheKey(client_data.q.qname, self.NSA_QTYPE)]
                for nsa in nsa_value.data:
                    query.ar(
                        RR(
                            rname=nsa.rname,
                            rclass=nsa.rclass,
                            rtype=nsa.rtype,
                            ttl=int(nsa_value.expiry_time - time.time()),
                            rdata=nsa.rdata
                        )
                    )

        self.debug_print(query)
        return query.pack()

    def __ask_forwarder(self, data_bytes: bytes) -> bytes:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(1)
            try:
                sock.connect(self.forwarder_server)
                sock.send(data_bytes)

                answer = sock.recv(1024)
                return answer
            except socket.timeout:
                raise ForwarderTimeout

    def save_cache(self) -> None:
        with open(self.cache_file_name, "wb") as file:
            pickle.dump(self.cache, file)

    def debug_print(self, value) -> None:
        if self._debug:
            print(value)
