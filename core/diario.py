from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

# Create your models here.

class Trade(models.Model):
    ESTRATEGIAS = [
        ("61.8", "61.8"),
        ("Trap", "Trap"),
        ("PingPong", "PingPong"),
        ("S3", "S3"),
        ("Max10", "Max10"),
        ("Rompimento", "Rompimento"),
        ("Win15", "Win15"),
        ("Win30", "Win30"),
        ("Win60", "Win60"),
    ]
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
    data_fim = models.DateField()
    ativo = models.CharField(max_length=20)
    quant = models.IntegerField()
    estrategia = models.CharField(max_length=20, choices=ESTRATEGIAS)
    lado = models.CharField(max_length=10, choices=LADOS)
    preco_entrada = models.DecimalField(max_digits=12, decimal_places=2)
    preco_saida = models.DecimalField(max_digits=12, decimal_places=2)
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
        if self.preco_entrada is None or self.preco_saida is None:
            return None
        if self.lado == "VENDA":
            return self.preco_entrada - self.preco_saida
        else:
            return self.preco_saida - self.preco_entrada

class IBOV(models.Model):
    mes_ano = models.CharField(max_length=7)  # Ex: 07/2024
    rentabilidade = models.DecimalField(max_digits=6, decimal_places=2)

class CDI(models.Model):
    mes_ano = models.CharField(max_length=7)  # Ex: 07/2024
    rentabilidade = models.DecimalField(max_digits=6, decimal_places=2)
