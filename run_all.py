import os
import subprocess

print("Iniciando bateria de testes com o Checker...\n")


sucessos = 0
falhas = 0

for i in range(1, 21):
    input_file = f"data/instance_{i:04d}.txt"
    output_file = f"saidas/saida_{i:04d}.txt"
    

    if os.path.exists(input_file) and os.path.exists(output_file):
        print(f"--- Avaliando Instância {i:04d} ---")
        
        resultado = subprocess.run(["python", "checker.py", input_file, output_file], capture_output=True, text=True)
        
        print(resultado.stdout.strip())
        
        if "True" in resultado.stdout:
            sucessos += 1
        else:
            falhas += 1
            
        print("-" * 40)
    else:
        print(f"PULOU: Saída ou entrada faltando para a instância {i:04d}\n")

print(f"\nResumo: {sucessos} soluções viáveis | {falhas} soluções inviáveis.")