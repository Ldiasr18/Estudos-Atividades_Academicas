# Tutorial servidor windows

Foi utilizado o virtualBox para criar as maquinas virtuais.

Foi utilizado o virtual box, com uma cópia do windows server 2016, a instalação foi normal. Foi escolhido a opção com interface gráfica. 
A senha escolhida foi: 123456Asd.

**obs: Algumas configurações vou passar por cima, já que foi detalhado na criação do ubuntuServer, recomendo que leie o documento do ubuntuServer antes desse caso para evitar dúvidas.

**obs2: Tudo aqui é basicamente clicar a aceitar, muita pouca configuração é feita "na mão", então não estranhe grande parte do tutorial seja "clique aqui, clique ali, escreva, clique d3e novo"


## Serviços funcionando:

- [x] DHCP
- [x] DNS
- [x] WEB
- [x] Banco de dados
- [x] E-mail
- [x] Sistema de arquivos
- [x] FTP

## Primeiros passos:

Antes de ligar a máquina, no virtualNBox, entre nas configurações da máquina ruindows, e ligue outro adaptador de rede, com uma rede internerta, e coloque um nome, estou usando lablocal

Como vamos trabalhar só com ipv4, desabilitaremos o ipv6 e vamos configurar um ip fix e um nome para o computador.

para isso, clique com o botão direito no icone do windows, clique em task manager, procure por network and internet, network and sharing center, clique em ethernet e propriedades.

desabilite o ipv6 e dê dois cliques no ipv4 e coloque um ip estático, estou usando: 172.16.21.1 com máscara de rede 255.255.255.0 

No dns, coloque o mesmo endereço do ip, pois criaremos um servidor dns em breve.

Para verificar se deu tudo certo, abra o cmd e escreva 
		
		ipconfig

Para mudar o nome do comuputador clique com o botão direito sobre o simbolo do window, system -> clique em change settings -> change e escolha um nome para o computador e depois clique em ok. Será perguntado se quer reiniciar o computador, reinicie e pronto.


## Active directory

Mesmo não usando, se faz necessário a instalação do active directory no windows server, para isso, clique em "add roles and features", selecione o Active directory domain service, clique em next, adicionar recursos, next, next, install. Clique na bandeira que estará com um sinal de exclamação amarelo e inicie a configuração, na primeira tela clique em "add new forest" e escolha o nome do dominio, usarei lab.local aqui, clique em próximo, deixa as configurações padrões e coloque uma senha, aqui estou usando 123456Asd mesmo, clique em next, next, next, deixe padrão e clique em next, next, install, o computador deve reiniciar, faça login e pronto. 

## DHCP

Para instalar o serviço de DHCP clique em "add roles and features", clique em próximo, selecione a primeira opção: "Role-based or feature based intallations", clique em próximo, selecione o servidor (já deve estar selecionado por padrão), e clique em próximo. Marque a opção de servidor de dhcp, vai abrir uma caixa informando os recursos adicionais, aceite, clique em próximo, não é necessário instalação nenhum outro recurso no momento então clique em próximo, próximo, clique para instalar e espere terminar de instalar.

Do lado esquerdo, aparecerá o DHCP, clique nele, com o botão direito clique no servirdor, escolhar "DHCP manager", clique com o botão direito direito no ipv4 e adicione um nome para o escopo de ip, e defina a faixa de ip. Como nome usei ruindowsClientes, para faixa usei, 172.16.21.100 - 172.16.21.200, com máscara 255.255.255.0 (/24). A próxima tela irá perguntar se quiser excluir ips do escopo, porém como não precisamos, apenas clique em próximo, deixe o tempo padrão, clique em avançar, será pedido por um gatreway padrão, por agora deixe 172.16.21.1, selecione o ip do servidor de DNS, usaremos o 172.16.21.1 e 8.8.8.8 por agora, clque em avançar até ser perguntado se quer ativar o escopo agora, deixe na opção sim e pronto.

Se quiser ver no servidor se funcionou, basta clicar em "leases" dentro do escopo do ipv4, deve aparecer um ip emprestado para o cliente.


## DNS

Como o servidor DNS, é instalado junto ao active directory, só precisamos adicionar o reverso para aparecer quando usarmos o comando nslookup no cliente, para isso, clique em dns no lado esquerdo, clique com o botão direito do mouse no servidor e clique em DNS manager. Clique no servidor, procure por Reverse lookup Zones, clique com o botão direito, selecione "new zone", dê next até a tela que pede o network ID, coloque os três primeiros números do ip (no meu caso 172.16.21), clique next e finish, clique com o botão direito na nova pasta criada, selecione "new pointer PTR", coloque o ip do servidor, e coloque um nome, no meu caso coloquei ServidorLocalRuindows. e pronto.

## Criando o portforwarding

para o cliente ter acesso a internet, vamos fazer um portfowarding, para isso "add roles and features", selecione o servidor, roles, procure por remote access, selecione role services, ative o routing, selecione o add features, next, next e install.

após a instalação, clique em tools no topo do server manager, selecione routing and remote access, clqie com botrão direito no servidor, selecione configure and enable routing and remote access, clique em next, selecione NAT, next, selecione a interface que será usada para conectar a internet (no meu caso estava com o nome ethernet), finish.

## Servidor web

quando fizemos o portfowarding já instalamos também o IIS que é um servidor web do windows, para acessa-lo, basta escrever o nome do seu computador.noemdominio.

Para fins de teste, eu criei um site, deixei a pasta em downloads mesmo. Para colocar o site no ar:

clique no iis do lado esquerdo, botão direito no servidor: internet information services (IIS) manager, selecione o servidor, clique em sites, do lado direito, clique em add website, coloque um nome do site, no caso usei "teste", selecione o path para a pasta com os arquivos do site, em hostname coloque o nome do site, no caso usei teste também, então o acesso é feito por "teste.lab.local", agora precisamos colocar ele no dns.

clique em dns, botão direito, manager e tal. clique em foward lookup zones, vá até a pasta do seu dominio, clique com o botão direito, selecion "new host A or AAA", coloque um nome (coloquei teste mesmo), e selecione o ip, como é só pra teste, coloquei 172.16.21.1 mesmo e deixe selecionado "create associated pointer (PTR) record", clique em add host e pronto.


## Servidor SMTP

Basta ir em "add roles and features". selecione o servidor e na sessão de "features", escolha "SMTP Server",  instale. Para configurar, clique em tools no canto superior direito do server manager e escolha "internet information services 6.0", selecione  o servidor e clique com botão direito no "smtp virtual server"e  vá em propriedades, na nova tela, clique em "Access" e selecione relay.., cliqe em add, e coloque o localhost (127.0.0.1). Agora vamos instalar o telnet para os testes. clique "add roles and fetures", na sessão de features, procure por "telnet client", adicione e instale.

Para testar local:
abra o powershell, e digite:
(substitua lablocal.lab.local pelo seu dominio)
	
	telnet lablocal.lab.local 25
	EHLO server
	MAIL FROM: <email_enviando@lablocal.lab.local>
	RCPT TO: <email_recipiente@lablocal.lab.local>
	DATA
	subjetc: teste
	[texto de teste]
	.
	
para ver os emails, vá em:
c:\inetpub\mailroot\Drop

no caso os emails serão dropados porque não existem clientes registrados ainda, mas se encontrar mensagens nessa pasta, é poque os emails foram enviados.

## IMAP E POP3

baixe e instale o mailenabler, na tela de nomes preencha os dois campos, coloque uma senha e na parte de dns, coloque 172.16.21.1 e 8.8.8.8

webmail caso queira usar: mewebmail.localhost

Para criar os clientes:
Abra o Mail Enable, nos programas instalados
clique em messaging manager -> post offices, clique com o botão direito e clique em create postoffice, ou clique em create postoffice do lado direito do programa,
colo que o nome do cliente e coloque uma senha, eu criei cliente e cliente2, tudo pronto, agora você pode acessar os emails por newmail.localhost em um browser ou configure um cliente thunderbird no cliente. Para isso adicione o nome do cliente, e o @[dominio] tem que ser o dominio completo, @lablocal.lab.local, para enviar email use @lab.local, por causa do dns e eu to com preguiça de criar um no momento.
 
## FTP

Abra o server manager, "add roles and features", selecione o  servidor, vá até "server roles", procure e expanda o "web server (IIS) e marque o FTP server e instale. Abra o gerenciador do IIS, selecione o servidor local, clique em sites e clique em "ADD FTP site" do lado direito, dê um nome, no caso escolhi "ftpServer" e adicione o caminho para a pasta, coloquei no desktop mesmo, em uma pasta com nome "ftp". Desmarque o "startFtp site autiomatically" e não marque a opção "no SSL". em autenticação marque "basic" e authorization coloque "all users" dê as permilçẽos de leitura e escrita. clique em finish. agora vamos configurar o usuário do cliente.

vá me "tools" no topo direito do management, clique em 'active directory users and computers", clique no servidor, vá em users,clique com o botão direito, add new user. coloque um nome, estou usando usuarioftp, e logon usuarioftp, defina uma senha, estou usando 123456Asd. Desative o "user must change password at next logon" e marque "password never expires", conclua a criação do usuário.

Agora volte ao gerenciador do IIS, selecione o site FTP, clique em "FTP Windows Server - FTP
" (imagem de umas chaves), clique em "add allow rule", "add all users" e marque as opções de leitura e escrita. 

agora vá até a pasta criada para o ftp, clique com botão direito e vá em segurança,clique em editar > adicionar, escreva o nome do usuário e clique em checknames, ele deve ser encontrado, clique em ok e dê as permissões de usuário no quadro em baixo, e clique em apply e ok.

e tudo deve estar pronto. para teste consulte a parte do cliente.


## Sistema de arquivos

vamos usar o sbm nativo do windows a maior parte da configuração nesse caso será no cliente.

no servidor, primeiro vamos criar a pasta para o compartilhamento, criei no desktop mesmo, uma pasta com o nome "compartilhado", clique com o botão direito na pasta, vá em "sharing" "advanced sharing", clique em permissions e adicione os usuário do dominio, aqui vou usar o próprio usuarioftp, clique em apply e ok.

agora vá até o cliente para terminar as configurações.

## Banco de dados

baixe o mysql installer do site oficial, escolha "server only". siga com a instalação até type and networking, aqui certifique a opção "open windows firewall ports for network access", next, adicione uma senha, usando a de sempre 123456Asd.

agora vamos criar o usuário para o cliente, abra o mysql command line client e digite a senha.
escreva os seguintes comandos:

	CREATE USER 'cliente'@'%' IDENTIFIED BY 'senha123';
	GRANT ALL PRIVILEGES ON *.* TO 'cliente'@'%' WITH GRANT OPTION;
	FLUSH PRIVILEGES;
	exit

agora vá para sessão cliente.


# Cliente

Para o cliente estamos usando uma máquina debian 13, com o desktop Xfce.

O ideal seria windows para usar o active directory mas meu note não aguenta o sevidor e um windows rodando simultaneamente.

A instalação foi normal, não foi selecionado nenhuma opção extra.

Antes de ligar a máquina, após a instalação, vá nas configurações da máquina no virtual box, e mude o adaptador de rede para rede interna com o mesmo nome da rede colocada no ruindows, no meu caso, lablocal.


## DHCP 

Para testar, se foi configurado a rede interna no virtualBox, basta digitar 
		
		ip a

E deve aparacer um ip na faixa configurada.

## DNS

Para testar o dns, depois de configurado, basta escrever o comando:

		nslookup [ip ou dominio]

se tiver um retorno é porque tudo deu certo.

## PortFowarding

Para testar basta tentar acessar a interte.

## Servidor web

Basta colocar o dominio que foi registrado no dns, no meu caso, teste.lab.local.

## Servidor email smtp
abra um termimal e digite:

	telnet lablocal.lab.local 25
	EHLO server
	MAIL FROM: <email_enviando@lablocal.lab.local>
	RCPT TO: <email_recipiente@lablocal.lab.local>
	DATA
	subjetc: teste
	[texto de teste]
	.

## Ftp
para testar, primeiro precisamos instalar o ftp no debian

	sudo apt install ftp
	
ao terminar a instalação coloque escreva no terminal:

	ftp 172.16.21.1

quando pedir o nome coloque "lab.local\usuarioftp" OU usuarioftp@lab.local
coloque a senha 123456Asd e se receber 230 user logged in, tudo deve estar pronto.

para enviar um arquivo qualquer para teste:

antes de logar:
	
	touch arquivoteste.txt
	ftp lablocal.lab.local
	[login]
	ls
	put arquivoteste.txt
	ls 
	quit
	
## compartilhamento de arquivo

primeiro precisamos instalar os pacotes necessários:
	
	sudo apt update
	sudo apt install smbclient
	sudo apt install nautilus

agora usando o terminal com o smbclient:

	smbclient -U LAB\usuarioftp //172.16.21.1/compartilhado
	
e para visualizar usando o nautilus usando o seu gerenciador de arquivos:
abra o gerenciador de arquivos e na área de pesquisa escreva:

	smb://172.16.21.1/compartilhado

## banco de dados

primeiro vamos baixar o cliente mysql com:

	sudo apt install default-mysql-client

agora vamos conectar ao servidor com:
	
	mysql -h 172.16.21.1 -u cliente -p --ssl=0
	
se tudo ocorreu bem deve aparecer o login no terminal.

mande alguns comandos para fins de teste:

	SHOW DATABSES;
	CREATE DATABASE demonstracao_redes;
	SHOW DATABASES;
	USE demonstracao_redes;
	exit
	exit
	