import random
import pytest

from playwright.sync_api import Page, expect
from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage


def test_cadastrar_novo_aporte_carteira(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
):
    """Valida a criação do aporte e sua exibição na tabela."""
    navbar.navegar_para_carteira()

    dias_inv = "0"
    dias_plan = "365"

    portfolio_page.cadastrar_aporte(
        ativo="Poupança",
        quantidade="2500.00",
        preco="1.00",
        dias_inv=dias_inv,
        dias_plan=dias_plan,
    )

    # Busca a linha específica recém-criada combinando Ativo + Prazo em dias
    linha_aporte = portfolio_page.obter_linha_por_ativo_e_prazo(
        "Poupança", dias_inv, dias_plan
    )

    expect(linha_aporte).to_be_visible(timeout=5000)
    expect(linha_aporte).to_contain_text("Poupança")


def test_cadastrar_aporte_outro_ativo_cdb(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
):
    """Valida o cadastro de um ativo diferente (CDB) com outro prazo."""
    navbar.navegar_para_carteira()

    dias_inv = "10"
    dias_plan = "720"

    portfolio_page.cadastrar_aporte(
        ativo="CDB",
        quantidade="3000.00",
        preco="1.00",
        dias_inv=dias_inv,
        dias_plan=dias_plan,
    )

    linha_aporte = portfolio_page.obter_linha_por_ativo_e_prazo(
        "CDB", dias_inv, dias_plan
    )

    expect(linha_aporte).to_be_visible(timeout=5000)
    expect(linha_aporte).to_contain_text("CDB")


def test_cadastro_aumenta_total_de_linhas(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
):
    """Valida que a tabela ganha exatamente uma linha após o cadastro."""
    navbar.navegar_para_carteira()

    total_inicial = portfolio_page.total_de_ativos_listados()

    portfolio_page.cadastrar_aporte(
        ativo="Poupança",
        quantidade="1500.00",
        preco="1.00",
        dias_inv="30",
        dias_plan="180",
    )

    expect(portfolio_page.linhas_tabela_carteira).to_have_count(
        total_inicial + 1, timeout=5000
    )


def test_linha_cadastrada_exibe_prazo_informado(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
):
    """Valida que a linha mostra o prazo digitado no formato 'X / Y dias'."""
    navbar.navegar_para_carteira()

    portfolio_page.cadastrar_aporte(
        ativo="Poupança",
        quantidade="800.00",
        preco="1.00",
        dias_inv="45",
        dias_plan="400",
    )

    linha_aporte = portfolio_page.obter_linha_por_ativo_e_prazo(
        "Poupança", "45", "400"
    )

    expect(linha_aporte).to_be_visible(timeout=5000)
    expect(linha_aporte).to_contain_text("45 / 400 dias")


def criar_aporte(portfolio_page: PortfolioPage, quantidade: str):
    """Cria um aporte com prazo aleatório e retorna a linha dele."""
    dias_plan = str(random.randint(1000, 3000))
    portfolio_page.cadastrar_aporte(
        ativo="Poupança",
        quantidade=quantidade,
        preco="1.00",
        dias_inv="0",
        dias_plan=dias_plan,
    )
    linha = portfolio_page.obter_linha_por_ativo_e_prazo(
        "Poupança", "0", dias_plan)
    expect(linha).to_be_visible(timeout=10000)
    return linha


def test_remover_ativo_da_tabela(logged_page: Page,
                                 navbar: NavbarComponent,
                                 portfolio_page: PortfolioPage):
    """Exclui um aporte e valida que ele sai da tabela."""
    navbar.navegar_para_carteira()
    linha = criar_aporte(portfolio_page, "1234.00")
    total_antes = portfolio_page.total_de_ativos_listados()

    portfolio_page.excluir_linha(linha)

    expect(linha).to_have_count(0, timeout=10000)
    expect(portfolio_page.linhas_tabela_carteira).to_have_count(
        total_antes - 1, timeout=10000)


def test_remover_ativo_recalcula_patrimonio(logged_page: Page,
                                            navbar: NavbarComponent,
                                            portfolio_page: PortfolioPage):
    """O card de Patrimônio Total deve mudar ao excluir um aporte."""
    navbar.navegar_para_carteira()
    linha = criar_aporte(portfolio_page, "1234.00")
    patrimonio_antes = portfolio_page.aguardar_patrimonio_estavel()

    portfolio_page.excluir_linha(linha)
    expect(linha).to_have_count(0, timeout=10000)

    expect(
        portfolio_page.card_patrimonio_total,
        "Patrimônio Total não foi recalculado após a exclusão",
    ).not_to_have_text(patrimonio_antes, timeout=10000)


def test_cancelar_exclusao_mantem_ativo(logged_page: Page,
                                        navbar: NavbarComponent,
                                        portfolio_page: PortfolioPage):
    """Ao cancelar a confirmação, nada deve mudar na carteira."""
    navbar.navegar_para_carteira()
    linha = criar_aporte(portfolio_page, "500.00")
    patrimonio_antes = portfolio_page.aguardar_patrimonio_estavel()

    mensagens = portfolio_page.excluir_linha(linha, confirmar=False)

    if not mensagens:
        pytest.skip("A aplicação não abriu diálogo nativo de confirmação.")

    patrimonio_depois = portfolio_page.aguardar_patrimonio_estavel()
    expect(linha).to_be_visible()
    assert patrimonio_depois == patrimonio_antes

    # Limpeza da massa de teste
    portfolio_page.excluir_linha(linha, confirmar=True)
    expect(linha).to_have_count(0, timeout=10000)
