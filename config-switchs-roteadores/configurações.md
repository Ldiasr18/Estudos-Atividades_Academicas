# configuração switches.

link cisco recomendações: 

https://www.cisco.com/c/pt_br/solutions/small-business/resource-center/networking/how-to-setup-network-switch.html

## Configuração Básica:
! - exemplo - 
```
> en
# conf t
(config)# hostname S1
(config)# no ip domain-lookup
(config)# enable secret class
(config)# line console 0
(config-line)# password cisco
(config-line)# login
(config-line)# line vty 0 4
(config-line)# password cisco
(config-line)# login
(config)# service password-encryption
(config)# banner motd $ Apenas usuários autorizados! $
! Apenas se quiser desativar as interfaces
!(config-if-range)# interface range f0/1-4, f0/7-24, g0/1-2  
!(config-if-range)# shutdown
!(config-if-range)# exit
exit
# copy running-config startup-config

```

## Ativar ipv6

```
(config)# ipv6 unicast-routing

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

Colocar um gateway padrão

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
transport input telnet
password cisco
login
end

```

Configuração do ssh:

```

S1# show ip ssh                                     !verificar suporte
S1(config)# ip domain-name cisco.com
S1(config)# crypto key generate rsa                 !1024 bits quando perguntado
S1(config)# username admin secret ccna              !Para usuários autenticados localmente

!- configurar as linhas vty

S1(config)# line vty 0 15                           !ou a quantia de linhas vty que o dispositivo tiver
S1(config-line)# transport input ssh
S1(config-line)# login local                        
S1(config-line)# exit
S1(config)# ip ssh version 2

```
    
Adicionar descrição em interfaces 
```
description [coisas aqui escritas]
```

Interface de loopback
```
(config)# interface loopback [numero]
(config-if)#ip [ip] [máscara]
```


