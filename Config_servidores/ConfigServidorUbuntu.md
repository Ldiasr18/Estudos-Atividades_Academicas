# Observações iniciais

Todo o projeto foi desenvolvido em um computador com Debian 13 (trixie), caso utilize outro sistema operacional, é possível que seja necessário adaptar os comando ou configurações utilizadas.

# Passo a Passo

## Instalar o virtual box

Baixe o arquivo de instalação, no meu caso é um arquivo .deb, para instalar o pacote, vá até o local do arquivo e abra um terminal na pasta (utilize `cd` ou botão direito do mouse -> abrir no terminal), e digite o seguinte comando: 

	sudo apt install ./nome-do-arquivo.deb
	
ou

	sudo dpkg -i ./nome-do-arquivo.deb

## Instalação do servidor

Não foi feito nenhuma modificação durante a instalação, todas as opções escolhidas foram as padrões (exceto teclado, que foi alterado para português Brasil). Nenhum snap foi selecionado para instalação.

# Configuração VirtualBox

O primeiro passo é configurar as redes no VirtualBox, particularmente eu gosto de acessar via terminal usando ssh, é mais fácil de organizar e gerenciar a máquina virtual. Para isso selecione a máquina servidor clique em configurações (no topo do virtual box), em seguida vá até redes o adaptador 1 deve estar selecionado como NAT, mantenha essa configuração e clique em redirecionamento de portas. Adicione uma nova regra de redirecionamento, um dos botões do lado direito. Na porta de hospedeiro coloque 2222 e na porta de convidado coloque 22.
Ainda nas configurações de rede.  
Habilite o adaptador 2 e ligue-o a rede interna, coloque um nome, no meu caso escolhi redeTeste.  
Entre nas configurações da máquina cliente vá até rede e coloque rede interna no adaptador 1, COLOQUE O MESMO nome escolhido para a máquina servidor (redeTeste se estiver usando o mesmo que eu).

## Configurações servidor

Inicie a máquina servidor, e instale o servidor ssh, caso não tenha, com 

	sudo apt install openssh-server

Para estabelecer a comunicação, em sua máquina host abra o terminal e digite:  
 
	ssh usuárioDoServidor@localhost -p 2222

(subistitua usuárioDoServidor pelo nome do usuário do servidor). 

Ligue a máquina servidor. O primeiro passo é identificar o nome da interface, no meu caso era enp0s3 e enp0s8. A enp0s3 estava a interface NAT, enp0s8 era da rede interna, usarei essa nomeclatura nos arquivos, substitua pelo nome da interface correspondente na sua maquina.  
Para isso utilize o seguinte comando:

	ip link show

deve ter uma saída semelhante a essa: 

>1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00  
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP mode DEFAULT group default qlen 1000
    link/ether 08:00:27:d8:e1:e6 brd ff:ff:ff:ff:ff:ff  
3: enp0s8: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN mode DEFAULT group default qlen 1000
    link/ether 08:00:27:3e:96:77 brd ff:ff:ff:ff:ff:ff

Agora vamos inicializar a interface de rede interna, para isso temos que modificar o arquivo de interfaces localizado em:  
`/etc/netplan/50-cloud-init.yaml`

primeiro faça um backup com: 

	sudo cp /etc/netplan/50-cloud-init.yaml /etc/netplan/50-cloud-init.yaml.bak

use o comando:

	sudo nano /etc/netplan/50-cloud-init.yaml

O arquivo deve ter uma configuração semelhante a essa: 

```
network:
  version: 2
  ethernets:
    enp0s3: #Aqui será o nome da interface NAT da sua máquina
      dhcp4: true
```
	
vamos adicionar a seguinte configuração:

``` 
enp0s8: #Substitua pela interface rede interna da sua máquina. 
  addresses: [172.16.21.1/24] #ip/mascara de rede da máquina, já que não pegaremos por dhcp
  dhcp4: false #desligando o dhcp dessa interface
  optional: true #essa configuração é usada para evitar tempo extra de boot, pode demorar alguns segundos/minutos a mais caso não tenha.
```

no fim o arquivo deve ficar assim: 

``` 
network:
  version: 2
  ethernets:
    enp0s3: 
      dhcp4: true
    enp0s8:
      addresses: [172.16.21.1/24]  
      dhcp4: alse 
      optional: true 
```

Para aplicar as configurações:

	sudo netplan apply

# Serviço de DHCP
### Configuração do servidor

Agora vamos iniciar a configuração do serviço DHCP:  
Primeiro atualize o repositório com: 

	sudo apt update 

Agora faça download do KEA com:

	sudo apt install kea
	
(Configure uma senha ou use uma aleatória para que o daemon inicialize)

Agora vamos criar a configuração do do serviço, para isso, primeiro faça um backup do arquivo de configuração: (Aqui eu prefiro renomear o arquivo do que fazer uma cópia, caso queira fazer uma cópia, use `cp` no lugar de `mv`)

	sudo mv /etc/kea/kea-dhcp4.conf /etc/kea/kea-dhcp4.conf.bak 
	
Criando um arquivo de configuração: 

	sudo nano /etc/kea/kea-dhcp4.conf

Coloque as seguintes configurações no arquivo: 

```
{
    "Dhcp4": {
        "interfaces-config": {
            "interfaces": ["enp0s8"] #Aqui troque para sua interface de rede interna
        },
        "control-socket": {
            "socket-type": "unix",
            "socket-name": "/run/kea/kea4-ctrl-socket"
        },
        "lease-database": {
            "type": "memfile",
            "lfc-interval": 3600
        },
        "valid-lifetime": 600,
        "max-valid-lifetime": 7200,
        "subnet4": [{
            "id": 1,
            "subnet": "172.16.21.0/24",
            "pools": [{
                "pool": "172.16.21.100 - 172.16.21.199"
            }],
            "option-data": [{
                    "name": "routers",
                    "data": "172.16.21.1"
                },
                {
                    "name": "domain-name-servers",
                    "data": "8.8.8.8, 8.8.4.4"
                },
                {
                    "name": "domain-name",
                    "data": "lab.local"
                }
            ]
        }]
    }
}

```

Salve o arquivo e verifique a sintaxe com: 
	
	sudo kea-dhcp4 -t /etc/kea/kea-dhcp4.conf

Reinicie o serviço com:
	
	sudo systemctl restart kea-dhcp4-server

Verifique o status do servidor com: 
	
	sudo systemctl status kea-dhcp4-server
	
Se tudo foi configurado corretamente, o servidor estará ativo.

### Configuração do cliente

Agora para testar, iremos configurar um cliente que receberá o ip do serviço previamente configurado.

O primeiro passo é configurar a interface, encontre o nome de sua interface com o comando:

	ip link show

De forma semelhante de quando configuramos o servidor, porém aqui provavelmente só terá duas interfaces.
 
Em seguida abra o arquivo de configuração com: 

	sudo nano /etc/network/interfaces

O arquivo deve ter algo semelhante a isso:

```
auto lo  
iface lo inet loopback
```

Adicione as seguintes linhas:  
(substitua o enp0s3 pelo nome de sua interface)

```
auto enp0s3 
iface enp0s3 inet dhcp 
```

reinicie a rede do cliente com:
	
	sudo systemctl restart networking	

Verifique se recebeu um ip com: 
	
	ip address show
	
Se tudo ocorreu bem, na interface enp0s3 ou equivalente deve ter um ip dentro da faixa 172.16.21.100 - 172.16.21.199

Teste a conexão com:
	
	ping 172.16.21.1

Se tiver resposta é porque está funcionando.

### Verificação no servidor

Use ping para verificar se existe conexão com o cliente:
	
	ping ipDoCliente

para verificar por leases (concessão de IPs) use:

	sudo cat /var/lib/kea/kea-leases4.csv
	
Para monitorar os logs:

	sudo journalctl -u kea-dhcp4-server -f

## Adicionando conectividade com a internet

Para fornecer acesso à máquina cliente, vamos usar o IP fowarding, ou encaminhamento de portas, transferindo os pacotes de uma interface não conectada a interna a outra com conexão a internet.

Para isso, primeiro temos que habilitar o ip forwarding no sistema, utilize o seguinte comando para abrir o arquivo de configuração: 

		sudo nano /etc/sysctl.conf 

E procure pela linha: `net.ipv4.ip_forward=1`, provavelmente estará como comentário, basta remover o `#` no inicio, caso não exista a linha, adicione-a.

Para reiniciar o file de configuração no kernel, digite o seguinte comando:

	sudo sysctl -p
	
Se tudo ocorreu conforme o esperado, o seguinte comando retornará 1:
	
	cat /proc/sys/net/ipv4/ip_forward
	
Agora vamos aplicar as regras ipTable para NAT:
Primeiro vamos limpar as regras já existentes com os seguintes comandos: 

	sudo iptables -t nat -F
	sudo iptables -F

#### ATENÇÃO

Isso remove todas as configurações, não é recomendado usar fora de um ambiente controlado.

`-t nat`seleciona tabela NAT (usado para redirecionamento de portas, mascara, etc).
`-F ` é de flush, ou seja limpar, esvaziar.

Agora vamos configurar o NAT, utilize o seguinte comando:
	
	sudo iptables -t nat -A POSTROUTING -o enp0s3 -j MASQUERADE

Não esqueça de substituir a interface pela correspondente sua máquina.

Explicações:

- t nat: Trabalha na tabela NAT
- A POSTROUTING: Adiciona à cadeia POSTROUTING (pacotes saindo)
- o enp0s3: Na interface enp0s3 (que tem internet)
- j MASQUERADE: Substitui o IP de origem pelo IP do servidor


Para permitir o forwarding entre as interfaces: 
Tráfego da rede interna para a internet:
	
	sudo iptables -A FORWARD -i enp0s8 -o enp0s3 -j ACCEPT

Tráfego de volta (respostas):
	
	sudo iptables -A FORWARD -i enp0s3 -o enp0s8 -m state --state RELATED,ESTABLISHED -j ACCEPT
	
	
Explicação dos comandos: 

`sudo iptables -A FORWARD -i enp0s8 -o enp0s3 -j ACCEPT`

- -A FORWARD: Adiciona uma regra à cadeia FORWARD (que controla o tráfego que passa pelo computador, mas não é destinado a ele)
- -i enp0s8: Interface de entrada - tráfego vindo da rede interna
- -o enp0s3: Interface de saída - tráfego saindo para a internet
- -j ACCEPT: Ação - permitir/aceitar o tráfego

`sudo iptables -A FORWARD -i enp0s3 -o enp0s8 -m state --state RELATED,ESTABLISHED -j ACCEPT`

- -A FORWARD: Novamente, na cadeia de encaminhamento
- -i enp0s3: Interface de entrada - tráfego vindo da internet
- -o enp0s8: Interface de saída - tráfego saindo para a rede interna
- -m state: Módulo que verifica o estado da conexão
- --state RELATED,ESTABLISHED: Apenas tráfego que é:
- + ESTABLISHED: Parte de uma conexão já estabelecida
- + RELATED: Relacionado a uma conexão existente (ex: FTP data connection)
- -j ACCEPT: Permitir

Para instalar o pacote de persistência:

	sudo apt install iptables-persistent -y

Salvar as regras atuais:

	sudo netfilter-persistent save
	
Verificar se o serviço está ativo:

	sudo systemctl enable netfilter-persistent

Para testar, ligue ou reinicie a máquina cliente, ou renove o DHCP, e teste a conexão, com a internet.
Se tudo foi configurado corretamente o cliente terá agora acesso.  

# Serviço DNS

Primeiro vamos atualizar os repositórios e instalar o BIND9

	sudo apt update
	sudo apt install bind9 bind9utils bind9-doc -y
	
Para verificar se o serviço está ativo: 

	sudo systemctl status bind9
	
Se estiver ativo, tudo está funcionando, caso esteja inativo, utilize o comando abaixo para iniciar:

	sudo systemctl start bind9
	
Agora vamos configurar o arquivo de opções globais, mas primeiro vamos fazer um backup do arquivo original:

	sudo cp /etc/bind/named.conf.options /etc/bind/named.conf.options.bak	
	
Agora vamos editar o arquivo de configuração:

	sudo nano /etc/bind/named.conf.options
	
No arquivo de configurações:
	
```
options {
    // Diretório onde ficam arquivos de zona e cache
    directory "/var/cache/bind";
    
    // Escutar conexões na interface da rede interna
    listen-on { 172.16.21.1; };      // IP do servidor na rede lab
    listen-on-v6 { none; };           // Desabilita IPv6 (não estamos usando nesse lab)
    
    // Quem pode fazer consultas DNS
    allow-query { 172.16.21.0/24; localhost; };
    // ^ Apenas clientes da rede 172.16.21.x e localhost
    
    // Servidores DNS para encaminhar consultas externas
    forwarders {
        8.8.8.8;      // Google DNS
        8.8.4.4;      // Google DNS secundário
    };
    
    // Permite consultas recursivas (necessário para forward)
    recursion yes;
    
    // Validação DNSSEC (segurança)
    dnssec-validation auto;
    
    // Não envia versão do BIND por segurança
    version "DNS Server - Lab Local";
    
    // Logs para monitoramento
    querylog yes;
};

```	
	
Explicações: 

- directory: Onde o BIND armazena arquivos temporários

- listen-on: Em qual IP o DNS escuta consultas

- allow-query: Quem tem permissão para usar este DNS

- forwarders: Para onde enviar consultas que não são da nossa rede

- recursion yes: Permite resolver nomes de internet para os clientes	
	
### Configuração zonas

Agora vamos configurar as zonas locais:
Entre nas configurações usando: 

`sudo nano /etc/bind/named.conf.local`
	
```
//LISTA DE NOMES → IPs (Zona Direta)
// Quando procurar por nomes .lab.local, usar este arquivo: 

zone "lab.local" {
    type master;
    file "/etc/bind/db.lab.local";
};

//LISTA DE IPs → NOMES (Zona Reversa)  
//Quando perguntar por IPs 172.16.21.x, usar este arquivo
zone "21.16.172.in-addr.arpa" {
    type master;
    file "/etc/bind/db.172.16.21";
};
```

Agora vamos configurar as zonas:
Direta:

`sudo nano /etc/bind/db.lab.local`

Já estou criando também os ips e nomes que usaremos no futuro (web, email, db, arquivos...), apesar disso, ainda vamos voltar e editar esse arquivo no futuro.  

```
; TTL (Time To Live) - quanto tempo guardar em cache
$TTL 604800

; CABEÇALHO DA ZONA - copiar e aumentar o número quando mudar
@ IN SOA lab.local. admin.lab.local. (
    2025102701    ; Número de série: AAMMDDVV (ano,mês,dia,versão mude para sua data e qual versão de modificação)
    604800        ; Refresh: atualizar a cada 7 dias
    86400         ; Retry: tentar novamente em 1 dia
    2419200       ; Expire: expirar em 28 dias
    604800 )      ; TTL negativo: cache de erros por 7 dias

; SERVIDOR DE NOMES AUTORITATIVO
@ IN NS ns1.lab.local.

; =============================================
; REGISTROS A (NOME -> IP) - OS MAIS IMPORTANTES!
; =============================================
; --- já organizando tudo que será feito e seus endereços --- 
; --- INFRAESTRUTURA ---
ns1     IN A 172.16.21.1    ; Servidor DNS
server  IN A 172.16.21.1    ; Servidor principal
router  IN A 172.16.21.1    ; Gateway padrão

; --- SERVIÇOS WEB ---
www     IN A 172.16.21.1    ; Site principal
web     IN A 172.16.21.1    ; Site alternativo/admin

; --- EMAIL ---
mail    IN A 172.16.21.1    ; Servidor de email
webmail IN A 172.16.21.1    ; Interface web do email

; --- BANCO DE DADOS ---
db      IN A 172.16.21.1    ; Banco de dados
mysql   IN A 172.16.21.1    ; MySQL
pgsql   IN A 172.16.21.1    ; PostgreSQL

; --- ARQUIVOS ---
ftp     IN A 172.16.21.1    ; Servidor FTP
nas     IN A 172.16.21.1    ; Sistema de arquivos
files   IN A 172.16.21.1    ; Arquivos compartilhados

; --- APELIDOS (CNAME) ---
dhcp    IN CNAME server     ; dhcp.lab.local → server.lab.local
dns     IN CNAME ns1        ; dns.lab.local → ns1.lab.local

;DOMÍNIO PADRÃO TAMBÉM APONTA PARA O SERVIDOR
@       IN A 172.16.21.1    ; lab.local → 172.16.21.1
```


Agora vamos criar a zona reversa: 

	sudo nano /etc/bind/db.172.16.21
	
Use o ip que está seu servidor/serviço.

``` 
; TTL padrão
$TTL 604800

;MESMO CABEÇALHO DA OUTRA ZONA
@ IN SOA lab.local. admin.lab.local. (
    2025102701    ; Número de série
    604800        ; Refresh
    86400         ; Retry  
    2419200       ; Expire
    604800 )      ; TTL negativo

;MESMO SERVIDOR DE NOMES
@ IN NS ns1.lab.local.

; ============================
; REGISTROS PTR (IP → NOME) 
; ============================

; ÚLTIMO OCTETO DO IP . IN PTR nome.completo.
; Basicamente todos serão 1 IN PTR. 
1 IN PTR ns1.lab.local.
1 IN PTR server.lab.local.
1 IN PTR router.lab.local.
1 IN PTR www.lab.local.
1 IN PTR web.lab.local.
1 IN PTR mail.lab.local.
1 IN PTR webmail.lab.local.
1 IN PTR db.lab.local.
1 IN PTR mysql.lab.local.
1 IN PTR pgsql.lab.local.
1 IN PTR ftp.lab.local.
1 IN PTR nas.lab.local.
1 IN PTR files.lab.local.
```

1 IN PTR ->  basicamente significa que o ip terminados em 1 apontam para serviços que estão hospedados no servidor.

Agora precisamos dar permissão aos arquivos:

	sudo chown bind:bind /etc/bind/db.*
	sudo chmod 644 /etc/bind/db.*
	
chmod 664 = rw - rw - r -> curiosidade

Agora vamos verificar os arquivos para garantir que não há erros de sintaxe: 

```
# Verificar sintaxe da configuração principal
sudo named-checkconf

# Verificar zona direta
sudo named-checkzone lab.local /etc/bind/db.lab.local

# Verificar zona reversa
sudo named-checkzone 21.16.172.in-addr.arpa /etc/bind/db.172.16.21
```

Se nenhum problema for encontrado, reiniciar os serviços:

	sudo systemctl restart bind9

Verificar se está ativo: 

	sudo systemctl status bind9


Agora vamos configurar o KEA/DHCP para usar o dns local:

	sudo nano /etc/kea/kea-dhcp4.conf


Localize e altere a seção: 

```
{
  "name": "domain-name-servers",
  "data": "172.16.21.1"  // Mudando para IP do nosso DNS
},
{
  "name": "domain-search", 
  "data": "lab.local"    // Domínio padrão para buscas
}

```

reinicie o kea:
	
	sudo systemctl restart kea-dhcp4-server


### Teste no cliente

Inicie/reinicie a máquina cliente ou renove a configuração DHCP.

use o comando `cat /etc/resolv.conf` para ver se o nome do servidor dns está correto.

faça alguns testes: 
```
# Testes nomes locais
nslookup server.lab.local
nslookup www.lab.local

# Teste resolução reversa
nslookup 172.16.21.1

# Teste nome da internet
nslookup google.com

```

Para ver em tempo real os pedidos do cliente, utilize o seguinte comando no servidor:  

`sudo tcpdump -i enp0s8 -n port 53` 


# Servidor WEB com apache2

Baixe o apache com:

	sudo apt install apache2

Por padrão tudo já deve estar configurado, para acessar a página do cliente entre o IP do servidor ou `www.lab.local` no browser (Navegador). 

Você deve ver a página padrão do apache.

# Banco de dados com MYSQL

Update do repositório e instalação:
	
	sudo apt update
	
	sudo apt install mysql-server -y

verificar se instalou:

	sudo systemctl status mysql

Para testar se está funcionando:

	sudo service mysql status

ou 

	sudo ss -tap | grep mysql

Com o comando a cima você deve ver uma saida como: 

```
LISTEN 0      70         127.0.0.1:33060       0.0.0.0:*     users:(("mysqld",pid=7429,fd=21))                     
LISTEN 0      151        127.0.0.1:mysql       0.0.0.0:*     users:(("mysqld",pid=7429,fd=26))
```
 
Se o servidor não iniciou corretamente tente os seguinte comando: 

	sudo service mysql restart

Para se conectar ao mysql:

	sudo mysql -u root -p
	
Digite a senha de root.  

Agora vamos criar um database para testar:
(lembre que # no inicio indica comentário, eu prefiro camelCase, mas use o nome e formato que quiser no lugar do *labDatabase*)

```sql
#Criar o data base
CREATE DATABASE labDatabase;

#mostrar banco de dados:
SHOW DATABASES;

#sair
EXIT;
```

Como já adicionamos no DNS nas sessão anterior não precisamos atualizar o db dele.

Agora vamos colocar o ip correto para acesso remoto, abra o arquivo com: 

	sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

Procure pela linha:  
(muito provavel que o ip 192.168.0.5 seja outro em sua máquina, mas o importante é encontrar a linha bind-address)

`bind-address            = 192.168.0.5`

substitua o ip pelo ip do servidor, se estiver seguindo esse tutorial o ip será:

`172.16.21.1`

Agora vamos criar um usuário para teste:

```sql
#Não esqueça de substituir o ip pelo que está sendo usado caso não esteja usando o mesmo que eu

#Criando usuário usuarioLab, ip de acesso com % no final para que qualquer octeto funcional dentro da rede funcione, e senha 123 

#atenção pra letra maiúscula na senha `C`e o número 1.

CREATE USER  'cliente'@'172.16.21.%' IDENTIFIED BY 'Cl1ente@';

#Dar permissões de acesso:
GRANT ALL PRIVILEGES ON *.* TO 'cliente'@'172.16.21.%';

#Aplicar mudanças:

FLUSH PRIVILEGES;

#sair
EXIT
```

Por algum motivo tive que reiniciar o MYSQL antes de testar no cliente no meu teste em outro computador, em teoria não seria necessário, mas, caso precise:

	sudo service mysql restart

### Teste no Cliente

Inicie a máquina cliente, instale o MYSQL client, até o momento não existe o repositório do mysql por padrão no debian, então é necessário baixar do seguinte site:   

[MySQL APT Repository](https://dev.mysql.com/downloads/repo/apt/)

 Instale  o pacote abrindo a pasta de download no terminal ou caminhando usando `cd` e usando o comando:
 	
 	sudo dpkg -i nomedoarquivo.deb
 	
Após a instalação atualize o repositório e instale o mysql client com:

```
#Atulizar o repositório
sudo apt update

#instalar o mysql-client
sudo apt install mysql-client -y
```

Para fazer login no servidor mysql:

	mysql -h db.lab.local -u cliente -p

Coloque sua senha, se tudo foi configurado corretamente a conexão sera estabelecida e você vera: `mysql>` nop terminal

# Servidor de e-mail

Instalar o postfix para SMTP e Dovecot para IMAP/POP3 

	sudo apt install postfix dovecot-imapd dovecot-pop3d mailutils -y
	
Durante a instalação selecione `Internet Site`. Como nome do mail eu utilizei `lab.local`

#### Configurar o Postfix

Agora vamos configurar o postfix(SMTP):
Utilize:

	sudo nano /etc/postfix/main.cf 

Substitua a configuração por:  
```
# Configurações básicas
myhostname = mail.lab.local
mydomain = lab.local
myorigin = $mydomain

# Onde escutar
inet_interfaces = all
inet_protocols = all

# Redes permitidas
mynetworks = 127.0.0.0/8 172.16.21.0/24

# Domínios que aceitamos
mydestination = $myhostname, localhost.$mydomain, localhost, $mydomain

# Configurações de entrega
home_mailbox = Maildir/
mailbox_size_limit = 0

# Segurança - não é o suficiente mas melhor que nada
smtpd_recipient_restrictions = permit_mynetworks, reject_unauth_destination

```

Reinicie o Postfix

```
sudo systemctl restart postfix
sudo systemctl enable postfix
```

#### Configurar o Dovecot:

Entre nas configurações: 

	sudo nano /etc/dovecot/dovecot.conf
	
Adicione ou modifique as linhas:

```
# Protocolos
protocols = imap pop3

# Onde escutar
listen = *

# Desabilitar SSL para lab (simplificação)
ssl = no
disable_plaintext_auth = no

# Autenticação
auth_mechanisms = plain login

# Onde estão os emails
mail_location = maildir:~/Maildir
```

Configurar autenticação:
Abra o arquivo de configuração:

	sudo nano /etc/dovecot/conf.d/10-auth.conf

verifique/Adicione ou modifique:

```
disable_plaintext_auth = no
auth_mechanisms = plain login
```

Configure o email:

	sudo nano /etc/dovecot/conf.d/10-mail.conf
	
Modifique o mail location para::  

`mail_location = maildir:~/Maildir`

Reinicie o Dovecot:

```
sudo systemctl restart dovecot
sudo systemctl enable dovecot
```

Adicione um usuário para teste:

	sudo adduser cliente

Digite uma senha.

Adicione os registros DNS:

	sudo nano /etc/bind/db.lab.local 
	
Adicione as seguintes linhas:

```
smtp    IN A 172.16.21.1  
imap    IN A 172.16.21.1
pop3    IN A 172.16.21.1
```

Adicione as zona reversa:

```
1 IN PTR smtp.lab.local.
1 IN PTR imap.lab.local.
1 IN PTR pop3.lab.local.
```

Aumente o número de série:
	
	sudo rndc reload

Teste no servidor se tudo está correto:

```
#Verificar serviços
sudo systemctl status postfix dovecot

#Testar envio local
echo "Primeiro email de teste" | mail -s "Teste Inicial" cliente@lab.local

#Verificar se email chegou
sudo ls -la /home/cliente/Maildir/new/
```

Teste a autenticação Dovecot:

	sudo doveadm auth test cliente

### Teste no cliente

baixe o thunderBird

	sudo apt install thunderBird
	
Configure com o nome do usuário que criamos para teste
```
Nome: Cliente
Endereço de email: cliente@lab.local
Senha: 123
```

Se precisar a configuração manual é: 

```
IMAP:
- Servidor: imap.lab.local (ou 172.16.21.1 se DNS não funcionar)
- Porta: 143
- SSL: Nenhum
- Autenticação: 123

SMTP:
- Servidor: smtp.lab.local (ou 172.16.21.1 se DNS não funcionar)  
- Porta: 25
- SSL: Nenhum
- Autenticação: 123
```

Teste se está funcionando enviando um email para o endereço do cliente (de você como cliente para você mesmo)

# Sistema de arquivos com SAMBA2

Para instalar o samba:

```
sudo apt update
sudo apt install samba -y
```

Para verificar se foi instalado corretamente use:
	
	sudo systemctl status smbd

Configuração:

Primeiro vamos fazer um backup do arquivo original:

	sudo cp /etc/samba/smb.conf /etc/samba/smb.conf.bak
	
Agora abra o arquivo de configuração:

	sudo nano /etc/samba/smb.conf

Adicione essa configuração: (vou colocar as configurações com explicações de cada parte porque fiquei extremamente confuso durante a configuração, deixo aqui como uma ajuda)
```
[global]

    # Nome do grupo de trabalho (igual ao Windows)
    workgroup = WORKGROUP
    
    # Descrição do servidor que aparece na rede
    server string = Servidor de Arquivos Lab Local
    
    # Nome NetBIOS do servidor (como aparece no Windows)
    netbios name = NAS-LAB
    

    # Tipo de segurança: *user* = autenticação por usuário/senha
    security = user
    
    # Usuários inválidos são tratados como convidados
    map to guest = bad user
    
    # Não funciona como proxy DNS
    dns proxy = no
    
    # Samba só escuta neste IP específico
    interfaces = 172.16.21.1
    
    # Só usa as interfaces listadas acima
    bind interfaces only = yes
    
    # Arquivo de log por cliente (%m = nome do cliente)
    log file = /var/log/samba/log.%m
    
    # Tamanho máximo do arquivo de log em KB
    max log size = 1000
    
    # Tipo de logging (arquivo)
    logging = file


[public]
    # Descrição que aparece quando listam os compartilhamentos
    comment = Compartilhamento Publico - Acesso Livre
    
    # Caminho absoluto no servidor onde ficam os arquivos
    path = /srv/samba/public
    
    #VISIBILIDADE E ACESSO
    
    # Aparece na lista de compartilhamentos
    browsable = yes
    
    # Permite escrita
    writable = yes
    
    # Permite acesso sem senha
    guest ok = yes
    
    # Somente leitura ou não
    read only = no
    
    # PERMISSÕES DE ARQUIVOS
    
    # Permissões para novos arquivos 
    create mask = 0777
    
    # Permissões para novas pastas (todos podem ler+escrever+executar)
    directory mask = 0777
    
    
    # CONFIGURAÇÃO DE USUÁRIO CONVIDADO
    
    # Só permite acesso como convidado 
    guest only = yes
    
    # Qual usuário do sistema representa o convidado
    guest account = nobody
    
    #COMPATIBILIDADE COM WINDOWS
    
	#ESSA PARTE NÃO É OBRIGATÓRIA
    # Não armazena atributos DOS (oculto, sistema, etc)
    store dos attributes = no
    
    # Mapeamento de atributos entre Windows e Linux
    map archive = no
    map hidden = no
    map read only = no
    map system = no

#AQUI VOLTA A SER OBRIGATÓRIO
[homes]
    # Descrição do compartilhamento
    comment = Diretorio Home do Usuario
    
    # Caminho dinâmico: %U será substituído pelo nome do usuário
    path = /home/%U
    
    # SEGURANÇA - ACESSO RESTRITO
    
    # Não aparece na lista de compartilhamentos (segurança)
    browsable = no
    
    # Usuário pode escrever na sua própria pasta
    writable = yes
    
    # Apenas o próprio usuário pode acessar (%S = nome do compartilhamento)
    valid users = %S
    
    # Não permite acesso sem senha
    guest ok = no
    
    # PERMISSÕES RESTRITAS
    
    # Apenas o dono tem acesso aos arquivos (ler+escrever+executar)
    create mask = 0700
    
    # Apenas o dono tem acesso às pastas (ler+escrever+executar)
    directory mask = 0700
    
    # Força estas permissões
    force create mode = 0700
    force directory mode = 0700

[backup]
    # Descrição
    comment = Area de Backup Segura
    
    # Caminho no servidor
    path = /srv/samba/backup
    
    # Aparece na lista? (sim)
    browsable = yes
    
    # Permite escrita? (sim)
    writable = yes
    
    # ACESSO RESTRITO A USUÁRIOS ESPECÍFICOS
    
    # Não permite acesso sem senha
    guest ok = no
    
    # PERMISSÕES PARA GRUPO
    
    # Permissões para novos arquivos (dono+grupo podem ler+escrever)
    create mask = 0660
    
    # Permissões para novas pastas (dono+grupo podem ler+escrever+acessar)
    directory mask = 0770

```
 


#### Criando os diretórios e permissões: 

```
# Criar diretório
sudo mkdir -p /srv/samba/public

# Dar permissões
sudo chown nobody:nogroup /srv/samba/public
sudo chmod 0777 /srv/samba/public

# Criar arquivo de teste
echo "Bem-vindo ao compartilhamento Samba do lab.local" | sudo tee /srv/samba/public/LEIAME.txt

```

Criar um usuário SAMBA:
```
# Adicionar seu usuário ao Samba

sudo smbpasswd -a $USER

# Criar usuário específico para Samba

sudo adduser --system --no-create-home samba-user
sudo smbpasswd -a samba-user
```

Aplicar as configurações:

```
sudo systemctl restart smbd
sudo systemctl enable smbd

#Verificar status:
sudo systemctl status smbd
```


Atualizar o DNS:

	sudo nano /etc/bind/db.lab.local
	
adicione as seguinte linhas: (algumas já devem estar presentes, acredito que nas e files)
```
nas    IN A 172.16.21.1
files  IN A 172.16.21.1
samba  IN A 172.16.21.1
```

Atualize a zona reversa:

	sudo nano /etc/bind/db.172.16.21

Adicione: 

```
1 IN PTR nas.lab.local.
1 IN PTR files.lab.local.
1 IN PTR samba.lab.local.
```

Atualize o número de série:

	sudo rndc reload

### Teste no cliente:

Primeiro vamos instalar o Samba client:

```
sudo apt update
sudo apt install smbclient cifs-utils -y
```

Para listar compartilhamentos disponíveis: 

	smbclient -L nas.lab.local -U%
	
conectar ao compartilhamento público:

	smbclient //nas.lab.local/public -N

Dentro do smbcliente testar:

```
- ls (listar arquivos)
- get LEIAME.txt (baixar arquivo)
- put [arquivo] (enviar arquivo)
- quit (sair)
```


Agora vamos montar o compartilhamento de arquivos:

```
# Criar ponto de montagem
sudo mkdir -p /mnt/nas-public

# Montar compartilhamento público
sudo mount -t cifs //nas.lab.local/public /mnt/nas-public -o username=guest,password=

# Para verificar
ls -la /mnt/nas-public/
```

Para acesso via interface gráfica, caso não esteja instalado, pode se utilizar o nautilus, instale com o seguinte comando: 

	sudo apt install nautilus 
	
Agora para acessar usando a interface gráfica coloque o seguinte endereço na barra de pesquisa do gerenciador de arquivos: 

	smb://files.lab.local/public

#### Testar conexão: 

No cliente:

	echo "Arquivo teste" > testeCliente.txt
	
	smbclient //nas.lab.local/public -N -c "put testeCliente.txt"

No servidor:

	ls -la /srv/samba/public/

O arquivo enviado pelo cliente `testeCliente.txt` deve estar na pasta.


Para acessar a home do usuário que criamos (o cliente): 

	smbclient //nas.lab.local/homes -U $USER

# Servidor FTP

Primeiro vamos instalar o vsftpd

```
sudo apt update
sudo apt install vsftpd -y
```

Fazer um backup do arquivo de configuração: 

	sudo cp /etc/vsftpd.conf /etc/vsftpd.conf.backup

Verificar a instalação: 

	sudo systemctl status vsftpd
	
Agora vamos configurar o ftp:  
primeiro abra o arquivo de configuração com: 

	sudo nano /etc/vsftpd.conf

Substitua pela seguinte configuração: 

```
# ================
# CONEXÕES BÁSICAS
# ================

# Escutar em IPv4
listen=YES

# Não escutar em IPv6 (simplificação)
listen_ipv6=NO

# Endereço específico para escutar (opcional, remove para escutar em todos)
# listen_address=172.16.21.1

# Porta do FTP (padrão 21)
listen_port=21

# ==============
# ACESSO ANÔNIMO
# ==============

# Permitir acesso anônimo? (não = mais seguro)
anonymous_enable=NO

# =========================
# ACESSO DE USUÁRIOS LOCAIS
# =========================

# Permitir usuários locais do sistema
local_enable=YES

# Permitir que usuários locais façam upload
write_enable=YES

# Máscara de permissões para novos arquivos (022 = dono lê/escreve, outros só leem)
local_umask=022

# =======================
# DIRETÓRIOS E LIMITAÇÕES
# =======================

# Diretório inicial do usuário fica "preso" (não pode acessar diretórios superiores)
chroot_local_user=YES

# Permitir que usuários escrevem mesmo com chroot ativo
allow_writeable_chroot=YES

# Diretório padrão para usuários anônimos (se habilitado)
# anon_root=/var/ftp

# =========================
# TRANSFERÊNCIA DE ARQUIVOS
# =========================

# Permitir upload de arquivos
write_enable=YES

# Permissão para criar novos diretórios
anon_mkdir_write_enable=YES

# Permissão para upload de arquivos anônimos (se habilitado)
# anon_upload_enable=YES

# =========
# SEGURANÇA
# =========

# Usar SSL/TLS? (não para lab local)
ssl_enable=NO

# Log de transferências
xferlog_enable=YES

# Arquivo de log
xferlog_file=/var/log/vsftpd.log

# Formato do log
xferlog_std_format=YES

# =====================
# CONFIGURAÇÕES DE REDE
# =====================

# Endereço passivo para transferências de dados
pasv_enable=YES

# Endereço para modo passivo (IP do servidor)
pasv_address=172.16.21.1

# Range de portas para modo passivo
pasv_min_port=30000
pasv_max_port=31000

# ===================
# MENSAGENS E BANNERS
# ===================

# Banner de boas-vindas
ftpd_banner=Bem-vindo ao servidor FTP do Lab Local

# =================
# USUÁRIOS E GRUPOS
# =================

# Impedir usuários listados em /etc/vsftpd.userlist de acessarem
userlist_enable=YES

# Negar acesso aos usuários da lista (em vez de permitir)
userlist_deny=YES

# Arquivo com lista de usuários banidos
userlist_file=/etc/vsftpd.userlist

# ==========
# LIMITAÇÕES
# ==========

# Tempo máximo de sessão ociosa (5 minutos)
idle_session_timeout=300

# Tempo máximo para transferência de dados (5 minutos)
data_connection_timeout=300

# Número máximo de clientes (50 conexões)
max_clients=50

# Número máximo de conexões por IP (5 conexões)
max_per_ip=5
```

Criar uma lista de usuários:

	sudo touch /etc/vsftpd.userlist

Agora vamos recarregar e habilitar o vsftpd:

```
# Recarregar configuração
sudo systemctl restart vsftpd

# Habilitar inicialização automática
sudo systemctl enable vsftpd

# Verificar status
sudo systemctl status vsftpd
```

Não é necessário adicionar ao dns, pois adicionamos na configuração inicial

Agora vamos adicionar o cliente ao fpt:

	#Garantir que o cliente as permissões corretas
	sudo chmod 755 /home/cliente
	
	#Criar um arquivo teste no cliente, para isso vamos logar como cliente
	su - cliente
	#Digite a senha
	echo "teste" > texte.txt
	
	#Voltar para o servidor:
	su - servidor
	#digite a senha

Caso necessário recarregue as configurações (pra mim foi necessário)

```
sudo systemctl restart vsftpd
sudo systemctl status vsftpd
```

#### Teste no cliente

Primeiro vamos instalar o ftp 

```
sudo apt update
sudo apt install ftp -y
```

Agora vamos testar o DNS e a conexão:  
Primeira vamos criar um arquivo que será enviado
	
	echo "teste de envio" > testeEnvio.txt


```
# Testar DNS
nslookup ftp.lab.local

# Conectar via FTP (com usuário ftpuser)
ftp ftp.lab.local

# Comandos para testar dentro do FTP:
ftp> pwd
# Deve mostrar: /home/cliente


# Mostrar os arquivos, incluindo teste.txt
ftp> ls -la


# Baixar o arquivo para o cliente
ftp> get teste.txt

# Fazer upload para o servidor
ftp> put testeEnvio.txt

#Criar uma pasta
ftp> mkdir nova_pasta

#Mover para pasta
ftp> cd nova_pasta

ftp> put testeEnvio.txt

ftp> quit

```

No servidor verifique se os arquivos foram enviados e pasta criada:

```
# Verificar se o arquivo chegou no diretório do cliente
sudo ls -la /home/cliente/

# Verificar permissões
sudo ls -la /home/cliente/arquivo_local.txt

```


Para acessar por interface gráfica use: 

	ftp://ftp.lab.local
	
Na barra de endereços de seu gerenciador de arquivos.

# Erros, correções e dicas
## Cliente

Como estou no  debian, o usuário não está no grupo de sudoers por padrão, para adicionar faça login como sudo usando: 

	su -

Depois adicione o usuário como sudoer:

	usermod -aG sudo nomeDoUsuário

Reinicie a máquina.



## Virtual Box

- É possível que tenha um erro para executar a maquina virtual no virtualbox no meu caso, aconteceu o seguinte erro: 
`VirtualBox Error VERR_VMX_IN_VMX_ROOT_MODE`
	+ Para corrigir segui o tutorial do seguinte site: [How to Fix Virtual Machines Not Starting in Ubuntu 25.04](https://randomblog.hu/how-to-fix-virtual-machines-not-starting-in-ubuntu-25-04-virtualbox-error-verr_vmx_in_vmx_root_mode/

## Configurações pra mim (deletar depois)

Adicionando um página web: 
acessar arquivos no cliente e que baixei no git:
	
	smb://files.lab.local/public

acessar o arquivo no servidor:

	/srv/samba/public/

acesso ao apache no servidor: 

	/var/www/html/pag

