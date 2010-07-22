#!/bin/bash

cenarios=`./rodar_cenario.py | sed -n 's/Cen.*veis: *//p'`

for i in $cenarios ; do
	echo "== Cenario $i =="
	./rodar_cenario.py $i | tee cenario_$i.txt
done
