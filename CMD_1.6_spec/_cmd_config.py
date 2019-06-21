# coding: latin-1
###############################################################################
# Ficheiro de configuração do URL do WSDL a utilizar e da APPLICATION_ID
#
# cmd_config.py  (Python 3)
#
# Copyright (c) 2019 Devise Futures, Lda.
# Developed by José Miranda - jose.miranda@devisefutures.com
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
###############################################################################
"""
Ficheiro de configuração do URL do WSDL a utilizar e da APPLICATION_ID fornecida pela AMA.
"""

# ApplicationId da entidade, fornecida pela AMA
APPLICATION_ID = 'Change to your ApplicationId'


#
# A partir deste ponto, não alterar
#
def get_wsdl(env):
    """Devolve URL do WSDL do SCMD.

    Parameters
    ----------
    t : int
        WSDL a devolver: 0 para preprod, 1 para prod.

    Returns
    -------
    string
        URL do WSDL do SCMD.

    """
    wsdl = {
        0: 'https://preprod.cmd.autenticacao.gov.pt/Ama.Authentication.Frontend/CCMovelDigitalSignature.svc?wsdl',
        1: 'TBD'
    }
    # Get the function from switcher dictionary
    return wsdl.get(env, lambda: 'No valid WSDL')


def get_appid():
    """Devolve APPLICATION_ID (fornecida pela AMA).

    Returns
    -------
    string
        APPLICATION_ID da entidade, fornecida pela AMA.

    """
    return APPLICATION_ID
