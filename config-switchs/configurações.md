# configuração switches.

link cisco recomendações: 

https://www.cisco.com/c/pt_br/solutions/small-business/resource-center/networking/how-to-setup-network-switch.html

## Configuração Básica:
! - exemplo - 
```
en
conf t
hostname S1
no ip domain-lookup
enable secret class
line console 0
password cisco
login
line vty 0 4
password cisco
login
service password-encryption
banner motd $ Apenas usuários autorizados! $
interface range f0/1-4, f0/7-24, g0/1-2
shutdown
exit
exit
copy running-config startup-config

```

## Configuração de vlan

Criação e ativação da vlan

```

# configure terminal
# vlan 99 ! cria vlan 99
# exit
# interface vlan99 ! entra na interface vlan para config

# ip address [ip] [mascara] 
# ipv6 address [ip/mascara]
# ipv6 address fe80::2 link-local
# no shutdown
# exit

```

Vincular portas a vlan

```

interface range [f0/1 – 24],[g0/1 - 2] ! selecionar em ranges ou interface
switchport access vlan [n°] ! vincular as interfaces selecionadas anteriormente a vlan
exit


```

Colocar um gateway padrão para acesso remoto

```

ip default-gateway [ip]

```

Criar senha para a porta de console

```

line con 0
logging synchronous
password cisco
login
exit

```

Configurar o VTY para permitir acesso telnet

```

line vty 0 15
password cisco
login
end

```
