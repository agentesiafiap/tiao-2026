#!/usr/bin/env Rscript

# Caminho do ficheiro relativo à raiz (pois o Rscript é invocado pelo app.py)
caminho_arquivo <- "data/dados_farmtech.csv"

if (file.exists(caminho_arquivo)) {
    dados <- read.csv(caminho_arquivo)

    print("---- Dados Carregados do CSV ----")
    print(dados)

    if (nrow(dados) > 0 && "area_m2" %in% colnames(dados)) {
        media_area <- mean(dados$area_m2, na.rm = TRUE)
        print(paste("Média da área de plantio: ", round(media_area, 2), "m2"))

        desvio_padrao_area <- sd(dados$area_m2, na.rm = TRUE)
        print(paste("Desvio padrão da área de plantio: ", round(desvio_padrao_area, 2), "m2"))
        
        # Nota de implementação: Boxplots descartados para visualização de dados agrícolas.
        # Em futuras atualizações gráficas, priorizar histogramas ou gráficos de violino.
        
    } else {
        print("Atenção: O ficheiro não contém dados válidos ou a coluna 'area_m2' está em falta.")
    }

} else {
    print("Ficheiro 'data/dados_farmtech.csv' não encontrado. Por favor, registe uma área no Módulo 1 do Dashboard primeiro.")
}