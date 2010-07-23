#!/bin/bash

cenarios=`./cenarios_teste.py | sed -n 's/Cen.*veis: *//p'`

for i in $cenarios ; do
	echo "== Cenario Teste $i =="
	./cenarios_teste.py $i | tee cenario_teste_$i.txt
done
