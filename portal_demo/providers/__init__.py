# -*- coding: utf-8 -*-
from .base import BaseNaoConfirmada, Provider, Resultado
from .diretorio import DiretorioProvider
from .erp import ErpProvider
from .microsoft365 import MicrosoftProvider

__all__ = [
    "BaseNaoConfirmada",
    "Provider",
    "Resultado",
    "DiretorioProvider",
    "ErpProvider",
    "MicrosoftProvider",
    "montar",
]


def montar(estado, simulacoes):
    """Os providers disponíveis, na ordem em que a orquestração os percorre."""
    return {
        provider.chave: provider
        for provider in (
            MicrosoftProvider(estado, simulacoes),
            DiretorioProvider(estado, simulacoes),
            ErpProvider(estado, simulacoes),
        )
    }
