# CMD-SOAP - Teste das operações do serviço SCMD (Signature CMD)

Na diretoria CMD_1.6_spec encontra os ficheiros que lhe permitem testar as
operações do serviço SCMD (Signature
CMD), de acordo com a versão 1.6 da "CMD - Especificação dos serviços de
Assinatura", utilizando a linguagem de programação python (versão 3).

Nessa diretoria encontram-se três ficheiros:

+ cmd_soap_msg.py - contém as funções que preparam e executam os comandos
SOAP do SCMD, nomeadamente:
  + GetCertificate
  + CCMovelSign
  + CCMovelMultipleSign
  + ValidateOtp
+ \_cmd_config.py - Ficheiro que deve ser renomeado para cmd_config.py e onde
deve colocar o ApplicationId fornecido pela AMA.
+ test_cmd_wsdl.py - Permite-lhe testar os vários comandos SOAP do SCMD.


### 1. Utilização da aplicação de testes

As várias opções da _command line interface_ (CLI) da aplicação de testes podem
ser visualizadas  através da execução de `python3 test_cmd_wsdl.py -h`.

As opções de cada operação podem ser visualizadas  através da execução de
`python3 test_cmd_wsdl.py <oper> -h`, em que `<oper>` é uma das seguintes
operações:

+ "GetCertificate" ou "gc"
  + testa o comando SOAP GetCertificate do SCMD
+ "CCMovelSign" ou "ms"
  - testa o comando SOAP CCMovelSign do SCMD
+ "CCMovelMultipleSign" ou "mms"
  - testa o comando SOAP CCMovelMultipleSign do SCMD
+ "ValidateOtp" ou "otp"
  - testa o comando SOAP ValidateOtp do SCMD
+ "TestAll" ou "test"
  - testa automaticamente a sequência de comandos GetCertificate, CCMovelSign e
ValidateOtp, verificando no final a assinatura,  baseado na assinatura
recebida, na hash gerada e na chave pública do certificado recebido.

Por defeito é feita a ligação ao serviço SCMD de pré-produção - no caso de
pretender utilizar o serviço SCMD de produção tem que incluir o argumento
opcional `-prod` na linha de comando.

#### 1.1 Exemplo do "TestAll"

Para efetuar o teste à sequência de comandos GetCertificate, CCMovelSign e
ValidateOtp, deve utilizar a seguinte linha de comando:

        python3 test_cmd_wsdl.py test -prod ../LICENSE '+351 000000000' 12345678

sendo a resposta esperada a seguinte:


        test Command Line Program (for Preprod/Prod Signature CMD (SOAP) version 1.6 technical specification)
        version: 1.0

        +++ Test All inicializado +++

         0% ... Leitura de argumentos da linha de comando - file: ../LICENSE user: +351 000000000 pin: 12345678
        10% ... A contactar servidor SOAP CMD para operação GetCertificate

        20% ... Certificado emitido para "JOSÉ EDUARDO PINA DE MIRANDA" pela Entidade de Certificação "EC de Chave Móvel Digital de Assinatura Digital Qualificada do Cartão de Cidadão 00003" na hierarquia do "Cartão de Cidadão 006"
        30% ... Leitura do ficheiro ../LICENSE
        40% ... Geração de hash do ficheiro ../LICENSE
        50% ... Hash gerada (em base64): OXLcl0T2SZ8Pmy2/dmlvKuetivmyPd5m1q+Gyd+zaYY=
        60% ... A contactar servidor SOAP CMD para operação CCMovelSign
        70% ... ProcessID devolvido pela operação CCMovelSign: 64947c5a-8f59-4c27-a665-a10697fc0308
        80% ... A iniciar operação ValidateOtp
        Introduza o OTP recebido no seu dispositivo: 255305
        90% ... A contactar servidor SOAP CMD para operação ValidateOtp
        100% ... Assinatura (em base 64) devolvida pela operação ValidateOtp: IOrEF2zu+MSls8E6FHI5oT84nyEok5fCmF6RHGeEK83rsViIzpih4qOyRue8iEndEKI0vpXtg0nMKcVWhkI9gwzHia8GJ9XH4+iFRj2jvSX/MNiBYuPldeouHK05/Tuw6760X3hNpJvVu+JVtO86maVExv64PJNh3Huf4zvW5HM3TUu0xQ1nup4rdn49b0DYPqymrFp3Q+Zj5h6xO2/354HqsstPfymz28GmOqqFecX/woAlizvGHVnFnazN+qeV/Z01gDv2kqkGdqtcYHStNN1Ivb0gjkmihTyp4eYL+PykzLXd2qOc+x2ibQyf/BUh1i09ayHCL5JIDzoTVtpZtNBVClbZLafTRUKfF0f8+SD7y1/j3RKPuAr/hIKlGuS+1B6h6fVk6Z3arRUFlL+ZCXo3Usiy2MkvUb0toxsVRFaPCZRNjqpuBDhMkphIEXD4wAaP0Q1wZ1n1V1AV06L50res4Io94iU64N6xu915xVAAFX9yQBtBYjFaG6WS9IA0
        110% ... A validar assinatura ...
        Assinatura verificada com sucesso, baseada na assinatura recebida, na hash gerada e na chave pública do certificado de JOSÉ EDUARDO PINA DE MIRANDA

        +++ Test All finalizado +++



### 2. Notas genéricas:

1. Necessário instalar as seguintes packages python, por exemplo com recurso ao
pip3:

  - hashlib
  - logging
  - zeep
  - argparse           
  - base64
  - pem
  - OpenSSL
  - Crypto

2. A aplicação deve ser utilizada com Python 3.7.3 ou superior

3. Antes de utilizar, renomeie o ficheiro \_cmd_config.py para cmd_config.py
e introduza o APPLICATION_ID da sua entidade (atribuído pela AMA)

4. Licença: GNU GENERAL PUBLIC LICENSE Version 3
