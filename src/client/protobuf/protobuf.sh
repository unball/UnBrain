# Usar protoc versão 3.20.1 é obrigatório para compilar os protobufs

# eu baixei essa versão do github, deszipei e botei o caminho
# completo aqui. Não é gambiarra se funciona!!

#/home/nana/Downloads/protobuf-3.20.1/bin/protoc --python_out=./ *.proto
protoc --python_out=./ *.proto
