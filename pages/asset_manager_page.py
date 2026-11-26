from playwright.sync_api import Page, Locator
from pages.base_page import BasePage


class AssetManagerPage(BasePage):
    """Representa a aba Gerenciar Taxas (AssetManager.jsx - US05)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.tabela_taxas = page.locator("table").first
        self.linhas_tabela = page.locator("table tbody tr")
        self.mensagem_sucesso = page.get_by_text("foi salva com sucesso")

    def obter_linha_do_ativo(self, nome_ativo: str) -> Locator:
        """Retorna a linha da tabela correspondente ao ativo."""
        return self.linhas_tabela.filter(has_text=nome_ativo).first

    def obter_input_taxa(self, nome_ativo: str) -> Locator:
        """Campo 'Nova taxa' da linha do ativo."""
        return self.obter_linha_do_ativo(nome_ativo).locator("input")

    def obter_botao_salvar(self, nome_ativo: str) -> Locator:
        """Botão 'Salvar Alteração' da linha do ativo."""
        return self.obter_linha_do_ativo(nome_ativo).get_by_role(
            "button", name="Salvar Alteração"
        )

    def obter_taxa_atual(self, nome_ativo: str) -> str:
        """Lê o valor da taxa exibido no input do ativo."""
        return self.obter_input_taxa(nome_ativo).input_value()

    def obter_taxa_salva(self, nome_ativo: str) -> Locator:
        """Célula 'Taxa anual salva' (ex.: 6.17% a.a.)."""
        return self.obter_linha_do_ativo(nome_ativo).locator("td").nth(2)

    def alterar_taxa(self, nome_ativo: str, novo_valor: str):
        """Preenche a nova taxa e clica em salvar."""
        campo = self.obter_input_taxa(nome_ativo)
        campo.wait_for(state="visible")
        campo.fill(novo_valor)
        self.obter_botao_salvar(nome_ativo).click()
