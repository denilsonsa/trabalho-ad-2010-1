#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:ts=4 sw=4 et

import heapq
import sys


class HeapDeEventos(list):
    """Implementação de uma fila com prioridades."""

    def adicionar(self, tempo, evento):
        heapq.heappush(self, ())

    def remover(self):
        """Retorna uma tupla (tempo, evento)"""
        return heapq.heappop(self)


class Host(object):
    """ """

    def __init__(self):
        pass


def main():
    print "Hello!"


if __name__ == "__main__":
    main()
