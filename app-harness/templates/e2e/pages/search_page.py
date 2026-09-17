"""Exemplo de Page Object Model (POM) — padrão exigido pela skill qa-playwright-e2e.

Regras (Aula 10):
- Locators SEMÂNTICOS: get_by_role / get_by_label — nunca CSS/XPath frágil.
- Cada tela = uma classe; cada fluxo = um método reutilizável.
- Interceptação de rede para setups determinísticos.
"""

from playwright.sync_api import Page


class SearchPage:
    def __init__(self, page: Page):
        self.page = page
        # Locators semânticos — únicos pontos de contato com o DOM
        self.search_input = page.get_by_role("searchbox", name="Buscar veículos")
        self.search_button = page.get_by_role("button", name="Buscar")
        self.result_list = page.get_by_role("list", name="Resultados")
        self.empty_state = page.get_by_role("region", name="Sem resultados")

    def search(self, term: str) -> "SearchPage":
        self.search_input.fill(term)
        self.search_button.click()
        self.page.wait_for_load_state("networkidle")
        return self

    def has_results(self) -> bool:
        return self.result_list.is_visible() and not self.empty_state.is_visible()

    def result_count(self) -> int:
        return self.result_list.get_by_role("listitem").count()