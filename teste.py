from configuracao.config import Configuracao
from comunicacao.nbservidor import ConexaoThread
import json
import time

config = Configuracao()
servidor = config.get_servidores()[0]
lista_bkps = {'comando':'list_bkps_prontos'}

thread1 = ConexaoThread(servidor, lista_bkps)
thread1.start()

iniciar_ftp = {'comando':'iniciar_ftp', 'backup':{'path':'/home/marcelo/backup/backup1', 'arquivo':'backup_1_terca_0745.zip', 'nome':'backup_1'}}
thread2 = ConexaoThread(servidor, iniciar_ftp)
thread2.start()

loop = True

while loop:
    if  not thread1.is_alive():
        print('if 1')
        conteudo = thread1.get_conteudo()
        print('conteudo: {}'.format(conteudo))

    if not thread2.is_alive():
        loop = False
        print('if 2')
        conteudo = thread2.get_conteudo()
        print('conteudo: {}'.format(conteudo))

    time.sleep(10)
