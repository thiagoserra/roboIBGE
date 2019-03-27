'''
Spider IPCA v.1
---------------
Captura variação do IPCA do site do IBGE

Para o Blog Ciência de Dados
Thiago Serra F. Carvalho (C073835)
'''
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time


class Captura:
    '''
    PASSO 1: Abrir o navegador
    O objeto webdriver é o responsável pela manipulação do navegador
    '''
    nav = webdriver.Chrome()

    '''
    um método auxiliar apenas aguardar 'x' segundos e ir nos dando no terminal o status da operação
    '''
    def aguarde(self, tempo, texto):
        print("[i] " + texto + "...Aguardando...")
        time.sleep(tempo)
        self.nav.maximize_window()

    '''
    o método principal da nossa classe de captura
    '''
    def inicio(self):
        '''
        PASSO 2: Abrir o site alvo
        Aqui setamos o endereço e mandamos o navegador para o site
        '''
        print("------------------------------------------------------")
        self.aguarde(2, "Navegando até a página...")
        strUrl = "https://sidra.ibge.gov.br/home/ipca/brasil"
        self.nav.get(strUrl)


        '''
        PASSO 3: Localizar na página a tabela
        Aqui usaremos o beautifulSoup para analisar o código fonte da página
        '''
        # pagina: variavel que guarda todo o código html da página alvo
        print("------------------------------------------------------")
        self.aguarde(2, "Capturando o código da página...")
        pagina = BeautifulSoup(self.nav.page_source, 'html.parser')

        # vamos então localizar nosso div alvo e gravar tudo que está dentro dessa tag numa variavel
        tabela = pagina.find('div' , attrs={'id': 'ipca-q1' })


        # Aqui instaciamos um objeto do tipo parser
        parser = parserTabelaIPCA()
        saida = parser.analisaTabela(tabela)
        print("------------------------------------------------------")
        self.aguarde(2, "Tratando os dados...")
        print("------------------------------------------------------")
        print( saida )
        print("------------------------------------------------------")


        # fechando o navegador
        self.nav.close()
        self.nav.quit()


class parserTabelaIPCA:
    '''
    Este é o 'coração' do sistema, onde nós analisamos a tabela alvo e
    pegamos o que nos interessa: os dados dentro de cada <td>
    '''
    def analisaTabela(self, tabela):
        nColunas = 0
        nLinhas = 0
        column_names = []


        #contar o numero de linhas e colunas
        for row in tabela.find_all("tr"):
            td_tags = row.find_all("td")
            if len(td_tags) > 0:
                nLinhas+=1
                if nColunas == 0:
                    nColunas = len(td_tags)

            #captura o titulo das colunas - se tiver thead/th
            th_tags = row.find_all("th", attrs={"tabela-titulo"})
            if len(th_tags) > 0 and len(column_names) == 0:
                for th in th_tags:
                    column_names.append(th.get_text())

        # contar numero de nomes na lista e comparar com o n. de colunas
        if len(column_names) > 0 and len(column_names) != nColunas:
            raise Exception("[e] Quantidade de colunas difere da quantidade de titulos de colunas capturados!")

        #separando para o dataFrame os titulos das colunas
        columns = column_names if len(column_names) > 0 else range(0,nColunas)

        #criando um arquivo CSV para saida do processamento
        fname = 'C:\\TEMP\\base.csv'
        txt_column = ""

        #gravar titulos das colunas no arquivo texto
        txt_column = (";").join(column_names)
        with open(fname, "a", encoding="utf-8") as f:
            f.write(txt_column+"\n")

        #criando o dataframe com o pandas para armazenar os dados
        df = pd.DataFrame(columns = columns, index= range(0,nLinhas))
        row_marker = 0

        #percorre as celulas para extrair o texto e gravar no arquivo
        for row in tabela.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            txt_cell = ""
            for column in columns:
                df.iat[row_marker,column_marker] = column.get_text()
                column_marker += 1
                txt_cell = txt_cell + column.get_text() + "; "
            if len(columns) > 0:
                row_marker += 1
            if(txt_cell != ""):
                #salvando a saida no arquivo criado
                with open(fname, "a", encoding="utf-8") as f:
                    f.write(str(txt_cell) +"\n")

        return df


# Nosso programa para rodar esse código é bastante simples
print("------------------------------- -> Spider IPCA v.1 <-")
tela = Captura()
tela.inicio()
print("[i] Finalizado!")
print("------------------------------------------------------")
