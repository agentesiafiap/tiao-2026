# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# Iniciando a coleta de dados

# 🚜 FarmTech Solutions: Visão Computacional para Saúde Animal e Segurança

## 👨‍🎓 Integrantes: 
- <a href="">Daniel Emilio Baião</a>
- <a href="">Erik Criscuolo</a>
- <a href="">Marcus Vinícius Loureiro Garcia</a> 
- <a href="">Sidney William de Paula Dias,</a> 
- <a href="">Hugo Rodrigues Carvalho Silva</a>

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="https://www.linkedin.com/in/sabrina-otoni-22525519b/">Sabrina Otoni</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/company/inova-fusca">André Godoi Chiovato</a>


## 🎯 Objetivo do Projeto
Este repositório contém a Prova de Conceito (PoC) desenvolvida para a **FarmTech Solutions**, focada na expansão de serviços de inteligência artificial para as verticais de **Saúde Animal Especializada** e **Segurança Patrimonial**.

## 📖 1. Contexto e Estratégia de Negócio
A FarmTech Solutions expandiu sua expertise em IA agrícola para novos mercados. Para esta fase, selecionamos dois alvos que representam desafios reais de visão computacional:
* **🐶 Saúde Animal (Shih Tzu):** Monitoramento clínico e bem-estar animal. A pelagem complexa do Shih Tzu serve como teste de estresse para a identificação de texturas.
* **🚗 Segurança Patrimonial (Nissan Kicks):** Controle de acesso e segurança perimetral. Focamos na distinção específica do modelo SUV para garantir maior rigor na vigilância.

## 🛠️ 2. Tecnologias e Metodologia
O projeto foi desenvolvido em ambiente **Google Colab com aceleração por GPU (Tesla T4)**, utilizando as bibliotecas:
* **PyTorch / YOLOv5:** Para detecção de objetos com consciência espacial (Bounding Boxes).
* **TensorFlow / Keras:** Para o estudo de ablação em redes de classificação (CNN).
* **Make Sense AI:** Para anotação e rotulação do dataset customizado.
* **Scikit-Learn / Seaborn:** Para geração de matrizes de confusão e análise estatística.

## 📁 3. Acesso aos Dados e Imagens
Devido ao volume de dados e arquivos de resultados, as imagens originais, os pesos dos modelos treinados e os logs de métricas estão disponíveis no link abaixo:

🔗 **[Acesse a Pasta Compartilhada no Google Drive](https://drive.google.com/drive/folders/1zLoxEAL4GQQSpSXkrGD2G2smPgUa_2-b?usp=share_link)**
*(Nesta pasta você encontrará os datasets de treino/teste)*

🔗 **[Acesse a Arquivo Compartilhada no Google Drive](https://drive.google.com/file/d/1QrHlhDsjmlKlN3ViOFLqtrdUyx7hq-_t/view?usp=share_link)**
*(Neste arquivo você encontrará notebook com as analises e as capturas dos resultados de inferência)*

/content/drive/MyDrive/FIAP_IA/Computer_Vision/
```
├── 📂 dataset_farmtech/               # Estrutura para YOLOv5 (Detecção)
│   ├── 📂 images/                     # Imagens originais (.jpg ou .png)
│   │   ├── 📂 train/                  # Imagens de treinamento
│   │   ├── 📂 val/                    # Imagens de validação
│   │   └── 📂 test/                   # Imagens inéditas para teste final
│   ├── 📂 labels/                     # Arquivos de anotação (.txt do Make Sense)
│   │   ├── 📂 train/                  # Labels das imagens de treino
│   │   ├── 📂 val/                    # Labels das imagens de validação
│   └── 📄 data.yaml                   # Configuração das classes (Shih Tzu e Kicks)
│
├── 📂 dataset_farmtech_cnn/                    # Estrutura para Keras (Classificação)
│   ├── 📂 train/                      # Dados de Treinamento
│   │   ├── 📂 nissan_kicks/           # Imagens da classe 0
│   │   └── 📂 shih_tzu/               # Imagens da classe 1
│   ├── 📂 val/                        # Dados de Validação
│   │   ├── 📂 nissan_kicks/
│   │   └── 📂 shih_tzu/
│   └── 📂 test/                       # Dados de Teste (Inéditos)
│       ├── 📂 nissan_kicks/
│       └── 📂 shih_tzu/
```
## 📊 4. Achados Técnicos e Performance

### Detecção (YOLOv5)
* **Baseline:** Demonstrado como insuficiente para distinção de raças e modelos específicos.
* **Epoch 30 vs 60:** A evolução para 60 épocas consolidou a diagonal principal da Matriz de Confusão, reduzindo erros entre classes, embora tenha exigido um ajuste fino no *Confidence Threshold* para mitigar ruídos de background.

### Classificação (Ablation Study CNN)
Realizamos um comparativo rigoroso entre três arquiteturas:
1.  **VGG16 (Benchmark):** 100% de Acurácia | Loss: 0.0000.
2.  **CNN V1 (Rasa):** 100% de Acurácia | Loss: 0.4748.
3.  **CNN V2 (Profunda):** 100% de Acurácia | Loss: 0.0000.
*Nossa CNN V2 customizada empatou com o benchmark de mercado, provando que a profundidade adicional e o ajuste fino do Softmax foram decisivos.*

## 🎬 5. Demonstração em Vídeo
Confira a explicação detalhada do projeto, análise de gráficos e demonstração prática no link abaixo:
👉 **[Link para o Vídeo de Apresentação (YouTube)]((https://youtu.be/bOZni4vVJX8)**

## 6. Conclusão
pós a realização de múltiplos experimentos e a análise das métricas de performance (Acurácia, Perda, Matriz de Confusão e Curvas de Aprendizado), a equipe técnica da **FarmTech Solutions** consolidou o seguinte diagnóstico para a expansão nas verticais de Saúde Animal e Segurança Patrimonial:

###6.1. **Comparativo de Detecção (YOLOv5)**


| Modelo | Performance Técnica | Viabilidade de Negócio |
| :--- | :--- | :--- |
| **YOLO Baseline** | Baixa.| Inadequado. | - |
| **YOLO 30 Épocas** | Média. | PoC Inicial. | - |
| **YOLO 60 Épocas** | Alta. | Recomendado. | - |


###6.2. **Comparativo de Classificação (Estudo de Ablação CNN)**

O teste cego realizado com imagens inéditas (Pasta `test`) revelou resultados de excelência, onde a métrica de desempate foi a Função de Perda (Loss):

- **VGG16 (Benchmark)**: Atingiu **100% de Acurácia e Loss de 0.0000**. Provou que o problema é perfeitamente solucionável com Transfer Learning. Nota-se que presença de poucas epocas para atingir uma acurácia de 100%

- **CNN V1 (Rasa):** Atingiu **100% de Acurácia** e um **Loss de 0.4748**. Embora assertiva, a arquitetura de apenas 1 blocos convolucionais carrega "hesitação" matemática, apresentando resultados distintos quando treinas com epocas diferentes

- **CNN V2 (Profunda):** Atingiu **100% de Acurácia** e **Loss de 0.0000**. Ao adicionarmos mais camadas `Conv2D()` e `MaxPooling`, nossa arquitetura própria empatou com o benchmark de mercado (VGG16), com números de parâmetros menores, possibilidade sua utilização em maquinas de menor porte para que ocorra uma classificação adequada.

###6.3. **Veredito para Produção**

Para a expansão da FarmTech Solutions, o veredito final do grupo é a utilização do **YOLOv5** treinado por **60 épocas**.

**Por que não usar apenas a CNN?**
Embora a nossa **CNN V2** tenha atingido valores matemáticos adequados na classificação, ela é "cega" quanto à localização. Em sistemas de segurança patrimonial (identificação de veículos em portarias) e saúde animal (rastreamento de pets), a **Consciência Espacial** fornecida pelas Bounding Boxes do YOLO é indispensável.

**Recomendação Final:**
O projeto está aprovado para a transição de Prova de Conceito (PoC) para o ambiente de produção. A robustez demonstrada nas matrizes de confusão e o erro zero nos testes inéditos garantem que a FarmTech Solutions possui agora uma tecnologia de Visão Computacional.

## 📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>
