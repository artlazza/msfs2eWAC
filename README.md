# msfs2fltplan eWac
 Esse programa foi desenvolvido baseado no msfs2fltplan (https://github.com/musurca/msfs2fltplan/). A ideia foi adaptá-lo para fornecer informações do Microsoft Flight Simulator 2020 ao aplicativo eWac para iOS, muito utilizado para navegação no Brasil. Essa ferramenta permite que você defina o endereço IP do seu dispositivo iOS com eWac e obtenha informações em tempo real do simulador no aplicativo.

## Instalação
1) Instalar a versão de 64-bit do [Python 3](https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe). (Tenha a certeza de adicionar o Python à variável de ambiente PATH.
2) Baixe [a última versão deste programa](https://github.com/artlazza/msfs2fltplan/releases/download/v1.2/msfs2fltplaneWac-v1.2.zip) e extraia para um diretório à sua escolha, como `C:\fltplan`

## Como Usar
1) Abra o Microsoft Flight Simulator
2) Utilizando a linha de comando (cmd.exe), selecione o diretório onde você instalou esse repositório (p. ex. `cd C:\fltplan\msfs2fltplaneWac-v1.2\msfs2fltplan-master`)
3) Uma vez no diretório digite `connect [endereço_ip]` sendo que o IP é o do seu dispositivo iOS rodando o eWac. Tanto o computador rodando o MSFS e o dispositivo iOS têm que estar na mesma rede. Por exemplo:
```
connect 192.168.1.209
``` 
4) Siga as instruções dos seguintes vídeos para configurar o eWac no iOS para receber informações. [Vídeo de configuração do iOS - eWac Aplicativos Aeronáuticos](https://www.youtube.com/watch?v=p97PYZCamAQ&ab_channel=AplicativosAeron%C3%A1uticos)
5) Pronto! Seu eWac já deve estar recebendo as informações do MSFS 2020.

NOTA: Você também consegue enviar as informações para múltiplos aparelhos utilizando o eWac (por exemplo um iPhone e um iPad simultaneamente), basta digitar no passo 3:
```
connect 192.168.1.209 192.168.1.202
```

## Dependências
* [Python 3](https://www.python.org/downloads/)
* [Python-SimConnect](https://github.com/odwdinc/Python-SimConnect)
* eWac SUL ([iOS](https://apps.apple.com/br/app/ewac-sul/id417469266)) ou eWac NORTE ([iOS](https://apps.apple.com/br/app/ewac-norte/id417472070))
