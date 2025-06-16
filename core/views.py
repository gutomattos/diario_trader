from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Trade, IBOV, CDI, Estrategia, Aporte, Retirada
import json
from collections import defaultdict
from django.db.models import Sum
from django.utils.dateparse import parse_date
from decimal import Decimal

# Create your views here.

@login_required
def home(request):
    return render(request, 'core/home.html')

@login_required
def trade_list(request):
    ordem = request.GET.get('ordem', 'desc')
    if ordem == 'asc':
        trades = Trade.objects.filter(usuario=request.user).order_by('data_fim')
    else:
        trades = Trade.objects.filter(usuario=request.user).order_by('-data_fim')
    return render(request, 'core/trade_list.html', {'trades': trades, 'ordem': ordem})

@login_required
def trade_create(request):
    estrategias = Estrategia.objects.all()
    if request.method == 'POST':
        data_inicio = parse_date(request.POST.get('data_inicio'))
        data_fim_raw = request.POST.get('data_fim')
        data_fim = parse_date(data_fim_raw) if data_fim_raw else None
        ativo = request.POST.get('ativo')
        quant = int(request.POST.get('quant'))
        estrategia_nome = request.POST.get('estrategia')
        estrategia = Estrategia.objects.get(nome=estrategia_nome)
        lado = request.POST.get('lado')
        preco_entrada = request.POST.get('preco_entrada')
        preco_saida_raw = request.POST.get('preco_saida')
        preco_saida = preco_saida_raw if preco_saida_raw else None
        descricao = request.POST.get('descricao')
        if data_fim and preco_saida:
            status = 'FINALIZADO'
        else:
            status = 'ABERTO'
        Trade.objects.create(
            usuario=request.user,
            data_inicio=data_inicio,
            data_fim=data_fim,
            ativo=ativo,
            quant=quant,
            estrategia=estrategia,
            lado=lado,
            preco_entrada=preco_entrada,
            preco_saida=preco_saida,
            descricao=descricao,
            status=status
        )
        return redirect('trade_list')
    return render(request, 'core/trade_form.html', {'estrategias': estrategias})

@login_required
def ibov_list(request):
    ibovs = IBOV.objects.all()
    return render(request, 'core/ibov_list.html', {'ibovs': ibovs})

@login_required
def ibov_create(request):
    if request.method == 'POST':
        mes_ano = request.POST.get('mes_ano')
        rentabilidade = request.POST.get('rentabilidade')
        IBOV.objects.create(mes_ano=mes_ano, rentabilidade=rentabilidade)
        return redirect('ibov_list')
    return render(request, 'core/ibov_form.html')

@login_required
def ibov_edit(request, ibov_id):
    ibov = get_object_or_404(IBOV, id=ibov_id)
    if request.method == 'POST':
        ibov.mes_ano = request.POST.get('mes_ano')
        ibov.rentabilidade = request.POST.get('rentabilidade')
        ibov.save()
        return redirect('ibov_list')
    return render(request, 'core/ibov_form.html', {'ibov': ibov, 'editando': True})

@login_required
def ibov_delete(request, ibov_id):
    ibov = get_object_or_404(IBOV, id=ibov_id)
    ibov.delete()
    return redirect('ibov_list')

@login_required
def cdi_list(request):
    cdis = CDI.objects.all()
    return render(request, 'core/cdi_list.html', {'cdis': cdis})

@login_required
def cdi_create(request):
    if request.method == 'POST':
        mes_ano = request.POST.get('mes_ano')
        rentabilidade = request.POST.get('rentabilidade')
        CDI.objects.create(mes_ano=mes_ano, rentabilidade=rentabilidade)
        return redirect('cdi_list')
    return render(request, 'core/cdi_form.html')

@login_required
def cdi_edit(request, cdi_id):
    cdi = get_object_or_404(CDI, id=cdi_id)
    if request.method == 'POST':
        cdi.mes_ano = request.POST.get('mes_ano')
        cdi.rentabilidade = request.POST.get('rentabilidade')
        cdi.save()
        return redirect('cdi_list')
    return render(request, 'core/cdi_form.html', {'cdi': cdi, 'editando': True})

@login_required
def cdi_delete(request, cdi_id):
    cdi = get_object_or_404(CDI, id=cdi_id)
    cdi.delete()
    return redirect('cdi_list')

@login_required
def dashboard(request):
    trades = Trade.objects.filter(usuario=request.user, status='FINALIZADO')
    # Estratégias x Lucro
    estrategia_lucro = defaultdict(float)
    for t in trades:
        estrategia_lucro[str(t.estrategia)] += float(t.lucro_reais())
    # Usar todas as estratégias cadastradas
    todas_estrategias = [e.nome for e in Estrategia.objects.all()]
    estrategia_labels = todas_estrategias
    estrategia_data = [estrategia_lucro.get(e, 0) for e in estrategia_labels]

    # Ativo x Lucro
    ativo_lucro = defaultdict(float)
    for t in trades:
        ativo_lucro[t.ativo] += float(t.lucro_reais())
    ativo_labels = list(ativo_lucro.keys())
    ativo_data = list(ativo_lucro.values())

    # Resultado por mês (usando data_fim)
    mes_lucro = defaultdict(float)
    for t in trades:
        mes = t.data_fim.strftime('%m/%Y')
        mes_lucro[mes] += float(t.lucro_reais())
    mes_labels = sorted(mes_lucro.keys(), key=lambda x: (x[3:], x[:2]))
    mes_data = [mes_lucro[mes] for mes in mes_labels]

    # Resultado acumulado
    acumulado_labels = mes_labels.copy()
    acumulado_data = []
    total = 0
    for mes in acumulado_labels:
        total += mes_lucro[mes]
        acumulado_data.append(total)

    # IBOV e CDI acumulados
    ibovs = {i.mes_ano: float(i.rentabilidade) for i in IBOV.objects.all()}
    cdis = {c.mes_ano: float(c.rentabilidade) for c in CDI.objects.all()}
    ibov_data = []
    cdi_data = []
    ibov_total = 0
    cdi_total = 0
    for mes in acumulado_labels:
        ibov_total += ibovs.get(mes, 0)
        cdi_total += cdis.get(mes, 0)
        ibov_data.append(ibov_total)
        cdi_data.append(cdi_total)

    # Percentual de acerto total
    total_trades = trades.count()
    trades_lucro = [t for t in trades if t.lucro_reais() > 0]
    percentual_acerto = (len(trades_lucro) / total_trades * 100) if total_trades else 0

    # Percentual de acerto por estratégia
    estrategia_acerto = {}
    for estrategia in estrategia_labels:
        trades_estrat = [t for t in trades if str(t.estrategia) == estrategia]
        if trades_estrat:
            acertos = [t for t in trades_estrat if t.lucro_reais() > 0]
            estrategia_acerto[estrategia] = len(acertos) / len(trades_estrat) * 100
        else:
            estrategia_acerto[estrategia] = 0

    # Payoff total
    lucros = [float(t.lucro_reais()) for t in trades if t.lucro_reais() > 0]
    prejuizos = [abs(float(t.lucro_reais())) for t in trades if t.lucro_reais() < 0]
    payoff_total = (sum(lucros) / len(lucros)) / (sum(prejuizos) / len(prejuizos)) if lucros and prejuizos else 0

    # Payoff por estratégia
    estrategia_payoff = {}
    for estrategia in estrategia_labels:
        t_estrat = [t for t in trades if str(t.estrategia) == estrategia]
        lucros_estrat = [float(t.lucro_reais()) for t in t_estrat if t.lucro_reais() > 0]
        prejuizos_estrat = [abs(float(t.lucro_reais())) for t in t_estrat if t.lucro_reais() < 0]
        if lucros_estrat and prejuizos_estrat:
            estrategia_payoff[estrategia] = (sum(lucros_estrat) / len(lucros_estrat)) / (sum(prejuizos_estrat) / len(prejuizos_estrat))
        else:
            estrategia_payoff[estrategia] = 0

    # Patrimônio inicial (campo editável)
    patrimonio_inicial = request.session.get('patrimonio_inicial', 0)
    if request.method == 'POST' and 'patrimonio_inicial' in request.POST:
        try:
            patrimonio_inicial = float(request.POST.get('patrimonio_inicial'))
            request.session['patrimonio_inicial'] = patrimonio_inicial
        except:
            pass

    # Somar aportes e subtrair retiradas
    total_aportes = Aporte.objects.aggregate(total=Sum('valor'))['total'] or Decimal('0')
    total_retiradas = Retirada.objects.aggregate(total=Sum('valor'))['total'] or Decimal('0')

    # Garantir que patrimonio_inicial seja Decimal
    try:
        patrimonio_inicial = Decimal(str(patrimonio_inicial))
    except:
        patrimonio_inicial = Decimal('0')

    # Patrimônio atual
    lucro_total = sum([(t.lucro_reais() or Decimal('0')) for t in trades])
    patrimonio_atual = patrimonio_inicial + total_aportes - total_retiradas + lucro_total

    # Trades não finalizados
    trades_nao_finalizados = Trade.objects.filter(usuario=request.user).exclude(status='FINALIZADO')

    # Lucro acumulado em R$ (apenas trades)
    lucro_acumulado_rs = sum([(t.lucro_reais() or Decimal('0')) for t in trades])
    # Lucro acumulado em % (apenas trades)
    lucro_acumulado_percent = ((lucro_acumulado_rs / patrimonio_inicial) * 100) if patrimonio_inicial else 0
    # Max Drawdown
    patrimonio_evolucao = [patrimonio_inicial]
    for v in acumulado_data:
        patrimonio_evolucao.append(patrimonio_inicial + Decimal(str(v)))
    max_drawdown = 0
    if patrimonio_evolucao:
        topo = patrimonio_evolucao[0]
        for valor in patrimonio_evolucao:
            if valor > topo:
                topo = valor
            drawdown = (topo - valor) / topo if topo else 0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
    max_drawdown_percent = max_drawdown * 100

    # Resultado acumulado percentual IBOV e CDI (usando o último valor acumulado)
    resultado_ibov_percent = ibov_data[-1] if ibov_data else 0
    resultado_cdi_percent = cdi_data[-1] if cdi_data else 0

    # Pontos mês a mês para WINFUT e WDOFUT
    pontos_mes_win = defaultdict(float)
    pontos_mes_wdo = defaultdict(float)
    for t in trades:
        if t.ativo == 'WINFUT' and t.data_fim:
            mes = t.data_fim.strftime('%m/%Y')
            pts = t.pts()
            if pts is not None:
                pontos_mes_win[mes] += float(pts)
        elif t.ativo == 'WDOFUT' and t.data_fim:
            mes = t.data_fim.strftime('%m/%Y')
            pts = t.pts()
            if pts is not None:
                pontos_mes_wdo[mes] += float(pts)
    # Garantir que todos os meses presentes em qualquer ativo estejam nos labels
    meses_pontos = sorted(set(list(pontos_mes_win.keys()) + list(pontos_mes_wdo.keys())), key=lambda x: (x[3:], x[:2]))
    pontos_win_data = [pontos_mes_win.get(m, 0) for m in meses_pontos]
    pontos_wdo_data = [pontos_mes_wdo.get(m, 0) for m in meses_pontos]

    grafico_cores_barras = []
    for i, t in enumerate(trades.order_by('data_inicio')):
        if t.ativo in ['WINFUT', 'WDOFUT']:
            valor = float(t.pts() or 0)
        else:
            valor = float(t.lucro_reais() or 0)
        if valor < 0:
            grafico_cores_barras.append('rgba(220, 53, 69, 0.7)')  # vermelho
        else:
            grafico_cores_barras.append('rgba(54, 162, 235, 0.5)')  # azul

    context = {
        'estrategia_labels': json.dumps(estrategia_labels),
        'estrategia_data': json.dumps(estrategia_data),
        'ativo_labels': json.dumps(ativo_labels),
        'ativo_data': json.dumps(ativo_data),
        'mes_labels': json.dumps(mes_labels),
        'mes_data': json.dumps(mes_data),
        'acumulado_labels': json.dumps(acumulado_labels),
        'acumulado_data': json.dumps(acumulado_data),
        'ibov_data': json.dumps(ibov_data),
        'cdi_data': json.dumps(cdi_data),
        'percentual_acerto': percentual_acerto,
        'estrategia_acerto': estrategia_acerto,
        'payoff_total': payoff_total,
        'estrategia_payoff': estrategia_payoff,
        'patrimonio_inicial': patrimonio_inicial,
        'patrimonio_atual': patrimonio_atual,
        'trades_nao_finalizados': trades_nao_finalizados,
        'lucro_acumulado_rs': lucro_acumulado_rs,
        'lucro_acumulado_percent': lucro_acumulado_percent,
        'max_drawdown_percent': max_drawdown_percent,
        'resultado_ibov_percent': resultado_ibov_percent,
        'resultado_cdi_percent': resultado_cdi_percent,
        'pontos_meses_labels': json.dumps(meses_pontos),
        'pontos_win_data': json.dumps(pontos_win_data),
        'pontos_wdo_data': json.dumps(pontos_wdo_data),
        'grafico_cores_barras': grafico_cores_barras,
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def trade_edit(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id, usuario=request.user)
    estrategias = Estrategia.objects.all()
    if request.method == 'POST':
        trade.data_inicio = parse_date(request.POST.get('data_inicio'))
        data_fim_raw = request.POST.get('data_fim')
        trade.data_fim = parse_date(data_fim_raw) if data_fim_raw else None
        trade.ativo = request.POST.get('ativo')
        trade.quant = int(request.POST.get('quant'))
        estrategia_nome = request.POST.get('estrategia')
        trade.estrategia = Estrategia.objects.get(nome=estrategia_nome)
        trade.lado = request.POST.get('lado')
        trade.preco_entrada = request.POST.get('preco_entrada')
        preco_saida_raw = request.POST.get('preco_saida')
        trade.preco_saida = preco_saida_raw if preco_saida_raw else None
        trade.descricao = request.POST.get('descricao')
        if trade.data_fim and trade.preco_saida:
            trade.status = 'FINALIZADO'
        else:
            trade.status = 'ABERTO'
        trade.save()
        return redirect('trade_list')
    return render(request, 'core/trade_form.html', {'trade': trade, 'editando': True, 'estrategias': estrategias})

@login_required
def trade_delete(request, trade_id):
    trade = get_object_or_404(Trade, id=trade_id, usuario=request.user)
    trade.delete()
    return redirect('trade_list')

@login_required
def trade_delete_multiple(request):
    if request.method == 'POST':
        ids = request.POST.getlist('selected_trades')
        Trade.objects.filter(id__in=ids, usuario=request.user).delete()
    return redirect('trade_list')

@login_required
def dashboard_abertos(request):
    trades = Trade.objects.filter(usuario=request.user, status='ABERTO')
    # Estratégias x Lucro
    estrategia_lucro = defaultdict(float)
    for t in trades:
        estrategia_lucro[t.estrategia] += float(t.lucro_reais())
    estrategia_labels = [str(e) for e in estrategia_lucro.keys()]
    estrategia_data = list(estrategia_lucro.values())
    # Ativo x Lucro
    ativo_lucro = defaultdict(float)
    for t in trades:
        ativo_lucro[t.ativo] += float(t.lucro_reais())
    ativo_labels = list(ativo_lucro.keys())
    ativo_data = list(ativo_lucro.values())
    # Resultado por mês (usando data_fim)
    mes_lucro = defaultdict(float)
    for t in trades:
        mes = t.data_fim.strftime('%m/%Y')
        mes_lucro[mes] += float(t.lucro_reais())
    mes_labels = sorted(mes_lucro.keys(), key=lambda x: (x[3:], x[:2]))
    mes_data = [mes_lucro[mes] for mes in mes_labels]
    # Resultado acumulado
    acumulado_labels = mes_labels.copy()
    acumulado_data = []
    total = 0
    for mes in acumulado_labels:
        total += mes_lucro[mes]
        acumulado_data.append(total)
    # Percentual de acerto total
    total_trades = trades.count()
    trades_lucro = [t for t in trades if t.lucro_reais() > 0]
    percentual_acerto = (len(trades_lucro) / total_trades * 100) if total_trades else 0
    # Percentual de acerto por estratégia
    estrategia_acerto = {}
    for estrategia in estrategia_labels:
        trades_estrat = [t for t in trades if t.estrategia == estrategia]
        if trades_estrat:
            acertos = [t for t in trades_estrat if t.lucro_reais() > 0]
            estrategia_acerto[estrategia] = len(acertos) / len(trades_estrat) * 100
        else:
            estrategia_acerto[estrategia] = 0
    # Payoff total
    lucros = [float(t.lucro_reais()) for t in trades if t.lucro_reais() > 0]
    prejuizos = [abs(float(t.lucro_reais())) for t in trades if t.lucro_reais() < 0]
    payoff_total = (sum(lucros) / len(lucros)) / (sum(prejuizos) / len(prejuizos)) if lucros and prejuizos else 0
    # Payoff por estratégia
    estrategia_payoff = {}
    for estrategia in estrategia_labels:
        t_estrat = [t for t in trades if t.estrategia == estrategia]
        lucros_estrat = [float(t.lucro_reais()) for t in t_estrat if t.lucro_reais() > 0]
        prejuizos_estrat = [abs(float(t.lucro_reais())) for t in t_estrat if t.lucro_reais() < 0]
        if lucros_estrat and prejuizos_estrat:
            estrategia_payoff[estrategia] = (sum(lucros_estrat) / len(lucros_estrat)) / (sum(prejuizos_estrat) / len(prejuizos_estrat))
        else:
            estrategia_payoff[estrategia] = 0
    context = {
        'estrategia_labels': json.dumps(estrategia_labels),
        'estrategia_data': json.dumps(estrategia_data),
        'ativo_labels': json.dumps(ativo_labels),
        'ativo_data': json.dumps(ativo_data),
        'mes_labels': json.dumps(mes_labels),
        'mes_data': json.dumps(mes_data),
        'acumulado_labels': json.dumps(acumulado_labels),
        'acumulado_data': json.dumps(acumulado_data),
        'percentual_acerto': percentual_acerto,
        'estrategia_acerto': estrategia_acerto,
        'payoff_total': payoff_total,
        'estrategia_payoff': estrategia_payoff,
        'titulo_dashboard': 'Dashboard de Trades em Aberto',
    }
    return render(request, 'core/dashboard_abertos.html', context)

@login_required
def dashboard_nao_finalizados(request):
    trades = Trade.objects.filter(usuario=request.user).exclude(status='FINALIZADO')
    context = {
        'trades': trades,
        'titulo_dashboard': 'Trades Não Finalizados',
    }
    return render(request, 'core/dashboard_nao_finalizados.html', context)

@login_required
def aporte_list(request):
    aportes = Aporte.objects.all().order_by('-data')
    return render(request, 'core/aporte_list.html', {'aportes': aportes})

@login_required
def aporte_create(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        valor = request.POST.get('valor')
        Aporte.objects.create(data=data, valor=valor)
        return redirect('aporte_list')
    return render(request, 'core/aporte_form.html')

@login_required
def aporte_edit(request, aporte_id):
    aporte = get_object_or_404(Aporte, id=aporte_id)
    if request.method == 'POST':
        aporte.data = request.POST.get('data')
        aporte.valor = request.POST.get('valor')
        aporte.save()
        return redirect('aporte_list')
    return render(request, 'core/aporte_form.html', {'aporte': aporte, 'editando': True})

@login_required
def aporte_delete(request, aporte_id):
    aporte = get_object_or_404(Aporte, id=aporte_id)
    if request.method == 'POST':
        aporte.delete()
        return redirect('aporte_list')
    return render(request, 'core/aporte_confirm_delete.html', {'aporte': aporte})

@login_required
def retirada_list(request):
    retiradas = Retirada.objects.all().order_by('-data')
    return render(request, 'core/retirada_list.html', {'retiradas': retiradas})

@login_required
def retirada_create(request):
    if request.method == 'POST':
        data = request.POST.get('data')
        valor = request.POST.get('valor')
        Retirada.objects.create(data=data, valor=valor)
        return redirect('retirada_list')
    return render(request, 'core/retirada_form.html')

@login_required
def retirada_edit(request, retirada_id):
    retirada = get_object_or_404(Retirada, id=retirada_id)
    if request.method == 'POST':
        retirada.data = request.POST.get('data')
        retirada.valor = request.POST.get('valor')
        retirada.save()
        return redirect('retirada_list')
    return render(request, 'core/retirada_form.html', {'retirada': retirada, 'editando': True})

@login_required
def retirada_delete(request, retirada_id):
    retirada = get_object_or_404(Retirada, id=retirada_id)
    if request.method == 'POST':
        retirada.delete()
        return redirect('retirada_list')
    return render(request, 'core/retirada_confirm_delete.html', {'retirada': retirada})

@login_required
def raio_x_trade(request):
    ativo = request.GET.get('ativo', None)
    data_inicio = request.GET.get('data_inicio', None)
    data_fim = request.GET.get('data_fim', None)
    trades = Trade.objects.filter(usuario=request.user, status='FINALIZADO')
    if ativo:
        trades = trades.filter(ativo=ativo)
    if data_inicio:
        trades = trades.filter(data_inicio__gte=data_inicio)
    if data_fim:
        trades = trades.filter(data_inicio__lte=data_fim)

    quantidade = trades.count()

    # Taxa de acerto: trades com lucro > 0
    acertos = 0
    for t in trades:
        lucro = t.lucro_reais()
        if lucro is not None and lucro > 0:
            acertos += 1
    taxa_acerto = (acertos / quantidade * 100) if quantidade > 0 else 0

    # Estratégias e suas taxas de acerto
    estrategias_acerto = {}
    estrategias = trades.values_list('estrategia__nome', flat=True).distinct()
    for est in estrategias:
        trades_est = trades.filter(estrategia__nome=est)
        total_est = trades_est.count()
        acertos_est = 0
        for t in trades_est:
            lucro = t.lucro_reais()
            if lucro is not None and lucro > 0:
                acertos_est += 1
        estrategias_acerto[est] = round((acertos_est / total_est * 100), 2) if total_est > 0 else 0

    # Rentabilidade acumulada (%)
    rentabilidade_acumulada_percent = None
    if ativo not in ['WINFUT', 'WDOFUT']:
        soma_percent = 0
        for t in trades:
            perc = t.lucro_percentual()
            if perc is not None:
                soma_percent += float(perc)
        rentabilidade_acumulada_percent = round(soma_percent, 2)

    # Dados para gráfico
    grafico_labels = []
    grafico_barras = []
    grafico_linha = []
    pts_total = 0
    rentabilidade_acumulada = 0
    for t in trades.order_by('data_inicio'):
        label = t.data_inicio.strftime('%d/%m/%Y')
        grafico_labels.append(label)
        if t.ativo in ['WINFUT', 'WDOFUT']:
            pts = t.pts() or 0
            grafico_barras.append(float(pts))
            pts_total += float(pts)
            rentabilidade_acumulada += float(pts)
            grafico_linha.append(rentabilidade_acumulada)
        else:
            lucro = float(t.lucro_reais() or 0)
            grafico_barras.append(lucro)
            perc = t.lucro_percentual() or 0
            rentabilidade_acumulada += float(perc)
            grafico_linha.append(rentabilidade_acumulada)

    # Card 1: Total de Lucro (R$)
    total_lucro_rs = sum([float(t.lucro_reais() or 0) for t in trades])

    # Card 2: Média Cts por trade (apenas WINFUT/WDOFUT)
    media_cts = None
    if ativo in ['WINFUT', 'WDOFUT'] and quantidade > 0:
        soma_quant = sum([t.quant for t in trades])
        media_cts = round(soma_quant / quantidade, 2)

    grafico_cores_barras = []
    for i, t in enumerate(trades.order_by('data_inicio')):
        if t.ativo in ['WINFUT', 'WDOFUT']:
            valor = float(t.pts() or 0)
        else:
            valor = float(t.lucro_reais() or 0)
        if valor < 0:
            grafico_cores_barras.append('rgba(220, 53, 69, 0.7)')  # vermelho
        else:
            grafico_cores_barras.append('rgba(54, 162, 235, 0.5)')  # azul

    context = {
        'ativo': ativo,
        'quantidade': quantidade,
        'taxa_acerto': round(taxa_acerto, 2),
        'grafico_labels': grafico_labels,
        'grafico_barras': grafico_barras,
        'grafico_linha': grafico_linha,
        'pts_total': pts_total if ativo in ['WINFUT', 'WDOFUT'] else None,
        'ativos': Trade.objects.filter(usuario=request.user, status='FINALIZADO').values_list('ativo', flat=True).distinct(),
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'estrategias_acerto': estrategias_acerto,
        'rentabilidade_acumulada_percent': rentabilidade_acumulada_percent,
        'total_lucro_rs': total_lucro_rs,
        'media_cts': media_cts,
        'grafico_cores_barras': grafico_cores_barras,
    }
    return render(request, 'core/raio_x_trade.html', context)
