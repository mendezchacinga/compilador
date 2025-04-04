from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# Diccionario ampliado de traducciones
traducciones = {
    # Estructuras de control
    "si": "if",
    "sino": "else",
    "sino si": "else if",
    "en caso de que": "switch",
    "caso": "case",
    "por defecto": "default",
    "mientras": "while",
    "hacer mientras": "do while",
    "para": "for",
    "intentar": "try",
    "capturar": "catch",
    "lanzar": "throw",
    
    # Operadores y comparaciones
    "es menor que": "<",
    "es mayor que": ">",
    "es menor o igual que": "<=",
    "es mayor o igual que": ">=",
    "es igual a": "==",
    "no es igual a": "!=",
    "y": "&&",
    "o": "||",
    "no": "!",
    "negación": "!",
    "módulo": "%",
    "incrementar": "++",
    "decrementar": "--",
    
    # Palabras clave
    "retornar": "return",
    "romper": "break",
    "continuar": "continue",
    "clase": "class",
    "estructura": "struct",
    "enumeración": "enum",
    "plantilla": "template",
    "espacio de nombres": "namespace",
    "usar": "using",
    "público": "public",
    "privado": "private",
    "protegido": "protected",
    "este": "this",
    "nuevo": "new",
    "eliminar": "delete",
    "eliminar[]": "delete[]",
    "tamaño de": "sizeof",
    "tipo de": "typeid",
    "constante": "const",
    "estático": "static",
    "volátil": "volatile",
    "mutable": "mutable",
    "amigo": "friend",
    "operador": "operator",
    
    # Tipos de datos
    "entero": "int",
    "entero corto": "short",
    "entero largo": "long",
    "entero largo largo": "long long",
    "flotante": "float",
    "doble": "double",
    "doble largo": "long double",
    "carácter": "char",
    "carácter ancho": "wchar_t",
    "booleano": "bool",
    "vacío": "void",
    "auto": "auto",
    "nulo": "nullptr",
    
    # E/S y librerías
    "incluir": "#include",
    "lib estándar": "<iostream>",
    "lib cadenas": "<string>",
    "lib vectores": "<vector>",
    "lib mapas": "<map>",
    "imprimir": "std::cout <<",
    "leer": "std::cin >>",
    "fin de línea": "std::endl",
    "espacio de nombres estándar": "std",
    
    # Memoria
    "puntero": "*",
    "referencia": "&",
    "referencia constante": "const &",
    "puntero inteligente": "std::shared_ptr",
    "puntero único": "std::unique_ptr",
    
    # Excepciones
    "excepción": "exception",
    "rango inválido": "out_of_range",
    "desbordamiento": "overflow_error",
    
    # STL
    "vector": "std::vector",
    "mapa": "std::map",
    "par": "std::pair",
    "conjunto": "std::set",
    "cadena": "std::string",
    "iterador": "iterator"
}

def traducir_tipo(tipo):
    # Maneja tipos compuestos como "puntero a entero"
    if "puntero a" in tipo:
        return traducir_tipo(tipo.replace("puntero a", "").strip()) + "*"
    if "referencia a" in tipo:
        return traducir_tipo(tipo.replace("referencia a", "").strip()) + "&"
    return traducciones.get(tipo, tipo)

def traducir_valor(valor):
    # Maneja valores especiales
    if valor == "verdadero":
        return "true"
    if valor == "falso":
        return "false"
    if valor == "nulo":
        return "nullptr"
    return valor

def traducir_expresion(expresion):
    expresion = expresion.strip()
    
    # Manejar comparaciones primero
    comparaciones = {
        "es menor que": "<",
        "es mayor que": ">",
        "es menor o igual que": "<=",
        "es mayor o igual que": ">=",
        "es igual a": "==",
        "no es igual a": "!="
    }
    
    for espanol, op in comparaciones.items():
        if espanol in expresion:
            partes = expresion.split(espanol)
            if len(partes) == 2:
                izquierda = traducir_expresion(partes[0].strip())
                derecha = traducir_expresion(partes[1].strip())
                return f"{izquierda} {op} {derecha}"
    
    # Manejar operadores lógicos
    if " y " in expresion:
        partes = expresion.split(" y ")
        return " && ".join([traducir_expresion(p.strip()) for p in partes])
    
    if " o " in expresion:
        partes = expresion.split(" o ")
        return " || ".join([traducir_expresion(p.strip()) for p in partes])
    
    # Maneja operadores infijos
    ops_infijos = {
        "sumado con": "+",
        "restado con": "-",
        "multiplicado por": "*",
        "dividido por": "/",
        "módulo de": "%",
        "elevado a": "pow",
        "desplazado a la izquierda por": "<<",
        "desplazado a la derecha por": ">>"
    }
    
    for espanol, cpp in ops_infijos.items():
        if espanol in expresion:
            partes = expresion.split(espanol)
            if len(partes) == 2:
                izquierda = traducir_expresion(partes[0])
                derecha = traducir_expresion(partes[1])
                if cpp == "pow":
                    return f"std::pow({izquierda}, {derecha})"
                return f"({izquierda} {cpp} {derecha})"
    
    # Maneja llamadas a funciones
    match = re.match(r"([a-zA-ZáéíóúñÑ\s]+) de (.*)", expresion)
    if match:
        funcion = match.group(1).strip()
        argumentos = match.group(2).strip()
        if funcion in traducciones:
            return f"{traducciones[funcion]}({traducir_expresion(argumentos)})"
    
    # Maneja accesos a miembros
    if " de " in expresion:
        partes = expresion.split(" de ")
        objeto = traducir_expresion(partes[-1])
        for parte in reversed(partes[:-1]):
            objeto = f"{objeto}.{traducir_expresion(parte)}"
        return objeto
    
    # Reemplazo simple de palabras clave
    palabras = expresion.split()
    traducidas = [traducciones.get(p, p) for p in palabras]
    return " ".join(traducidas)

def traducir_declaracion_variable(declaracion):
    # Ejemplo: "entero x igual a 5"
    partes = declaracion.split()
    tipo = traducir_tipo(partes[0])
    nombre = partes[1]
    
    if len(partes) > 3 and partes[2] == "igual" and partes[3] == "a":
        valor = " ".join(partes[4:])
        return f"{tipo} {nombre} = {traducir_valor(valor)};"
    return f"{tipo} {nombre};"

# Analisis Lexico y Sintactico
def traducir_funcion(declaracion, cuerpo):
    # Ejemplo: "entero función suma(entero a, entero b) que retorna a + b"
    match = re.match(r"([a-zA-ZáéíóúñÑ\s]+)\s+funci[óo]n\s+([a-zA-Z_]\w*)\s*\((.*)\)", declaracion)
    if not match:
        return declaracion
    
    tipo_retorno = traducir_tipo(match.group(1).strip())
    nombre = match.group(2)
    parametros = match.group(3)
    
    # Traducir parámetros
    params_trad = []
    for param in parametros.split(","):
        param = param.strip()
        if not param:
            continue
        partes_param = param.split()
        tipo_param = traducir_tipo(partes_param[0])
        nombre_param = partes_param[1]
        params_trad.append(f"{tipo_param} {nombre_param}")
    
    # Traducir cuerpo
    cuerpo_trad = cuerpo.strip()
    if cuerpo_trad.startswith("retorna "):
        cuerpo_trad = f"return {traducir_expresion(cuerpo_trad[8:])};"
    else:
        cuerpo_trad = traducir_frase(cuerpo_trad)
    
    return f"{tipo_retorno} {nombre}({', '.join(params_trad)}) {{\n    {cuerpo_trad}\n}}"
# Analisis Lexico y Sintactico
def traducir_frase(frase):
    frase = frase.strip().lower()
    
    # Estructuras de control
    if frase.startswith("si "):
        partes = frase[3:].split(" entonces")
        condicion = traducir_expresion(partes[0].strip())
        codigo = f"if ({condicion})"
        if len(partes) > 1 and partes[1].strip():
            cuerpo = traducir_frase(partes[1].strip())
            codigo += " {\n    " + cuerpo + "\n}"
        return codigo
    
    elif frase.startswith("sino si "):
        partes = frase[8:].split(" entonces")
        condicion = traducir_expresion(partes[0].strip())
        codigo = f"else if ({condicion})"
        if len(partes) > 1 and partes[1].strip():
            cuerpo = traducir_frase(partes[1].strip())
            codigo += " {\n    " + cuerpo + "\n}"
        return codigo
    
    elif frase == "sino":
        return "else"
    
    elif frase.startswith("mientras "):
        partes = frase[9:].split(" hacer")
        condicion = traducir_expresion(partes[0].strip())
        codigo = f"while ({condicion})"
        if len(partes) > 1 and partes[1].strip():
            cuerpo = traducir_frase(partes[1].strip())
            codigo += " {\n    " + cuerpo + "\n}"
        return codigo
    
    elif frase.startswith("para "):
        partes = frase[5:].split(" hacer")
        config = partes[0].strip()
        # Formato: "para i desde 0 hasta 10 paso 1"
        match = re.match(r"([a-zA-Z_]\w*)\s+desde\s+(.*)\s+hasta\s+(.*?)(?:\s+paso\s+(.*))?", config)
        if match:
            var = match.group(1)
            inicio = traducir_expresion(match.group(2))
            fin = traducir_expresion(match.group(3))
            paso = match.group(4)
            if paso:
                codigo = f"for (int {var} = {inicio}; {var} <= {fin}; {var} += {paso})"
            else:
                codigo = f"for (int {var} = {inicio}; {var} <= {fin}; ++{var})"
        else:
            codigo = f"for ({config})"
        
        if len(partes) > 1 and partes[1].strip():
            cuerpo = traducir_frase(partes[1].strip())
            codigo += " {\n    " + cuerpo + "\n}"
        return codigo
    
    # Declaración de variables
    elif any(frase.startswith(tipo + " ") for tipo in ["entero", "flotante", "doble", "carácter", "booleano", "cadena"]):
        return traducir_declaracion_variable(frase)
    
    # Funciones
    elif " función " in frase or "función " in frase:
        partes = frase.split(" que ")
        if len(partes) > 1:
            return traducir_funcion(partes[0], partes[1])
    
    # Inclusión de librerías
    elif frase.startswith("incluir "):
        lib = frase[8:].strip()
        if lib in traducciones:
            lib = traducciones[lib]
        return f'#include {lib}'
    
    # Espacio de nombres
    elif frase.startswith("usar espacio de nombres "):
        ns = frase[24:].strip()
        return f"using namespace {ns};"
    
    # Imprimir
    elif frase.startswith("imprimir "):
        contenido = traducir_expresion(frase[9:])
        return f'std::cout << {contenido} << std::endl;'
    
    # Leer
    elif frase.startswith("leer "):
        variable = traducir_expresion(frase[5:])
        return f'std::cin >> {variable};'
    
    # Asignaciones
    elif " igual a " in frase:
        variable, valor = frase.split(" igual a ")
        return f"{traducir_expresion(variable)} = {traducir_expresion(valor)};"
    
    # Expresiones simples
    resultado = traducir_expresion(frase)
    if not frase.endswith(";") and not frase.endswith("}") and not frase.endswith("{"):
        resultado += ";"
    return resultado

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/traducir', methods=['POST'])
def traducir():
    texto = request.form['texto']
    codigo = traducir_frase(texto)
    return jsonify({'codigo': codigo})

if __name__ == '__main__':
    app.run(debug=True)