import dns.resolver
import dns.zonefile
import logging

logger = logging.getLogger()
logger.setLevel("INFO")


def ip_ptr(ip, server="8.8.8.8"):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server]
    try:
        answers = resolver.resolve(dns.reversename.from_address(ip), 'PTR', lifetime=3)

    except dns.resolver.NXDOMAIN:
        logger.info("No results found")
        return ["No PTR"]
    except dns.resolver.LifetimeTimeout:
        logger.info("Timeout reaching DNS server")
        return ["DNS Server error"]
    data = [item.to_text() for item in answers]
    return data


def dns_lookup(domain, record="A", server="8.8.8.8"):
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [server]
    try:
        answers = resolver.resolve(domain, record)

    except dns.resolver.NXDOMAIN:
        logger.info("No results found")
        return ["No DNS"]
    data = [item.to_text() for item in answers]
    return data
