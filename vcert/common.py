import datetime
import dateutil.parser
import time
import logging as log
from pprint import pprint
from http import HTTPStatus
from .errors import ConnectionError, ServerUnexptedBehavior


MIME_JSON = "application/json"
MINE_HTML = "text/html"
MINE_TEXT = "text/plain"
MINE_ANY = "*/*"


class CertRequest:
    def __init__(self, csr=None, friendly_name=None, pickup_id=None, chain_option=None):
        self.csr = csr
        self.friendly_name = friendly_name
        self.pickup_id = pickup_id
        self.chain_option = chain_option




class CertStatuses:
    REQUESTED = 'REQUESTED'
    PENDING = 'PENDING'


class CertField(str):
    def __init__(self, *args, **kwargs):
        self.locked = False
        super(CertField, self).__init__(*args, **kwargs)


class Zone:
    def __init__(self, id, company_id, tag, zonetype, cert_policy_ids, default_cert_identity_policy, default_cert_use_policy, system_generated, creation_date):
        """
        :param str id:
        :param str company_id:
        :param str tag:
        :param str zonetype:
        :param cert_policy_ids:
        :param str default_cert_identity_policy:
        :param str default_cert_use_policy:
        :param bool system_generated:
        :param datetime.datetime creation_date:
        """
        self.id = id
        self.company_id = company_id
        self.tag = tag
        self.zonetype = zonetype
        self.cert_policy_ids = cert_policy_ids
        self.default_cert_identity_policy = default_cert_identity_policy
        self.default_cert_use_policy = default_cert_use_policy
        self.system_generated = system_generated
        self.creation_date = creation_date

    def __repr__(self):
        return "%s (%s)" % (self.tag, self.id)

    def __str__(self):
        return self.tag

    @classmethod
    def from_server_response(cls, d):
        return cls(d['id'], d['companyId'], d['tag'], d['zoneType'], d['certificatePolicyIds'],
                   d['defaultCertificateIdentityPolicyId'], d['defaultCertificateUsePolicyId'], d['systemGenerated'],
                   dateutil.parser.parse(d['creationDate']))


class ZoneConfig:
    def __init__(self, organization, organizational_unit, country, province, locality, CustomAttributeValues,
                 SubjectCNRegexes, SubjectORegexes, SubjectOURegexes, SubjectSTRegexes, SubjectLRegexes,
                 SubjectCRegexes, SANRegexes, AllowedKeyConfigurations, KeySizeLocked, HashAlgorithm):
        """
        :param CertField organization:
        :param list[str] organizational_unit:
        :param CertField country:
        :param CertField province:
        :param CertField locality:
        :param dict[str, str] CustomAttributeValues:
        :param list[str] SubjectCNRegexes:
        :param list[str] SubjectORegexes:
        :param list[str] SubjectOURegexes:
        :param list[str] SubjectSTRegexes:
        :param list[str] SubjectLRegexes:
        :param list[str] SubjectCRegexes:
        :param list[str] SANRegexes:
        :param AllowedKeyConfigurations:
        :param bool KeySizeLocked:
        :param HashAlgorithm:
        """

    @classmethod
    def from_server_response(cls, d):
        return cls()


class Policy:
    class Type:
        CERTIFICATE_IDENTITY = "CERTIFICATE_IDENTITY"
        CERTIFICATE_USE = "CERTIFICATE_USE"

    def __init__(self, policy_type=None, id=None, company_id=None, name=None, system_generated=None, creation_date=None, cert_provider_id=None,
                 SubjectCNRegexes=None, SubjectORegexes=None, SubjectOURegexes=None, SubjectSTRegexes=None, SubjectLRegexes=None,
                 SubjectCRegexes=None, SANRegexes=None, KeyTypes=None, KeyReuse=None):
        """
        :param str policy_type:
        :param str id:
        :param str company_id:
        :param str name:
        :param bool ystem_generated:
        :param datetime.datetime creation_date:
        :param str cert_provider_id:
        :param list[str] SubjectCNRegexes:
        :param list[str] SubjectORegexes:
        :param list[str] SubjectOURegexes:
        :param list[str] SubjectSTRegexes:
        :param list[str] SubjectLRegexes:
        :param list[str] SubjectCRegexes:
        :param list[str] SANRegexes:
        :param KeyTypes:
        :param bool KeyReuse:
        """
        self.policy_type = policy_type
        self.id = id
        self.company_id = company_id
        self.name = name
        self.system_generated = system_generated
        self.creation_date = creation_date
        self.cert_provider_id = cert_provider_id
        self.SubjectCNRegexes = SubjectCNRegexes
        self.SubjectORegexes = SubjectORegexes
        self.SubjectOURegexes = SubjectOURegexes
        self.SubjectSTRegexes = SubjectSTRegexes
        self.SubjectLRegexes = SubjectLRegexes
        self.SubjectCRegexes = SubjectCRegexes
        self.SANRegexes = SANRegexes
        self.KeyTypes = KeyTypes
        self.KeyReuse = KeyReuse

    @classmethod
    def from_server_response(cls, d):
        pprint(d)
        return cls(d['certificatePolicyType'], d['id'], d['companyId'], d['name'], d['systemGenerated'],
                   dateutil.parser.parse(d['creationDate']), d.get('certificateProviderId'),
                   d.get('subjectCNRegexes', []), d.get('subjectORegexes', []), d.get('subjectOURegexes', []),
                   d.get('subjectSTRegexes', []), d.get('subjectLRegexes', []), d.get('subjectCRegexes', []),
                   d.get('sanRegexes', []), d.get('keyTypes'), d.get('keyReuse'))

    def __repr__(self):
        return "policy [%s] %s (%s)" % (self.policy_type, self.name, self.id)


class CertificateRequest:
    def __init__(self, id, status):
        self.id = id
        self.status = status

    @classmethod
    def from_server_response(cls, d):
        return cls(d['id'], d['status'])

    @classmethod
    def from_tpp_server_response(cls, d):
        return cls(d['CertificateDN'], d['Guid'])

class Certificate:
    def __init__(self, id, status):
        self.id = id
        self.status = status

    @classmethod
    def from_server_response(cls, d):
        return cls(d['id'], d['status'])


class CommonConnection:
    def _get_cert_status(self, request_id):
        raise NotImplementedError

    def _get_policy_by_ids(self, policy_ids):
        raise NotImplementedError

    def ping(self):
        raise NotImplementedError

    def auth(self):
        raise NotImplementedError

    def register(self, email):
        raise NotImplementedError

    def get_zone_by_tag(self, tag):
        """
        :param str tag:
        :rtype Zone
        """
        raise NotImplementedError

    def build_request(self, country, province, locality, organization, organization_unit, common_name):
        """
        :param str csr: Certitficate in PEM format
        :param str zone: Venafi zone tag name
        """
        raise NotImplementedError

    def request_cert(self, csr, zone):
        """
        :param str csr: Certitficate in PEM format
        :param str zone: Venafi zone tag name
        """
        raise NotImplementedError

    def retrieve_cert(self, request_id):
        raise NotImplementedError

    def revoke_cert(self, request):
        raise NotImplementedError

    def renew_cert(self, request):
        raise NotImplementedError

    def read_zone_conf(self, tag):
        """
        :param str tag:
        :rtype ZoneConfig
        """
        raise NotImplementedError

    def gen_request(self, zone_config, request):
        raise NotImplementedError

    def import_cert(self, request):
        raise NotImplementedError

    def make_request_and_wait_certificate(self, csr, zone):
        """
        :param str csr:
        :param str zone:
        """
        pickup_id = self.request_cert(csr, zone)
        log.info("Send certificate request, got pickupId: %s" % pickup_id)
        while True:
            time.sleep(10)
            log.info("Checking status for %s" % pickup_id)
            cert = self._get_cert_status(pickup_id)
            if cert.status not in (CertStatuses.REQUESTED, CertStatuses.PENDING):
                break
        log.info("Status: %s" % cert.status)
        return cert

    @staticmethod
    def process_server_response(r):
        if r.status_code not in (HTTPStatus.OK, HTTPStatus.ACCEPTED):
            raise ConnectionError("Server status: %s, %s\n Response: %s", (r.status_code, r.request.url, r._content))
        content_type = r.headers.get("content-type")
        if content_type == MINE_TEXT:
            log.debug(r.text)
            return r.status_code, r.text
        elif content_type == MINE_HTML:
            log.debug(r.text)
            return r.status_code, r.text
        # content-type in respons is  application/json; charset=utf-8
        elif content_type.startswith(MIME_JSON):
            log.debug(r.content.decode())
            return r.status_code, r.json()
        else:
            log.error("unexpected content type: %s for request %s" % (content_type, r.request.url))
            raise ServerUnexptedBehavior