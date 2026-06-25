from controllers.sistema_controller import SistemaController
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="customtkinter" )

if __name__ == "__main__":
    aplicacao = SistemaController()
    aplicacao.iniciar()
    