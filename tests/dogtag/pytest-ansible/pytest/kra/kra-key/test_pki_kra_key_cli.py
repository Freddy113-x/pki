#!/usr/bin/python
# -*- coding: UTF-8 -*-

"""
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Description: PKI KRA KEY CLI tests
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#   The following kra-key cli commands needs to be tested:
#   pki kra-key-find
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Author: Akshay Adhikari <aadhikar@redhat.com>
#
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#   Copyright (c) 2017 Red Hat, Inc. All rights reserved.
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

import pytest

@pytest.mark.parametrize('cmd', ('', '--help'))
def test_pki_kra_key_help(ansible_module, cmd):
    """
    :id: 4baa8437-caab-4578-96ab-f942678aac00

    :Title: RHCS-TC Test pki kra-key with '' and '--help'

    :Test: Test pki kra-key with '' and '--help'

    :Description:
            This command will test the pki kra-key with '' and '--help' option,
            for '' option it is expected to show the keys form the database, and
            for '--help' it should show the help message.

    :Requirement: pki kra-key

    :CaseComponent: \-

    :Type:

    :Steps:
            1. pki kra-key
            2. pki kra-key --help
    :ExpectedResults:
            1. Both options should list various option assosiacted with kra-key.
    """
    contacted = ansible_module.command('pki kra-key %s' % cmd)
    for (host, result) in contacted.items():
        assert "kra-key-template-find   List request template IDs" in result['stdout']
        assert "kra-key-template-show   Get request template" in result['stdout']
        assert "kra-key-request-find    Find key requests" in result['stdout']
        assert "kra-key-request-show    Get key request" in result['stdout']
        assert "kra-key-request-review  Review key request" in result['stdout']
        assert "kra-key-find            Find keys" in result['stdout']
        assert "kra-key-show            Get key" in result['stdout']
        assert "kra-key-mod             Modify the status of a key" in result['stdout']
        assert "kra-key-generate        Generate key" in result['stdout']
        assert "kra-key-archive         Archive a secret in the DRM." in result['stdout']
        assert "kra-key-retrieve        Retrieve key" in result['stdout']
        assert "kra-key-recover         Create a key recovery request" in result['stdout']