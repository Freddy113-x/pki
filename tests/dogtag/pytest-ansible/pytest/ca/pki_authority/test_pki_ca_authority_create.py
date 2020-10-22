"""
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Description: ca-authority tests for Create
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Author: Deepak Punia
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2019 Red Hat, Inc. All rights reserved.
#
#   This copyrighted material is made available to anyone wishing
#   to use, modify, copy, or redistribute it subject to the terms
#   and conditions of the GNU General Public License version 2.
#
#   This program is distributed in the hope that it will be
#   useful, but WITHOUT ANY WARRANTY; without even the implied
#   warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#   PURPOSE. See the GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public
#   License along with this program; if not, write to the Free
#   Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301, USA.
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import logging
from pki.testlib.common.utils import UserOperations, ProfileOperations
import random,binascii
import re
from pki.testlib.common.certlib import os,sys,pytest

try:
    from pki.testlib.common import constants
except Exception as e:
    if os.path.isfile('/tmp/test_dir/constants.py'):
        sys.path.append('/tmp/test_dir')
        import constants

userop = UserOperations(nssdb=constants.NSSDB)
profop = ProfileOperations(nssdb=constants.NSSDB)

log = logging.getLogger()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@pytest.mark.parametrize('args', ['--help', binascii.b2a_hex(os.urandom(10)), ''])
def test_pki_ca_authority_create_help(ansible_module, args):
    """
    :Title: Test pki ca-authority-create --help command.
    :Description: test pki ca-authority-create help command
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c SECret.123
                -n "PKI CA Administrator for Example.Org" ca-authority-create --help
        2. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c SECret.123
                -n "PKI CA Administrator for Example.Org" ca-authority-create asdf
    :Expected results:
        1. It should return help message.
    """
    cmd_out = ansible_module.pki(cli="ca-authority-create",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick='"{}"'.format(constants.CA_ADMIN_NICK),
                                 extra_args='{}'.format(args))
    for result in cmd_out.values():
        if args == '--help':
            assert result['rc'] == 0
            assert "usage: ca-authority-create <dn>" in result['stdout']
            log.info("Successfully ran : '{}'".format(result['cmd']))
        elif args == '':
            assert result['rc'] >= 1
            assert "ERROR: No DN specified." in result['stderr']
            log.info("Successfully ran : '{}'".format(result['cmd']))
        else:
            assert result['rc'] >= 1
            assert 'ERROR: Must specify parent authority' in result['stderr']
            log.info("Successfully run : '{}'".format(result['cmd']))


def test_pki_ca_authority_create_when_authority_is_created(ansible_module):
    """
    :Title: pki ca-authority-create when authority is disabled
    :Description: Execute pki ca-authority-create when authority is disabled
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c SECret.123
                -n "PKI CA Administrator for Example.Org" ca-authority-create testcaUserCert1
                CN="Authority Name" --parent "Authority ID"
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c SECret.123
                -n "PKI CA Administrator for Example.Org" ca-authority-create testcaUserCert1
                CN="Authority Name" --parent "Authority ID"

    :Expected results:
        1. It should show valid error the authority
    """
    test_CN = 'test_CN{}'.format(random.randint(1111, 99999999))
    # find the parent authority id
    authority_id_find = ansible_module.pki(cli="ca-authority-show",
                                           nssdb=constants.NSSDB,
                                           dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                           port=constants.CA_HTTP_PORT,
                                           hostname=constants.MASTER_HOSTNAME,
                                           certnick="'{}'".format(constants.CA_ADMIN_NICK),
                                           extra_args='--host-authority')

    for result in authority_id_find.values():
        authority_id = re.findall('ID:.*', result['stdout'])
        authority_id = authority_id[0].split(":")[1].strip()
    # Create the sub authority with help of parent authority id
    cmd_out = ansible_module.pki(cli="ca-authority-create",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick="'{}'".format(constants.CA_ADMIN_NICK),
                                 extra_args="CN='{}' --parent {}".format(test_CN, authority_id))
    for result in cmd_out.values():
        if result['rc'] == 0:
            assert "Authority DN:" in result['stdout']
            assert "ID:" in result['stdout']
            assert "Parent ID:      {}".format(authority_id) in result['stdout']
            assert "Issuer DN:" in result['stdout']
            assert "Serial no:" in result['stdout']
            assert "Enabled:        true" in result['stdout']
            assert "Ready to sign:  true" in result['stdout']
            log.info("Successfully ran : '{}'".format(result['cmd']))
        else:
            assert result['rc'] >= 1
            log.info("Failed to ran : '{}'".format(result['cmd']))
            pytest.fail()
    # Create again already created authority
    cmd_out = ansible_module.pki(cli="ca-authority-create",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick="'{}'".format(constants.CA_ADMIN_NICK),
                                 extra_args="CN='{}' --parent {}".format(test_CN, authority_id))
    for result in cmd_out.values():
        if result['rc'] >= 1:
            assert "ConflictingOperationException" in result['stderr']
            log.info("Successfully ran : '{}'".format(result['cmd']))
        else:
            assert result['rc'] == 0
            log.info("Failed to ran : '{}'".format(result['cmd']))
            pytest.fail()

    # Search the Sub authority id
    authority_id_find = ansible_module.pki(cli="ca-authority-find",
                                           nssdb=constants.NSSDB,
                                           dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                           port=constants.CA_HTTP_PORT,
                                           hostname=constants.MASTER_HOSTNAME,
                                           certnick="'{}'".format(constants.CA_ADMIN_NICK),
                                           extra_args='--dn "CN={}"'.format(test_CN))
    for result in authority_id_find.values():
        authority_id = re.findall('ID:.*', result['stdout'])
        authority_id = authority_id[0].split(":")[1].strip()
    # Disable the authority
    cmd_out = ansible_module.pki(cli="ca-authority-disable",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick="'{}'".format(constants.CA_ADMIN_NICK),
                                 extra_args="{}".format(authority_id))
    for result in cmd_out.values():
        if result['rc'] == 0:
            assert "Enabled:        false" in result['stdout']
            log.info("Successfully ran : '{}'".format(result['cmd']))
        else:
            assert result['rc'] >= 1
            log.info("Failed to ran : '{}'".format(result['cmd']))
            pytest.fail()
    # delete the authority
    cmd_out = ansible_module.pki(cli="ca-authority-del",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick="'{}'".format(constants.CA_ADMIN_NICK),
                                 extra_args="{} --force".format(authority_id))
    for result in cmd_out.values():
        if result['rc'] == 0:
            assert 'Deleted authority "{}"'.format(authority_id) in result['stdout']
            log.info("Successfully ran : '{}'".format(result['cmd']))
        else:
            assert result['rc'] >= 1
            log.info("Failed to ran : '{}'".format(result['cmd']))
            pytest.fail()


def test_pki_ca_authority_create_as_anonymous_user(ansible_module):
    """
    :Title: pki ca-authority-create as anonymous user
    :Description: Execute pki ca-authority-create as anonymous user should fail
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com
                -c SECret.123 ca-authority-create caAgentFoobar
    :Expected results:
        2. It should return Forbidden Exception

    """
    test_CN = 'test_CN{}'.format(random.randint(1111, 99999999))

    # find the parent authority id
    authority_id_find = ansible_module.pki(cli="ca-authority-show",
                                           nssdb=constants.NSSDB,
                                           dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                           port=constants.CA_HTTP_PORT,
                                           hostname=constants.MASTER_HOSTNAME,
                                           certnick="'{}'".format(constants.CA_ADMIN_NICK),
                                           extra_args='--host-authority')

    for result in authority_id_find.values():
        authority_id = re.findall('ID:.*', result['stdout'])
        authority_id = authority_id[0].split(":")[1].strip()

    # Create the sub authority with help of parent authority id
    cmd_out = ansible_module.pki(cli="ca-authority-create",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick="anonymous",
                                 extra_args="CN='{}' --parent {}".format(test_CN, authority_id))
    for result in cmd_out.values():
        if result['rc'] >= 1:
            assert "Certificate not found: anonymous" in result['stderr']
            log.info("Successfully ran : '{}'".format(result['cmd']))
        else:
            assert result['rc'] == 0
            log.info("Failed to ran : '{}'".format(result['cmd']))
            pytest.fail()


def test_pki_ca_authority_create_as_non_existing_parent_authority(ansible_module):
    """
    :Title: pki ca-authority-create as non-existing parent authority
    :Description: Issue pki ca-authority-create as non-existing parent authority should fail
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c SECret.123
           -n "PKI CA Administrator for Example.Org" ca-authority-create
    :Expected results:
        1. It should return a NotFound Exception
    """
    test_CN = 'test_CN{}'.format(random.randint(1111, 99999999))
    cmd_out = ansible_module.pki(cli="ca-authority-create",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick='"{}"'.format(constants.CA_ADMIN_NICK),
                                 extra_args="CN='{}' --parent NonExistingAuthority".format(test_CN))
    for result in cmd_out.values():
        if result['rc'] >= 1:
            assert 'ERROR: Bad CA ID: NonExistingAuthority' in result['stderr']
            log.info("Successfully ran : {}".format(result['cmd']))
        else:
            log.error("Failed to run : {}".format(result['cmd']))
            pytest.fail()


@pytest.mark.parametrize("valid_user_cert", ["CA_AdminV", "CA_AgentV", "CA_AuditV"])
def test_pki_ca_authority_create_with_valid_user_cert(valid_user_cert, ansible_module):
    """
    :Title: pki ca-authority-create with different valid user's cert
    :Description: Executing pki ca-authority-create using valid user cert should pass
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
    Create the authority with different valid user's certs
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c SECret.123
                -n "Admin Cert" ca-authority-create testcaUserCert1 CN="Authority Name" --parent "Authority ID"
    :Expected results:
        1. It should create the authority
        2. It should disable the authority with only CA_AdminV.
        3. other certs failed with Authorization ERROR
    """
    test_CN = 'test_CN{}'.format(random.randint(1111, 99999999))

    # Search the parent authority id
    authority_id_find = ansible_module.pki(cli="ca-authority-show",
                                           nssdb=constants.NSSDB,
                                           dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                           port=constants.CA_HTTP_PORT,
                                           hostname=constants.MASTER_HOSTNAME,
                                           certnick="'{}'".format(constants.CA_ADMIN_NICK),
                                           extra_args='--host-authority')

    for result in authority_id_find.values():
        authority_id = re.findall('ID:.*', result['stdout'])
        authority_id = authority_id[0].split(":")[1].strip()

    # Create the sub authority
    cmd_out = ansible_module.pki(cli="ca-authority-create",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick="'{}'".format(valid_user_cert),
                                 extra_args="CN='{}' --parent {}".format(test_CN, authority_id))
    for result in cmd_out.values():
        if result['rc'] == 0:
            if valid_user_cert == 'CA_AdminV':
                assert "Authority DN:" in result['stdout']
                assert "ID:" in result['stdout']
                assert "Parent ID:      {}".format(authority_id) in result['stdout']
                assert "Issuer DN:" in result['stdout']
                assert "Serial no:" in result['stdout']
                assert "Enabled:        true" in result['stdout']
                assert "Ready to sign:  true" in result['stdout']
                log.info("Successfully ran : '{}'".format(result['cmd']))
            else:
                log.error("Failed to ran : '{}'".format(result['cmd']))
                pytest.fail()
        else:
            assert 'Authorization Error' in result['stderr']
            log.info("Successfully ran : '{}'".format(result['cmd']))


@pytest.mark.parametrize("revoked_user_cert", ["CA_AdminR", "CA_AgentR", "CA_AuditR"])
def test_pki_ca_authority_create_with_revoked_user_cert(revoked_user_cert, ansible_module):
    """
    :Title: pki ca-authority-create with different revoked user's cert
    :Description: Executing pki ca-authority-create using Revoked user cert should failed
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
    Create the authority with different revoked user's certs
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c SECret.123
                    -n "revoke Cert" ca-authority-create testcaUserCert1
                    CN="Authority Name" --parent "Authority ID"
    :Expected results:
        1. It should create the authority
        2. it should failed with revoked certificate
    """
    test_CN = 'test_CN{}'.format(random.randint(1111, 99999999))

    # find the parent authority id
    authority_id_find = ansible_module.pki(cli="ca-authority-show",
                                           nssdb=constants.NSSDB,
                                           dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                           port=constants.CA_HTTP_PORT,
                                           hostname=constants.MASTER_HOSTNAME,
                                           certnick="'{}'".format(constants.CA_ADMIN_NICK),
                                           extra_args='--host-authority')
    for result in authority_id_find.values():
        authority_id = re.findall('ID:.*', result['stdout'])
        authority_id = authority_id[0].split(":")[1].strip()

    # Create the sub authority
    cmd_out = ansible_module.pki(cli="ca-authority-create",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick="'{}'".format(revoked_user_cert),
                                 extra_args="CN='{}' --parent {}".format(test_CN, authority_id))
    for result in cmd_out.values():
        if result['rc'] >= 1:
            assert "PKIException: Unauthorized" in result['stderr']
            log.info("Successfully ran : '{}'".format(result['cmd']))
        else:
            assert result['rc'] == 0
            log.info("Failed to ran : '{}'".format(result['cmd']))
            pytest.fail()


@pytest.mark.parametrize("expired_user_cert", ["CA_AdminE", "CA_AgentE", "CA_AuditE"])
def test_pki_ca_authority_create_with_expired_user_cert(expired_user_cert, ansible_module):
    """
    :Title: pki ca-authority-create with different Expired user's cert
    :Description: Executing pki ca-authority-create using Expired user cert should failed
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
    Create the authority with different Expired user's certs
        1. pki -d /opt/pki/certdb -P http -p 20080 -h pki1.example.com -c SECret.123
                -n "Admin Cert" ca-authority-create testcaUserCert1 CN="Authority Name" --parent "Authority ID"
    :Expected results:
        1. It should create the authority
        2. Authority disable failed with expired certificate
    """
    test_CN = 'test_CN{}'.format(random.randint(1111, 99999999))

    # find the parent authority id
    authority_id_find = ansible_module.pki(cli="ca-authority-show",
                                           nssdb=constants.NSSDB,
                                           dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                           port=constants.CA_HTTP_PORT,
                                           hostname=constants.MASTER_HOSTNAME,
                                           certnick="'{}'".format(constants.CA_ADMIN_NICK),
                                           extra_args='--host-authority')

    for result in authority_id_find.values():
        authority_id = re.findall('ID:.*', result['stdout'])
        authority_id = authority_id[0].split(":")[1].strip()

    # create the sub authority
    cmd_out = ansible_module.pki(cli="ca-authority-create",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick="'{}'".format(expired_user_cert),
                                 extra_args="CN='{}' --parent {}".format(test_CN, authority_id))
    for result in cmd_out.values():
        if result['rc'] >= 1:
            assert "CERTIFICATE_EXPIRED" in result['stderr']
            log.info("Successfully Run : '{}'".format(result['cmd']))
        else:
            assert result['rc'] == 0
            log.info("Failed to ran : '{}'".format(result['cmd']))
            pytest.fail()


def test_pki_ca_authority_create_with_normal_user_cert(ansible_module):
    """
    :Title: pki ca-authority-create with normal user cert
    :Description: Issue pki ca-authority-create with normal user cert should fail
    :Requirement:
    :Setup: Use the subsystems setup in ansible to run subsystem commands
    :Steps:
        1. Add User
        2. Generate User Cert
        3. Add Cert to User
        4. Add User cert in database
        5. disable profile using the same user cert
    :Expected results:
        1. It should return an Forbidden Exception.
    """
    # Add the user
    user = 'testUserFooBar'
    fullName = 'testUserFooBar'
    subject = "UID={},CN={}".format(user, fullName)
    userop.add_user(ansible_module, 'add', userid=user, user_name=fullName)
    # Generate user cert
    cert_id = userop.process_certificate_request(ansible_module,
                                                 subject=subject,
                                                 request_type='pkcs10',
                                                 algo='rsa',
                                                 keysize='2048',
                                                 profile='caUserCert')
    # Add cert to user
    ansible_module.pki(cli='ca-user-cert-add',
                       nssdb=constants.NSSDB,
                       dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                       port=constants.CA_HTTP_PORT,
                       hostname=constants.MASTER_HOSTNAME,
                       certnick='"{}"'.format(constants.CA_ADMIN_NICK),
                       extra_args='{} --serial {}'.format(user, cert_id))
    # Import Cert to db
    cert_import = 'pki -d {} -c {} -p {} -h {} client-cert-import "{}" ' \
                  '--serial {}'.format(constants.NSSDB,
                                       constants.CLIENT_DIR_PASSWORD,
                                       constants.CA_HTTP_PORT,
                                       constants.MASTER_HOSTNAME, user,
                                       cert_id)
    ansible_module.command(cert_import)

    test_CN = 'test_CN{}'.format(random.randint(1111, 99999999))

    # find the root authority DN
    authority_id_find = ansible_module.pki(cli="ca-authority-show",
                                           nssdb=constants.NSSDB,
                                           dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                           port=constants.CA_HTTP_PORT,
                                           hostname=constants.MASTER_HOSTNAME,
                                           certnick="'{}'".format(constants.CA_ADMIN_NICK),
                                           extra_args='--host-authority')

    for result in authority_id_find.values():
        authority_id = re.findall('ID:.*', result['stdout'])
        authority_id = authority_id[0].split(":")[1].strip()

    # Create the authority with admin cert
    cmd_out = ansible_module.pki(cli="ca-authority-create",
                                 nssdb=constants.NSSDB,
                                 dbpassword=constants.CLIENT_DATABASE_PASSWORD,
                                 port=constants.CA_HTTP_PORT,
                                 hostname=constants.MASTER_HOSTNAME,
                                 certnick='"{}"'.format(user),
                                 extra_args="CN='{}' --parent {}".format(test_CN, authority_id))
    for result in cmd_out.values():
        if result['rc'] >= 1:
            log.info("Successfully run : '{}'".format(result['cmd']))
        else:
            log.info("Failed to ran : '{}'".format(result['cmd']))
            pytest.fail()
    # Remove the cert from nssdb
    cert_remove = 'pki -d {} -c {} -p {} -h {} client-cert-del {}'.format(
        constants.NSSDB,
        constants.CLIENT_DIR_PASSWORD,
        constants.CA_HTTP_PORT,
        constants.MASTER_HOSTNAME, user)
    ansible_module.command(cert_remove)