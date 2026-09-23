# Configuração Switches

## Sequencia de inicialização

5 etapas de inicialização:

1. programa POST - verifica subsistema CPU. Testa, CPU, DRAM e sistema de arquivo flash.
2. Carrega software carregador de inicialização (Boot loader).
3. O carregador inicializa os registros da CPU.
4. O carregador inicializa o sistema de arquivos da memoria flash.
5. O carregador carrega uma imagem do software de sistema operacional do IOS padrão na memória e passa o controle para o IOS.

O SO inicializa as interfaces usando o arquivo de configuração no startup-config (config.txt).

O comando:

```

# show boot

```

Mostra como o arquivo de inicialização está definido.

Para definir a variável de ambiente BOOT, usa-se o comando:

```

(config)# boot system [path para variável] 

```

### Exemplo de configuração do SVI do Switch 

Configuração da interface de gerenciamento

```
S1# conf t
S1(config)# interface vlan 99
s1(config-if)# ip address 172.17.99.11 255.255.255.0
S1(config-if)# ipv6 address 2001:db8:acad:99::1/64
s1(config-if)# no shutdown
S1(config-if)# end 
S1# copy running-config startup-config

```

Configuração gateway padrão:

```
S1# configure terminal
S1(config)# ip default-gateway 172.17.99.1
S1(config-if)# end
S1# copy running-config startup-config

```

Verificar configuração:

```
S1# show ip interface brief

```

### Configurar as portas de switch camada fisica

Modo duplex e Velocidade

obs.: para dispositivos conhecidos como servidores, workstation ou dispositivos de rede, a prática recomendada é definir manualmente as configurações de velocidade e duplex.

Exemplo comandos para configurar velocidade (speed) e duplex:

```

S1# configure terminal
S1(config)# interface FastEthernet 0/1
S1(config-if)# duplex full
S1(config-if)# speed 100
S1(config-if)# end
S1# copy running-config startup-config

```

### MDIX

Cobos diferentes -straight-through e crossover) eram necessários para conectar dispositivos. 

Quando usar auto-MDIX em uma interface, a velocidade e o duplex devem ser configuradas para auto para que opere corretamente.

Comando para ativação:

```

S1(config-if)# mdix auto

```

Comando para verificar a configuração auto-MDIX em uma interface especifica:

```

S1# show controllers ethernet-controller fa0/1 phy | include MDIX

```

### Configuração SSH

Para habilitar o ssh em um dispositivo, primeiro deve-se conferir se a versão do IOS e os recursos que possui. 

Verifique com o comando 

```

S1# show version

```

Para o caso do IOS da cisco, um arquivo que tenha a combinação "k9" suporta recursos criptográficos. exemplo de saída: (coloquei o k9 entre aspas simples para ficar mais fácil a visualização)

    Cisco IOS Software, C2960 Software (C2960-LANBASE'K9'-M), Version 15.0(2)SE7, RELEASE SOFTWARE (fc1)
    

## Loop back

Interface lógica interna do roteador. Não se conecta a nenhum outro dispositivo nem é atribuida a uma interface.

Multiplas interfaces de loopback podem ser atribuidas num mesmo roteador.
