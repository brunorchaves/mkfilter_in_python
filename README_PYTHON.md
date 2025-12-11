# mkfilter.py - Python Digital Filter Designer

Implementação em Python do mkfilter, uma ferramenta para design de filtros digitais IIR (Infinite Impulse Response).

## Características

- **Tipos de Filtros**: Butterworth, Bessel, Chebyshev
- **Tipos de Banda**: Lowpass, Highpass, Bandpass, Bandstop
- **Transformações**: Bilinear Transform (BLT) ou Matched Z-Transform
- **Geração de Código C**: Gera código C pronto para copiar e colar

## Instalação

Requer Python 3.6+ e NumPy:

```bash
pip install numpy
```

## Uso Básico

### Sintaxe

```bash
python mkfilter.py [TIPO_FILTRO] [TIPO_BANDA] -o ORDEM -a ALPHA [ALPHA2] [OPÇÕES]
```

### Parâmetros Principais

**Tipo de Filtro:**
- `-Bu`: Butterworth (resposta plana na banda passante)
- `-Be`: Bessel (atraso de grupo constante)
- `-Ch RIPPLE`: Chebyshev (RIPPLE em dB, deve ser negativo, ex: -1.0)

**Tipo de Banda:**
- `-Lp`: Lowpass (passa-baixa)
- `-Hp`: Highpass (passa-alta)
- `-Bp`: Bandpass (passa-faixa)
- `-Bs`: Bandstop (rejeita-faixa / notch)

**Parâmetros:**
- `-o ORDEM`: Ordem do filtro (1-10)
- `-a ALPHA [ALPHA2]`: Frequência normalizada = f_corner / f_sample
  - Para Lp/Hp: um valor
  - Para Bp/Bs: dois valores (frequências inferior e superior)

**Opções de Transformação:**
- `-z`: Usa matched z-transform ao invés de bilinear transform
- `-w`: Desabilita pre-warping de frequências

**Opções de Saída:**
- `-l`: Saída compacta (formato compatível com gencode)
- `-c`, `--code`: Gera código C otimizado
- `--code-simple`: Gera código C simples com loops

## Exemplos

### 1. Filtro Butterworth Passa-Baixa

Filtro de 4ª ordem, frequência de corte em 1kHz com taxa de amostragem de 10kHz:

```bash
python mkfilter.py -Bu -Lp -o 4 -a 0.1
```

**Alpha = 0.1** porque 1000 Hz / 10000 Hz = 0.1

### 2. Filtro Butterworth Passa-Alta

Filtro de 3ª ordem, frequência de corte em 500Hz com taxa de amostragem de 8kHz:

```bash
python mkfilter.py -Bu -Hp -o 3 -a 0.0625
```

### 3. Filtro Butterworth Passa-Faixa

Filtro de 6ª ordem, passa-faixa de 1kHz a 2kHz com taxa de amostragem de 10kHz:

```bash
python mkfilter.py -Bu -Bp -o 6 -a 0.1 0.2
```

### 4. Filtro Chebyshev com Ripple

Filtro de 5ª ordem com -1dB de ripple na banda passante:

```bash
python mkfilter.py -Ch -1.0 -Lp -o 5 -a 0.15
```

### 5. Gerar Código C

Para gerar código C pronto para usar:

```bash
python mkfilter.py -Bu -Lp -o 4 -a 0.1 -c
```

Saída:
```c
/* Digital filter designed by mkfilter.py */
/* Bu Lp filter, order 4 */
/* alpha1=0.1, alpha2=0.1 */

#define NZEROS 4
#define NPOLES 4
#define GAIN   1.000000000e+00

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
  yv[4] = ( 0.0004913149 * xv[0])
           + ( 0.0019652596 * xv[1])
           + ( 0.0029478894 * xv[2])
           + ( 0.0019652596 * xv[3])
           + ( 0.0004913149 * xv[4])
           + ( -0.8008026028 * yv[0])
           + ( 3.1248888493 * yv[1])
           + ( -4.5805143348 * yv[2])
           + ( 3.0607892997 * yv[3]);
  return yv[4];
}
```

### 6. Formato Compacto para Pós-Processamento

```bash
python mkfilter.py -Bu -Lp -o 4 -a 0.1 -l
```

Saída compacta:
```
G  = 1.0000000000e+00
NZ = 4
  4.9131488438e-04
  1.9652595375e-03
  2.9478893063e-03
  1.9652595375e-03
  4.9131488438e-04
NP = 4
 -8.0080260276e-01
  3.1248888493e+00
 -4.5805143348e+00
  3.0607892997e+00
 -1.0000000000e+00
```

## Como Funciona

### 1. Design no Plano S (Analógico)

O filtro começa como um protótipo analógico passa-baixa no plano S (Laplace):

- **Butterworth**: Polos distribuídos uniformemente em semicírculo
- **Bessel**: Polos da tabela pré-calculada (atraso de grupo constante)
- **Chebyshev**: Modificação dos polos Butterworth para ripple especificado

### 2. Normalização

Transforma o protótipo passa-baixa para o tipo de filtro desejado:

- **Lowpass**: Escala os polos por ω₁
- **Highpass**: Inversão LP→HP
- **Bandpass**: Transforma cada polo em par de polos complexos conjugados
- **Bandstop**: Similar ao bandpass mas com zeros adicionais

### 3. Pre-warping (opcional)

Para a transformada bilinear, compensa a distorção de frequência:

```
ω_warped = tan(π × f_corner/f_sample) / π
```

### 4. Transformação para Plano Z (Digital)

**Bilinear Transform (padrão):**
```
z = (2 + s) / (2 - s)
```

**Matched Z-Transform (opção `-z`):**
```
z = exp(s)
```

### 5. Expansão de Polinômios

Converte polos e zeros em coeficientes da equação de recorrência:

```
y[n] = Σ(xcoeff[i] × x[n-i]) + Σ(ycoeff[i] × y[n-i])
```

## Usando o Código C Gerado

### Exemplo de Integração

```c
#include <stdio.h>

// Cole aqui o código gerado por mkfilter.py
#define NZEROS 4
#define NPOLES 4
#define GAIN   1.000000000e+00

static float xv[NZEROS+1], yv[NPOLES+1];

static float filterStep(float input)
{
  // ... código gerado ...
}

// Função para processar um buffer de dados
void processBuffer(float *input, float *output, int length)
{
  for (int i = 0; i < length; i++) {
    output[i] = filterStep(input[i]);
  }
}

int main()
{
  // Exemplo: sinal de teste
  float input[100];
  float output[100];

  // Gera sinal de entrada (ex: senoide + ruído)
  for (int i = 0; i < 100; i++) {
    input[i] = sin(2.0 * 3.14159 * 0.05 * i);  // 0.05 = 5% da taxa de amostragem
  }

  // Processa
  processBuffer(input, output, 100);

  // Exibe resultado
  for (int i = 0; i < 100; i++) {
    printf("%f %f\n", input[i], output[i]);
  }

  return 0;
}
```

### Para Sistemas Embedded

O código gerado é otimizado para microcontroladores:

- Usa `float` ao invés de `double` (mais eficiente em ARM Cortex-M)
- Não usa alocação dinâmica
- Arrays estáticos de tamanho fixo
- Operações simples (multiplicação e adição)

## Usando como Biblioteca Python

```python
from mkfilter import MkFilter, generate_c_code

# Criar filtro
mkf = MkFilter()

# Butterworth passa-baixa de 4ª ordem
xcoeffs, ycoeffs = mkf.design(
    filter_type='Bu',  # Butterworth
    band_type='Lp',    # Lowpass
    order=4,
    alpha1=0.1         # f_corner / f_sample
)

# Obter coeficientes
print("Coeficientes X (entrada):", xcoeffs)
print("Coeficientes Y (saída):", ycoeffs)

# Ganho na banda passante
gain = mkf.get_gain()
print("Ganho:", gain)

# Gerar código C
c_code = generate_c_code(mkf)
print(c_code)

# Implementar filtro em Python
import numpy as np

def apply_filter(signal, xcoeffs, ycoeffs, gain):
    """Aplica o filtro IIR ao sinal"""
    nzeros = len(xcoeffs) - 1
    npoles = len(ycoeffs) - 1

    # Buffers
    xv = np.zeros(nzeros + 1)
    yv = np.zeros(npoles + 1)
    output = np.zeros(len(signal))

    for n, sample in enumerate(signal):
        # Shift x values
        xv[:-1] = xv[1:]
        xv[-1] = sample / gain

        # Shift y values
        yv[:-1] = yv[1:]

        # Compute output
        yv[-1] = np.dot(xcoeffs, xv) + np.dot(ycoeffs[:-1], yv[:-1])
        output[n] = yv[-1]

    return output

# Exemplo de uso
import matplotlib.pyplot as plt

# Gerar sinal de teste: senoide de 0.05*fs + senoide de 0.4*fs
fs = 1000  # Taxa de amostragem
t = np.linspace(0, 1, fs)
signal = np.sin(2*np.pi*50*t) + 0.3*np.sin(2*np.pi*400*t)

# Aplicar filtro passa-baixa (corte em 0.1*fs = 100 Hz)
filtered = apply_filter(signal, xcoeffs, ycoeffs, gain)

# Plotar
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(t[:200], signal[:200], label='Original')
plt.plot(t[:200], filtered[:200], label='Filtrado')
plt.xlabel('Tempo (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.title('Sinal no Tempo')

plt.subplot(1, 2, 2)
plt.magnitude_spectrum(signal, Fs=fs, label='Original')
plt.magnitude_spectrum(filtered, Fs=fs, label='Filtrado')
plt.legend()
plt.title('Espectro de Frequência')
plt.tight_layout()
plt.show()
```

## Comparação de Tipos de Filtros

### Butterworth (-Bu)
- **Vantagem**: Resposta plana na banda passante
- **Desvantagem**: Fase não-linear
- **Uso**: Aplicações gerais onde magnitude uniforme é importante

### Bessel (-Be)
- **Vantagem**: Atraso de grupo constante (fase linear)
- **Desvantagem**: Transição mais suave (roll-off lento)
- **Uso**: Áudio, telecomunicações, onde preservar a forma de onda é crítico

### Chebyshev (-Ch)
- **Vantagem**: Transição mais abrupta que Butterworth
- **Desvantagem**: Ripple na banda passante
- **Uso**: Quando é necessária transição acentuada e ripple é aceitável

## Dicas

1. **Escolha de Alpha**: Para frequência de corte fc e taxa de amostragem fs:
   ```
   alpha = fc / fs
   ```

2. **Ordem do Filtro**:
   - Ordem maior = transição mais abrupta
   - Ordem maior = mais computação
   - Comece com ordem 2-4, aumente se necessário

3. **Estabilidade**:
   - Todos os polos devem estar dentro do círculo unitário no plano Z
   - O programa verifica automaticamente

4. **Pre-warping**:
   - Use sempre (padrão) com bilinear transform
   - Desabilite apenas se souber o que está fazendo

5. **Matched Z-Transform**:
   - Use apenas para frequências baixas (alpha < 0.1)
   - Bilinear é mais estável em geral

## Diferenças em Relação ao mkfilter Original

1. **Sintaxe de argumentos**: Mantida compatível
2. **Linguagem**: Python ao invés de C++
3. **Dependência**: Requer NumPy
4. **Precisão**: Usa `float64` (C usa `double`)
5. **Código gerado**: Otimizado para uso moderno

## Referências

- Original mkfilter: http://www-users.cs.york.ac.uk/~fisher/mkfilter
- A.J. Fisher, University of York
- "Digital Filters" by DeFatta et al.

## Licença

Este código é baseado no mkfilter original de A.J. Fisher.
Implementação Python: 2024

## Autor

Portado para Python mantendo compatibilidade com mkfilter original.
