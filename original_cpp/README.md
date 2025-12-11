# Implementação Original em C++

Esta pasta contém os arquivos originais do mkfilter em C++ de A.J. Fisher (University of York).

## Conteúdo

- **src/** - Código-fonte C++ original
  - `mkfilter.cpp` - Programa principal de design de filtros
  - `gencode.cpp` - Gerador de código C
  - `complex.cpp` - Aritmética complexa
  - `mkshape.cpp` - Design de filtros FIR
  - `mkaverage.cpp` - Filtros de média móvel
  - `readdata.cpp` - Leitura de dados

- **Makefile** - Arquivo de build para compilar os programas C++

- **doc.pdf** - Documentação original completa
- **doc.ps** - Documentação em PostScript
- **doc.al** - Arquivo de documentação

## Como Compilar (Opcional)

Se você quiser compilar e usar a versão original em C++:

```bash
cd original_cpp
make
```

Isso gerará os executáveis:
- `mkfilter` - Designer de filtros IIR
- `gencode` - Gerador de código C
- `mkshape` - Designer de filtros FIR
- `mkaverage` - Filtros de média móvel

## Por Que Usar a Versão Python?

A versão Python no diretório raiz ([../mkfilter.py](../mkfilter.py)) oferece:

✅ **Não precisa compilar** - funciona imediatamente
✅ **Mesma funcionalidade** - resultados idênticos
✅ **Mais fácil de integrar** - use como biblioteca Python
✅ **Gera código C** - igual ao gencode original
✅ **Multiplataforma** - Windows, Linux, macOS

## Quando Usar a Versão C++?

Use a versão C++ original se:
- Você precisa de máxima performance para design de muitos filtros
- Você está trabalhando em um ambiente sem Python
- Você quer comparar com a implementação original
- Você está contribuindo para o projeto original

## Referências

- **Projeto original**: http://www-users.cs.york.ac.uk/~fisher/mkfilter
- **Autor**: A.J. Fisher, University of York
- **Email**: fisher@minster.york.ac.uk

## Nota

Estes arquivos foram movidos para esta pasta para manter o diretório raiz limpo e focado na implementação Python. A implementação Python é 100% compatível com esta versão C++.
