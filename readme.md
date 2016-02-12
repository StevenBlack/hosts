#Arquivo de hosts mesclados

Este repositório consolida vários arquivos 'hosts' confiáveis e mescla-os em um único arquivo de hosts com duplicatas removidas.

**Atualmente este arquivo de hosts contém 27,139 entradas únicas.**

## Objetivos do arquivo de hosts mesclados

Os objetivos deste repositório são

1) combinar automaticamente uma lista de hosts de alta qualidade

2) retirar duplicatas da lista combinada

3) manter o arquivo resultante com um tamanho razoável

Uma fonte de alta qualidade é definida aqui como uma que é ativamente curada. Uma fonte de hosts deve ser frequentemente
atualizada pelos seus responsáveis com adições e remoções. Quanto maior o arquivo de hosts, maior é o nível de cuidado
esperado.

Por exemplo, o (enorme) arquivo de hosts do [hosts-file.net](http://hosts-file.net) **não** está incluído aqui pois
ele é muito grande (mais de 300,000 entradas) e atualmente não demonstra um nível correspondente de cuidados.

É esperado que este arquivo de hosts mesclados funcione bem em dispositivos de mesa ou portáteis suportando uma grande
variedade de sistemas operacionais.

## Fontes de dados de hosts mesclados

Atualmente os arquivos de 'hosts' das seguintes fontes são mesclados:

* O [arquivo de hosts Adaway](http://adaway.org/hosts.txt), atualizado regularmente.
* Arquivo de hosts do MVPs.org em[http://winhelp2002.mvps.org/hosts.htm](http://winhelp2002.mvps.org/hosts.htm), atualizado
mensalmente.
* Dan Pollock em [http://someonewhocares.org/hosts/](http://someonewhocares.org/hosts/) atualizado regularmente.
* Malware Domain List em [http://www.malwaredomainlist.com/](http://www.malwaredomainlist.com/), atualizado regularmente.
* Peter Lowe em [http://pgl.yoyo.org/adservers/](http://pgl.yoyo.org/adservers/), atualizado regularmente.
* A pequena lista do autor Steven Black [aqui](https://raw.github.com/StevenBlack/hosts/master/data/StevenBlack/hosts).

Você pode adicionar mais fontes colocando-as na pasta 'data/'. Forneça uma cópia do novo arquivo 'hosts'
e coloque sua url de atualização em 'update.info'. A rotina 'updateHostsFile.py' irá automaticamente
atualizar o arquivo 'hosts' de cada fonte todas as vezes que um novo arquivo mesclado é gerado.

## Como incorporar meus próprios hosts?

Se você possui um arquivo de hosts própiro, coloque-o no arquivo 'myhosts'. O conteúdo deste arquivo é adicionado ao
arquivo de hosts mesclados durante o processo de atualização.

## Usando updateHostsFile.py

Este script Python vai gerar um arquivo de hosts personalizado baseado nas fontes da pasta 'data/'.
Você pode fazer com que o script busque uma versão atualizada pela internet (definida pelo arquivo update.info
no diretório da fonte), ou ele usará o arquivo 'hosts' já encontrado locamente.

Utilização

    python updateHostsFile.py

**ATENÇÃO** este script foi testado com a versão 2.7.10 do Python.

## O que é um arquivo de hosts?

Um arquivo de hosts, chamado 'hosts' (sem extensão de arquivo), é um arquivo de texto puro usado por todos
os sistemas operacionais para mapear nomes e endereços IP.

Na maioria dos sistemas operacionais, o arquivo 'hosts' é preferencial ao 'DNS'. Então se um nome é resolvido
pelo arquivo 'hosts', a requisição nunca sai do computador.

Ter um arquivo 'hosts' inteligente permite bloquear malwares, adwares e outras irritações.

Por exemplo, para anular requisições para alguns servidores da doubleclick.net, você pode adicionar estas
linhas ao seu arquivo 'hosts':

    # bloquear servidores doubleClick
    127.0.0.1 ad.ae.doubleclick.net
    127.0.0.1 ad.ar.doubleclick.net
    127.0.0.1 ad.at.doubleclick.net
    127.0.0.1 ad.au.doubleclick.net
    127.0.0.1 ad.be.doubleclick.net
    # etc...


## Por que usar '0.0.0.0' em vez de '127.0.0.1'?
Usar '0.0.0.0' é mais rápido pois você não precisa esperar por um timeout. Isso também não interfere com um servidor
web que esteja rodando no PC local.

## Por que não usar somente '0' em vez de '0.0.0.0'?
Nós tentamos isso. Usar '0' não funciona em todos os casos.

## Localização do seu arquivo de hosts
Para modificar o seu arquivo 'hosts' atual, procure-o nos seguintes lugares e modifique-o com um editor de texto.

**Mac OS X, iOS, Android, Linux**: pasta '/etc/hosts'.

**Windows**: pasta '%SystemRoot%\system32\drivers\etc\hosts'.

## Recarregar o arquivo de hosts
O seu sistema operacional cria um cachê de DNS. Você pode reiniciar ou rodar os seguintes comandos para remover
manualmente o cachê de DNS uma vez que o novo arquivo de hosts for configurado.

### Mac OS X
Abra o Terminal e rode:

'sudo dscacheutil -flushcache;sudo killall -HUP mDNSResponder'

### Windows
Abra o Prompt de Comando:

**Windows XP**: Inciar -> Executar -> 'cmd'

**Windows Vista, 7**: Iniciar -> digite 'cmd' -> clique com o botão direito em Prompt de Comando ->
"Executar como Administrador"

**Windows 8**: Iniciar -> Arrastar para Cima -> Todos os Aplicativos -> Sistema ->
clique com o botão direito em Prompt de Comando -> "Executar como Administrador"

e rode o seguinte comando:

'ipconfig /flushdns'

### Linux
Abra um Terminal e execute o seguinte comando com privilégios de superusuário:

**Debian/Ubuntu** 'sudo /etc/rc.d/init.d/nscd restart'

**Linux com systemd**: 'sudo systemctl restart network.service'

**Linux Fedora**: 'sudo systemctl restart NetworkManager.service'

**Arch Linux/Manjaro**: 'sudo systemctl restart NetworkManager.service'
