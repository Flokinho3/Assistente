package main

import (
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
	FILE_VERSAO = "Sistema/Vercao.json"
	WEB_VERSAO  = "https://raw.githubusercontent.com/Flokinho3/Assistente/main/Sistema/Vercao.json"
	PROJETO     = "https://github.com/Flokinho3/Assistente.git"
)

// Função principal
func main() {
	version()
}

// Verifica e sincroniza versões
func version() {
	// Lê a versão do arquivo local
	fileVersion := strings.TrimSpace(readLocalFile(FILE_VERSAO))

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
