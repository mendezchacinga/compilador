import re

# Expresiones regulares para identificar condicionales en español
condicional_pattern = re.compile(r'Si\s+(\w+)\s+es\s+(mayor|menor)\s+que\s+(\w+),\s+entonces\s+(.+)')

# Función para traducir una frase condicional a código C++
def traducir_condicional(frase):
    match = condicional_pattern.match(frase)
    if match:
        variable1, comparador, variable2, accion = match.groups()
        
        # Mapear comparadores en español a operadores en C++
        if comparador == "mayor":
            operador = ">"
        elif comparador == "menor":
            operador = "<"
        else:
            return "Error: Comparador no reconocido"
        
        # Generar el código C++
        codigo_cpp = f"if ({variable1} {operador} {variable2}) {{\n  // {accion}\n}}"
        return codigo_cpp
    else:
        return "Error: Frase no reconocida como condicional"
    
frase_condicional = "Si x es mayor que y, entonces imprime 'x es mayor'"
codigo_generado = traducir_condicional(frase_condicional)
print(codigo_generado)