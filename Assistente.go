package main

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

// Constantes para arquivos locais e URL remota
const (
	FILE_VERSAO     = "Sistema/Vercao.json"
	WEB_VERSAO      = "https://raw.githubusercontent.com/Flokinho3/Assistente/main/Sistema/Vercao.json"
	PROJETO         = "https://github.com/Flokinho3/Assistente.git"
	PYTHON_VERSION  = "3.11"
)

// Diretório base do programa
var BaseDir string

// Inicializa o caminho base do programa
func init() {
	exePath, err := os.Executable()
	if err != nil {
		fmt.Println("Erro ao obter o caminho do executável:", err)
		os.Exit(1)
	}
	BaseDir = filepath.Dir(exePath)
}

// Função principal
func main() {
	version()
	checkPythonVersion()
}

// Verifica e sincroniza versões
func version() {
	// Caminho absoluto do arquivo local de versão
	localVersionPath := filepath.Join(BaseDir, FILE_VERSAO)

	// Lê a versão do arquivo local
	fileVersion := strings.TrimSpace(readLocalFile(localVersionPath))

	// Baixa a versão do servidor remoto
	webVersion := strings.TrimSpace(download(WEB_VERSAO))

	// Compara as versões
	if fileVersion != webVersion {
		fmt.Println("Versões diferentes! ")
		if compareVersions(fileVersion, webVersion) {
			fmt.Println("Atualizando para a versão mais recente...")
			clone()
		} else {
			fmt.Println("Versão local é maior que a versão remota! Não é necessário atualizar.")
		}
	} else {
		fmt.Println("Versão já está atualizada!")
	}

	if fileVersion != "" {
		fmt.Println("Versão do arquivo local: ", fileVersion)
	}
	fmt.Println("Versão remota: ", webVersion)
}

// Faz download do conteúdo de uma URL
func download(url string) string {
	resp, err := http.Get(url)
	if err != nil {
		fmt.Println("Erro ao fazer download:", err)
		return ""
	}
	defer resp.Body.Close()

	body, err := ioutil.ReadAll(resp.Body)
	if err != nil {
		fmt.Println("Erro ao ler o conteúdo da resposta:", err)
		return ""
	}
	return string(body)
}

// Faz clone do projeto
func clone() {
	// Obtém o diretório "Documents" do usuário
	docDir, err := os.UserHomeDir()
	if err != nil {
		fmt.Println("Erro ao obter o diretório do usuário:", err)
		return
	}
	assistentePath := filepath.Join(docDir, "Documents", "Assistente")

	// Cria o diretório, se necessário
	err = os.MkdirAll(assistentePath, 0755)
	if err != nil {
		fmt.Println("Erro ao criar o diretório:", err)
		return
	}

	// Clona o projeto do GitHub
	cmd := exec.Command("git", "clone", PROJETO, assistentePath)
	err = cmd.Run()
	if err != nil {
		fmt.Println("Erro ao clonar o projeto:", err)
		return
	}

	fmt.Println("Projeto clonado com sucesso em:", assistentePath)
}

// Lê o conteúdo de um arquivo local
func readLocalFile(path string) string {
	data, err := ioutil.ReadFile(path)
	if err != nil {
		fmt.Println("Erro ao ler o arquivo local:", err)
		return ""
	}
	return string(data)
}

// Compara versões no formato "1.0.1"
func compareVersions(local, remote string) bool {
	localParts := strings.Split(local, ".")
	remoteParts := strings.Split(remote, ".")

	for i := 0; i < len(localParts) && i < len(remoteParts); i++ {
		if localParts[i] < remoteParts[i] {
			return true
		} else if localParts[i] > remoteParts[i] {
			return false
		}
	}

	// Caso as versões tenham tamanhos diferentes
	return len(localParts) < len(remoteParts)
}

// Verifica a versão do Python
func checkPythonVersion() {
	// Cria o comando para obter a versão do Python
	cmd := exec.Command("python", "--version")

	// Captura a saída do comando
	var out bytes.Buffer
	cmd.Stdout = &out
	cmd.Stderr = &out // Algumas versões do Python escrevem na saída de erro
	err := cmd.Run()

	if err != nil {
		fmt.Println("Erro ao verificar a versão do Python:", err)
		return
	}

	// Obtém a saída como string
	output := strings.TrimSpace(out.String())
	fmt.Println("Versão detectada do Python:", output)

	// Verifica se a versão detectada contém a versão esperada
	if strings.Contains(output, PYTHON_VERSION) {
		fmt.Println("Versão do Python correta!")

		// Pergunta se deseja iniciar com o Windows
		var resposta string
		fmt.Println("Deseja iniciar com o Windows? (s/n)")
		fmt.Scanln(&resposta)

		if strings.ToLower(resposta) == "s" {
			err := addToStartup()
			if err != nil {
				fmt.Println("Erro ao configurar inicialização com o Windows:", err)
			} else {
				fmt.Println("Configuração concluída com sucesso!")
			}
		} else {
			fmt.Println("Início automático com o Windows não configurado.")
		}
	} else {
		fmt.Println("Versão do Python incorreta! Por favor, instale a versão", PYTHON_VERSION)
	}
}

// Adiciona o programa ao iniciar do Windows
func addToStartup() error {
	// Caminho absoluto para o script Python
	scriptPath := filepath.Join(BaseDir, "main.py")
	if _, err := os.Stat(scriptPath); os.IsNotExist(err) {
		return fmt.Errorf("arquivo Python não encontrado: %s", scriptPath)
	}

	// Cria o comando para executar o script
	execCommand := fmt.Sprintf("python %q", scriptPath)

	// Diretório Startup do Windows
	startupPath := filepath.Join(os.Getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "Assistente.bat")

	// Cria o arquivo .bat para iniciar o programa
	err := os.WriteFile(startupPath, []byte(execCommand), 0644)
	if err != nil {
		return fmt.Errorf("erro ao criar arquivo de inicialização: %v", err)
	}

	fmt.Println("Arquivo de inicialização criado em:", startupPath)
	return nil
}
