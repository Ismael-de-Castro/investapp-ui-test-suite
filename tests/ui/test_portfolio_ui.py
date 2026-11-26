from playwright.sync_api import Page, expect
from pages.navbar_component import NavbarComponent
from pages.portfolio_page import PortfolioPage


def test_cadastrar_novo_aporte_carteira(
    logged_page: Page,
    navbar: NavbarComponent,
    portfolio_page: PortfolioPage,
):
    """Valida a criação de aporte e renderização exata na tabela da carteira."""
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