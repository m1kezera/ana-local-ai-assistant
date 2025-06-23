from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

class ChromeBot:
    def __init__(self):
        self.driver = self.iniciar_navegador(headless=True)
        self.headless_mode = True
        logging.info("ChromeBot iniciado com modo headless.")

    def iniciar_navegador(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        try:
            return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        except Exception as e:
            logging.error(f"❌ Falha ao iniciar navegador Chrome: {e}")
            return None

    def executar_comando_no_site(self, comando, url):
        if not self.driver:
            return {"status": "erro", "mensagem": "Falha ao iniciar o navegador Chrome.", "dados": None}

        try:
            logging.info(f"🌍 Acessando URL: {url}")
            self.driver.get(url)
            time.sleep(3)

            comando = comando.lower()

            if "clicar" in comando:
                return self._clicar_enviar()

            if "preencher" in comando and "com" in comando:
                return self._preencher_campo(comando)

            return {
                "status": "ok",
                "mensagem": f"🌐 Página '{url}' carregada com sucesso. Nenhuma ação adicional executada.",
                "dados": None
            }

        except Exception as e:
            if self.headless_mode:
                logging.warning("⚠️ Modo headless falhou, tentando reabrir com Chrome visível...")
                try:
                    self.driver.quit()
                except: pass
                self.driver = self.iniciar_navegador(headless=False)
                self.headless_mode = False
                return self.executar_comando_no_site(comando, url)
            else:
                logging.error(f"❌ Erro de navegação/interação: {e}")
                return {
                    "status": "erro",
                    "mensagem": f"Erro ao acessar ou interagir com o site: {str(e)}",
                    "dados": None
                }

    def _clicar_enviar(self):
        try:
            botao = self.driver.find_element(
                By.XPATH,
                "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'enviar')]"
            )
            botao.click()
            return {
                "status": "ok",
                "mensagem": "✅ Botão 'enviar' clicado com sucesso.",
                "dados": None
            }
        except Exception as e:
            logging.warning(f"Botão 'enviar' não encontrado: {e}")
            return {
                "status": "erro",
                "mensagem": "❌ Botão 'enviar' não encontrado na página.",
                "dados": None
            }

    def _preencher_campo(self, comando):
        try:
            partes = comando.split("com")
            campo_label = partes[0].split("preencher")[-1].strip()
            valor = partes[1].strip()

            campo = self.driver.find_element(
                By.XPATH,
                f"//input[contains(translate(@placeholder, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{campo_label.lower()}')]"
            )
            campo.send_keys(valor)
            return {
                "status": "ok",
                "mensagem": f"📝 Campo '{campo_label}' preenchido com '{valor}'.",
                "dados": None
            }
        except Exception as e:
            logging.warning(f"Campo '{campo_label}' não encontrado: {e}")
            return {
                "status": "erro",
                "mensagem": f"❌ Campo '{campo_label}' não localizado na página.",
                "dados": None
            }

# Teste isolado
if __name__ == "__main__":
    bot = ChromeBot()
    resposta = bot.executar_comando_no_site("navegar para https://google.com", "https://google.com")
    print(resposta)
