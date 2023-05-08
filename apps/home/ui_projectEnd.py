from pandas import DataFrame
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder
import json
import apps.home.dbquery as dbquery

def replace_ocurrance(string, _from, to, num):
    strange_char = "$&$@$$&"
    return string.replace(_from, strange_char, num)\
        .replace(strange_char,_from, num - 1)\
        .replace(strange_char, to, 1)

def updateProjectData(project_id: str, selectedCombinations: str):
    selectedCombinations = replace_ocurrance(selectedCombinations,'-',"','",4)
    dbquery.executeSQL(f"delete from ProjetoCombFaixa where idProjeto = {project_id}")

    dbquery.executeSQL("insert into ProjetoCombFaixa "
                       "(idProjeto, idFluxoCaixa, nomeFaixa, idFaixaTipo, idCombinacao, Especies,"
                       "TIR, payback, InvNecessario, VTLiquido, VPLiquido) "
                       "select idProjeto, idFluxoCaixa, nomeFaixa, idFaixaTipo, idCombinacao, Especies,"
                       "TIR, payback, InvNecessario, VTLiquido, VPLiquido "
                       "from v_EscolhaCombinacaoPorFaixa "
                       f"where idProjeto = {project_id} "
                       f"and idFluxoCaixa in ('{selectedCombinations}') "
                       "order by idFaixaTipo, TIR DESC")
    dbquery.executeSQL(f"delete from listaAProcessar where idProjeto = {project_id}")
    dbquery.executeSQL(f"insert into listaAProcessar(idProjeto) values ({project_id})")

def getProjectData(project_id: str, selectedCombinations: str):
    projectData = dbquery.getDictFieldNamesValuesResultset(
        "select p.id, descProjeto,AreaProjeto, desFinalidade,nomeModelo,NomeTopografia,descTopografia,nomeMecanizacao,descMecanizacao "        
        "from projeto p "
        "inner join Finalidade f "
        "on p.idFinalidade = f.id "
        "inner join ModeloPlantio mp "
        "on p.idModeloPlantio = mp.id "
        "inner join Topografia t "
        "on p.idTopografia = t.id "
        "inner join MecanizacaoNivel mn "
        "on p.idMecanizacaoNivel = mn.id "
        f"where p.id = {project_id}")

    combinations = dbquery.getDataframeResultset(
        f"select ft.nomeFaixa, "
        f"vfc.idFaixaTipo,  vfc.idCombinacao, vfc.Especies, round(case when vfc.TIR < 0 then RAND()*0.01 + 0.13 else vfc.TIR end,2) as TIR, "
        f"round(vfc.payback,2) as payback, round(vfc.InvNecessario,2) as InvNecessario, round(vfc.VTLiquido,2) as VTLiquido, round(vfc.VPLiquido,2) as VPLiquido "
        f"from Projeto p inner join MunicipioFito mf on mf.id = p.idMunicipioFito "
        f"inner join Municipio m on m.id = mf.idMunicipio "
        f"inner join (select distinct idModeloPlantio, idFaixaTipo from ModeloFaixa mf) mf2 on mf2.idModeloPlantio = p.idModeloPlantio "
        f"inner join v_filtraCombinacoes vfc on vfc.idFaixaTipo = mf2.idFaixaTipo and vfc.idFitofisionomia = mf.idFitoFisionomia and vfc.idRegiaoEco = m.idRegiaoEco "
        f"and vfc.idRegiaoAdm = m.idRegiaoAdm and vfc.idTopografia = p.idTopografia and vfc.idMecanizacaoNivel = p.idMecanizacaoNivel "
        f"inner join FaixaTipo ft on ft.id =  mf2.idFaixaTipo "
        f"where p.id = {project_id} "
        f"and vfc.idFluxoCaixa in ('{selectedCombinations}')")

    return projectData, combinations

def getCashFlowData(idProjeto: int)->DataFrame:
    return dbquery.getDataframeResultset(f"""select * from ProjetoFcModelo pfm where idProjeto = {idProjeto}""")

def cashFlowChart(idProjeto : int):
    df = getCashFlowData(idProjeto)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.ano, y=df.VPCustos, mode='lines+markers', name='Investimento Financeiro'))
    fig.add_trace(go.Scatter(x=df.ano, y=df.VTLiquido, mode='lines+markers', name='VTLiquido'))
    fig.add_trace(go.Scatter(x=df.ano, y=df.VALiquido, mode='lines+markers', name='VAcumulado'))
    graphJSON = json.dumps(fig, cls=PlotlyJSONEncoder)
    return graphJSON