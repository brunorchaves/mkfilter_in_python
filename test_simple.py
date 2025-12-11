#!/usr/bin/env python3
"""
Teste simples do mkfilter.py
Demonstra o uso básico sem dependências pesadas
"""

import sys
from mkfilter import MkFilter, generate_c_code


def test_butterworth_lowpass():
    """Teste 1: Filtro Butterworth Passa-Baixa"""
    print("=" * 70)
    print("TESTE 1: Butterworth Lowpass")
    print("=" * 70)

    mkf = MkFilter()
    xcoeffs, ycoeffs = mkf.design(
        filter_type='Bu',
        band_type='Lp',
        order=4,
        alpha1=0.1
    )

    print(f"[OK] Filtro criado com sucesso")
    print(f"  Ordem: 4")
    print(f"  Tipo: Butterworth Lowpass")
    print(f"  Alpha: 0.1")
    print(f"  Ganho: {mkf.get_gain():.6f}")
    print(f"  Nº coeficientes X: {len(xcoeffs)}")
    print(f"  Nº coeficientes Y: {len(ycoeffs)}")

    # Verificar que os polos estão dentro do círculo unitário
    import numpy as np
    poles_magnitude = np.abs(mkf.zplane.poles)
    all_stable = np.all(poles_magnitude < 1.0)

    if all_stable:
        print(f"[OK] Filtro estavel (todos os polos dentro do circulo unitario)")
        print(f"  Magnitude máxima dos polos: {poles_magnitude.max():.6f}")
    else:
        print(f"[WARN] AVISO: Filtro instavel!")

    return mkf


def test_highpass():
    """Teste 2: Filtro Passa-Alta"""
    print("\n" + "=" * 70)
    print("TESTE 2: Butterworth Highpass")
    print("=" * 70)

    mkf = MkFilter()
    xcoeffs, ycoeffs = mkf.design(
        filter_type='Bu',
        band_type='Hp',
        order=3,
        alpha1=0.2
    )

    print(f"[OK] Filtro passa-alta criado")
    print(f"  Ordem: 3")
    print(f"  Alpha: 0.2")
    print(f"  Ganho: {mkf.get_gain():.6f}")

    return mkf


def test_bandpass():
    """Teste 3: Filtro Passa-Faixa"""
    print("\n" + "=" * 70)
    print("TESTE 3: Butterworth Bandpass")
    print("=" * 70)

    mkf = MkFilter()
    xcoeffs, ycoeffs = mkf.design(
        filter_type='Bu',
        band_type='Bp',
        order=4,
        alpha1=0.1,
        alpha2=0.3
    )

    print(f"[OK] Filtro passa-faixa criado")
    print(f"  Ordem: 4")
    print(f"  Banda: 0.1 a 0.3")
    print(f"  Ganho: {mkf.get_gain():.6f}")

    return mkf


def test_chebyshev():
    """Teste 4: Filtro Chebyshev"""
    print("\n" + "=" * 70)
    print("TESTE 4: Chebyshev Lowpass")
    print("=" * 70)

    mkf = MkFilter()
    xcoeffs, ycoeffs = mkf.design(
        filter_type='Ch',
        band_type='Lp',
        order=4,
        alpha1=0.15,
        chebrip=-1.0
    )

    print(f"[OK] Filtro Chebyshev criado")
    print(f"  Ordem: 4")
    print(f"  Ripple: -1.0 dB")
    print(f"  Alpha: 0.15")
    print(f"  Ganho: {mkf.get_gain():.6f}")

    return mkf


def test_code_generation(mkf):
    """Teste 5: Geração de Código C"""
    print("\n" + "=" * 70)
    print("TESTE 5: Geração de Código C")
    print("=" * 70)

    c_code = generate_c_code(mkf)

    # Verificar que o código contém as partes esperadas
    checks = [
        ("#define NZEROS", "Definicao NZEROS"),
        ("#define NPOLES", "Definicao NPOLES"),
        ("#define GAIN", "Definicao GAIN"),
        ("xv[NZEROS+1]", "Buffer xv"),
        ("yv[NPOLES+1]", "Buffer yv"),
        ("filterStep", "Funcao filterStep"),
        ("return yv", "Return statement"),
    ]

    all_ok = True
    for check_str, description in checks:
        if check_str in c_code:
            print(f"  [OK] {description}")
        else:
            print(f"  [FAIL] {description} - NAO ENCONTRADO")
            all_ok = False

    if all_ok:
        print(f"\n[OK] Codigo C gerado com sucesso")
        print(f"  Tamanho: {len(c_code)} bytes")
        print(f"  Linhas: {c_code.count(chr(10))}")
    else:
        print(f"\n[FAIL] Codigo C com problemas")

    return all_ok


def test_filter_application():
    """Teste 6: Aplicação do Filtro a um Sinal"""
    print("\n" + "=" * 70)
    print("TESTE 6: Aplicação do Filtro")
    print("=" * 70)

    try:
        import numpy as np

        # Criar filtro
        mkf = MkFilter()
        xcoeffs, ycoeffs = mkf.design(
            filter_type='Bu',
            band_type='Lp',
            order=4,
            alpha1=0.1
        )

        # Criar sinal de teste: impulso
        signal = np.zeros(100)
        signal[10] = 1.0

        # Aplicar filtro
        gain = mkf.get_gain()
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

        # Verificar que o filtro produziu saída
        max_output = np.max(np.abs(output))
        energy = np.sum(output**2)

        print(f"[OK] Filtro aplicado ao sinal")
        print(f"  Amplitude máxima de saída: {max_output:.6f}")
        print(f"  Energia do sinal filtrado: {energy:.6f}")

        if max_output > 0 and energy > 0:
            print(f"[OK] Filtro esta produzindo saida valida")
            return True
        else:
            print(f"[FAIL] Filtro nao produziu saida valida")
            return False

    except ImportError:
        print("[SKIP] NumPy nao disponivel - teste de aplicacao ignorado")
        return None


def main():
    """Executa todos os testes"""
    print("\n")
    print("=" * 70)
    print(" " * 20 + "MKFILTER.PY - TESTES")
    print("=" * 70)
    print()

    results = {}

    try:
        # Teste 1
        mkf1 = test_butterworth_lowpass()
        results['Butterworth Lowpass'] = True

        # Teste 2
        mkf2 = test_highpass()
        results['Butterworth Highpass'] = True

        # Teste 3
        mkf3 = test_bandpass()
        results['Butterworth Bandpass'] = True

        # Teste 4
        mkf4 = test_chebyshev()
        results['Chebyshev'] = True

        # Teste 5
        code_ok = test_code_generation(mkf1)
        results['Geração de Código C'] = code_ok

        # Teste 6
        filter_ok = test_filter_application()
        if filter_ok is not None:
            results['Aplicação do Filtro'] = filter_ok

        # Resumo
        print("\n" + "=" * 70)
        print("RESUMO DOS TESTES")
        print("=" * 70)

        for test_name, result in results.items():
            status = "[OK] PASSOU" if result else "[FAIL] FALHOU"
            print(f"  {status:15} - {test_name}")

        all_passed = all(results.values())
        print()
        if all_passed:
            print("[OK] TODOS OS TESTES PASSARAM!")
            print("\nO mkfilter.py esta funcionando corretamente.")
            print("\nProximos passos:")
            print("  1. Veja exemplos em: example_usage.py")
            print("  2. Leia a documentacao: README_PYTHON.md")
            print("  3. Guia rapido: QUICK_START.md")
            return 0
        else:
            print("[FAIL] ALGUNS TESTES FALHARAM")
            return 1

    except Exception as e:
        print(f"\n[ERROR] ERRO DURANTE OS TESTES: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
