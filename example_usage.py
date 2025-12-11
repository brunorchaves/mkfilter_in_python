#!/usr/bin/env python3
"""
Exemplos de uso do mkfilter.py
Demonstra diferentes tipos de filtros e como aplicá-los a sinais
"""

import numpy as np
import matplotlib.pyplot as plt
from mkfilter import MkFilter, generate_c_code


def apply_filter(signal, mkf):
    """
    Aplica o filtro IIR ao sinal usando os coeficientes calculados

    Args:
        signal: Array numpy com o sinal de entrada
        mkf: Objeto MkFilter com o filtro já projetado

    Returns:
        Array numpy com o sinal filtrado
    """
    xcoeffs = mkf.xcoeffs
    ycoeffs = mkf.ycoeffs
    gain = mkf.get_gain()

    nzeros = len(xcoeffs) - 1
    npoles = len(ycoeffs) - 1

    # Buffers de estado
    xv = np.zeros(nzeros + 1)
    yv = np.zeros(npoles + 1)
    output = np.zeros(len(signal))

    # Processa cada amostra
    for n, sample in enumerate(signal):
        # Shift x values (entrada)
        xv[:-1] = xv[1:]
        xv[-1] = sample / gain

        # Shift y values (saída)
        yv[:-1] = yv[1:]

        # Compute output usando equação de recorrência
        yv[-1] = np.dot(xcoeffs, xv) + np.dot(ycoeffs[:-1], yv[:-1])
        output[n] = yv[-1]

    return output


def example1_lowpass():
    """Exemplo 1: Filtro Butterworth Passa-Baixa"""
    print("=" * 70)
    print("EXEMPLO 1: Filtro Butterworth Passa-Baixa")
    print("=" * 70)

    # Criar filtro
    mkf = MkFilter()
    mkf.design(
        filter_type='Bu',  # Butterworth
        band_type='Lp',    # Lowpass
        order=4,           # Ordem 4
        alpha1=0.1         # Corte em 10% da taxa de amostragem
    )

    # Imprimir resumo
    print("\nResumo do Filtro:")
    print(f"Tipo: Butterworth Lowpass, Ordem: 4")
    print(f"Frequência normalizada: 0.1 (se fs=1000Hz, fc=100Hz)")
    print(f"Ganho: {mkf.get_gain():.6f}")

    print("\nCoeficientes X (entrada):")
    for i, c in enumerate(mkf.xcoeffs):
        print(f"  x[{i}]: {c:15.10f}")

    print("\nCoeficientes Y (saída):")
    for i, c in enumerate(mkf.ycoeffs[:-1]):
        print(f"  y[{i}]: {c:15.10f}")

    # Gerar sinal de teste: soma de senoides
    fs = 1000  # Taxa de amostragem
    t = np.linspace(0, 2, 2 * fs, endpoint=False)

    # Sinal = 50 Hz (dentro da banda) + 400 Hz (fora da banda)
    signal = np.sin(2*np.pi*50*t) + 0.5*np.sin(2*np.pi*400*t)

    # Aplicar filtro
    filtered = apply_filter(signal, mkf)

    # Plotar resultado
    plt.figure(figsize=(14, 8))

    # Sinal no tempo
    plt.subplot(2, 2, 1)
    plt.plot(t[:500], signal[:500], 'b-', alpha=0.7, label='Original')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Amplitude')
    plt.title('Sinal Original (primeiros 0.5s)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 2, 2)
    plt.plot(t[:500], filtered[:500], 'r-', alpha=0.7, label='Filtrado')
    plt.xlabel('Tempo (s)')
    plt.ylabel('Amplitude')
    plt.title('Sinal Filtrado (primeiros 0.5s)')
    plt.legend()
    plt.grid(True, alpha=0.3)

    # FFT
    plt.subplot(2, 2, 3)
    fft_orig = np.fft.rfft(signal)
    freqs = np.fft.rfftfreq(len(signal), 1/fs)
    plt.plot(freqs, 20*np.log10(np.abs(fft_orig) + 1e-10), 'b-', alpha=0.7)
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title('Espectro - Original')
    plt.xlim([0, 500])
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 2, 4)
    fft_filt = np.fft.rfft(filtered)
    plt.plot(freqs, 20*np.log10(np.abs(fft_filt) + 1e-10), 'r-', alpha=0.7)
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title('Espectro - Filtrado')
    plt.xlim([0, 500])
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('example1_lowpass.png', dpi=150)
    print("\nGráfico salvo como: example1_lowpass.png")

    # Gerar código C
    print("\n" + "=" * 70)
    print("Código C Gerado:")
    print("=" * 70)
    print(generate_c_code(mkf))


def example2_highpass():
    """Exemplo 2: Filtro Butterworth Passa-Alta"""
    print("\n\n" + "=" * 70)
    print("EXEMPLO 2: Filtro Butterworth Passa-Alta")
    print("=" * 70)

    mkf = MkFilter()
    mkf.design(
        filter_type='Bu',
        band_type='Hp',
        order=3,
        alpha1=0.2  # Corte em 20% da taxa de amostragem
    )

    print(f"\nGanho: {mkf.get_gain():.6f}")

    # Sinal de teste: DC + baixa frequência + alta frequência
    fs = 1000
    t = np.linspace(0, 2, 2 * fs, endpoint=False)
    signal = 1.0 + np.sin(2*np.pi*50*t) + 0.5*np.sin(2*np.pi*350*t)

    filtered = apply_filter(signal, mkf)

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(t[:500], signal[:500], label='Original', alpha=0.7)
    plt.plot(t[:500], filtered[:500], label='Filtrado', alpha=0.7)
    plt.xlabel('Tempo (s)')
    plt.ylabel('Amplitude')
    plt.title('Highpass: Remove DC e baixas frequências')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    fft_orig = np.fft.rfft(signal)
    fft_filt = np.fft.rfft(filtered)
    freqs = np.fft.rfftfreq(len(signal), 1/fs)
    plt.plot(freqs, 20*np.log10(np.abs(fft_orig) + 1e-10), label='Original', alpha=0.7)
    plt.plot(freqs, 20*np.log10(np.abs(fft_filt) + 1e-10), label='Filtrado', alpha=0.7)
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title('Espectro')
    plt.xlim([0, 500])
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('example2_highpass.png', dpi=150)
    print("Gráfico salvo como: example2_highpass.png")


def example3_bandpass():
    """Exemplo 3: Filtro Butterworth Passa-Faixa"""
    print("\n\n" + "=" * 70)
    print("EXEMPLO 3: Filtro Butterworth Passa-Faixa")
    print("=" * 70)

    mkf = MkFilter()
    mkf.design(
        filter_type='Bu',
        band_type='Bp',
        order=4,
        alpha1=0.15,  # Frequência inferior
        alpha2=0.25   # Frequência superior
    )

    print(f"\nGanho: {mkf.get_gain():.6f}")
    print(f"Banda passante: 0.15 a 0.25 (150Hz a 250Hz se fs=1000Hz)")

    # Sinal com múltiplas frequências
    fs = 1000
    t = np.linspace(0, 2, 2 * fs, endpoint=False)
    signal = (np.sin(2*np.pi*50*t) +      # 50 Hz - abaixo da banda
              np.sin(2*np.pi*200*t) +      # 200 Hz - dentro da banda
              np.sin(2*np.pi*400*t))       # 400 Hz - acima da banda

    filtered = apply_filter(signal, mkf)

    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.plot(t[:500], signal[:500], label='Original (50+200+400 Hz)', alpha=0.7)
    plt.plot(t[:500], filtered[:500], label='Filtrado (~200 Hz)', alpha=0.7)
    plt.xlabel('Tempo (s)')
    plt.ylabel('Amplitude')
    plt.title('Bandpass: Passa apenas 150-250 Hz')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    fft_orig = np.fft.rfft(signal)
    fft_filt = np.fft.rfft(filtered)
    freqs = np.fft.rfftfreq(len(signal), 1/fs)
    plt.plot(freqs, 20*np.log10(np.abs(fft_orig) + 1e-10), label='Original', alpha=0.7)
    plt.plot(freqs, 20*np.log10(np.abs(fft_filt) + 1e-10), label='Filtrado', alpha=0.7)
    plt.axvline(150, color='g', linestyle='--', alpha=0.5, label='Banda')
    plt.axvline(250, color='g', linestyle='--', alpha=0.5)
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title('Espectro')
    plt.xlim([0, 500])
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('example3_bandpass.png', dpi=150)
    print("Gráfico salvo como: example3_bandpass.png")


def example4_chebyshev():
    """Exemplo 4: Comparação Butterworth vs Chebyshev"""
    print("\n\n" + "=" * 70)
    print("EXEMPLO 4: Butterworth vs Chebyshev")
    print("=" * 70)

    # Butterworth
    mkf_bu = MkFilter()
    mkf_bu.design(filter_type='Bu', band_type='Lp', order=4, alpha1=0.2)

    # Chebyshev com -1 dB ripple
    mkf_ch = MkFilter()
    mkf_ch.design(filter_type='Ch', band_type='Lp', order=4, alpha1=0.2, chebrip=-1.0)

    # Sinal de teste
    fs = 1000
    t = np.linspace(0, 2, 2 * fs, endpoint=False)

    # Sweep logarítmico de frequências
    from scipy.signal import chirp
    signal = chirp(t, f0=10, f1=500, t1=2, method='logarithmic')

    filtered_bu = apply_filter(signal, mkf_bu)
    filtered_ch = apply_filter(signal, mkf_ch)

    plt.figure(figsize=(12, 5))

    # Resposta em frequência
    plt.subplot(1, 2, 1)
    fft_bu = np.fft.rfft(filtered_bu)
    fft_ch = np.fft.rfft(filtered_ch)
    freqs = np.fft.rfftfreq(len(signal), 1/fs)

    plt.plot(freqs, 20*np.log10(np.abs(fft_bu) + 1e-10), label='Butterworth', alpha=0.7)
    plt.plot(freqs, 20*np.log10(np.abs(fft_ch) + 1e-10), label='Chebyshev -1dB', alpha=0.7)
    plt.axvline(200, color='r', linestyle='--', alpha=0.5, label='Corte (200 Hz)')
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title('Resposta em Frequência')
    plt.xlim([0, 400])
    plt.ylim([-80, 10])
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Zoom na banda passante
    plt.subplot(1, 2, 2)
    plt.plot(freqs, 20*np.log10(np.abs(fft_bu) + 1e-10), label='Butterworth', alpha=0.7)
    plt.plot(freqs, 20*np.log10(np.abs(fft_ch) + 1e-10), label='Chebyshev -1dB', alpha=0.7)
    plt.axhline(-1, color='r', linestyle=':', alpha=0.5, label='Ripple -1dB')
    plt.xlabel('Frequência (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title('Zoom: Banda Passante (note o ripple)')
    plt.xlim([0, 200])
    plt.ylim([-3, 1])
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('example4_comparison.png', dpi=150)
    print("Gráfico salvo como: example4_comparison.png")

    print("\nObservações:")
    print("- Butterworth: Resposta plana na banda passante")
    print("- Chebyshev: Transição mais abrupta, mas com ripple de -1dB")


def example5_frequency_response():
    """Exemplo 5: Resposta em Frequência de Diferentes Ordens"""
    print("\n\n" + "=" * 70)
    print("EXEMPLO 5: Efeito da Ordem do Filtro")
    print("=" * 70)

    fs = 1000
    t = np.linspace(0, 2, 2 * fs, endpoint=False)

    # Impulso
    impulse = np.zeros(len(t))
    impulse[100] = 1.0

    plt.figure(figsize=(14, 10))

    orders = [2, 4, 6, 8]
    for idx, order in enumerate(orders):
        mkf = MkFilter()
        mkf.design(filter_type='Bu', band_type='Lp', order=order, alpha1=0.2)

        # Resposta ao impulso
        impulse_response = apply_filter(impulse, mkf)

        # Resposta em frequência
        fft_response = np.fft.rfft(impulse_response)
        freqs = np.fft.rfftfreq(len(impulse_response), 1/fs)

        # Plot resposta ao impulso
        plt.subplot(2, 2, idx + 1)
        plt.plot(freqs, 20*np.log10(np.abs(fft_response) + 1e-10))
        plt.axvline(200, color='r', linestyle='--', alpha=0.5)
        plt.xlabel('Frequência (Hz)')
        plt.ylabel('Magnitude (dB)')
        plt.title(f'Ordem {order}: Transição {"suave" if order <= 4 else "abrupta"}')
        plt.xlim([0, 400])
        plt.ylim([-100, 10])
        plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('example5_orders.png', dpi=150)
    print("Gráfico salvo como: example5_orders.png")

    print("\nObservações:")
    print("- Ordem maior = transição mais abrupta")
    print("- Ordem maior = mais computação")
    print("- Para a maioria dos casos, ordem 2-6 é suficiente")


def main():
    """Executa todos os exemplos"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 15 + "MKFILTER.PY - EXEMPLOS DE USO" + " " * 24 + "║")
    print("╚" + "═" * 68 + "╝")

    try:
        example1_lowpass()
        example2_highpass()
        example3_bandpass()
        example4_chebyshev()
        example5_frequency_response()

        print("\n\n" + "=" * 70)
        print("TODOS OS EXEMPLOS CONCLUÍDOS COM SUCESSO!")
        print("=" * 70)
        print("\nArquivos gerados:")
        print("  - example1_lowpass.png")
        print("  - example2_highpass.png")
        print("  - example3_bandpass.png")
        print("  - example4_comparison.png")
        print("  - example5_orders.png")
        print("\nPara mais informações, consulte README_PYTHON.md")

    except ImportError as e:
        print(f"\nERRO: Biblioteca necessária não encontrada: {e}")
        print("Instale as dependências:")
        print("  pip install numpy matplotlib scipy")
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
