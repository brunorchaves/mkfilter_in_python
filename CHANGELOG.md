# Changelog - mkfilter.py

## [1.1.0] - 2024-12-11

### Adicionado ✨
- **Especificação de frequências em Hz**: Agora você pode usar `-f` e `-s` para especificar frequências diretamente em Hz, sem precisar calcular alpha manualmente!

```bash
# Antes (ainda funciona)
python mkfilter.py -Bu -Lp -o 4 -a 0.1

# Agora (MAIS FÁCIL!)
python mkfilter.py -Bu -Lp -o 4 -f 1000 -s 10000
```

### Exemplos da Nova Funcionalidade

**Lowpass:**
```bash
# Corte em 1 kHz, amostragem 10 kHz
python mkfilter.py -Bu -Lp -o 4 -f 1000 -s 10000 -c
```

**Highpass:**
```bash
# Corte em 500 Hz, amostragem 8 kHz
python mkfilter.py -Bu -Hp -o 3 -f 500 -s 8000 -c
```

**Bandpass:**
```bash
# Passa apenas 1-3 kHz, amostragem 10 kHz
python mkfilter.py -Bu -Bp -o 4 -f 1000 3000 -s 10000 -c
```

**Notch (eliminar 60 Hz):**
```bash
# Remove 60 Hz ± 2 Hz, amostragem 1 kHz
python mkfilter.py -Bu -Bs -o 2 -f 58 62 -s 1000 -c
```

### Parâmetros

| Parâmetro | Descrição |
|-----------|-----------|
| `-f <freq>` | Frequência de corte em Hz |
| `-f <f1> <f2>` | Frequências inferior e superior (para BP/BS) |
| `-s <fs>` | Taxa de amostragem em Hz |
| `-a <alpha>` | **Forma antiga** - alpha normalizado (ainda funciona) |

### Compatibilidade

✅ **100% retrocompatível** - A opção `-a` continua funcionando normalmente
✅ **Resultados idênticos** - Apenas a interface mudou, a matemática é a mesma
✅ **Sem breaking changes** - Código existente continua funcionando

---

## [1.0.0] - 2024-12-11

### Inicial 🎉

- Implementação completa do mkfilter em Python
- Suporte a filtros Butterworth, Bessel e Chebyshev
- Tipos: Lowpass, Highpass, Bandpass, Bandstop
- Transformada Bilinear (BLT) com pre-warping
- Matched Z-Transform
- Geração automática de código C
- 100% compatível com mkfilter original
- 6 testes automatizados (todos passam ✅)
- Documentação completa
- Exemplos práticos
