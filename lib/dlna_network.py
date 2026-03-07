# ==================================================================
# dlna_network.py
# ==================================================================
# VintageRadio - Librairie.
# David de Lorenzo (2026)
# ==================================================================
import socket
import http.client
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from typing import List, Optional, Tuple
from lib.dlna_logger import get_logger


SSDP_ADDR = "239.255.255.250"
SSDP_PORT = 1900
MSEARCH_MSG = "\r\n".join([
    'M-SEARCH * HTTP/1.1',
    f'HOST: {SSDP_ADDR}:{SSDP_PORT}',
    'MAN: "ssdp:discover"',
    'MX: 3',  # wait up to 3 seconds for replies
    'ST: urn:schemas-upnp-org:device:MediaServer:1',
    '', ''
]).encode('utf-8')


# ----------------------------------------------------------------------- #
# Cette classe gère les messages réseau Discovery SDP et SOAP pour communiquer
# avec le serveur DLNA.
# ----------------------------------------------------------------------- #
class DLNANetwork:
    """All raw network interaction with DLNA/UPnP devices."""

    # --------------------------------------------------------------------- #
    # Constructeur
    # --------------------------------------------------------------------- #
    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        self.log = get_logger(__name__)

    # --------------------------------------------------------------------- #
    # 1️⃣  SSDP discovery
    # --------------------------------------------------------------------- #
    def discover_servers(self) -> List[Tuple[str, str]]:
        """
        Broadcast an M‑SEARCH request and collect responses.

        Returns
        -------
        List[Tuple[location_url, usn]]
            *location_url* – the URL of the device description XML  
            *usn*          – unique service name (used as an identifier)
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(self.timeout)

        # Send the multicast request
        sock.sendto(MSEARCH_MSG, (SSDP_ADDR, SSDP_PORT))

        servers: List[Tuple[str, str]] = []
        start = socket.getdefaulttimeout()
        try:
            while True:
                data, _ = sock.recvfrom(65507)
                headers = self._parse_ssdp_response(data.decode('utf-8', errors='ignore'))
                loc = headers.get('location')
                usn = headers.get('usn')
                if loc and usn:
                    servers.append((loc, usn))
        except socket.timeout:
            pass  # normal end of discovery window
        finally:
            sock.close()

        return servers

    # --------------------------------------------------------------------- #
    # Parse SSDP Discovery response.
    # --------------------------------------------------------------------- #
    @staticmethod
    def _parse_ssdp_response(resp: str) -> dict:
        """Very small header parser – SSDP responses are HTTP‑like."""
        lines = resp.split('\r\n')
        hdr = {}
        for line in lines[1:]:  # skip the status line
            if ':' not in line:
                continue
            k, v = line.split(':', 1)
            hdr[k.strip().lower()] = v.strip()
        return hdr

    # ------------------------------------------------------------------------ #
    # 2️⃣  Retrieve device description (XML) → extract the ContentDirectory URL
    # ------------------------------------------------------------------------ #
    @staticmethod
    def get_content_directory_control_url(desc_url: str) -> Optional[str]:
        """
        Pull the device description XML and locate the control URL for the
        ContentDirectory service (the one used for browsing media).
        """
        parsed = urlparse(desc_url)
        conn = http.client.HTTPConnection(parsed.hostname, parsed.port or 80, timeout=5)
        try:
            conn.request("GET", parsed.path or "/")
            resp = conn.getresponse()
        except Exception as e:
            # Gestion des erreurs réseau
            print(f"Failed to fetch device description: {e}")
            return None
        if resp.status != 200:
            return None
        xml_data = resp.read()
        conn.close()
        root = ET.fromstring(xml_data)
        ns = {'upnp': 'urn:schemas-upnp-org:device-1-0'}  # dictionary des namespace
        # root.tag contains namespace
        # Walk the service list looking for ContentDirectory. {*} means any namespace
        for service in root.iterfind('.//{*}service'):
            service_type = service.findtext('{*}serviceType')
            if service_type and 'ContentDirectory' in service_type:
                ctrl_url = service.findtext('{*}controlURL')
                # Resolve relative URLs against the base description URL
                if ctrl_url.startswith('http'):
                    # XMl contains control url
                    return ctrl_url
                else:
                    # control url needs base url prefix
                    base = f"{parsed.scheme}://{parsed.netloc}"
                    return base + (ctrl_url if ctrl_url.startswith('/') else '/' + ctrl_url)
        return None

    # --------------------------------------------------------------------- #
    # 3️⃣  SOAP “Browse” request – generic helper
    # --------------------------------------------------------------------- #
    @staticmethod
    def _soap_envelope(body: str) -> str:
        return f'''<?xml version="1.0" encoding="utf-8"?>
        <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
                    s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
          <s:Body>{body}</s:Body>
        </s:Envelope>'''

    # --------------------------------------------------------------------- #
    # Emet une requete SOAP et retourne la réponse XML
    # --------------------------------------------------------------------- #
    def browse(
            self,
            control_url: str,
            object_id: str = "0",
            browse_flag: str = "BrowseDirectChildren",
            filter_: str = "*",
            starting_index: int = 0,
            requested_count: int = 0,
            sort_criteria: str = ""
    ) -> Optional[ET.Element]:
        """
        Issue a SOAP Browse request and return the parsed XML result element
        (<Result>…)</Result>.  Caller can further walk the DIDL‑Lite tree.

        Parameters
        ----------
        control_url : str
            Full URL of the ContentDirectory control endpoint.
        object_id : str
            Identifier of the container to browse (root = "0").
        browse_flag : str
            Either “BrowseMetadata” or “BrowseDirectChildren”.
        filter_ : str
            Property filter – “*” means everything.
        starting_index : int
            Pagination – 0/0 means “all”.
        requested_count : int
            Pagination – 0/0 means “all”.
        sort_criteria : str
            Optional sorting expression.

        Returns
        -------
        xml.etree.ElementTree.Element | None
            The `<Result>` element (which itself contains a DIDL‑Lite XML
            fragment).  ``None`` on error.
        """
        # Build SOAP body
        body = f'''
        <u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">
          <ObjectID>{object_id}</ObjectID>
          <BrowseFlag>{browse_flag}</BrowseFlag>
          <Filter>{filter_}</Filter>
          <StartingIndex>{starting_index}</StartingIndex>
          <RequestedCount>{requested_count}</RequestedCount>
          <SortCriteria>{sort_criteria}</SortCriteria>
        </u:Browse>'''
        envelope = self._soap_envelope(body)

        parsed = urlparse(control_url)
        conn = http.client.HTTPConnection(parsed.hostname, parsed.port or 80, timeout=5)
        headers = {
            "Content-Type": 'text/xml; charset="utf-8"',
            "SOAPACTION": '"urn:schemas-upnp-org:service:ContentDirectory:1#Browse"',
            "Content-Length": str(len(envelope)),
        }
        path = parsed.path or "/"
        try:
            conn.request("POST", path, envelope.encode('utf-8'), headers)
            resp = conn.getresponse()
        except Exception as e:
            # Gestion des erreurs réseau
            print(f"Failed to fetch ContentDirectory: {e}")
            return None
        if resp.status != 200:
            conn.close()
            return None

        resp_xml = resp.read()
        conn.close()
        root = ET.fromstring(resp_xml)

        # Extract the <Result> element (it holds a DIDL‑Lite XML string)
        result_el = root.find('.//Result')
        if result_el is None or not result_el.text:
            return None

        # The text inside <Result> is itself XML – parse it
        # self.log.debug("Reception: %s", result_el.text)  # VERBOSE
        didl_root = ET.fromstring(result_el.text)
        return didl_root

    # --------------------------------------------------------------------- #
    # 4️⃣  Helper to collect MP3 URLs from a DIDL‑Lite container
    # --------------------------------------------------------------------- #
    # @staticmethod
    def extract_mp3_items(self, didl_root: ET.Element) -> List[str]:
        """
        Walk a DIDL‑Lite tree and return the list of URLs for items whose
        `@protocolInfo` indicates an audio/mpeg (MP3) resource.
        """
        mp3_urls: List[str] = []
        # Namespace used by most DLNA servers for DIDL‑Lite
        ns = {"didl": "urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/"}
        for item in didl_root.findall('.//{*}item'):
            for res in item.findall('{*}res'):
                protocol = res.attrib.get('protocolInfo', '')
                if 'audio/mpeg' in protocol.lower():
                    if res.text:
                        mp3_urls.append(res.text.strip())
        return mp3_urls
