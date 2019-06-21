# coding: latin-1
###############################################################################
# Teste das operações do serviço CMD (versão 1.6 da "CMD - Especificação dos serviços de Assinatura")
#
# test_cmd_old_wsdl.py  (Python 3)
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
Programa de teste (em Python3) das operações do serviço SCMD.

Linha de comando para exemplificar a comunicação com as várias operações do
serviço SCMD (SOAP), nomeadamente:
  + GetCertificate
          (applicationId: xsd:base64Binary, userId: xsd:string)
          -> GetCertificateResult: xsd:string
  + CCMovelSign
        (request: ns2:SignRequest)
        -> CCMovelSignResult: ns2:SignStatus
  + CCMovelMultipleSign
        (request: ns2:MultipleSignRequest, documents: ns2:ArrayOfHashStructure)
        -> CCMovelMultipleSignResult: ns2:SignStatus
  + ValidateOtp
        (code: xsd:string, processId: xsd:string,
            applicationId: xsd:base64Binary)
        -> ValidateOtpResult: ns2:SignResponse

Comunica com o serviço SCMD em preprod (versão 1.6), cujo WSDL se encontra em
https://preprod.cmd.autenticacao.gov.pt/Ama.Authentication.Frontend/CCMovelDigitalSignature.svc?wsdl

Notas:
   1 - Necessário instalar o ZEEP (https://python-zeep.readthedocs.io/en/master/)
   2 - Para inspecionar o WSDL deve-se efetuar: python3 -mzeep <wsdl>
"""

import sys
import argparse           # parsing de argumentos comando linha
from zeep import Client   # zeep para SOAP

import cmd_soap_msg
import cmd_config   # Nota: necessário renomear o ficheiro _cmd_config.py para cmd_config.py

TEXT = 'Preprod Signature CMD (SOAP) version 1.6 test Command Line Program'
VERSION = 'version: 1.0'


WSDL = cmd_config.get_wsdl(0)
APPLICATION_ID = cmd_config.get_appid()


def main():
    """Função main do programa."""
    if not APPLICATION_ID:
        print('Configure o APPLICATION_ID')
        sys.exit()
    args = args_parse()
    if len(sys.argv) > 1:
        if args.debug:
            cmd_soap_msg.debug()
        client = Client(WSDL)
        print(args.func(client, args))
    else:
        print('Use -h for usage:\n  ', sys.argv[0], '-h for all operations\n  ', sys.argv[0],
              '<oper1> -h for usage of operation <oper1>')


def args_parse():
    """Define as várias opções do comando linha."""
    parser = argparse.ArgumentParser(description=TEXT)
    parser.add_argument('-V', '--version', help='show program version', action='version',
                        version=VERSION)

    subparsers = parser.add_subparsers(title='CCMovelDigitalSignature Service',
                                       help='Signature CMD (SCMD) operations')

    # GetCertificate command
    gc_parser = subparsers.add_parser('GetCertificate', help='Get user certificate', aliases=['gc'],
                                      description='Get user certificate')
    gc_parser.add_argument('user', action='store', help='user phone number (+XXX NNNNNNNNN)')
    gc_parser.add_argument('-applicationId', action='store', help='CMD ApplicationId',
                           default=APPLICATION_ID)
    gc_parser.add_argument('-D', '--debug', help='show debug information', action='store_true')
    gc_parser.set_defaults(func=cmd_soap_msg.getcertificate)

    # CCMovelSign command
    ms_parser = subparsers.add_parser('CCMovelSign', help='Start signature process',
                                      aliases=['ms'], description='Start signature process')
    ms_parser.add_argument('user', action='store', help='user phone number (+XXX NNNNNNNNN)')
    ms_parser.add_argument('pin', action='store', help='CMD signature PIN')
    ms_parser.add_argument('-applicationId', action='store', help='CMD ApplicationId',
                           default=APPLICATION_ID)
    ms_parser.add_argument('-D', '--debug', help='show debug information', action='store_true')
    ms_parser.set_defaults(func=cmd_soap_msg.ccmovelsign)

    # CCMovelMultipleSign command
    mms_parser = subparsers.add_parser('CCMovelMultipleSign',
                                       help='Start multiple signature process', aliases=['mms'],
                                       description='Start multiple signature process')
    mms_parser.add_argument('user', action='store', help='user phone number (+XXX NNNNNNNNN)')
    mms_parser.add_argument('pin', action='store', help='CMD signature PIN')
    mms_parser.add_argument('-applicationId', action='store', help='CMD ApplicationId',
                            default=APPLICATION_ID)
    mms_parser.add_argument('-D', '--debug', help='show debug information', action='store_true')
    mms_parser.set_defaults(func=cmd_soap_msg.ccmovelmultiplesign)

    # ValidateOtp command
    val_parser = subparsers.add_parser('ValidateOtp', help='Validate OTP', aliases=['otp'],
                                       description='Validate OTP')
    val_parser.add_argument('OTP', action='store', help='OTP received in your device')
    val_parser.add_argument('ProcessId', action='store',
                            help='ProcessID received in the answer of the CCMovelSign/CCMovelMultipleSign command')
    val_parser.add_argument('-applicationId', action='store', help='CMD ApplicationId',
                            default=APPLICATION_ID)
    val_parser.add_argument('-D', '--debug', help='show debug information', action='store_true')
    val_parser.set_defaults(func=cmd_soap_msg.validate_otp)

    # testall command
    test_parser = subparsers.add_parser('TestAll', help='Automatically test all commands',
                                        aliases=['test'],
                                        description='Automatically test all commands')
    test_parser.add_argument('user', action='store', help='user phone number (+XXX NNNNNNNNN)')
    test_parser.add_argument('pin', action='store', help='CMD signature PIN')
    test_parser.add_argument('-applicationId', action='store', help='CMD ApplicationId',
                             default=APPLICATION_ID)
    test_parser.add_argument('-D', '--debug', help='show debug information', action='store_true')
    test_parser.set_defaults(func=testall)

    return parser.parse_args()


# Testa todos os comandos
def testall(client, args):
    """Prepara e executa todos os comandos SCMD em sequência."""
    print('+++\n+Testing GetCertificate\n+++')
    print(cmd_soap_msg.getcertificate(client, args))
    print('\n+++\n+Testing CCMovelSign\n+++')
    res = cmd_soap_msg.ccmovelsign(client, args)
    print(res)
    vars(args)['ProcessId'] = res['ProcessId']
    print('\n+++\n+Testing ValidateOtp\n+++')
    vars(args)['OTP'] = input('Enter OTP received in your device: ')
    print(cmd_soap_msg.validate_otp(client, args))
    print('\n+++\n+Testing CCMovelMultipleSign\n+++')
    res = cmd_soap_msg.ccmovelmultiplesign(client, args)
    print(res)
    vars(args)['ProcessId'] = res['ProcessId']
    print('\n+++\n+Testing ValidateOtp\n+++')
    vars(args)['OTP'] = input('Enter OTP received in your device: ')
    print(cmd_soap_msg.validate_otp(client, args))
    return '\n+++ Test All end\n'


if __name__ == "__main__":
    main()
