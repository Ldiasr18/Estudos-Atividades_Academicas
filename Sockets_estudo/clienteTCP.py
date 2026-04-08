import socket

#Declaração de "globais".

#Definindo tamanho da mensagem inicial.
HEADER = 64
#porta que vamos nos conectar
PORT = 5050
#Formato que vamos usar pra codificação e decodificação de mensagens (mesmo do servidor)
FORMAT = "utf-8"
#No caso do cliente, esse valor deveria mudar para o do servidor, como estamos fazendo tudo local, o endereço de loopback será usado (127.0.0.1)
SERVER = socket.gethostbyname(socket.gethostname())
#Definição de mensagem quando cliente desconecta
DISCONNECT_MESSAGE = "!DISCONNECT"
#aqui onde vamos conectar
ADDR = (SERVER, PORT)

#criação de socket cliente
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#aqui vamos conectar
cliente.connect(ADDR)

#Aqui vamos definir como mandar mensagem
def send(msg):
    mensagem = msg.encode(FORMAT)
    #aqui trabalhamos no que definimos no servidor, onde vamos enviar o tamanho da mensagem antes de enviar a mensagem.
    msg_length = len(mensagem)
    #Aqui vamos enviar o tamanho
    send_length = str(msg_length).encode(FORMAT)
    #Transformando pro tamanho correto
    send_length += b" " * (HEADER - len(send_length))
    #Enviando as duas mensagem, a primeira com o tamanho, e a segunda com a mensagem em si
    cliente.send(send_length)
    cliente.send(mensagem)
 
mensagem = " "
while mensagem != "!Desconectar":
    mensagem = input("Digite a mensagem para o chat: ")
    send(mensagem)

send(DISCONNECT_MESSAGE)