# mkfilter.py - Guia Rápido

## Instalação

```bash
pip install numpy
```

## Duas Formas de Especificar Frequências

### Opção 1: Frequências em Hz (Recomendado! ✨)
```bash
-f <frequência_Hz> -s <taxa_amostragem_Hz>
```
**Mais intuitivo!** Você especifica as frequências reais em Hz.

### Opção 2: Alpha Normalizado (Tradicional)
```bash
-a <alpha>
```
Onde `alpha = frequência / taxa_amostragem`

## Uso Rápido

### 1. Filtro Butterworth Passa-Baixa (mais comum)

**Opção A: Usando frequências em Hz (MAIS FÁCIL! ✨)**
```bash
# Filtro de 4ª ordem, corte em 1000 Hz, taxa de amostragem 10000 Hz
python mkfilter.py -Bu -Lp -o 4 -f 1000 -s 10000
```

**Opção B: Usando alpha normalizado**
```bash
# Mesmo filtro usando alpha = fc/fs = 1000/10000 = 0.1
python mkfilter.py -Bu -Lp -o 4 -a 0.1
```

### 2. Gerar Código C

```bash
# Gerar código C diretamente com frequências em Hz
python mkfilter.py -Bu -Lp -o 4 -f 1000 -s 10000 -c
```

**Saída:**
```c
/* Digital filter designed by mkfilter.py */
#define NZEROS 4
#define NPOLES 4
#define GAIN   2.072820954e+02

static float xv[NZEROS+1], yv[NPOLES+1];

static float filterStep(float input)
{
  xv[0] = xv[1];
  xv[1] = xv[2];
  xv[2] = xv[3];
  xv[3] = xv[4];
  xv[4] = input / GAIN;

  yv[0] = yv[1];
  yv[1] = yv[2];
  yv[2] = yv[3];
  yv[3] = yv[4];
  yv[4] = (  1.0000000000 * xv[0])
           + (  4.0000000000 * xv[1])
           + (  6.0000000000 * xv[2])
           + (  4.0000000000 * xv[3])
           + (  1.0000000000 * xv[4])
           + ( -0.1873794924 * yv[0])
           + (  1.0546654059 * yv[1])
           + ( -2.3139884144 * yv[2])
           + (  2.3695130072 * yv[3]);
  return yv[4];
}
```

**Como usar no seu código C:**
```c
int main() {
    float input_signal[1000];
    float output_signal[1000];

    // ... preencher input_signal ...

    // Processar cada amostra
    for (int i = 0; i < 1000; i++) {
        output_signal[i] = filterStep(input_signal[i]);
    }

    return 0;
}
```

### 3. Outros Tipos de Filtros

**Passa-Alta (remove DC e baixas frequências):**
```bash
# Corta tudo abaixo de 500 Hz (fs = 8000 Hz)
python mkfilter.py -Bu -Hp -o 3 -f 500 -s 8000 -c
```

**Passa-Faixa (mantém apenas uma banda):**
```bash
# Mantém apenas 1000-3000 Hz (fs = 10000 Hz)
python mkfilter.py -Bu -Bp -o 4 -f 1000 3000 -s 10000 -c
```

**Rejeita-Faixa/Notch (remove uma banda):**
```bash
# Remove ruído de 60 Hz da rede elétrica (fs = 1000 Hz)
python mkfilter.py -Bu -Bs -o 2 -f 58 62 -s 1000 -c
```

**Chebyshev (transição mais abrupta, com ripple):**
```bash
# -1.0 dB de ripple, corte em 5 kHz (fs = 44.1 kHz)
python mkfilter.py -Ch -1.0 -Lp -o 4 -f 5000 -s 44100 -c
```

## Comparação de Filtros

### Butterworth (`-Bu`)
- ✅ Resposta plana na banda passante
- ✅ Fácil de usar
- ❌ Fase não-linear
- **Use quando**: Precisa de resposta uniforme em magnitude

### Bessel (`-Be`)
- ✅ Atraso de grupo constante (fase linear)
- ❌ Transição suave (roll-off lento)
- **Use quando**: Precisa preservar a forma de onda (áudio, telecomunicações)

### Chebyshev (`-Ch -1.0`)
- ✅ Transição mais abrupta
- ❌ Ripple na banda passante
- **Use quando**: Precisa de corte acentuado e ripple é aceitável

## Parâmetros Importantes

### Ordem do Filtro (`-o`)
- **Ordem 2-4**: Leve, transição suave, uso geral
- **Ordem 6-8**: Moderado, transição acentuada
- **Ordem 10+**: Pesado, transição muito abrupta

**Regra prática:** Comece com ordem 4, aumente se necessário.

### Alpha (`-a`)
- **Para Lowpass/Highpass**: um valor
  - `alpha = f_corner / f_sample`
- **Para Bandpass/Bandstop**: dois valores
  - `alpha1 = f_inferior / f_sample`
  - `alpha2 = f_superior / f_sample`

**Exemplos:**
- Taxa 8000 Hz, corte 1000 Hz → alpha = 0.125
- Taxa 44100 Hz, corte 5000 Hz → alpha = 0.113
- Taxa 1000 Hz, banda 100-300 Hz → alpha1=0.1, alpha2=0.3

## Opções Adicionais

```bash
-l              # Formato compacto (para pós-processamento)
-c              # Gera código C otimizado
--code-simple   # Gera código C com loops (mais legível)
-z              # Usa matched z-transform (para frequências baixas)
-w              # Desabilita pre-warping
```

## Exemplos Práticos

### Filtro Anti-Aliasing (antes de reduzir taxa de amostragem)
```bash
# Taxa atual 48kHz, vai reduzir para 16kHz
# Cortar em 8kHz (frequência de Nyquist da nova taxa)
python mkfilter.py -Bu -Lp -o 6 -a 0.1667 -c  # 8000/48000
```

### Remoção de DC Offset
```bash
# Passa-alta com corte muito baixo
python mkfilter.py -Bu -Hp -o 2 -a 0.001 -c
```

### Remoção de 60 Hz (ruído da rede elétrica)
```bash
# Taxa 1000 Hz, notch em 60 Hz
python mkfilter.py -Bu -Bs -o 2 -a 0.058 0.062 -c
```

### Extração de Graves (áudio)
```bash
# Taxa 44100 Hz, passa-baixa em 200 Hz
python mkfilter.py -Bu -Lp -o 4 -a 0.00453 -c
```

### Extração de Agudos (áudio)
```bash
# Taxa 44100 Hz, passa-alta em 5000 Hz
python mkfilter.py -Bu -Hp -o 4 -a 0.1134 -c
```

## Uso como Biblioteca Python

```python
from mkfilter import MkFilter, generate_c_code
import numpy as np

# Criar e projetar filtro
mkf = MkFilter()
xcoeffs, ycoeffs = mkf.design(
    filter_type='Bu',
    band_type='Lp',
    order=4,
    alpha1=0.1
)

# Aplicar ao sinal
def apply_filter(signal, xcoeffs, ycoeffs, gain):
    nzeros = len(xcoeffs) - 1
    npoles = len(ycoeffs) - 1
    xv = np.zeros(nzeros + 1)
    yv = np.zeros(npoles + 1)
    output = np.zeros(len(signal))

    for n, sample in enumerate(signal):
        xv[:-1] = xv[1:]
        xv[-1] = sample / gain
        yv[:-1] = yv[1:]
        yv[-1] = np.dot(xcoeffs, xv) + np.dot(ycoeffs[:-1], yv[:-1])
        output[n] = yv[-1]

    return output

# Usar
signal = np.random.randn(1000)
filtered = apply_filter(signal, xcoeffs, ycoeffs, mkf.get_gain())

# Gerar código C
c_code = generate_c_code(mkf)
print(c_code)
```

## Dicas Importantes

1. **Sempre normalize alpha corretamente**: `alpha = f / f_sample`
2. **Comece com ordem baixa** (2-4) e aumente se necessário
3. **Use Butterworth** para a maioria dos casos
4. **Teste antes de usar** em produção
5. **Inicialize os buffers** (`xv`, `yv`) com zeros

## Verificação Rápida

Para verificar se o filtro está correto, use a opção sem `-c` para ver detalhes:

```bash
python mkfilter.py -Bu -Lp -o 4 -a 0.1
```

Você verá:
- Polos e zeros no plano S e Z
- Ganho em DC, centro e alta frequência
- Equação de recorrência

## Ajuda

```bash
python mkfilter.py -h
```

## Mais Informações

- [README_PYTHON.md](README_PYTHON.md) - Documentação completa
- [example_usage.py](example_usage.py) - Exemplos com gráficos
- [mkfilter original](http://www-users.cs.york.ac.uk/~fisher/mkfilter)
