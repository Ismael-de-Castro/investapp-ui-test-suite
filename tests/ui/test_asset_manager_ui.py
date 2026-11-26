from playwright.sync_api import Page, expect
from pages.navbar_component import NavbarComponent
from pages.asset_manager_page import AssetManagerPage

ATIVO = "Poupança"


def test_visualizar_tabela_de_taxas(
    logged_page: Page,
    navbar: NavbarComponent,
    asset_manager_page: AssetManagerPage,
):
    """US05: a aba Gerenciar Taxas exibe a tabela com os ativos."""
    navbar.navegar_para_gerenciar_taxas()

    expect(asset_manager_page.tabela_taxas).to_be_visible()
    expect(asset_manager_page.linhas_tabela.first).to_be_visible()
    expect(asset_manager_page.obter_linha_do_ativo(ATIVO)).to_be_visible()


def test_salvar_taxa_exibe_mensagem_de_sucesso(
    logged_page: Page,
    navbar: NavbarComponent,
    asset_manager_page: AssetManagerPage,
):
    """US05: ao salvar uma nova taxa, a aplicação exibe a confirmação."""
    navbar.navegar_para_gerenciar_taxas()
    taxa_original = asset_manager_page.obter_taxa_atual(ATIVO)
    nova_taxa = "7.50" if taxa_original != "7.50" else "8.50"

    try:
        asset_manager_page.alterar_taxa(ATIVO, nova_taxa)
        expect(asset_manager_page.mensagem_sucesso).to_be_visible(timeout=5000)
    finally:
        navbar.navegar_para_gerenciar_taxas()
        asset_manager_page.alterar_taxa(ATIVO, taxa_original)


def test_taxa_alterada_persiste_apos_recarregar(
    logged_page: Page,
    navbar: NavbarComponent,
    asset_manager_page: AssetManagerPage,
):
    """US05: a taxa salva deve continuar exibida após recarregar a página."""
    navbar.navegar_para_gerenciar_taxas()
    taxa_original = asset_manager_page.obter_taxa_atual(ATIVO)
    nova_taxa = "7.50" if taxa_original != "7.50" else "8.50"

    try:
        asset_manager_page.alterar_taxa(ATIVO, nova_taxa)
        expect(asset_manager_page.mensagem_sucesso).to_be_visible(timeout=5000)

        asset_manager_page.recarregar()
        navbar.navegar_para_gerenciar_taxas()
        expect(asset_manager_page.obter_taxa_salva(ATIVO)).to_contain_text(
            f"{nova_taxa}% a.a."
        )
    finally:
        navbar.navegar_para_gerenciar_taxas()
        asset_manager_page.alterar_taxa(ATIVO, taxa_original)
