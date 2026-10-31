# Painel da Sala

Relógio e previsão do tempo de Campinas (SP) para abrir no navegador da TV.
Dados: Open-Meteo.

## Instalado como app na TV

O painel roda como app Tizen (`tizen-app/`), instalado pelo Mac com o Tizen Studio CLI.
Para atualizar a TV depois de editar `index.html`, com a TV ligada e na mesma rede:

```bash
./atualizar-tv.sh
```

O certificado de autor fica em `~/tizen-studio-data/keystore/author/paineltv.p12`
(dados em `~/tizen-studio-data/painel-tv-cert.txt`). Guarde esse arquivo: atualizações
só são aceitas pela TV se assinadas com o mesmo certificado.
