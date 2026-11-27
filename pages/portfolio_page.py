from playwright.sync_api import Page, Locator, Dialog, expect
from pages.base_page import BasePage


class PortfolioPage(BasePage):
    """Representa a aba da Carteira de Investimentos (Portfolio.jsx)."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Formulário de Cadastro
        self.select_ativo = page.locator("[data-testid='select-asset-name']")
        self.input_quantidade = page.locator("[data-testid='input-asset-amount']")
        self.input_preco_compra = page.locator("[data-testid='input-asset-price']")
        self.input_dias_investidos = page.locator("[data-testid='input-asset-days-invested']")
        self.input_dias_planejados = page.locator("[data-testid='input-asset-planned-days']")
        self.botao_adicionar = page.locator("[data-testid='btn-add-asset']")

        # Indicadores e Tabela
        self.card_patrimonio_total = page.locator("[data-testid='summary-current-val']")
        self.linhas_tabela_carteira = page.locator("[data-testid='table-portfolio'] tbody tr")
        self.alerta_erro = page.locator("[data-testid='portfolio-error']")

    def cadastrar_aporte(self, ativo: str, quantidade: str, preco: str, dias_inv: str, dias_plan: str):
        """Preenche todos os campos do formulário e submete o novo aporte."""
        self.select_ativo.wait_for(state="visible")
        try:
            self.select_ativo.select_option(value=ativo)
        except Exception:
            self.select_ativo.select_option(label=f"{ativo}")
        self.input_quantidade.fill(quantidade)
        self.input_preco_compra.fill(preco)
        self.input_dias_investidos.fill(dias_inv)
        self.input_dias_planejados.fill(dias_plan)
        self.botao_adicionar.click()

    def obter_linha_por_ativo_e_prazo(self, nome_ativo: str, dias_inv: str, dias_plan: str) -> Locator:
        """
        Localiza especificamente a linha do ativo que corresponde aos dias cadastrados,
        evitando colisão com outros aportes do mesmo ativo.
        """
        texto_prazo = f"{dias_inv} / {dias_plan} dias"
        return self.linhas_tabela_carteira.filter(has_text=nome_ativo).filter(has_text=texto_prazo).first

    def obter_ultimo_ativo_cadastrado(self, nome_ativo: str) -> Locator:
        """Retorna a última linha inserida na tabela para o ativo informado."""
        return self.linhas_tabela_carteira.filter(has_text=nome_ativo).last

    def total_de_ativos_listados(self) -> int:
        """Retorna o número atual de registros na tabela da carteira ignorando a mensagem de vazio."""
        self.page.wait_for_selector("[data-testid='table-portfolio'] tbody", timeout=5000)
        # Se contiver a mensagem de tabela vazia (colSpan="7"), o total é 0
        if self.linhas_tabela_carteira.filter(has_text="Nenhum ativo cadastrado").count() > 0:
            return 0
        return self.linhas_tabela_carteira.count()

    def obter_linha_por_ativo(self, nome_ativo: str) -> Locator:
        """Retorna a última linha da tabela para o ativo informado."""
        return self.linhas_tabela_carteira.filter(has_text=nome_ativo).last

    def excluir_linha(self, linha: Locator,
                      confirmar: bool = True) -> list[str]:
        """Exclui a linha, tratando a confirmação. Retorna as mensagens."""
        mensagens: list[str] = []

        def tratar_dialogo(dialogo: Dialog):
            mensagens.append(dialogo.message)
            if confirmar:
                dialogo.accept()
            else:
                dialogo.dismiss()

        # O listener precisa existir antes do clique
        self.page.on("dialog", tratar_dialogo)
        try:
            linha.locator("[data-testid^='btn-delete-asset-']").click()
        finally:
            self.page.remove_listener("dialog", tratar_dialogo)
        return mensagens

    def excluir_primeiro_ativo(self) -> list[str]:
        """Exclui o ativo da primeira linha da tabela."""
        return self.excluir_linha(self.linhas_tabela_carteira.first)

    def aguardar_patrimonio_estavel(self) -> str:
        """Espera o card de Patrimônio Total parar de mudar."""
        expect(self.card_patrimonio_total).to_be_visible()
        anterior = self.card_patrimonio_total.inner_text()
        repeticoes = 0
        for _ in range(20):
            self.page.wait_for_timeout(500)
            atual = self.card_patrimonio_total.inner_text()
            repeticoes = repeticoes + 1 if atual == anterior else 0
            if repeticoes >= 2:
                return atual.strip()
            anterior = atual
        raise AssertionError("O card de Patrimônio Total não estabilizou.")
