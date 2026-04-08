#!/bin/bash


echo "Digite uma opção: (1) Criar switch (2) Criar Hosts (3) Deletar hosts"
read -rp "Escolha: " escolha


liga_host()
{
  ip link add s1-eth"$1" type veth peer name h"$1"-eth0
  ip link set s1-eth"$1" master sw1
  ip link set s1-eth"$1" up
  
  ip link set h"$1"-eth0 netns h"$1"
  ip netns exec h"$1" ip link set dev h"$1"-eth0 address "$2"
  ip netns exec h"$1" ip addr add "$3" dev h"$1"-eth0
  ip netns exec h"$1" ip link set h"$1"-eth0 up
  ip netns exec h"$1" ip link set lo up
}

#cria switch 
cria_switch()
{

echo "Criando switch virtual.."
ip link add name sw1 type bridge

echo "ligando o switch.."
ip link set sw1 up

}

cria_hosts()
{

  read -rn "Digite quantos hosts deseja criar: " 

  for ((i = 1; i <= hosts; i++))
  do
    ip netns add h"$i"
    #cria mac
    if [ $i -lt 10 ]
    then
      mac="02:aa:aa:aa:aa:0$i"
    else
      mac="02:aa:aa:aa:aa:$i"
    fi

    ip="10.10.0.$i/24"
    liga_host "$i" "$mac" "$ip"
  done

}

deleta_hosts()
{

  ip link delete sw1 2>/dev/null || true
  for ((i=1; i<= hosts; i++))
  do
    ip netns delete h"$i"
  done

}

case "$escolha" in
  1) echo "Criando switch .."
    cria_switch
    echo "switch criado com sucesso"
    ;;
  
  2)
    cria_hosts
    echo "Hosts criados com sucesso"
  ;;
  
  3) 
    echo "Deletando hosts .."
    deleta_hosts
    echo "Hosts deletados com sucesso"
  ;; 

  4) 
    echo testes
    testa_rede
  ;;

esac
