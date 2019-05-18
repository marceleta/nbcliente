from configuracao.config import Configuracao
from servico.servico import Download_ftp, Download_thread

config = Configuracao()
servidor = config.get_servidores()[0]
path_destino = config.get_backup_dir(servidor.nome)
print('path_destino: {}'.format(path_destino))
d = {
    'conteudo':{
            'id':1,
            'arquivo':'backup_1_quinta_1415.zip',
            'path':'/home/marcelo/backup/backup1',
            'hash_verificacao':'arquivo.hash_verificacao',
            'data_criacao':'arquivo.data_criacao',
            'tamanho':100,
            'backup':'backup_1',
            'is_enviado':'True'
            }
    }
down_ftp = Download_ftp(d['conteudo'], path_destino, servidor.obj_ftp)
down_thread = Download_thread(down_ftp, 'backup_1')
down_thread.start()
