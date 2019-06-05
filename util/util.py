import datetime
import logging

logging.basicConfig(filename='nbcliente.log', filenome='a', format='%(asctime)s - %(levelname)s - %(message)s',datefmt='%d/%m/%Y %I:%M')

class DataConv:

    dict_dia_semana = [
        'segunda',
        'terca',
        'quarta',
        'quinta',
        'sexta',
        'sabado',
        'domingo'
    ]


    @staticmethod
    def data_hoje():
        '''
        Retorna a data no momento do chamado
        '''
        data_hoje = datetime.datetime.now()
        data = datetime.date(day=data_hoje.day, month=data_hoje.month, year=data_hoje.year)

        return data

    @staticmethod
    def hora_agora():
        '''
        Retorna a hora no momento da chamada
        '''
        data_hoje = datetime.datetime.now()
        hora = datetime.time(hour=data_hoje.hour, minute=data_hoje.minute)

        return hora

    @staticmethod
    def str_to_time(str_time):
        '''
        formato da hora: HH:MM
        '''
        d_hora = datetime.datetime.strptime(str_time, '%H:%M')
        hora = datetime.time(hour=d_hora.hour, minute=d_hora.minute)

        return hora

    @staticmethod
    def hoje_dia_semana(self):
        dia = datetime.datetime.today().weekday()
        return dict_dia_semana[dia]

class Log:
    
    @staticmethod
    def debug(mensagem):
        logging.debug(mensagem)

    @staticmethod
    def info(mensagem):
        logging.info(mensagem)

    @staticmethod
    def warning(mensagem):
        logging.warning(mensagem)

    @staticmethod
    def error(mensagem):
        logging.error(mensagem)