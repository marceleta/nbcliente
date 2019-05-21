from configuracao.config import Configuracao
from comunicacao.servidor import SelectorServer
from db.modelos import Persistir

Persistir.criar_db()
config = Configuracao()
config_servidor = config.get_servidor()
servidor = SelectorServer(config_servidor.host, config_servidor.porta, config_servidor.qtd_conexoes)
servidor.serve_forever()
