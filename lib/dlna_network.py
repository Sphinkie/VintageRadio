# ==================================================================
# lib/dlna_network.py
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

log = get_logger(__name__)

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

    # --------------------------------------------------------------------- #
    # SSDP discovery. Renvoie une liste de couples (url, uuid):
    # ('http://192.168.0.32:50001/desc/device.xml',
    #  'uuid:00113281-0ddb-0011-db0d-db0d81321100::urn:schemas-upnp-org:device:MediaServer:1')
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
        log.info("Start server discovery (for 5s)")
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
        log.info("%d servers found", len(servers))
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
    # Emet une requete SOAP et retourne en réponse un DIDL XML.
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
            The `<Result>` element (which itself contains a DIDL‑Lite XML fragment). ``None`` on error.
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
    # Récupère TOUS les MP3 d'un serveur (récursif) - Dure 40 secondes.
    # Alternative pour scan_all_musics (qui est plus simple et plus rapide)
    # --------------------------------------------------------------------- #
    def browse_recursive(self, control_url: str, object_id: str = "0", depth: int = 0) -> Optional[ET.Element]:
        """
        Récupère récursivement tous les MP3 d'un serveur DLNA.
        Fonctionne avec n'importe quel serveur DLNA (Synology, MiniDLNA, Jellyfin, etc.).
        Garantit de trouver tous les fichiers, même dans des dossiers cachés.
        Plus lent, plus complexe, que simplement interroger le container 'All music".
        
        Args:
            control_url: URL de contrôle ContentDirectory
            object_id: ID du conteneur à parcourir (début à "0")
            depth: Profondeur actuelle (pour éviter les boucles infinies)
            
        Returns:
            The `<Result>` element (which contains a DIDL‑Lite XML fragment). ``None`` on error.
        """
        if depth > 10:  # Limite de profondeur pour éviter les boucles
            log.warning(f"Profondeur maximale atteinte: {depth}")
            return None
        # -------------------------------------------------------------
        # Initialize full_didl properly (DIDL-Lite root element)
        # Only initialize at depth 0 (top-level call)
        # -------------------------------------------------------------
        if depth == 0:
            full_didl = ET.Element('{urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/}DIDL-Lite')
        else:
            full_didl = None

        try:
            log.debug(f"> browse {object_id}")
            didl = self.browse(control_url, object_id=object_id)
            if didl is None:
                return None

            # Extraire les items MP3 de ce conteneur
            for item in didl.findall('.//{*}item'):
                log.debug(f"  didl {object_id} has item")
                if full_didl is not None:
                    full_didl.append(item)

            # Récursivement parcourir les sous-conteneurs
            for container in didl.findall('.//{*}container'):
                container_id = container.attrib.get('id', '')
                if container_id:
                    sub_didl = self.browse_recursive(control_url, container_id, depth + 1)
                    if sub_didl is not None:
                        # Merge sub_didl items into full_didl
                        for item in sub_didl.findall('.//{*}item'):
                            full_didl.append(item)

        except TypeError as e:
            # 'type' object is not iterable error
            log.error(f"Erreur de type lors du browse du conteneur {object_id}: {e}")
            return full_didl
        except Exception as e:
            log.error(f"Erreur lors du browse du conteneur {object_id}: {e}")
            return full_didl
        return full_didl

    # --------------------------------------------------------------------- #
    # Ajoute tous les <item> du DIDL 'B' dans le DIDL 'A'.
    # --------------------------------------------------------------------- #
    @staticmethod
    def xml_merge(a: ET.Element, b: ET.Element) -> ET.Element:
        for bchild in b:
            a.append(bchild)
        return a


# -------------------------------------------------------------
# TESTS
# -------------------------------------------------------------
if __name__ == "__main__":
    # -------------------------------------------------------------
    # Test de la concaténation des XML
    # -------------------------------------------------------------
    xml_1 = "<DIDL-Lite><item id='28$2857$@2913'><title>Black Magic Woman</title><res>http://192.168.0.101:50002/m/MP3/2913.mp3</res></item></DIDL-Lite>"
    xml_2 = "<DIDL-Lite><item id='28$1245$@1245'><title>Sunny Afternoon</title><res>http://192.168.0.101:50002/m/MP3/1245.mp3</res></item></DIDL-Lite>"
    tree_1 = ET.fromstring(xml_1)
    tree_2 = ET.fromstring(xml_2)
    tree_3 = DLNANetwork.xml_merge(tree_1, tree_2)
    print(ET.tostring(tree_3))
