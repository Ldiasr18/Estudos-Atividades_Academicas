import socket
import threading

#Declaração de "globais".
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
#Endereço para bind, recebe uma tupla, servidor e porta.
ADDR = (SERVER, PORT)
#Definindo tamanho da mensagem inicial.
HEADER = 64
#Formato que vamos usar pra codificação e decodificação de mensagens
FORMAT = "utf-8"
#Definição de mensagem quando cliente desconecta
DISCONNECT_MESSAGE = "!DISCONNECT"

#Socket Servidor
servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Aqui faz o binding entre socket e endereço, basicamente coloca os dois pra funcionar juntos.
servidor.bind(ADDR)

def handle_cliente(conn, addr):
    print(f"[NOVA CONEXÃO] {addr} conectado" )

    connected = True
    while connected:
        #Aqui definimos quantos bytes serão recebidos do cliente ,também é bloqueante (por isso estamos usando threads, por enquanto)
        msg_length = conn.recv(HEADER).decode(FORMAT)
    #Quando o cliente conecta o servidor recebe uma mensagem sem nenhum conteudo indicando a coneção, para evitar o erro quando tentamos converter para int
    #vamos criar um if, que verifica se existe conteúdo na mensagem
        if msg_length:
            #Aqui definimos a primeira mensagem que vai "trazer" o tamanho real da mensagem
            msg_length = int(msg_length)
            #Aqui onde recebemos a mensagem propriamente
            msg = conn.recv(msg_length).decode(FORMAT)
            #Aqui verificamos a mensagem de desconectar do cliente
            if msg == DISCONNECT_MESSAGE:
                connected = False
            #print mensagem que o cliente envia
            print(f"[{addr}] {msg}")
            #Aqui enviar do servidor pro cliente:
            conn.send("Msg received".encode(FORMAT))

    conn.close()


def inicio():
    servidor.listen()
    print(f"[OUVINDO] o Servidor está ouvindo no ip {SERVER}")

    while True:
        #código bloqueante, retorna o socket que vai representar a conexão com o cliente e o endeço dop cliente.
        conn, addr = servidor.accept()
        #criando uma thread nova para manter a conexão.
        thread = threading.Thread(target=handle_cliente, args=(conn, addr))
        thread.start()
        #Só mostrando quantas conexões estão ativas no servidor
        print(f"[Conexões ativas] {threading.active_count() - 1}")

print("[Iniciando] servidor está iniciando... ")
inicio()