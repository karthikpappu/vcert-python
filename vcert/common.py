import datetime
import dateutil.parser
import time
import logging as log
from oscrypto import asymmetric
from csrbuilder import CSRBuilder, pem_armor_csr


class CertStatuses:
    REQUESTED = 'REQUESTED'
    PENDING = 'PENDING'


class CertField(str):
    def __init__(self, *args, **kwargs):
        self.locked = false
        super(CertField, self).__init__(*args, **kwargs)


class Zone:
    def __init__(self, id, company_id, tag, zonetype, cert_policy_ids, default_cert_identity_policy, default_cert_user_policy, system_generated, creation_date):
        """
        :param str id:
        :param str company_id:
        :param str tag:
        :param str zonetype:
        :param cert_policy_ids:
        :param str default_cert_identity_policy:
        :param str default_cert_user_policy:
        :param bool system_generated:
        :param datetime.datetime creation_date:
        """
        self.id = id
        self.company_id = company_id
        self.tag = tag
        self.zonetype = zonetype
        self.cert_policy_ids = cert_policy_ids
        self.default_cert_identity_policy = default_cert_identity_policy
        self.default_cert_user_policy = default_cert_user_policy
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


def build_request(country, province, locality, organization, organization_unit, common_name):
    public_key, private_key = asymmetric.generate_pair('rsa', bit_size=2048)

    data = {
        'country_name': country,
        'state_or_province_name': province,
        'locality_name': locality,
        'organization_name': organization,
        'common_name': common_name,
    }
    if organization_unit:
        data['organizational_unit_name'] = organization_unit
    builder = CSRBuilder(
        data,
        public_key
    )
    builder.hash_algo = "sha256"
    builder.subject_alt_domains = [common_name]
    request = builder.build(private_key)
    return pem_armor_csr(request)


class CertificateRequest:
    def __init__(self, id, status):
        self.id = id
        self.status = status

    @classmethod
    def from_server_response(cls, d):
        return cls(d['id'], d['status'])


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

    def request_cert(self, csr, zone):
        """
        :param str csr:
        :param str zone:
        """
        raise NotImplementedError

    def retrieve_cert(self, request):
        raise NotImplementedError

    def revoke_cert(self, request):
        raise NotImplementedError

    def renew_cert(self, request):
        raise NotImplementedError

    def read_zone_conf(self):
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