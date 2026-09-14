# Project Overview --- Voltix

## 1. Visão geral

A **Voltix** é uma plataforma de e-commerce especializada na
comercialização de produtos de tecnologia, como computadores,
componentes de hardware, periféricos e acessórios.

A plataforma será composta por uma área de comércio eletrônico destinada
aos clientes e uma área interna para gerenciamento da operação.

A área interna contará com funcionalidades administrativas e um **CRM
(Customer Relationship Management) integrado**, permitindo que
funcionários autorizados acompanhem informações dos clientes, seus
pedidos, histórico de compras e atendimentos realizados.

A proposta da Voltix é integrar a operação de vendas e o relacionamento
com os clientes em uma única plataforma.

------------------------------------------------------------------------

## 2. Problema

Uma operação de e-commerce envolve diferentes informações relacionadas a
produtos, clientes, pedidos e atendimentos.

Quando as informações comerciais e de relacionamento com o cliente não
estão integradas, torna-se mais difícil acompanhar sua jornada,
consultar seu histórico de compras e manter um registro organizado dos
atendimentos realizados.

A Voltix busca solucionar esse problema por meio da integração entre uma
plataforma de e-commerce e um CRM, centralizando informações importantes
da operação e do relacionamento com os clientes.

------------------------------------------------------------------------

## 3. Objetivos

### Objetivo geral

Desenvolver uma plataforma de e-commerce de tecnologia integrada a um
CRM para gerenciamento de vendas, clientes e relacionamento.

### Objetivos específicos

-   permitir o cadastro e autenticação de clientes;
-   disponibilizar um catálogo de produtos de tecnologia;
-   permitir a navegação e pesquisa de produtos;
-   permitir a utilização de um carrinho de compras;
-   permitir a realização e acompanhamento de pedidos;
-   disponibilizar ao cliente seu histórico de compras;
-   permitir o gerenciamento de produtos e categorias;
-   permitir o acompanhamento dos pedidos pela equipe interna;
-   centralizar informações dos clientes em um CRM;
-   disponibilizar o histórico de compras dos clientes no CRM;
-   permitir o registro e consulta de atendimentos;
-   facilitar o acompanhamento do relacionamento entre a empresa e seus
    clientes.

------------------------------------------------------------------------

## 4. Público-alvo / usuários

A Voltix possuirá inicialmente três tipos principais de usuários:

### 4.1 Cliente

Representa o consumidor que utiliza o e-commerce para pesquisar e
adquirir produtos.

O cliente poderá:

-   criar uma conta;
-   autenticar-se na plataforma;
-   consultar produtos;
-   pesquisar produtos;
-   navegar pelas categorias;
-   adicionar e remover produtos do carrinho;
-   realizar pedidos;
-   acompanhar seus pedidos;
-   consultar seu histórico de compras.

### 4.2 Funcionário

Representa o usuário interno responsável pelo acompanhamento da operação
e relacionamento com os clientes.

De acordo com suas permissões, poderá:

-   consultar clientes;
-   consultar pedidos;
-   acompanhar informações relacionadas às vendas;
-   acessar informações disponíveis no CRM;
-   visualizar o histórico de compras dos clientes;
-   registrar atendimentos;
-   consultar o histórico de atendimentos;
-   registrar informações relevantes sobre o relacionamento com o
    cliente.

### 4.3 Administrador

Representa o usuário com permissões administrativas sobre a plataforma.

Poderá:

-   cadastrar e gerenciar produtos;
-   cadastrar e gerenciar categorias;
-   acompanhar e gerenciar pedidos;
-   consultar clientes;
-   acessar as funcionalidades administrativas do CRM;
-   gerenciar informações necessárias à operação da plataforma.

As permissões específicas de cada tipo de usuário serão detalhadas
posteriormente nas especificações correspondentes.

------------------------------------------------------------------------

## 5. Escopo

### 5.1 Dentro do escopo inicial

O escopo inicial da Voltix contempla:

-   cadastro e autenticação de clientes;
-   catálogo de produtos;
-   pesquisa de produtos;
-   categorias de produtos;
-   carrinho de compras;
-   criação de pedidos;
-   acompanhamento de pedidos;
-   histórico de compras;
-   painel administrativo;
-   gerenciamento de produtos;
-   gerenciamento de categorias;
-   gerenciamento de pedidos;
-   CRM de clientes;
-   histórico de compras integrado ao CRM;
-   registro e histórico de atendimentos;
-   informações de relacionamento com clientes.

### 5.2 Fora do escopo inicial

Inicialmente, não fazem parte do escopo:

-   marketplace com vendedores externos;
-   integração fiscal para emissão real de documentos fiscais;
-   integração real com transportadoras;
-   sistema avançado de recomendação utilizando inteligência artificial;
-   chatbot automatizado;
-   aplicativo móvel nativo.

Essas funcionalidades poderão ser avaliadas futuramente, mas não fazem
parte do escopo inicial do projeto.

------------------------------------------------------------------------

## 6. Principais funcionalidades

### 6.1 E-commerce

A área de e-commerce deverá permitir:

-   cadastro e autenticação de clientes;
-   visualização do catálogo;
-   pesquisa de produtos;
-   navegação por categorias;
-   visualização das informações dos produtos;
-   gerenciamento do carrinho de compras;
-   criação de pedidos;
-   acompanhamento dos pedidos;
-   consulta ao histórico de compras.

### 6.2 Área administrativa

A área administrativa deverá permitir:

-   cadastro e gerenciamento de produtos;
-   gerenciamento de categorias;
-   consulta e gerenciamento de pedidos;
-   consulta aos clientes cadastrados;
-   acesso às funcionalidades administrativas de acordo com as
    permissões do usuário.

### 6.3 CRM

O CRM deverá permitir:

-   consultar informações dos clientes;
-   visualizar o histórico de compras;
-   consultar pedidos associados ao cliente;
-   registrar atendimentos;
-   consultar o histórico de atendimentos;
-   registrar informações relevantes sobre o relacionamento com o
    cliente.

Funcionalidades mais específicas do CRM poderão ser adicionadas
posteriormente por meio das mudanças incrementais do projeto.

------------------------------------------------------------------------

## 7. Requisitos e restrições importantes

A Voltix deverá manter uma separação clara entre as funcionalidades
destinadas aos clientes e as funcionalidades internas da plataforma.

Usuários deverão acessar somente as funcionalidades compatíveis com suas
permissões.

Clientes não poderão acessar recursos administrativos nem informações
internas do CRM.

As informações compartilhadas entre o e-commerce e o CRM deverão
permanecer consistentes.

O sistema deverá preservar a integridade das informações relacionadas a
clientes, produtos, pedidos e atendimentos.

Novas funcionalidades que alterem significativamente o escopo ou a
arquitetura deverão ser avaliadas antes de serem incorporadas ao
projeto.

------------------------------------------------------------------------

## 8. Arquitetura tecnológica

A Voltix utilizará uma arquitetura que separa a interface da aplicação
das funcionalidades de backend e persistência de dados.

### Frontend

O frontend será desenvolvido utilizando **Reflex**, opção escolhida pelo
grupo entre as tecnologias disponibilizadas para a disciplina. O Reflex
será responsável pela construção das interfaces utilizadas pelos
clientes e pelos usuários internos da plataforma.

### Backend e dados

O backend utilizará **Xano**, com **XanoScript** para definição e
implementação das funcionalidades suportadas pela plataforma, incluindo
APIs, lógica de negócio e operações relacionadas aos dados.

O armazenamento e o gerenciamento dos dados serão realizados por meio da
infraestrutura disponibilizada pelo Xano.

### Comunicação

O frontend desenvolvido em Reflex deverá se comunicar com os recursos
disponibilizados pelo backend no Xano. Os detalhes específicos das
integrações serão definidos nas especificações e mudanças
correspondentes durante o desenvolvimento.

### Versionamento

O projeto utilizará **Git** para controle de versão e **GitHub** como
repositório remoto para armazenamento e colaboração entre os integrantes
do grupo.

### Desenvolvimento orientado por especificações

O **OpenSpec** será utilizado para fornecer contexto aos agentes de
Inteligência Artificial e organizar o planejamento e o desenvolvimento
incremental das mudanças do projeto.

Decisões arquiteturais mais específicas poderão ser definidas durante a
evolução do projeto e deverão ser documentadas quando passarem a fazer
parte das regras permanentes da Voltix.

------------------------------------------------------------------------

## 9. Princípios de desenvolvimento

O desenvolvimento da Voltix deverá seguir os seguintes princípios:

-   desenvolvimento incremental;
-   separação clara de responsabilidades;
-   reutilização de código e componentes quando apropriado;
-   evitar duplicação desnecessária;
-   preservar a consistência entre funcionalidades relacionadas;
-   documentar decisões relevantes;
-   revisar mudanças antes da implementação;
-   evitar alterações não relacionadas à mudança atual;
-   utilizar OpenSpec para planejar e acompanhar mudanças relevantes.

------------------------------------------------------------------------

## 10. Segurança e integridade

A Voltix deverá considerar a segurança e a integridade das informações
durante seu desenvolvimento.

As regras de autorização deverão ser aplicadas no backend, não
dependendo exclusivamente das restrições apresentadas pela interface.

Informações internas do CRM e recursos administrativos deverão ser
acessíveis somente por usuários autorizados.

Informações relacionadas a clientes deverão ser acessadas apenas quando
necessárias para as funcionalidades autorizadas.

Operações envolvendo clientes, produtos, pedidos e atendimentos deverão
preservar a consistência dos dados.

Requisitos específicos de segurança deverão ser detalhados nas
especificações das funcionalidades correspondentes quando necessário.

------------------------------------------------------------------------

## 11. Estratégia de desenvolvimento

A Voltix será desenvolvida incrementalmente utilizando OpenSpec.

Antes da implementação, o projeto deverá ser analisado para identificar
suas principais funcionalidades, dependências e possíveis riscos.

As funcionalidades serão divididas em mudanças menores e verificáveis.

Cada mudança relevante deverá passar pelo processo de especificação,
revisão e implementação definido para o projeto.

O desenvolvimento não deverá tentar implementar toda a plataforma de uma
única vez.

Após a conclusão e validação de uma mudança, ela poderá ser consolidada
antes do início das próximas mudanças.

------------------------------------------------------------------------

## 12. Fonte de verdade e documentação

A documentação da Voltix será utilizada para manter o contexto global do
projeto e orientar seu desenvolvimento.

Os principais documentos serão:

-   `docs/project-overview.md`: apresenta a visão geral do projeto;
-   `docs/domain-model.md`: descreve os principais conceitos e
    relacionamentos do domínio;
-   `AGENTS.md`: estabelece as instruções para os agentes de
    Inteligência Artificial que trabalharem no projeto;
-   `openspec/config.yaml`: fornece contexto e regras aos workflows do
    OpenSpec;
-   `openspec/specs/`: mantém o comportamento consolidado do sistema;
-   `openspec/changes/`: mantém as mudanças que estiverem sendo
    planejadas ou implementadas.

Mudanças relevantes no escopo, domínio, arquitetura ou regras
permanentes do projeto deverão ser refletidas na documentação
correspondente.
