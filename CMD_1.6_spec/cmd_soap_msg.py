# coding: latin-1
###############################################################################
# Teste das operações do serviço CMD (versão 1.6 da "CMD - Especificação dos serviços de
# Assinatura")
#
# Mensagens CMD SOAP
#
# cmd_soap_msg.py  (Python 3)
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
Funções que preparam e executam os comandos SOAP do SCMD, nomeadamente:
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
"""

import hashlib            # hash SHA256
import logging.config     # debug
from zeep import Client   # zeep para SOAP
import cmd_config


# Função para ativar o debug, permitindo mostrar mensagens enviadas e recebidas do servidor SOAP
def debug():
    """Activa o debug, mostrando as mensagens enviadas e recebidas do servidor SOAP."""
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'verbose': {'format': '>> %(name)s: %(message)s'}
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'zeep.transports': {
                'level': 'DEBUG',
                'propagate': True,
                'handlers': ['console'],
            },
        }
    })
    print('>> Debug: On')


def getclient(env=0):
    """Devolve o cliente de ligação ao servidor SOAP da CMD.

    Parameters
    ----------
    int
        WSDL a devolver: 0 para preprod, 1 para prod.

    Returns
    -------
    Zeep.Client
        Devolve o cliente de ligação ao servidor SOAP da CMD.

    """
    return Client(cmd_config.get_wsdl(env))


def getappid():
    """Devolve o APPLICATION_ID.

    Returns
    -------
    Zeep.Client
        Devolve o APPLICATION_ID.

    """
    return cmd_config.get_appid()


# GetCertificate(applicationId: xsd:base64Binary, userId: xsd:string)
#                                       -> GetCertificateResult: xsd:string
def getcertificate(client, args):
    """Prepara e executa o comando SCMD GetCertificate.

    Parameters
    ----------
    client : Client (zeep)
        Client inicializado com o WSDL.
    args : argparse.Namespace
        argumentos a serem utilizados na mensagem SOAP.

    Returns
    -------
    str
        Devolve o certificado do cidadão e a hierarquia de certificação.

    """
    request_data = {
        'applicationId': args.applicationId.encode('UTF-8'),
        'userId': args.user
    }
    return client.service.GetCertificate(**request_data)


# CCMovelSign(request: ns2:SignRequest) -> CCMovelSignResult: ns2:SignStatus
# ns2:SignRequest(ApplicationId: xsd:base64Binary, DocName: xsd:string,
#                  Hash: xsd:base64Binary, Pin: xsd:string, UserId: xsd:string)
# ns2:SignStatus(Code: xsd:string, Field: xsd:string, FieldValue: xsd:string,
#                   Message: xsd:string, ProcessId: xsd:string)
def ccmovelsign(client, args):
    """Prepara e executa o comando SCMD CCMovelSign.

    Parameters
    ----------
    client : Client (zeep)
        Client inicializado com o WSDL.
    args : argparse.Namespace
        argumentos a serem utilizados na mensagem SOAP.

    Returns
    -------
    SignStatus(Code: xsd:string, Field: xsd:string, FieldValue: xsd:string, Message: xsd:string,
    ProcessId: xsd:string)
        Devolve uma estrutura SignStatus com a resposta do CCMovelSing.

    """
    if 'docName' not in args:
        args.docName = 'docname teste'
    if 'hash' not in args:
        args.hash = hashlib.sha256(b'Nobody inspects the spammish repetition').digest()
    request_data = {
        'request': {
            'ApplicationId': args.applicationId.encode('UTF-8'),
            'DocName': args.docName,
            'Hash': hashlib.sha256(args.hash).digest(),
            # 'Hash': b'7Y\x871\xf3N\x8f\x89\xa0Z\xfd\xc0X\xe0\x1a3V\xa4\xea\xce\xbe;lv\xb6\xfbE\xd1Fw\xbd\x03',
            # 'Hash': hashlib.sha256(b'Nobody inspects the spammish repetition').digest(),
            'Pin': args.pin,
            'UserId': args.user
        }
    }
    return client.service.CCMovelSign(**request_data)


# CCMovelMultipleSign(request: ns2:MultipleSignRequest,
#                              documents: ns2:ArrayOfHashStructure)
#                                  -> CCMovelMultipleSignResult: ns2:SignStatus
# ns2:MultipleSignRequest(ApplicationId: xsd:base64Binary, Pin: xsd:string,
#                                                           UserId: xsd:string)
# ns2:ArrayOfHashStructure(HashStructure: ns2:HashStructure[])
# ns2:HashStructure(Hash: xsd:base64Binary, Name: xsd:string, id: xsd:string)
# ns2:SignStatus(Code: xsd:string, Field: xsd:string, FieldValue: xsd:string,
#                   Message: xsd:string, ProcessId: xsd:string)
def ccmovelmultiplesign(client, args):
    """Prepara e executa o comando SCMD CCMovelMultipleSign.

    Parameters
    ----------
    client : Client (zeep)
        Client inicializado com o WSDL.
    args : argparse.Namespace
        argumentos a serem utilizados na mensagem SOAP.

    Returns
    -------
    SignStatus
        Devolve uma estrutura SignStatus com a resposta do CCMovelMultipleSign.

    """
    request_data = {
        'request': {
            'ApplicationId': args.applicationId.encode('UTF-8'),
            'Pin': args.pin,
            'UserId': args.user
        },
        'documents': {
            'HashStructure': [
                {'Hash': hashlib.sha256(b'Nobody inspects the spammish repetition').digest(),
                 'Name': 'docname teste1', 'id': '1234'},
                {'Hash': hashlib.sha256(b'Always inspect the spammish repetition').digest(),
                 'Name': 'docname teste2', 'id': '1235'}
                ]}
    }
    return client.service.CCMovelMultipleSign(**request_data)


# ValidateOtp(code: xsd:string, processId: xsd:string, applicationId:
#                      xsd:base64Binary) -> ValidateOtpResult: ns2:SignResponse
# ns2:SignResponse(ArrayOfHashStructure: ns2:ArrayOfHashStructure,
#                          Signature: xsd:base64Binary, Status: ns2:SignStatus)
# ns2:ArrayOfHashStructure(HashStructure: ns2:HashStructure[])
# ns2:HashStructure(Hash: xsd:base64Binary, Name: xsd:string, id: xsd:string)
# ns2:SignStatus(Code: xsd:string, Field: xsd:string, FieldValue: xsd:string,
#                                   Message: xsd:string, ProcessId: xsd:string)
def validate_otp(client, args):
    """Prepara e executa o comando SCMD ValidateOtp.

    Parameters
    ----------
    client : Client (zeep)
        Client inicializado com o WSDL.
    args : argparse.Namespace
        argumentos a serem utilizados na mensagem SOAP.

    Returns
    -------
    SignResponse
        Devolve uma estrutura SignResponse com a resposta do CCMovelMultipleSign.

    """
    request_data = {
        'applicationId': args.applicationId.encode('UTF-8'),
        'processId': args.ProcessId,
        'code': args.OTP,
    }
    return client.service.ValidateOtp(**request_data)
