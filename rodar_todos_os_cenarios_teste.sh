#!/bin/bash

cenarios=`./rodar_cenario_teste.py | sed -n 's/Cen.*veis: *//p'`

for i in $cenarios ; do
	echo "== Cenario Teste $i =="
	./rodar_cenario_teste.py $i | tee cenario_teste_$i.txt
done
