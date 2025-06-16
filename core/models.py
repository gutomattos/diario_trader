from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Estrategia(models.Model):
    nome = models.CharField(max_length=20, unique=True)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['ordem', 'nome']

    def __str__(self):
        return self.nome

class Trade(models.Model):
    LADOS = [
        ("COMPRA", "Compra"),
        ("VENDA", "Venda"),
    ]
    STATUS_CHOICES = [
        ("ABERTO", "Aberto"),
        ("FINALIZADO", "Finalizado"),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)
    ativo = models.CharField(max_length=20)
    quant = models.IntegerField()
    estrategia = models.ForeignKey(Estrategia, on_delete=models.PROTECT)
    lado = models.CharField(max_length=10, choices=LADOS)
    preco_entrada = models.DecimalField(max_digits=12, decimal_places=2)
    preco_saida = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    descricao = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="FINALIZADO")

    def lucro_reais(self):
        if self.preco_entrada is None or self.preco_saida is None:
            return None
        if self.ativo == "WINFUT":
            fator = Decimal('0.2')
        elif self.ativo == "WDOFUT":
            fator = Decimal('10')
        else:
            fator = Decimal('1')
        if self.lado == "VENDA":
            return (self.preco_entrada - self.preco_saida) * self.quant * fator
        else:
            return (self.preco_saida - self.preco_entrada) * self.quant * fator

    def lucro_percentual(self):
        if self.preco_entrada is None or self.preco_saida is None:
            return None
        if self.lado == "VENDA":
            return (1 - self.preco_saida / self.preco_entrada) * 100
        else:
            return (self.preco_saida / self.preco_entrada - 1) * 100

    def pts(self):
        if self.ativo == "WINFUT":
            fator = Decimal('0.2')
        elif self.ativo == "WDOFUT":
            fator = Decimal('10')
        else:
            return None
        if self.lado == "VENDA":
            return (self.preco_entrada - self.preco_saida)
        else:
            return (self.preco_saida - self.preco_entrada) 

class IBOV(models.Model):
    mes_ano = models.CharField(max_length=7)  # Ex: 07/2024
    rentabilidade = models.DecimalField(max_digits=6, decimal_places=2)

class CDI(models.Model):
    mes_ano = models.CharField(max_length=7)  # Ex: 07/2024
    rentabilidade = models.DecimalField(max_digits=6, decimal_places=2)

class Aporte(models.Model):
    data = models.DateField()
    valor = models.DecimalField(max_digits=12, decimal_places=2)

class Retirada(models.Model):
    data = models.DateField()
    valor = models.DecimalField(max_digits=12, decimal_places=2)