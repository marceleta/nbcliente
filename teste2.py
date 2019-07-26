import ftplib
import time

def iniciar():
        resultado = False
        try:
            time.sleep(5)
            _ftp = ftplib.FTP('')
            _ftp.connect('marcelohome.hopto.org', 5002)
            _ftp.login(user='marcelo', passwd='cpf04687n')
            _ftp.set_pasv(False)
            destino = '/home/marcelo/backup' + '/' + 'backup_1_quarta_1100.zip'
            _ftp.retrbinary("RETR "+'backup_1_terca_1100.zip', open(destino, 'wb').write)
            resultado = True
        except ftplib.all_errors as msg:
            resultado = False

iniciar()
