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
Programa de teste (em Python3) das operações do serviço SCMD, para a versão 1.6
da especificação CMD.

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

Comunica com o serviço SCMD em preprod e prod (versão 1.6), cujo WSDL se encontra respetivamente
em
https://preprod.cmd.autenticacao.gov.pt/Ama.Authentication.Frontend/CCMovelDigitalSignature.svc?wsdl
e https://cmd.autenticacao.gov.pt/Ama.Authentication.Frontend/CCMovelDigitalSignature.svc?wsdl

Notas:
   1 - Necessário instalar o ZEEP (https://python-zeep.readthedocs.io/en/master/)
   2 - Para inspecionar o WSDL deve-se efetuar: python3 -mzeep <wsdl>
"""

import sys
import argparse           # parsing de argumentos comando linha
import hashlib            # hash SHA256
import base64
import pem
from OpenSSL import crypto
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA

import cmd_soap_msg
import cmd_config   # Nota: necessário renomear o ficheiro _cmd_config.py para cmd_config.py

TEXT = 'test Command Line Program (for Preprod/Prod Signature CMD (SOAP) version 1.6 technical specification)'
__version__ = '1.0'

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
        client = cmd_soap_msg.getclient(args.prod)
        print(args.func(client, args))
    else:
        print('Use -h for usage:\n  ', sys.argv[0], '-h for all operations\n  ', sys.argv[0],
              '<oper1> -h for usage of operation <oper1>')


def args_parse():
    """Define as várias opções do comando linha."""
    parser = argparse.ArgumentParser(description=TEXT)
    parser.add_argument('-V', '--version', help='show program version', action='version',
                        version='%(prog)s v' + sys.modules[__name__].__version__)

    subparsers = parser.add_subparsers(title='CCMovelDigitalSignature Service',
                                       help='Signature CMD (SCMD) operations')

    # GetCertificate command
    gc_parser = subparsers.add_parser('GetCertificate', help='Get user certificate', aliases=['gc'],
                                      description='Get user certificate')
    gc_parser.add_argument('user', action='store',
                           help='user phone number (+XXX NNNNNNNNN)')
    gc_parser.add_argument('-applicationId', action='store', help='CMD ApplicationId',
                           default=APPLICATION_ID)
    gc_parser.add_argument('-prod', action='store_true',
                           help='Use production SCMD service (preproduction SCMD service used by default)')
    gc_parser.add_argument(
        '-D', '--debug', help='show debug information', action='store_true')
    gc_parser.set_defaults(func=cmd_soap_msg.getcertificate)

    # CCMovelSign command
    ms_parser = subparsers.add_parser('CCMovelSign', help='Start signature process',
                                      aliases=['ms'], description='Start signature process')
    ms_parser.add_argument('user', action='store',
                           help='user phone number (+XXX NNNNNNNNN)')
    ms_parser.add_argument('pin', action='store', help='CMD signature PIN')
    ms_parser.add_argument('-applicationId', action='store', help='CMD ApplicationId',
                           default=APPLICATION_ID)
    ms_parser.add_argument('-prod', action='store_true',
                           help='Use production SCMD service (preproduction SCMD service used by default)')
    ms_parser.add_argument(
        '-D', '--debug', help='show debug information', action='store_true')
    ms_parser.set_defaults(func=cmd_soap_msg.ccmovelsign)

    # CCMovelMultipleSign command
    mms_parser = subparsers.add_parser('CCMovelMultipleSign',
                                       help='Start multiple signature process', aliases=['mms'],
                                       description='Start multiple signature process')
    mms_parser.add_argument('user', action='store',
                            help='user phone number (+XXX NNNNNNNNN)')
    mms_parser.add_argument('pin', action='store', help='CMD signature PIN')
    mms_parser.add_argument('-applicationId', action='store', help='CMD ApplicationId',
                            default=APPLICATION_ID)
    mms_parser.add_argument('-prod', action='store_true',
                            help='Use production SCMD service (preproduction SCMD service used by default)')
    mms_parser.add_argument(
        '-D', '--debug', help='show debug information', action='store_true')
    mms_parser.set_defaults(func=cmd_soap_msg.ccmovelmultiplesign)

    # ValidateOtp command
    val_parser = subparsers.add_parser('ValidateOtp', help='Validate OTP', aliases=['otp'],
                                       description='Validate OTP')
    val_parser.add_argument('OTP', action='store',
                            help='OTP received in your device')
    val_parser.add_argument('ProcessId', action='store',
                            help='ProcessID received in the answer of the CCMovelSign/CCMovelMultipleSign command')
    val_parser.add_argument('-applicationId', action='store', help='CMD ApplicationId',
                            default=APPLICATION_ID)
    val_parser.add_argument('-prod', action='store_true',
                            help='Use production SCMD service (preproduction SCMD service used by default)')
    val_parser.add_argument(
        '-D', '--debug', help='show debug information', action='store_true')
    val_parser.set_defaults(func=cmd_soap_msg.validate_otp)

    # testall command
    test_parser = subparsers.add_parser('TestAll', help='Automatically test all commands',
                                        aliases=['test'],
                                        description='Automatically test all commands')
    test_parser.add_argument('file', action='store', help='file')
    test_parser.add_argument('user', action='store',
                             help='user phone number (+XXX NNNNNNNNN)')
    test_parser.add_argument('pin', action='store', help='CMD signature PIN')
    test_parser.add_argument('-applicationId', action='store', help='CMD ApplicationId',
                             default=APPLICATION_ID)
    test_parser.add_argument('-prod', action='store_true',
                             help='Use production SCMD service (preproduction SCMD service used by default)')
    test_parser.add_argument(
        '-D', '--debug', help='show debug information', action='store_true')
    test_parser.set_defaults(func=testall)

    return parser.parse_args()


# Testa todos os comandos
def testall(client, args):
    """Prepara e executa todos os comandos SCMD em sequência."""
    print(TEXT + "\n" + __version__)
    print('\n+++ Test All inicializado +++\n')
    print(' 0% ... Leitura de argumentos da linha de comando - file: ' + args.file + ' user: '
          + args.user + ' pin: ' + args.pin)
    print('10% ... A contactar servidor SOAP CMD para operação GetCertificate')
    cmd_certs = cmd_soap_msg.getcertificate(client, args)
    if cmd_certs is None:
        print('Impossível obter certificado')
        exit()
    # certs[0] = user; certs[1] = root; certs[2] = CA
    certs = pem.parse(cmd_certs.encode())
    certs_chain = {'user': crypto.load_certificate(crypto.FILETYPE_PEM, certs[0].as_bytes()),
                   'ca': crypto.load_certificate(crypto.FILETYPE_PEM, certs[2].as_bytes()),
                   'root': crypto.load_certificate(crypto.FILETYPE_PEM, certs[1].as_bytes())
                   }
    print('20% ... Certificado emitido para "' + certs_chain['user'].get_subject().CN +
          '" pela Entidade de Certificação "' + certs_chain['ca'].get_subject().CN +
          '" na hierarquia do "' + certs_chain['root'].get_subject().CN + '"')
    print('30% ... Leitura do ficheiro ' + args.file)
    try:
        with open(args.file, "rb") as file:
            file_content = file.read()
    except Exception as e:
        print('Ficheiro não encontrado.')
        exit()
    print('40% ... Geração de hash do ficheiro ' + args.file)
    args.hash = hashlib.sha256(file_content).digest()
    print('50% ... Hash gerada (em base64): ' +
          base64.b64encode(args.hash).decode())
    print('60% ... A contactar servidor SOAP CMD para operação CCMovelSign')
    args.docName = args.file
    res = cmd_soap_msg.ccmovelsign(client, args)
    if res['Code'] != '200':
        print('Erro ' + res['Code'] + '. Valide o PIN introduzido.')
        exit()
    print('70% ... ProcessID devolvido pela operação CCMovelSign: ' +
          res['ProcessId'])
    vars(args)['ProcessId'] = res['ProcessId']
    print('80% ... A iniciar operação ValidateOtp')
    vars(args)['OTP'] = input('Introduza o OTP recebido no seu dispositivo: ')
    print('90% ... A contactar servidor SOAP CMD para operação ValidateOtp')
    res = cmd_soap_msg.validate_otp(client, args)
    if res['Status']['Code'] != '200':
        print('Erro ' + res['Status']['Code'] +
              '. ' + res['Status']['Message'])
        exit()
    print('100% ... Assinatura (em base 64) devolvida pela operação ValidateOtp: ' +
          base64.b64encode(res['Signature']).decode())
    print('110% ... A validar assinatura ...')
    # message = base64.b64decode(dtbs)
    digest = SHA256.new()
    digest.update(file_content)
    public_key = RSA.import_key(certs[0].as_bytes())
    verifier = PKCS1_v1_5.new(public_key)
    verified = verifier.verify(digest, res['Signature'])
    assert verified, 'Falha na verificação da assinatura'
    print('Assinatura verificada com sucesso, baseada na assinatura recebida, na hash gerada e ' +
          'na chave pública do certificado de ' + certs_chain['user'].get_subject().CN)
    return '\n+++ Test All finalizado +++\n'


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:  # catch *all* exceptions
        e = sys.exc_info()
        print("Error: %s" % str(e))
        exit()
